"""
This module defines TypedDict classes for representing metadata related to TV series and movies.
Classes:
    Actor: Represents an actor or cast member in a TV series or movie.
    CrewMember: Represents a crew member involved in the production of a TV series or movie.
    Episode: Represents metadata for a single episode of a TV series.
    Season: Represents metadata for a single season of a TV series.
    TVShowGeneralInfo: Represents general information about a TV series.
"""
from typing import TypedDict, Optional

class MetadataType(TypedDict):
    """
    Represents a metadata type for a media file.

    Attributes:
        name (str):
    """
    name: str


class Actor(MetadataType):
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

class CrewMember(MetadataType):
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

class Episode(MetadataType):
    """
    Represents metadata for a single episode of a TV series.

    Attributes:

        episode_name (str): The title of the episode.
        episode_number (int): The number of the episode in the season.
        overview (str): A brief summary or description of the episode.
        community_rating (float): The average community rating for the episode.
        air_date (str): The air date of the episode in `YYYY-MM-DD`
    """
    name: str
    series_name: str
    episode_name: str
    episode_number: int
    overview: str
    community_rating: float
    air_date: str
    still_url: str
    actors: list[Actor]
    guest_stars: list[Actor]
    crew: list[CrewMember]


class Season(MetadataType):
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
    name: str
    season_name: str
    season_number: int
    overview: str
    community_rating: float
    episode_count: int
    release_date: str
    poster_url: str
    episodes: list[Episode]
    series_name: str
    genres: list[str]
    actors: list[Actor]
    crew: list[CrewMember]

class TVShow(MetadataType):
    """
    Represents metadata for a TV series.

    Attributes:
        series_name (str): The name of the TV series.
        genres (list[str]): A list of genres associated with the series.
        seasons (list[Season]): A list of seasons in the series.
        cast (list[Actor]): A list of main cast members in the series.
        crew (list[CrewMember]): A list of crew members involved in the series.
    """
    name: str
    series_name: str
    genres: list[str]
    seasons: list[Season]
    cast: list[Actor]
    crew: list[CrewMember]

class TVShowGeneralInfo(MetadataType):
    """
    Represents general information about a TV series.

    Attributes:
        series_name (str): The name of the TV series.
        genres (list[str]): A list of genres associated with the series.
    """
    name: str
    series_name: str
    genres: list[str]
    number_of_seasons: int
