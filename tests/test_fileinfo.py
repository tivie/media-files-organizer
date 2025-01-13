from unittest.mock import patch, MagicMock
import pytest
from media_files_organizer.fileinfo import FileInfo

def mock_media_info_parse(file_path): # type: ignore[unused-argument]  # pylint: disable=unused-argument
    # Mocked MediaInfo object and tracks
    mock_media_info = MagicMock()

    # Mock video track
    video_track = MagicMock()
    video_track.track_type = "Video"
    video_track.format = "H.264"
    video_track.nominal_bit_rate = "5000000"
    video_track.width = "1920"
    video_track.height = "1080"
    video_track.display_aspect_ratio = "16:9"
    video_track.frame_rate = "24"
    video_track.scan_type = "progressive"
    video_track.default = "Yes"
    video_track.forced = "No"
    video_track.duration = "120000"  # 120 seconds

    # Mock audio track
    audio_track = MagicMock()
    audio_track.track_type = "Audio"
    audio_track.format = "AAC"
    audio_track.bit_rate = "128000"
    audio_track.language = "en"
    audio_track.channel_s = "2"
    audio_track.sampling_rate = "44100"
    audio_track.default = "Yes"
    audio_track.forced = "No"

    # Assign tracks to the mocked MediaInfo object
    mock_media_info.tracks = [video_track, audio_track]

    return mock_media_info

def test_get_mp4_media_info():
    file_path = "tests/mocks/mock_video.mp4"  # Path to the MP4 file
    result = FileInfo.get_media_info(file_path)

    # Validate video metadata
    assert result["video"]["codec"] == "MPEG-4 Visual"
    assert result["video"]["micodec"] == "MPEG-4 Visual"
    assert result["video"]["bitrate"] is None
    assert result["video"]["width"] == 320
    assert result["video"]["height"] == 240
    assert result["video"]["aspect"] == "1.333"
    assert result["video"]["framerate"] == "10.000"
    assert result["video"]["scantype"] == "Progressive"
    assert result["video"]["default"] is False
    assert result["video"]["forced"] is False
    assert result["video"]["duration"] == "0m 1s"
    assert result["video"]["durationinseconds"] == 1


def test_get_mkv_media_info():
    file_path = "tests/mocks/mock_video.mkv"  # Path to the MP4 file
    result = FileInfo.get_media_info(file_path)

    # Validate video metadata
    assert result["video"]["codec"] == "MPEG-4 Visual"
    assert result["video"]["micodec"] == "MPEG-4 Visual"
    assert result["video"]["bitrate"] is None
    assert result["video"]["width"] == 320
    assert result["video"]["height"] == 240
    assert result["video"]["aspect"] == "1.333"
    assert result["video"]["framerate"] == "10.000"
    assert result["video"]["scantype"] == "Progressive"
    assert result["video"]["default"] is True
    assert result["video"]["forced"] is False
    assert result["video"]["duration"] == "0m 1s"
    assert result["video"]["durationinseconds"] == 1

@patch("media_files_organizer.fileinfo.MediaInfo.parse", side_effect=mock_media_info_parse)
def test_get_media_info(mock_parse): # type: ignore[unused-argument]  # pylint: disable=unused-argument
    file_path = "mock_file.mp4"
    result = FileInfo.get_media_info(file_path)

    print(result)

    # Validate video metadata
    assert result["video"]["codec"] == "H.264"
    assert result["video"]["micodec"] == "H.264"
    assert result["video"]["bitrate"] == "5000000"
    assert result["video"]["width"] == "1920"
    assert result["video"]["height"] == "1080"
    assert result["video"]["aspect"] == "16:9"
    assert result["video"]["framerate"] == "24"
    assert result["video"]["scantype"] == "progressive"
    assert result["video"]["default"] is True
    assert result["video"]["forced"] is False
    assert result["video"]["duration"] == "2m 0s"
    assert result["video"]["durationinseconds"] == 120

    # Validate audio metadata
    assert len(result["audio"]) == 1
    audio = result["audio"][0]
    assert audio["codec"] == "AAC"
    assert audio["micodec"] == "AAC"
    assert audio["bitrate"] == "128000"
    assert audio["language"] == "en"
    assert audio["channels"] == "2"
    assert audio["samplingrate"] == "44100"
    assert audio["default"] is True
    assert audio["forced"] is False

if __name__ == "__main__":
    pytest.main()
