# pymediainfo.pyi
"""
This module provides type annotations for the `pymediainfo` library, which is used to extract media information from various media files.

Classes:
    Track: Represents a single track in a media file.
    MediaInfo: Represents information about a media file, including multiple tracks.

Track:
    Attributes:
        track_type (str): The type of the track (e.g., video, audio).
        other_duration (Optional[List[str]]): Other durations of the track.

    Methods:
        __init__(self, xml_dom_fragment: Any) -> None: Initializes a Track instance.
        __repr__(self) -> str: Returns a string representation of the Track instance.
        __eq__(self, other: Any) -> bool: Checks equality between two Track instances.
        to_data(self) -> Dict[str, Any]: Converts the Track instance to a dictionary.
        __getattribute__(self, name: str) -> Any: Gets an attribute of the Track instance.
        __getstate__(self) -> Dict[str, Any]: Gets the state of the Track instance for pickling.
        __setstate__(self, state: Dict[str, Any]) -> None: Sets the state of the Track instance for unpickling.

MediaInfo:
    Attributes:
        tracks (List[Track]): A list of tracks in the media file.

    Methods:
        __init__(self, xml: str, encoding_errors: str = "strict") -> None: Initializes a MediaInfo instance.
        __eq__(self, other: Any) -> bool: Checks equality between two MediaInfo instances.
        to_data(self) -> Dict[str, Any]: Converts the MediaInfo instance to a dictionary.
        to_json(self) -> str: Converts the MediaInfo instance to a JSON string.
        can_parse(cls, library_file: Optional[str] = None) -> bool: Checks if the library can parse the media file.
        parse(cls, filename: Union[str, Any], ...) -> Union[str, "MediaInfo"]: Parses the media file and returns a MediaInfo instance or a string.
        
    Properties:
        general_tracks: List[Track]: Returns a list of general tracks.
        video_tracks: List[Track]: Returns a list of video tracks.
        audio_tracks: List[Track]: Returns a list of audio tracks.
        text_tracks: List[Track]: Returns a list of text tracks.
        other_tracks: List[Track]: Returns a list of other tracks.
        image_tracks: List[Track]: Returns a list of image tracks.
        menu_tracks: List[Track]: Returns a list of menu tracks.
"""

from typing import Any, Dict, List, Optional, Union


class Track:
    """
    Represents a single track in a media file.
    """

    track_type: str
    other_duration: Optional[List[str]]

    def __init__(self, xml_dom_fragment: Any) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: Any) -> bool: ...
    def to_data(self) -> Dict[str, Any]: ...
    def __getattribute__(self, name: str) -> Any: ...
    def __getstate__(self) -> Dict[str, Any]: ...
    def __setstate__(self, state: Dict[str, Any]) -> None: ...


class MediaInfo:
    """
    Represents information about a media file.
    """

    tracks: List[Track]

    def __init__(self, xml: str, encoding_errors: str = "strict") -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    def to_data(self) -> Dict[str, Any]: ...
    def to_json(self) -> str: ...

    @classmethod
    def can_parse(cls, library_file: Optional[str] = None) -> bool: ...
    @classmethod
    def parse(
        cls,
        filename: Union[str, Any],
        library_file: Optional[str] = None,
        cover_data: bool = False,
        encoding_errors: str = "strict",
        parse_speed: float = 0.5,
        full: bool = True,
        legacy_stream_display: bool = False,
        mediainfo_options: Optional[Dict[str, str]] = None,
        output: Optional[str] = None,
        buffer_size: Optional[int] = 64 * 1024
    ) -> "MediaInfo": ...

    @property
    def general_tracks(self) -> List[Track]: ...
    @property
    def video_tracks(self) -> List[Track]: ...
    @property
    def audio_tracks(self) -> List[Track]: ...
    @property
    def text_tracks(self) -> List[Track]: ...
    @property
    def other_tracks(self) -> List[Track]: ...
    @property
    def image_tracks(self) -> List[Track]: ...
    @property
    def menu_tracks(self) -> List[Track]: ...
