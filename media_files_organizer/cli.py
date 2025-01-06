import argparse
import sys
import os
import requests
import re
from dotenv import load_dotenv
from rich.layout import Layout
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from rich.live import Live
#from tmdb_metadata import TMDBMetadata

console = Console()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Media Files Organizer: Organize TV Shows, Movies, or People-related media files."
    )

    # Define common positional arguments
    parser.add_argument(
        "tmdb_id", 
        type=int, 
        help="The TMDB ID for the media. This is required for fetching metadata."
    )
    parser.add_argument(
        "directory_path", 
        nargs="?", 
        default=os.getcwd(), 
        type=str, 
        help="The absolute or relative path to the directory where modifications will be performed. Defaults to the current working directory."
    )

    # Define flags
    parser.add_argument(
        "-t", "--tvshow", 
        action="store_true", 
        help="Specify if organizing a TV show."
    )
    parser.add_argument(
        "-m", "--movie", 
        action="store_true", 
        help="Specify if organizing a movie."
    )
    parser.add_argument(
        "-p", "--person", 
        action="store_true", 
        help="Specify if organizing media related to a person."
    )

    parser.add_argument(
        "-n", "--nfo", 
        action="store_true", 
        help="Only generate nfo metadata files for each episode or movie"
    )


    # Specific arguments for TV show
    parser.add_argument(
        "-s", "--season", 
        type=int, 
        help="Specify the season number if organizing a TV show. This is optional."
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate that one and only one of the flags is set
    if sum([args.tvshow, args.movie, args.person]) != 1:
        console.print("[red]Error: You must specify exactly one of --tvshow, --movie, or --person.[/red]")
        parser.print_help()
        sys.exit(1)

    return args


def list_supported_files(directory):
    supported_extensions = {".mp4", ".mkv"}
    media_files = []

    # Ensure the directory exists
    if not os.path.isdir(directory):
        console.print(f"Error: The directory '{directory}' does not exist.")
        sys.exit(1)

    # List files and filter by supported extensions in the root directory only
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)) and os.path.splitext(file)[1].lower() in supported_extensions:
            media_files.append(os.path.join(directory, file))

    if not media_files:
        console.print(f"No supported files (.mp4, .mkv) found in directory '{directory}'.")
        sys.exit(1)

    return media_files

def sanitize_filename(filename):
    # Remove forbidden characters for both Windows and Unix-like systems
    return re.sub(r'[\/:*?"<>|]', '', filename)

def confirm_metadata(data, is_tvshow, season=None):
    if is_tvshow:
        name = data.get("name", "Unknown TV Show")
        year = data.get("first_air_date", "Unknown Year")[:4]
        console.print(f"TV Show: {name} ({year})")
        if season:
            console.print(f"Season: {season}")
        # Interactive prefix confirmation for TV shows
        prefix = console.input("Enter a prefix for the TV show name (leave blank to keep as is): ")
        if prefix:
            data["name"] = f"{prefix} {name}"
            console.print(f"Updated TV Show Name: {data['name']}")
    else:
        name = data.get("title", "Unknown Movie")
        year = data.get("release_date", "Unknown Year")[:4]
        console.print(f"Movie: {name} ({year})")

    response = Confirm.ask("Is this information correct?")
    if not response:
        console.print("Aborting operation.")
        sys.exit(0)

def infer_season_from_filenames(media_files, season_to_test_against=None):
    season = season_to_test_against
    season_pattern = re.compile(r'(?:S|T)(\d{1,2})E\d{1,2}', re.IGNORECASE)

    for file in media_files:
        match = season_pattern.search(os.path.basename(file))
        if match:
            current_season = int(match.group(1))
            if season is None:
                season = current_season
            elif season != current_season:
                console.print(f"[red]Error: Mixed seasons detected in filenames. Found season {season} and {current_season}. Culprit file: {file}")
                sys.exit(1)

    if season is None:
        console.print("[red]Error: Could not infer season from filenames. Ensure filenames follow a pattern like S01E01.")
        sys.exit(1)

    return season

def extract_episode_number(filename):
    patterns = [
        r"(?:S\d{1,2}E(\d{1,2}))",  # Matches S01E01
        r"\bE(\d{1,2})\b",          # Matches E01
        r"Ep\.?(\d{1,2})",          # Matches Ep01, Ep.01
        r"^\d{1,2}\s+",             # Matches numbers at the start followed by space
        r"\b(\d{1,2})\b",           # Matches standalone numbers (final fallback)
        r"-\s*(\d{1,2})\s"          # Matches dash patterns
    ]

    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return int(match.group(1))

    console.print(f"[yellow]Warning: Could not extract episode number from filename: {filename}")
    return None

def generate_table(table_status):
    table = Table(title="Proposed File Renaming")
    table.add_column("Old Filename", justify="left", style="red")
    table.add_column("New Filename", justify="left", style="green")
    table.add_column("Status", justify="center", style="bold cyan")

    for old, new, status in table_status:
        table.add_row(old, new, f"[yellow]{status}[/yellow]")

    return table

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )
    layout["upper"].ratio = 4
    return layout

def rename_tv_show_files(media_files, data, season):
    series_name = sanitize_filename(data.get("name", "Unknown Show"))
    episodes = {ep["episode_number"]: ep.get("name", "Unknown Episode") for ep in data.get("episodes", [])}

    rename_pairs = []
    table_status = []
    parsed_media_files = []

    for file in media_files:
        episode_number = extract_episode_number(os.path.basename(file))
        nhecos = False
        if episode_number is None:
            new_path = file
            nhecos = True
        else:
            episode_title = sanitize_filename(episodes.get(episode_number, f"Episode {episode_number}"))
            extension = os.path.splitext(file)[1]
            new_name = f"{series_name}.S{season:02}E{episode_number:02}.{episode_title}{extension}"
            new_path = os.path.join(os.path.dirname(file), new_name)

        rename_pairs.append((file, new_path))
        if nhecos:
            table_status.append((os.path.basename(file), os.path.basename(new_path), "Skipping"))
            parsed_media_files.append(file)
        else:
            table_status.append((os.path.basename(file), os.path.basename(new_path), "Pending"))
            parsed_media_files.append(new_path)
        
    
    
    # Display proposed changes
    console.clear()
    table = generate_table(table_status)
    console.print(table)

    # Confirm with user
    confirm = Confirm.ask("Do you want to proceed with these changes?")
    if not confirm:
        console.print("Aborting operation.")
        sys.exit(0)

    console.clear()

    with Live(generate_table(table_status), refresh_per_second=4) as live:
        for i, (old, new) in enumerate(rename_pairs):
            try:
                os.rename(old, new)
                status = "[green]✔ Success[/green]"
            except Exception as e:
                status = f"[red]✘ Error: {str(e)}[/red]"

            table_status[i] = (os.path.basename(old), os.path.basename(new), status)
            live.update(generate_table(table_status))
    
    console.print("Renaming complete.")
    return parsed_media_files


def rename_movie_file(movie_file, data):
    title = sanitize_filename(data.get("title", "Unknown Movie").replace(" ", "_"))
    year = data.get("release_date", "Unknown Year")[:4]
    extension = os.path.splitext(movie_file)[1]
    new_name = f"{title}({year}){extension}"
    new_path = os.path.join(os.path.dirname(movie_file), new_name)

    try:
        os.rename(movie_file, new_path)
        console.print(f"Renamed file to: {new_path}")
    except Exception as e:
        console.print(f"[red]Error renaming file: {e}")


def generate_nfo_files_for_show(media_files, data, season):
    series_name = sanitize_filename(data.get("name", "Unknown Show"))
    episodes = {ep["episode_number"]: ep for ep in data.get("episodes", [])}

    for file in media_files:
        episode_number = extract_episode_number(os.path.basename(file))
        if episode_number is None:
            console.print(f"[red]Skipping .nfo generation for {file}: Episode number could not be determined.[/red]")
            continue

        episode_data = episodes.get(episode_number)
        if not episode_data:
            console.print(f"[red]No metadata found for episode {episode_number} in {file}.[/red]")
            continue

        # Generate .nfo content
        nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<episodedetails>
    <lockdata>false</lockdata>
    <title>{episode_data.get("name", "Unknown Title")}</title>
    <season>{episode_data.get("season_number", "Unknown Season")}</season>
    <episode>{episode_number}</episode>
    <showtitle>{series_name}</showtitle>
    <aired>{episode_data.get("air_date", "Unknown Date")}</aired>
    <plot>{episode_data.get("overview", "No description available.")}</plot>
</episodedetails>
"""

        # Save the .nfo file
        nfo_path = os.path.splitext(file)[0] + ".nfo"
        try:
            with open(nfo_path, "w", encoding="utf-8") as nfo_file:
                nfo_file.write(nfo_content)
            print(f"Generated .nfo file: {nfo_path}")
        except Exception as e:
            print(f"Error generating .nfo file for {file}: {e}")


    nfo_content = f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<episodedetails>
    <title>{episode_data.get("name", "Unknown Title")}</title>
    <season>{episode_data.get("season_number", "Unknown Season")}</season>
    <episode>{episode_number}</episode>
    <showtitle>{series_name}</showtitle>
    <aired>{episode_data.get("air_date", "Unknown Date")}</aired>
    <plot>{episode_data.get("overview", "No description available.")}</plot>
</episodedetails>



    """
    pass

def main():
    # Load environment variables from .env file
    load_dotenv()
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

    if not TMDB_API_KEY:
        console.print("[red]Error: TMDB_API_KEY not set in .env file or environment variables.[/red]")
        sys.exit(1)

    args = parse_arguments()

    # Get supported media files
    media_files = list_supported_files(args.directory_path)

    
    if args.movie:
        # Ensure there is exactly one supported file for a movie
        if len(media_files) != 1:
            console.print(f"[red]Error: Expected exactly one .mp4 or .mkv file for a movie, but found {len(media_files)}.[/red]")
            sys.exit(1)

        console.print(f"Flag set: Movie. TMDB ID: {args.tmdb_id}, Directory Path: {args.directory_path}")
        data = fetch_tmdb_data(TMDB_API_KEY, args.tmdb_id, "movie")
        confirm_metadata(data, is_tvshow=False)

        console.print("Generating NFO files for movie.")

        if not args.nfo:
            media_files = rename_movie_file(media_files[0], data)
        
        #generate_nfo_files_for_movie(media_files, data)


    elif args.tvshow:
        print(f"Flag set: TV Show. TMDB ID: {args.tmdb_id}, Directory Path: {args.directory_path}")
        if args.season:
            console.print(f"Season specified: {args.season}")
            season = infer_season_from_filenames(media_files, season_to_test_against=args.season)
            data = fetch_tmdb_data(TMDB_API_KEY, args.tmdb_id, "tv", season=args.season)
        else:
            season = infer_season_from_filenames(media_files)
            console.print(f"Inferred season: {season}")
            data = fetch_tmdb_data(TMDB_API_KEY, args.tmdb_id, "tv", season=season)

        
        confirm_metadata(data, is_tvshow=True, season=args.season)

        # Rename files
        if not args.nfo:
            media_files = rename_tv_show_files(media_files, data, season)

        generate_nfo_files_for_show(media_files, data)



    elif args.person:
        console.print("Flag set: Person. Not implemented yet.")
        sys.exit(0)

# Ensures the script runs when executed directly
if __name__ == "__main__":
    main()
