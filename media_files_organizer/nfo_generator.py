"""
nfo_generator

This module provides functionality for generating NFO files for TV show seasons and episodes. 
It includes metadata extraction and formatting tools, ensuring compatibility with media players
that support NFO metadata files.

Classes:
    - NFO: Handles NFO file generation for TV shows, seasons, and episodes.

Dependencies:
    - datetime: For working with dates and times.
    - FileInfo: Custom module for extracting media file metadata.
    - metadata_types: Contains types like Season and Episode.

Example Usage:
    from nfo_generator import NFO
    from metadata_types import Season, Episode

    season_data = {
        "series_name": "My Show",
        "season_number": 1,
        "season_name": "Season One",
        "release_date": "2023-01-01",
        "genres": ["Drama", "Mystery"],
        "actors": [{"name": "Actor One", "role": "Lead"}, {"name": "Actor Two", "role": "Supporting"}],
        "overview": "A thrilling season of mystery and drama.",
        "community_rating": 8.5,
        "episodes": [
            {
                "episode_name": "Episode 1",
                "episode_number": 1,
                "air_date": "2023-01-01",
                "overview": "The beginning of an intriguing mystery.",
                "community_rating": 8.7,
                "actors": [{"name": "Actor One", "role": "Detective"}],
            },
        ],
    }

    nfo = NFO(data=season_data)
    episode_nfo = nfo.generate_tvshow_episode(season_data["episodes"][0], "/path/to/episode.mp4")
    season_nfo = nfo.generate_tvshow_season()
    print(episode_nfo)
    print(season_nfo)
"""
from datetime import date, datetime
import re
import shutil
import requests
from jinja2 import Template
from media_files_organizer.fileinfo import FileInfo
from media_files_organizer.metadata_types import Episode, Season


class NFO:
    """
    Handles NFO file generation for TV shows, seasons, and episodes.

    Attributes:
        data (Season): The metadata for the season.
        media_type (str): The type of media, either 'tvshow' or 'movie'.
        base_path (str): The base directory for storing NFO files.
        series_dir (str): Directory name for the series.
        season_dir (str): Directory name for the season.
        full_path (str): Full path combining base_path, series_dir, and season_dir.

    Methods:
        - generate_tvshow_episode: Generate an NFO file for a specific episode.
        - generate_tvshow_season: Generate an NFO file for the season.
    """

    def __init__(self, data: Season, media_type: str ="tvshow", base_path: str ="/data/anime", series_dir: str|None = None, season_dir: str|None = None):
        """
        Initialize the NFO object with metadata and directory structure.

        Parameters:
            data (Season): The metadata for the season.
            media_type (str): The type of media ('tvshow' or 'movie'). Default is 'tvshow'.
            base_path (str): The base directory for storing NFO files in the remote server. Default is '/data/anime'.
            series_dir (str | None): Directory name for the series. Default is None.
            season_dir (str | None): Directory name for the season. Default is None.

        Raises:
            ValueError: If media_type is not 'tvshow' or 'movie'.
        """
        self.data = data
        if media_type not in ('tvshow', 'movie'):
            raise ValueError("Type must be either 'tvshow' or 'movie'.")
        self.media_type = media_type
        self.base_path = base_path

        if series_dir is None:
            self.series_dir: str = self.data["series_name"]

        if season_dir is None:
            self.season_dir: str = f"Season {self.data['season_number']} - {self.data['season_name']}"

        self.full_path = f"{self.base_path}/{self.series_dir}/{self.season_dir}"

        with open("media_files_organizer/templates/tv_show_episode.xml.jinja", encoding="utf-8") as file:
            tpl = file.read()
        self.tv_show_episode_template = Template(tpl)

        with open("media_files_organizer/templates/tv_show_season.xml.jinja", encoding="utf-8") as file:
            tpl = file.read()
        self.tv_show_season_template = Template(tpl)


    def _sanitize_filename(self, filename: str) -> str:
        # Remove forbidden characters for both Windows and Unix-like systems
        return re.sub(r'[\/:*?"<>|]', '', filename)

    def download_poster(self, directory: str) -> None:
        """
        Download the poster image for the TV show and save it to the specified directory.

        Parameters:
            directory (str): The directory to save the poster image.

        Returns:
            str: The local path to the downloaded poster image.
        """
        res = requests.get(self.data["poster_url"], stream=True, timeout=10)

        if res.status_code == 200:
            with open(directory.rstrip("/\\") + "/poster.jpg",'wb') as f:
                shutil.copyfileobj(res.raw, f)
        else:
            raise RuntimeError(f"Failed to download poster image: {res.status_code}")


    def _validate_data_tvshow(self):
        """
        Validate the metadata for the TV show.

        Raises:
            ValueError: If the data is empty.
        """
        if not self.data:
            raise ValueError("Data cannot be empty.")

    def _parse_date_and_get_year(self, date_str: str) -> tuple[str, str]:
        """
        Parse a date string and extract the year.

        Parameters:
            date_str (str): The date string in 'YYYY-MM-DD' format.

        Returns:
            tuple[str, str]: A tuple containing the parsed date and the year.
                             If the date is invalid, the original string and an empty year are returned.
        """
        try:
            release_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            year = str(release_date.year)
            release_date_str = str(release_date)
        except ValueError:
            release_date_str = date_str
            year = ""

        return (release_date_str, year)

    def generate_tvshow_episode(self, episode: Episode, filepath: str):
        """
        Generate an NFO file for a specific episode.

        Parameters:
            episode (Episode): The metadata for the episode.
            filepath (str): The path to the episode file.

        Returns:
            str: The NFO content for the episode.
        """
        genres = self.data["genres"]
        #ep = self.data["episodes"][episode_number]

        air_date, year = self._parse_date_and_get_year(episode["air_date"])

        s_num = str(self.data["season_number"])
        if s_num and len(s_num) < 2:
            s_num = f"0{s_num}"

        ep_num = str(episode["episode_number"])

        if ep_num and len(ep_num) < 2:
            ep_num = f"0{ep_num}"

        fileinfo = FileInfo.get_media_info(filepath)

        nfo = self.tv_show_episode_template.render({
            **episode,
            "genres": genres,
            "air_date": air_date,
            "year": year,
            "season_number": s_num,
            "episode_number": ep_num,
            "fileinfo": fileinfo
        })

        return nfo


    def generate_tvshow_season(self) -> str:
        """
        Generate an NFO file for the season.

        Returns:
            str: The NFO content for the season.
        """
        release_date, year = self._parse_date_and_get_year(self.data["release_date"])
        dateadded = date.today().strftime("%Y-%m-%d")

        nfo = self.tv_show_season_template.render({
            **self.data,
            "release_date": release_date,
            "year": year,
            "dateadded": dateadded,
            "series_name_safe": self._sanitize_filename(self.data["series_name"]),
        })

        return nfo
