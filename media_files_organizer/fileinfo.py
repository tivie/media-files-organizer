"""
file_info

A utility module for extracting media file information using the `pymediainfo` library.
This module provides functionality to retrieve detailed video and audio metadata 
from media files, including codec, bitrate, resolution, aspect ratio, and more.

Dependencies:
    - pymediainfo: Library for parsing media file metadata.

Classes:
    - FileInfo: A class containing static methods to extract and process media file metadata.

Example Usage:
    from file_info import FileInfo

    # Get media information from a file
    media_info = FileInfo.get_media_info("path/to/media/file.mp4")
    print(media_info["video"])
    print(media_info["audio"])
"""

from typing import TypedDict
from pymediainfo import MediaInfo


class VideoInfo(TypedDict):
    """
    A dictionary containing metadata about a video track in a media file.
    """
    codec: str
    micodec: str
    bitrate: str
    width: str
    height: str
    aspect: str
    aspectratio: str
    framerate: str
    scantype: str
    default: bool
    forced: bool
    duration: str
    durationinseconds: int

class AudioInfo(TypedDict):
    """
    A dictionary containing metadata about an audio track in a media file.
    """
    codec: str
    micodec: str
    bitrate: str
    language: str
    scantype: str
    channels: str
    samplingrate: str
    default: bool
    forced: bool



class MedaInfoStrut(TypedDict):
    """
    A dictionary containing metadata about a media file.
    """
    video: VideoInfo
    audio: list[AudioInfo]

class FileInfo:
    """
    A class to extract media file metadata using the `pymediainfo` library.

    Methods:
        - get_media_info(file_path: str) -> dict:
            Parses the specified media file and returns its video and audio metadata.

    Example:
        media_info = FileInfo.get_media_info("path/to/media/file.mp4")
        print(media_info["video"])
        print(media_info["audio"])
    """

    @staticmethod
    def get_media_info(file_path: str) -> MedaInfoStrut:
        """
        Get media file information using the pymediainfo library.

        This method parses the specified media file to extract detailed video and audio 
        metadata, such as codec, bitrate, resolution, aspect ratio, framerate, and more.

        Parameters:
            file_path (str): The path to the media file.

        Returns:
            dict: A dictionary with the following structure:
                - "video" (dict): Metadata about the video track (if present), including:
                    - codec (str): Video codec (e.g., H.264, HEVC).
                    - bitrate (int): Nominal bitrate of the video.
                    - width (int): Video width in pixels.
                    - height (int): Video height in pixels.
                    - aspect (str): Display aspect ratio.
                    - framerate (float): Video frame rate.
                    - scantype (str): Scan type (e.g., progressive, interlaced).
                    - default (bool): Whether the track is the default track.
                    - forced (bool): Whether the track is forced.
                    - duration (str): Duration of the video in "Xm Ys" format.
                    - durationinseconds (int): Duration in seconds.
                - "audio" (list): A list of dictionaries for each audio track, each containing:
                    - codec (str): Audio codec (e.g., AAC, AC-3).
                    - bitrate (int): Audio bitrate.
                    - language (str): Language of the audio track (default: "unknown").
                    - channels (int): Number of audio channels.
                    - samplingrate (int): Sampling rate in Hz.
                    - default (bool): Whether the track is the default track.
                    - forced (bool): Whether the track is forced.

        Raises:
            ValueError: If the file does not exist or cannot be parsed.

        Example:
            >>> media_info = FileInfo.get_media_info("path/to/media/file.mp4")
            >>> print(media_info["video"])
            >>> print(media_info["audio"])
        """

        media_info = MediaInfo.parse(file_path)

        video_info: VideoInfo = {
            "codec": "",
            "micodec": "",
            "bitrate": "",
            "width": "",
            "height": "",
            "aspect": "",
            "aspectratio": "",
            "framerate": "",
            "scantype": "",
            "default": False,
            "forced": False,
            "duration": "",
            "durationinseconds": 0,
        }
        audio_info: list[AudioInfo] = []

        for track in media_info.tracks:
            if track.track_type == "Video":
                duration_in_seconds = int(float(track.duration) / 1000)
                duration = f"{duration_in_seconds // 60}m {duration_in_seconds % 60}s"


                video_info: VideoInfo = {
                    "codec": track.format,
                    "micodec": track.format,
                    "bitrate": track.nominal_bit_rate,
                    "width": track.width,
                    "height": track.height,
                    "aspect": f"{track.display_aspect_ratio}",
                    "aspectratio": f"{track.display_aspect_ratio}",
                    "framerate": track.frame_rate,
                    "scantype": track.scan_type,
                    "default": track.default == 'Yes',
                    "forced": track.forced == 'Yes',
                    "duration": duration,
                    "durationinseconds": duration_in_seconds,
                }
            elif track.track_type == "Audio":
                audio_info_t: AudioInfo = {
                    "codec": track.format,
                    "micodec": track.format,
                    "bitrate": track.bit_rate,
                    "language": track.language or "unknown",
                    "scantype": "progressive",
                    "channels": track.channel_s,
                    "samplingrate": track.sampling_rate,
                    "default": track.default == 'Yes',
                    "forced": track.forced == 'Yes',
                }
                audio_info.append(audio_info_t)

        return {"video": video_info, "audio": audio_info}
