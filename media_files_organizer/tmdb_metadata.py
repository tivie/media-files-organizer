"""
tmdb_metadata

A module for interacting with The Movie Database (TMDb) API to fetch detailed metadata
for TV shows, movies, and persons. It provides functionality for retrieving information
such as general details, cast, crew, season-specific data, and episode-level data.

This module utilizes the `requests` library for HTTP requests

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

    # Initialize the TMDBMetadata class
    tmdb = TMDBMetadata(api_key="YOUR_API_KEY")

    # Fetch metadata for a TV series
    metadata = tmdb.fetch(media_type="tv", media_id=12345, season=1)

    # Access metadata
    print(metadata["series_name"])  # Example: "Breaking Bad"
    print(metadata["genres"])       # Example: ["Crime", "Drama", "Thriller"]

Dependencies:
    - requests: For making API requests.
"""
from typing import Literal, Any
import requests
from media_files_organizer.metadata_types import Actor, CrewMember, Episode, MetadataType, Season, TVShowGeneralInfo, TVShow


class TMDBMetadata:
    """
    A class to fetch metadata from the TMDb (The Movie Database) API.

    This class provides methods to fetch and parse detailed metadata for TV shows, 
    including general information, cast, season details, episode details, and crew 
    information. It uses the TMDb API for fetching data

    Attributes:
        base_url (str): The base URL for TMDb API requests.
        api_key (str): Your TMDb API key for authentication.

    Methods:
        get_tv_general_info(media_id: str|int) -> dict:
            Fetches general information about a TV series.

        get_tv_cast(media_id: str|int) -> list:
            Fetches cast information for a TV series.

        get_tv_season_info(media_id: str|int, season: int) -> dict:
            Fetches season-specific information for a TV series.

        get_episode_info(media_id: str|int, season: int, episode: int) -> dict:
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

    def __init__(self, api_key: str):
        """
        Initializes the TMDBMetadata class.

        Parameters:
        - api_key (str): Your TMDb API key.
        """
        self.api_key = api_key

    def _raise_for_status(self, message: str, response: requests.Response, params: dict[str,str]) -> None:
        """
        Raises an exception if the response status code is not 200.

        Parameters:
        - response (requests.Response): The HTTP response object.
        """
        msg = f"{message}\nURL: {response.url}\nHTTP Status: {response.status_code}\nparams:\n"
        for param in params:
            msg += f"  {param}: {params[param]}\n"
        raise RuntimeError(msg)


    def _parse_crew(self, crew: list[Any]) -> list[CrewMember]:
        """
        Parses crew information from TMDb response.

        Parameters:
        - crew (list): The list of crew data from TMDb.

        Returns:
        - list: A list of dictionaries containing crew details.
        """
        parsed_crew: list[CrewMember] = []

        for person in crew:
            name = person.get("name")

            if name is None:
                continue

            initial = name[0].upper()

            job = person.get("job")

            if job is None:
                joblist: list[dict[str, str]] = person.get("jobs")
                if joblist and len(joblist) > 1:
                    job = joblist[0].get("job")

            if job is None:
                job = "Crew"

            crewmember: CrewMember = {
                "name": name,
                "original_name": person.get("original_name"),
                "type": job,
                "photo": f"https://image.tmdb.org/t/p/original{person['profile_path']}" if person.get("profile_path") else None,
                "thumb": f"/config/data/metadata/People/{initial}/{name}/folder.jpg"
            }

            parsed_crew.append(crewmember)

        return parsed_crew

    def _parse_actors(self, actors: list[dict[str, Any]], actor_type: str = "Actor") -> list[Actor]:
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
            role = actor.get("character")
            
            if role is None:
                roles: list[dict[str, Any]]|None = actor.get("roles")
                if roles and len(roles) >= 1:
                    role = roles[0].get("character")
            if role is None:
                role = "Unknown"
            name = actor["name"]
            initial = name[0].upper()
            parsed_actors.append({
                "name": actor["name"],
                "original_name": actor["original_name"],
                "type": actor_type,
                "role": role,
                "photo": f"https://image.tmdb.org/t/p/original{actor['profile_path']}",
                "thumb": f"/config/data/metadata/People/{initial}/{name}/folder.jpg"
            })

        return parsed_actors

    def _parse_episodes(self, episodes: list[dict[str, Any]], series_name: str) -> list[Episode]:
        """
        Parses episode information from TMDb response.

        Parameters:
        - episodes (list): The list of episodes data from TMDb.

        Returns:
        - list: A list of dictionaries containing episode details.
        """
        parsed_episodes: list[Episode] = []

        for episode in episodes:
            actors: list[Any] = episode["cast"] if episode.get("cast") else []
            guest_stars: list[Any] = episode["guest_stars"] if episode.get("guest_stars") else []
            crew: list[Any] = episode["crew"] if episode.get("crew") else []

            parsed_episodes.append({
                "name": episode["name"],
                "series_name": series_name,
                "episode_number": episode["episode_number"],
                "episode_name": episode["name"],
                "overview": episode["overview"],
                "community_rating": episode["vote_average"],
                "air_date": episode["air_date"],
                "still_url": f"https://image.tmdb.org/t/p/original{episode['still_path']}",
                "actors": self._parse_actors(actors, actor_type="actor"),
                "guest_stars": self._parse_actors(guest_stars, actor_type="GuestStar"),
                "crew": self._parse_crew(crew)
            })

        return parsed_episodes



    def fetch_movie(self, media_id: str|int) -> dict[str, str]:
        """
        Fetches metadata for a movie.

        Parameters:
        - media_id (str or int): The ID of the movie on TMDb.

        Returns:
        - dict: A consolidated dictionary of metadata for the specified movie.
        """
        raise NotImplementedError("Movie metadata fetching is not implemented yet.")

    def fetch_person(self, media_id: str|int) -> dict[str, str]:
        """
        Fetches metadata for a person.

        Parameters:
        - media_id (str or int): The ID of the person on TMDb.

        Returns:
        - dict: A consolidated dictionary of metadata for the specified person.
        """
        raise NotImplementedError("Person metadata fetching is not implemented yet.")

    def fetch_tvshow(self, media_id: str|int) -> TVShow:
        """
        Fetches metadata for a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.
        - season (int): The season number.

        Returns:
        - dict: A consolidated dictionary of metadata for the specified TV series.
        """

        # initialize TVShow object
        tvshow: TVShow = {
            "name": "",
            "series_name": "",
            "genres": [],
            "seasons": [],
            "cast": [],
            "crew": []
        }

        gen_info: TVShowGeneralInfo = self.get_tv_general_info(media_id)
        tvshow["series_name"] = gen_info.get("series_name")
        tvshow["genres"] = gen_info.get("genres")
        num_seasons = gen_info.get("number_of_seasons")

        for i in range(1, num_seasons+1):
            tv_season_info: Season = self.get_tv_season_info(media_id, series_name=gen_info.get("series_name"), season=i)
            tvshow["seasons"].append(tv_season_info)

        tvshow["cast"] = self.get_tv_cast(media_id)
        tvshow["crew"] = self.get_tv_crew(media_id)

        return tvshow

    def fetch_tvshow_season(self, media_id: str|int, season: int) -> Season:
        """
        Fetches metadata for a specific season of a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.
        - season (int): The season number.

        Returns:
        - dict: A consolidated dictionary of metadata for the specified TV series season.
        """
        gen_info: TVShowGeneralInfo = self.get_tv_general_info(media_id)
        tv_season_info: Season = self.get_tv_season_info(media_id, series_name=gen_info.get("series_name"), season=season, genres=gen_info.get("genres"))

        return tv_season_info

    def fetch(self, media_type: Literal["tv", "tvshow", "movie", "person"], media_id: str|int, season: int|None = None) -> MetadataType:
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
        if media_type in ('tv', 'tvshow'):

            if season is None:
                return self.fetch_tvshow(media_id)
            else:
                return self.fetch_tvshow_season(media_id, season)

        elif media_type == "movie":
            raise NotImplementedError("Movie metadata fetching is not implemented yet.")

        elif media_type == "person":
            raise NotImplementedError("Person metadata fetching is not implemented yet.")

        else:
            raise ValueError("Unsupported media type")


    def get_tv_general_info(self, media_id: str|int) -> TVShowGeneralInfo:
        """
        Fetches general information about a TV series.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.

        Returns:
        - dict: A dictionary containing 'series_name' and 'genres'.
        """
        url = f"{self.base_url}/tv/{media_id}"
        params = {"api_key": self.api_key, "append_to_response": "aggregate_credits, credits"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            self._raise_for_status(f"Failed to fetch TVSERIES data from TMDb.", response=response, params=params)
            #raise RuntimeError(f"Failed to fetch TVSERIES data from TMDb. \nURL: {url}\nHTTP Status: {response.status_code}")

        data = response.json()

        return {
            "name": data["name"],
            "series_name": data["name"],
            "genres": [genre["name"] for genre in data["genres"]],
            "number_of_seasons": int(data["number_of_seasons"]),
        }

    def get_tv_cast(self, media_id: str|int) -> list[Actor]:
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

    def get_tv_crew(self, media_id: str|int) -> list[CrewMember]:
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
            self._raise_for_status(f"Failed to fetch ACTORS data from TMDb.", response=response, params=params)

        data = response.json()

        return self._parse_crew(data["crew"])

    def get_tv_season_info(self, media_id: str|int, series_name: str, season: int, genres: list[str]|None = None) -> Season:
        """
        Fetches season-specific information about a TV series SEASON.

        Parameters:
        - media_id (str or int): The ID of the TV series on TMDb.
        - season (int): The season number.
        - series_name (str): The name of the TV series.
        - genres (Optional[list]): A list of genres for the TV series.

        Returns:
        - dict: A dictionary containing season details such as name, number, overview, and more.
        """
        if genres is None:
            genres = []

        url = f"{self.base_url}/tv/{media_id}/season/{season}"
        params = {"api_key": self.api_key, "append_to_response": "aggregate_credits, credits"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            self._raise_for_status(f"Failed to fetch SEASON data from TMDb.", response=response, params=params)

        data = response.json()

        # inject cast into episode data
        for episode in data["episodes"]:
            episode["cast"] = data["aggregate_credits"]["cast"]

        return {
            "name": data["name"],
            "season_name": data["name"],
            "season_number": data["season_number"],
            "overview": data["overview"],
            "community_rating": data["vote_average"],
            "episode_count": len(data["episodes"]),
            "release_date": data["air_date"],
            "poster_url": f"https://image.tmdb.org/t/p/original{data['poster_path']}",
            "episodes": self._parse_episodes(data["episodes"], series_name),
            "series_name": series_name,
            "genres": genres,
            "actors": self._parse_actors(data["aggregate_credits"]["cast"]),
            "crew": self._parse_crew(data["aggregate_credits"]["crew"])
        }

    def get_episode_info(self, media_id: str|int, season: int, episode: int) -> Episode:
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

        show_gen_info = self.get_tv_general_info(media_id)

        if response.status_code != 200:
            self._raise_for_status(f"Failed to fetch EPISODE data from TMDb.", response=response, params=params)

        data = response.json()

        return {
            "name": data["name"],
            "series_name": show_gen_info["series_name"],
            "episode_number": data["episode_number"],
            "episode_name": data["name"],
            "overview": data["overview"],
            "community_rating": data["vote_average"],
            "air_date": data["air_date"],
            "still_url": f"https://image.tmdb.org/t/p/original{data['still_path']}",
            "actors": self._parse_actors(data["credits"]["cast"], actor_type="actor"),
            "guest_stars": self._parse_actors(data["credits"]["guest_stars"], actor_type="GuestStar"),
            "crew": self._parse_crew(data["credits"]["crew"])
        }
