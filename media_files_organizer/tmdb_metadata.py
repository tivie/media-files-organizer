"""
tmdb_metadata

A module for interacting with The Movie Database (TMDb) API to fetch detailed metadata
for TV shows, movies, and persons. It provides functionality for retrieving information
such as general details, cast, crew, season-specific data, and episode-level data.

This module utilizes the `requests` library for HTTP requests and supports styled console
output using the `rich` library.

Classes:
    TMDBMetadata:
        A class to manage communication with the TMDb API and parse its responses
        into structured metadata.

Functions (inside TMDBMetadata):
    - _get_tv_general_info(media_id: str | int) -> dict:
        Fetches general information about a TV series.

    - _get_tv_cast(media_id: str | int) -> list[dict]:
        Retrieves cast details for a TV series.

    - _get_tv_season_info(media_id: str | int, season: int) -> dict:
        Fetches metadata for a specific season of a TV series.

    - _get_episode_info(media_id: str | int, season: int, episode: int) -> dict:
        Retrieves metadata for a specific episode of a TV series.

    - fetch(media_type: Literal["tv", "tvshow", "movie", "person"], media_id: str | int, season: Optional[int] = None) -> dict:
        Consolidates metadata for a given media type and ID.

Exceptions:
    - RuntimeError:
        Raised when an API call fails with a non-200 HTTP status code.

    - NotImplementedError:
        Raised for unsupported media types ("movie" or "person") when attempted.

    - ValueError:
        Raised for invalid `media_type` values.

Usage:
    from tmdb_metadata import TMDBMetadata
    from rich.console import Console

    # Initialize the TMDBMetadata class
    tmdb = TMDBMetadata(api_key="YOUR_API_KEY", console=Console())

    # Fetch metadata for a TV series
    metadata = tmdb.fetch(media_type="tv", media_id=12345, season=1)

    # Access metadata
    print(metadata["series_name"])  # Example: "Breaking Bad"
    print(metadata["genres"])       # Example: ["Crime", "Drama", "Thriller"]

Dependencies:
    - requests: For making API requests.
    - rich: For styled console output.
"""
from typing import TypedDict, Optional, Literal
import requests
from rich.console import Console


class Actor(TypedDict):
    """
    Represents an actor or cast member in a TV series or movie.

    Attributes:
        name (str): The name of the actor.
        original_name (Optional[str]): The original name of the actor (if available).
        type (str): The type of role (e.g., "actor", "guest star").
        role (str): The character name played by the actor.
        photo (Optional[str]): The URL to the actor's profile photo (if available).
        thumb (Optional[str]): The local thumbnail path for the actor's profile.
    """
    name: str
    original_name: Optional[str]
    type: str
    role: str
    photo: Optional[str]
    thumb: Optional[str]

class CrewMember(TypedDict):
    """
    Represents a crew member involved in the production of a TV series or movie.

    Attributes:
        name (str): The name of the crew member.
        original_name (Optional[str]): The original name of the crew member (if available).
        type (str): The role or job performed by the crew member (e.g., "Director", "Writer").
        photo (Optional[str]): The URL to the crew member's profile photo (if available).
        thumb (Optional[str]): The local thumbnail path for the crew member's profile.
    """
    name: str
    original_name: Optional[str]
    type: str
    photo: Optional[str]
    thumb: Optional[str]

class Episode(TypedDict):
    """
    Represents metadata for a single episode of a TV series.

    Attributes:
        episode_number (int): The number of the episode in the season.
        episode_name (str): The title of the episode.
        overview (str): A brief summary or description of the episode.
        community_rating (float): The average community rating for the episode.
        air_date (str): The air date of the episode in `YYYY-MM-DD` format.
        still_url (str): The URL to the episode's promotional still image.
        actors (list[Actor]): A list of actors appearing in the episode.
        GuestStars (list[Actor]): A list of guest stars appearing in the episode.
        crew (list[CrewMember]): A list of crew members involved in the episode.
    """
    episode_number: int
    episode_name: str
    overview: str
    community_rating: float
    air_date: str
    still_url: str
    actors: list[Actor]
    GuestStars: list[Actor]
    crew: list[CrewMember]


class Season(TypedDict):
    """
    Represents metadata for a single season of a TV series.

    Attributes:
        season_name (str): The title of the season.
        season_number (int): The number of the season in the series.
        overview (str): A brief summary or description of the season.
        community_rating (float): The average community rating for the season.
        episode_count (int): The total number of episodes in the season.
        release_date (str): The release date of the season in `YYYY-MM-DD` format.
        poster_url (str): The URL to the season's promotional poster image.
        episodes (list[Episode]): A list of episodes in the season.
    """
    season_name: str
    season_number: int
    overview: str
    community_rating: float
    episode_count: int
    release_date: str
    poster_url: str
    episodes: list[Episode]

class TVShowGeneralInfo(TypedDict):
    """
    Represents general information about a TV series.

    Attributes:
        series_name (str): The name of the TV series.
        genres (list[str]): A list of genres associated with the series.
    """
    series_name: str
    genres: list[str]


class TMDBMetadata:
    """
    A class to fetch metadata from the TMDb (The Movie Database) API.

    This class provides methods to fetch and parse detailed metadata for TV shows, 
    including general information, cast, season details, episode details, and crew 
    information. It uses the TMDb API for fetching data and supports styled console 
    output using the `rich` library.

    Attributes:
        base_url (str): The base URL for TMDb API requests.
        api_key (str): Your TMDb API key for authentication.
        console (Console): A `rich.console.Console` instance for styled console output.

    Methods:
        _get_tv_general_info(media_id: str|int) -> dict:
            Fetches general information about a TV series.

        _get_tv_cast(media_id: str|int) -> list:
            Fetches cast information for a TV series.

        _get_tv_season_info(media_id: str|int, season: int) -> dict:
            Fetches season-specific information for a TV series.

        _get_episode_info(media_id: str|int, season: int, episode: int) -> dict:
            Fetches detailed information about a specific episode of a TV series.

        _parse_actors(actors: list, type: str = "actor") -> list:
            Parses actor information from the TMDb API response.

        _parse_crew(crew: list) -> list:
            Parses crew information from the TMDb API response.

        fetch(media_type: str, media_id: str|int, season: Optional[int] = None) -> dict:
            Fetches metadata for a given media type, such as a TV series.

    Raises:
        RuntimeError: If any API call fails with a non-200 HTTP status code.
        NotImplementedError: If fetching for "movie" or "person" types is attempted.
        ValueError: If an unsupported media type is provided.
    """
    base_url = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str, console: Console|None = None):
        """
        Initializes the TMDBMetadata class.

        Parameters:
        - api_key (str): Your TMDb API key.
        - console (Optional[Console]): A rich.console.Console instance for styled console output. Defaults to None.
        """
        self.api_key = api_key
        self.console = console or Console()

    def _get_tv_general_info(self, media_id: str|int) -> TVShowGeneralInfo:
        """
        Fetches general information about a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.

        Returns:
        - dict: A dictionary containing 'series_name' and 'genres'.
        """
        url = f"{self.base_url}/tv/{media_id}"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch TVSERIES data from TMDb. HTTP Status: {response.status_code}")
    
        data = response.json()

        return {
            "series_name": data["name"],
            "genres": [genre["name"] for genre in data["genres"]],
        }

    def _get_tv_cast(self, media_id: str|int) -> list[Actor]:
        """
        Fetches cast information for a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.

        Returns:
        - list: A list of dictionaries representing cast members.
        """
        url = f"{self.base_url}/tv/{media_id}/aggregate_credits"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch ACTORS data from TMDb. HTTP Status: {response.status_code}")

        data = response.json()
        to_ret: list[Actor] = []

        for cast in data["cast"]:
            name = cast["name"]
            initial = name[0].upper()

            actor: Actor = {
                "name": cast["name"],
                "original_name": cast.get("original_name"),
                "type": "actor",
                "role": cast["roles"][0]["character"],
                "photo": f"https://image.tmdb.org/t/p/original{cast['profile_path']}" if cast.get("profile_path") else None,
                "thumb": f"/config/data/metadata/People/{initial}/{name}/folder.jpg"
            }
            to_ret.append(actor)

        return to_ret

    def _get_tv_season_info(self, media_id: str, season: int) -> Season:
        """
        Fetches season-specific information about a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.
        - season (int): The season number.

        Returns:
        - dict: A dictionary containing season details such as name, number, overview, and more.
        """
        url = f"{self.base_url}/tv/{media_id}/season/{season}"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch SEASON data from TMDb. HTTP Status: {response.status_code}")

        data = response.json()

        return {
            "season_name": data["name"],
            "season_number": data["season_number"],
            "overview": data["overview"],
            "community_rating": data["vote_average"],
            "episode_count": len(data["episodes"]),
            "release_date": data["air_date"],
            "poster_url": f"https://image.tmdb.org/t/p/original{data['poster_path']}",
            "episodes": [],  # Initialize the episodes list
        }
    

    def _get_episode_info(self, media_id: str|int, season: int, episode: int) -> Episode:
        """
        Fetches information about a specific episode of a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.
        - season (int): The season number.
        - episode (int): The episode number.

        Returns:
        - dict: A dictionary containing episode details.
        """
        url = f"{self.base_url}/tv/{media_id}/season/{season}/episode/{episode}"
        params = {"api_key": self.api_key, "append_to_response": "credits"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch EPISODE data from TMDb. HTTP Status: {response.status_code}")

        data = response.json()

        return {
            "episode_number": data["episode_number"],
            "episode_name": data["name"],
            "overview": data["overview"],
            "community_rating": data["vote_average"],
            "air_date": data["air_date"],
            "still_url": f"https://image.tmdb.org/t/p/original{data['still_path']}",
            "actors": self._parse_actors(data["credits"]["cast"], actor_type="actor"),
            "GuestStars": self._parse_actors(data["credits"]["guest_stars"], actor_type="GuestStar"),
            "crew": self._parse_crew(data["credits"]["crew"])
        }


    def _parse_actors(self, actors: list[dict[str, str]], actor_type: str = "actor") -> list[Actor]:
        """
        Parses actor information from TMDb response.

        Parameters:
        - actors (list): The list of actors data from TMDb.
        - type (str): The type of actor (e.g., "actor", "GuestStar").

        Returns:
        - list: A list of dictionaries containing actor details.
        """
        parsed_actors: list[Actor] = []

        for actor in actors:
            name = actor["name"]
            initial = name[0].upper()
            parsed_actors.append({
                "name": actor["name"],
                "original_name": actor["original_name"],
                "type": actor_type,
                "role": actor["character"],
                "photo": f"https://image.tmdb.org/t/p/original{actor['profile_path']}",
                "thumb": f"/config/data/metadata/People/{initial}/{name}/folder.jpg"
            })

        return parsed_actors


    def _parse_crew(self, crew: list[dict[str, str]]) -> list[CrewMember]:
        """
        Parses crew information from TMDb response.

        Parameters:
        - crew (list): The list of crew data from TMDb.

        Returns:
        - list: A list of dictionaries containing crew details.
        """
        parsed_crew: list[CrewMember] = []

        for member in crew:
            name = member["name"]
            initial = name[0].upper()
            parsed_crew.append({
                "name": member["name"],
                "original_name": member["original_name"],
                "type": member["job"],
                "photo": f"https://image.tmdb.org/t/p/original{member['profile_path']}",
                "thumb": f"/config/data/metadata/People/{initial}/{name}/folder.jpg"
            })

        return parsed_crew


    def fetch(self, media_type: Literal["tv", "tvshow", "movie", "person"], media_id: str, season: int):
        """
        Fetches metadata for a given media type.

        Parameters:
        - media_type (str): The type of media (e.g., "tv").
        - media_id (str or int): The ID of the media on TMDb.
        - season (Optional[int]): The season number, required for TV series.

        Returns:
        - dict: A consolidated dictionary of metadata for the specified media.

        Raises:
        - NotImplementedError: If fetching for "movie" or "person" is attempted.
        - ValueError: If an unsupported media type is provided.
        """
        data = {}

        if media_type in ('tv', 'tvshow'):

            gen_info: TVShowGeneralInfo = self._get_tv_general_info(media_id)
            tv_season_info: Season = self._get_tv_season_info(media_id, season)

           
            data = {
                **gen_info,
                ** tv_season_info,
                "actors": self._get_tv_cast(media_id),
                "episodes": tv_season_info["episodes"]
            }

            for i in range(1, tv_season_info["episode_count"]+1):
                episode_info: Episode = self._get_episode_info(media_id, season, i)
                tv_season_info["episodes"].append(episode_info)


        elif media_type == "movie":
            raise NotImplementedError("Movie metadata fetching is not implemented yet.")

        elif media_type == "person":
            raise NotImplementedError("Person metadata fetching is not implemented yet.")

        else:
            raise ValueError("Unsupported media type")

        return data
