import argparse
import os
import sys
import re
#import time
from typing import Literal, Optional, TypedDict
from dotenv import load_dotenv
import requests
from rich.layout import Layout
from rich.console import RenderableType
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.table import Table
from media_files_organizer.nfo_generator import NFO
from media_files_organizer.tmdb_metadata import TMDBMetadata
from media_files_organizer.rich_ext.panel_input import InputHandler
from metadata_types import Actor, Season, Episode
from media_files_organizer.db_connector import DBActorWithRole, DBConnector  # Add this line to import DBConnector


class EpFile(TypedDict):
    episode_num: int
    path: str
    ext: str
    original_filename: str
    new_filename: str
    naked_filename: str
    status: Optional[Literal["OK", "ERROR"]]
    data: Episode|None


class MediaFilesOrganizer:

    episode_num_patterns: list[re.Pattern[str]] = [
        re.compile(r"(?:S\d{1,2}E(\d{1,2}))"),  # Matches S01E01
        re.compile(r"\bE(\d{1,2})\b"),          # Matches E01
        re.compile(r"Ep\.?(\d{1,2})"),          # Matches Ep01, Ep.01
        re.compile(r"EP\.?(\d{1,2})"),          # Matches Ep01, Ep.01
        re.compile(r"^\d{1,2}\s+"),             # Matches numbers at the start followed by space
        re.compile(r"\b(\d{1,2})\b"),           # Matches standalone numbers (final fallback)
        re.compile(r"-\s*(\d{1,2})\s")          # Matches dash patterns
    ]

    def __init__(self):
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=4)
        )

        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )

        self.layout["header"].update(
            Panel(Align.center("MEDIA FILES ORGANIZER", vertical="middle"), border_style="blue")
        )

        self.layout["main"]["left"].update(
            Panel("", border_style="blue")
        )

        self.right_table = Table(show_header=False, box=None)

        self.layout["main"]["right"].update(
            Panel(self.right_table, border_style="blue", title="Status Information")
        )

        self.layout["footer"].update(
            Panel("", border_style="blue")
        )
        self.live = Live(self.layout, refresh_per_second=4, redirect_stderr=False)
        self.console = self.live.console
        self.input_handler = InputHandler(self.layout, "footer")  # Initialize InputHandler
        self.args: argparse.Namespace | None = None
    
    def start(self):
        # Start the live display
        self.live.start()

    def stop(self):
        # Stop the live display
        self.live.stop()

    def __del__(self):
        self.live.stop()

    def parse_arguments(self) -> argparse.Namespace:
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
            "-a", "--suffix", 
            type=str,
            help="Specify if the season name should be added to the filename. This is optional."
        )

        # Specific arguments for TV show
        parser.add_argument(
            "-s", "--season", 
            type=int,
            help="Specify the season number if organizing a TV show. This is optional."
        )

        # SGeneral flag
        parser.add_argument(
            "-f", "--force", 
            type=int,
            help="Force the operation without asking for confirmation."
        )

        # Parse arguments
        args = parser.parse_args()
        self.args = args

        # Validate that one and only one of the flags is set
        if sum([args.tvshow, args.movie, args.person]) != 1:
            self.print("[red]Error: You must specify exactly one of --tvshow, --movie, or --person.[/red]\n")
            self.print(parser.format_help(), mode="a", title="ERROR", border_style="red")
            parser.print_help()
            sys.exit(1)

        return args

    def list_supported_files(self, directory: str) -> list[str]:
        supported_extensions = {".mp4", ".mkv", ".avi", ".m4v", "wmv"}
        media_files: list[str] = []

        # Ensure the directory exists
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Error: The directory '{directory}' does not exist.")

        # List files and filter by supported extensions in the root directory only
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)) and os.path.splitext(file)[1].lower() in supported_extensions:
                media_files.append(os.path.join(directory, file))

        if not media_files:
            raise FileNotFoundError(f"No supported files (mp4, mkv, avi, m4v or wmv) found in directory '{directory}'.")

        return media_files


    def infer_season_from_filenames(self, media_files: list[str], season_to_test_against: str|None = None) -> int:
        season = season_to_test_against
        season_pattern = re.compile(r'(?:S|T)(\d{1,2})E\d{1,2}', re.IGNORECASE)

        for file in media_files:
            match = season_pattern.search(os.path.basename(file))
            if match:
                current_season = int(match.group(1))
                if season is None:
                    season = current_season
                elif season != current_season:
                    raise ValueError(f"Mixed seasons detected in filenames. Found season {season} and {current_season}. Culprit file: {file}")

        if season is None:
            raise ValueError("Could not infer season from filenames. Ensure filenames follow a pattern like S01E01.")

        return int(season)
    
    def infer_episode_number_from_filename(self, filename: str) -> EpFile:
        for pattern in self.episode_num_patterns:
            match = pattern.search(filename)
            if match:
                return {
                    "episode_num": int(match.group(1)),
                    "path": os.path.dirname(filename),
                    "ext": os.path.splitext(filename)[1],
                    "original_filename": os.path.basename(filename),
                    "naked_filename": "",
                    "new_filename": "",
                    "status": None,
                    "data": None
                }
        raise ValueError(f"Could not infer episode number from filename: {filename}")

    def _sanitize_filename(self, filename: str):
        # Remove forbidden characters for both Windows and Unix-like systems
        return re.sub(r'[\/:*?"<>|]', '', filename)

    def create_new_episode_filename(self, data: Episode, season: int, ext: str, suffix: str|None = None) -> tuple[str, str]:
        series_name = self._sanitize_filename(data["series_name"])
        episode_name = self._sanitize_filename(data["episode_name"])
        episode_number = f"{data['episode_number']:02}"
        season_number = f"{season:02}"

        if suffix:
            new_filename = F"{series_name} {suffix}.S{season_number}E{episode_number}.{episode_name}{ext}"
            naked_filename = F"{series_name} {suffix}.S{season_number}E{episode_number}.{episode_name}"
        else:
            new_filename = F"{series_name}.S{season_number}E{episode_number}.{episode_name}{ext}"
            naked_filename = F"{series_name}.S{season_number}E{episode_number}.{episode_name}"
        
        new_filename = self._sanitize_filename(new_filename)
        naked_filename = self._sanitize_filename(naked_filename)
        return (new_filename, naked_filename)
    
    def table_with_files(self, episode_filelist: list[EpFile]) -> Table:
        table = Table()
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Original Filename", justify="left", style="magenta")
        table.add_column("New Filename", justify="left", style="green")
        table.add_column("", justify="center", style="bold cyan")
        

        for file in episode_filelist:
            status = {"OK": "[green]✓[/green]", "ERROR": "[red]✕[/red]"}.get(str(file.get("status", "")), "")
            table.add_row(str(file["episode_num"]), file["original_filename"], file["new_filename"], status)
        
        return table

    def print_error(self, message: str, title: str = "ERROR") -> None:
        self.print(f"[red]Error: {message}[/red]", title=title, border_style="red", mode="a", side = "left")

    def print_warning(self, message: str, title: str = "WARNING") -> None:
        self.print(f"[yellow]Warning: {message}[/yellow]", title=title, border_style="yellow", mode="a", side = "left")

    def print_notice(self, message: str, title: str = "NOTICE") -> None:
        self.print(f"[blue]Notice: {message}[/blue]", title=title, border_style="blue", mode="a", side = "left")

    def print_a(self, message: str) -> None:
        self.print(message, mode="a")

    def render(self, renderable: RenderableType) -> None:
        self.print(renderable, mode="r")

    def render_left(self, renderable: RenderableType) -> None:
        self.print(renderable, mode="r", side="left")

    def print_left(self, message: str) -> None:
        self.print(message, mode="a", side="left")

    def print_right(self, message: str, title: str = "Status Information") -> None:
        self.print(message, mode="a", side="right", title=title)

    # Function to update "main" content dynamically
    def print(self, new_content: str|RenderableType, mode: Literal["r", "a"] = "r", title: str|None = None, border_style: str = "blue", side: Literal["l", "left", "r", "right"] = "left") -> None:
        """
        Updates the 'main' content of the layout.

        Parameters:
            new_content (str | RenderableType): The new content to display.
            mode (str): The mode to use. 'r' to replace existing content, 'a' to append.
            title (str): The title of the panel.
            border_style (str): The border style of the panel.
            side (str): The side to update. 'l' or 'left' for left side, 'r' or 'right' for right side.
        
        Returns:
            None
        """
        lyt = self.layout["main"]["right"] if side in ["r", "right"] else self.layout["main"]["left"]

        renderable = lyt.renderable
        current_content = ""
        if isinstance(renderable, Panel) and isinstance(renderable.renderable, str):
            current_content = renderable.renderable  # Extract existing text if it's a string

        if mode == "a":
            updated_content = f"{current_content}\n{new_content}"
        elif mode == "r":
            updated_content = new_content
        else:
            raise ValueError("Invalid mode. Use 'r' to replace or 'a' to append.")

        lyt.update(Panel(updated_content, border_style=border_style, title=title))

    def confirm(self, msg: str) -> bool:
        """
        Displays a confirm prompt in the footer and captures user confirmation.
        """
        confirmed = self.input_handler.get_confirmation(f"{msg}") # type: ignore
        #self.live.refresh() # Ensure the live layout updates immediately
        return confirmed
    
    def dbactor_to_actor(self, dbactor: DBActorWithRole) -> Actor:
        name = dbactor["name"]
        initial = name[0].upper()
        return Actor(
            name=dbactor["name"],
            original_name=dbactor.get("full_name"),
            type="actor",  # Defaulting to "actor" or modify based on context
            role=dbactor["role"],
            photo=dbactor.get("photo_src_url"),
            thumb=f"/config/data/metadata/People/{initial}/{name}/folder.jpg"
        )
    
    def download_image(self, episode: EpFile):
        if not episode["data"]:
            self.print_a(f"No metadata found for episode {episode['episode_num']}. Skipping image download.")
            return
        
        url = episode["data"]["still_url"]
        final_filename = os.path.join(episode["path"], f"{episode['naked_filename']}-thumb.jpg")
        
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(final_filename, "wb") as image_file:
                for chunk in response.iter_content(1024):
                    image_file.write(chunk)
            self.print_a(f"Image saved as {final_filename}")
        else:
            self.print_error(f"Failed to download image. Status code: {response.status_code}")


## TODO - Implemente the force flag
## TODO - move tvshow function to a method in the MediaFilesOrganizer class
## TODO - Refactor main function so that its logic is in the MediaFilesOrganizer class



def tvshow(args: argparse.Namespace, mfo: MediaFilesOrganizer, tmdb: TMDBMetadata, media_files: list[str], directory: str, dbconn: DBConnector) -> None:
    # Let's validate the season number against the filenames
    # Infer the season from the filenames
    if args.season:
        mfo.print_left(f"Testing if filenames don't match passed season {args.season}...")
        try:
            season = mfo.infer_season_from_filenames(media_files, season_to_test_against=args.season)
        except ValueError as e:
            mfo.print_error(str(e))
            sys.exit(1)
        mfo.print_left(f"[green]Everything looks good. Season {args.season} confirmed.[/green]")
    else:
        mfo.print_left("No -s flag passed. Inferring season from filenames...")
        try:
            season = mfo.infer_season_from_filenames(media_files)
            mfo.print(f"Inferred season: {season}")
        except ValueError as e:
            mfo.print_error(str(e))
            sys.exit(1)

    mfo.right_table.add_row("Season:", str(season))


    # check if episode number in each file can be inferred
    mfo.print_left("Checking if episode numbers can be inferred from filenames...")
    warnings = False
    episode_filelist: list[EpFile] = []
    for file in media_files:
        try:
            episode_filelist.append(mfo.infer_episode_number_from_filename(file))
        except ValueError as e:
            warnings = True
            mfo.print_warning(str(e))
    
    if len(episode_filelist) != len(media_files):
        warnings = True
        mfo.print_warning(f"Some episode numbers could not be inferred.\nExpected: {len(media_files)}\nFound: {len(episode_filelist)}")

    if warnings:
        proceed = mfo.input_handler.get_confirmation("Some episode numbers could not be inferred. Do you want to proceed?", border_style="yellow")
        if not proceed:
            mfo.print_a("Exiting...")
            sys.exit(0)
        else:
            mfo.print_a("Proceeding with the available episode numbers.")
            
    warnings = False


    #proceed: bool = mfo.input_handler.get_confirmation("Do you want to proceed with the above settings?")
    #if not proceed:
    #    mfo.print("Exiting...")
    #    sys.exit(0)
    

    # Fetch TV show metadata
    mfo.print_left("Fetching TV show metadata...")
    try:
        data: Season = tmdb.fetch_tvshow_season(args.tmdb_id, season)
    except Exception as e:
        mfo.print_error(str(e))
        sys.exit(1)
    
    mfo.print_left("Done fetching metadata.")
    name = data["series_name"]
    ep_count = data["episode_count"]
    season_name = data["season_name"]
    mfo.right_table.add_row("TV Show Name:", name)
    mfo.right_table.add_row("Season name:", season_name)
    mfo.right_table.add_row("Nº of Season Episodes:", str(ep_count))



    # fetch portuguese metadata from local database
    db_season_id = dbconn.get_season_id_of_tvshow_by_tmdb_id(args.tmdb_id, season)
    if db_season_id:
        mfo.print_left("Fetching Portuguese metadata from local database...")
        db_actors = dbconn.get_actors_of_season(db_season_id)
        mfo.right_table.add_row("PT Season ID:", str(db_season_id))
    else:
        mfo.right_table.add_row("PT Season ID:", "[red]Not found[/red]")
        db_actors = []

    # validate metadada
    # 1. Check if the number of episodes in the metadata matches the number of files
    if ep_count != len(media_files):
        warnings = True
        mfo.print_warning(f"Number of episodes in metadata ({ep_count}) does not match the number of files ({len(media_files)}).")
    
    # 2. Check if the season name matches the inferred season
    if data["season_number"] != season:
        warnings = True
        mfo.print_warning(f"Season number in metadata ({data["season_number"]}) does not match the inferred season ({season}).")
    
    # if warnings, ask the user if they want to proceed
    if warnings:
        proceed = mfo.input_handler.get_confirmation("Some metadata mismatch was found. Do you want to proceed with the above settings?", border_style="yellow")
        if not proceed:
            mfo.print_a("Exiting...")
            sys.exit(0)
    else:
        mfo.print_left("[green]Everything looks good. Metadata validated successfully.[/green]")
        proceed = mfo.input_handler.get_confirmation("Do you wish to proceed with file renaming and metadata file creation?", border_style="green")
        if not proceed:
            mfo.print_a("Exiting...")
            sys.exit(0)

    # first let's update episode_filelist with the new filenames
    for file in episode_filelist:
        ep_num = file["episode_num"]
        episode_data: Episode|None = next((ep for ep in data["episodes"] if ep["episode_number"] == ep_num), None)
        if episode_data:
            (file["new_filename"], file["naked_filename"]) = mfo.create_new_episode_filename(episode_data, season, ext=file["ext"], suffix=args.suffix)
            file["data"] = episode_data
    
    # Display the proposed file renaming table
    mfo.render(mfo.table_with_files(episode_filelist))

    proceed = mfo.input_handler.get_confirmation("Do you wish to proceed with file renaming and metadata file creation?", border_style="green")
    if not proceed:
        mfo.print_a("Exiting...")
        sys.exit(0)

    # Rename files
    warnings = False
    count_fails = 0
    for file in episode_filelist:
        if file["new_filename"]:
            try:
                os.rename(os.path.join(file["path"], file["original_filename"]), os.path.join(file["path"], file["new_filename"]))
                file["status"] = "OK"
            except Exception as e:
                warnings = True
                count_fails = count_fails + 1
                file["status"] = "ERROR"
            
            mfo.render(mfo.table_with_files(episode_filelist))
            #time.sleep(0.1)  # Add a slight delay to show the status update
    
    mfo.right_table.add_row("File renaming:", "[green]Done[/green]" if not warnings else f"[red]{count_fails} errors[/red]")

    # Generate NFO files

    mfo.print_left("Generating NFO files...")
    
    proceed = mfo.input_handler.get_confirmation("Do you wish to proceed with metadata NFO file generation?", border_style="green")
    if not proceed:
        mfo.print("Exiting...", mode="r")
        sys.exit(0)

    new_actors = [mfo.dbactor_to_actor(person) for person in db_actors] + data["actors"]
    data["actors"] = new_actors
    nfo = NFO(data)
    season_nfo = nfo.generate_tvshow_season()

    # Save the season NFO file
    with open(os.path.join(directory, "season.nfo"), "w", encoding="utf-8") as f:
        f.write(season_nfo)

    for episode in episode_filelist:
        if episode["data"]:
            if len(db_actors) != 0:
                new_actors = [mfo.dbactor_to_actor(person) for person in db_actors] + episode["data"]["actors"]
                episode["data"]["actors"] = new_actors
            episode_nfo = nfo.generate_tvshow_episode(episode["data"], os.path.join(episode["path"], episode["new_filename"]))

            # Save the episode NFO file
            with open(os.path.join(episode["path"], f"{episode['naked_filename']}.nfo"), "w", encoding="utf-8") as f:
                f.write(episode_nfo)

    mfo.print_left("NFO files generated successfully.")
    mfo.right_table.add_row("NFO files:", "[green]Done[/green]")

    proceed = mfo.input_handler.get_confirmation("Do you wish to download episodes thumbnails?", border_style="green")
    if not proceed:
        mfo.print("Exiting...", mode="r")
        sys.exit(0)

    for episode in episode_filelist:
        if episode["data"]:
            mfo.download_image(episode)

    mfo.right_table.add_row("thumbnails:", "[green]Done[/green]")

def main():

    # Initialize the MediaFilesOrganizer class
    mfo = MediaFilesOrganizer()

    try:
        # start the live display for beauty
        mfo.start()

        # Load environment variables from .env file
        load_dotenv()
        TMDB_API_KEY = os.getenv("TMDB_API_KEY") # pylint: disable=invalid-name
        DB_PATH = os.getenv("DB_PATH") # pylint: disable=invalid-name

        # Ensure the TMDB API key is set
        if not TMDB_API_KEY:
            mfo.print_error("[red]TMDB API key not found in environment variables.[/red]")
            sys.exit(1)

        # Ensure the DB_PATH key is set
        if not DB_PATH:
            mfo.print_error("[red]DB_PATH key not found in environment variables.[/red]")
            sys.exit(1)

        # Initialize the TMDBMetadata class, responsible for fetching metadata from TMDB
        tmdb = TMDBMetadata(api_key=TMDB_API_KEY)
        dbconn = DBConnector(DB_PATH)  # Initialize the DBConnector class

        
        # Parse command-line arguments
        args = mfo.parse_arguments()
        
        # Get supported media files
        media_files = mfo.list_supported_files(args.directory_path)

        # First output the arguments for validation
        # should be roughly the same irrespective of the flag set
        
        mfo.right_table.add_row("TMDB_API_KEY:", TMDB_API_KEY)
        mfo.right_table.add_row("TMDB ID:", str(args.tmdb_id))
        mfo.right_table.add_row("Flag set:", "TV Show" if args.tvshow else "Movie" if args.movie else "Person")
        mfo.right_table.add_row("Directory Path:", args.directory_path)
        mfo.right_table.add_row("Nº of Files found:", str(len(media_files)))

        if args.movie:
            mfo.print_error("[red]Movie organization is not yet implemented[/red]")
            sys.exit(1)

        elif args.tvshow:
            tvshow(args, mfo=mfo, media_files=media_files, tmdb=tmdb, directory=args.directory_path, dbconn=dbconn)

    except FileNotFoundError as e:
        mfo.print_error(str(e))
    
    except KeyboardInterrupt as e:
        mfo.print_notice("Operation cancelled by user.")
        
    finally:
        mfo.stop()  # Ensure the live display is stopped properly

    sys.exit(0)


if __name__ == "__main__":
    main()