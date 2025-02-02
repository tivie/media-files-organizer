"""
Test cases for the NFO generator module

The NFO generator module is responsible for creating NFO files for TV show episodes, seasons, and movies.

The tests in this module cover the following scenarios:
1. Generating an NFO file for a TV show episode with valid metadata.
2. Generating an NFO file for a TV show season with valid metadata.

The tests use the pytest framework and the unittest.mock module to mock the FileInfo class's get_media_info method.
"""
from unittest.mock import MagicMock
import pytest
from media_files_organizer.nfo_generator import NFO
from media_files_organizer.fileinfo import FileInfo, MedaInfoStrut
from media_files_organizer.metadata_types import Season, Episode

@pytest.fixture(name="mock_file_info")
def mock_file_info_fixture():
    """
    Fixture for a mock media file metadata dictionary
    """
    return {
        "video": {
            "codec": "H.264",
            "micodec": "avc1",
            "bitrate": "1500",
            "width": "1920",
            "height": "1080",
            "aspect": "16:9",
            "aspectratio": "1.78",
            "framerate": "24",
            "scantype": "progressive",
            "default": True,
            "forced": False,
            "duration": "42m 15s",
            "durationinseconds": 2535,
        },
        "audio": [
            {
                "codec": "AAC",
                "micodec": "mp4a",
                "bitrate": "128",
                "language": "en",
                "scantype": "",
                "channels": "2",
                "samplingrate": "44100",
                "default": True,
                "forced": False,
            }
        ],
    }

@pytest.fixture(name="mock_episode")
def mock_episode_fixture():
    """
    Fixture for a mock episode metadata dictionary
    """
    return {
        "episode_number": 1,
        "episode_name": "Pilot",
        "series_name": "My Show",
        "overview": "The first episode of the series.",
        "community_rating": 8.5,
        "air_date": "2023-01-01",
        "still_url": "https://example.com/still.jpg",
        "actors": [{"name": "Actor One", "role": "Protagonist", "thumb": "https://example.com/thumb1.jpg"}],
        "guest_stars": [],
        "crew": [],
    }

@pytest.fixture(name="mock_season_data")
def mock_season_data_fixture():
    """
    Fixture for a mock season metadata dictionary
    """
    return {
        "series_name": "My Show",
        "season_number": 1,
        "season_name": "Season One",
        "release_date": "2023-01-01",
        "genres": ["Drama", "Mystery"],
        "actors": [
            {"name": "Actor One", "role": "Protagonist"},
            {"name": "Actor Two", "role": "Supporting"}
        ],
        "overview": "An exciting first season of the series.",
        "community_rating": 8.7,
        "poster_url": "https://example.com/poster.jpg"
    }

def test_generate_tvshow_episode(mock_episode: Episode, mock_season_data: Season, mock_file_info: MedaInfoStrut):
    """
    Test the generation of an NFO file for a TV show episode
    """
    # Mock the FileInfo.get_media_info method
    FileInfo.get_media_info = MagicMock(return_value=mock_file_info)

    # Initialize the NFO object
    nfo = NFO(data=mock_season_data)

    # Generate the NFO for the episode
    result = nfo.generate_tvshow_episode(mock_episode, "/path/to/episode.mp4")

    # Assert the generated NFO contains expected data
    assert "<title>Pilot</title>" in result
    assert "<showtitle>My Show</showtitle>" in result
    assert "<season>01</season>" in result
    assert "<episode>01</episode>" in result
    assert "<aired>2023-01-01</aired>" in result
    assert "<rating>8.5</rating>" in result
    assert "<plot>The first episode of the series.</plot>" in result
    assert "<genre>Drama</genre>" in result
    assert "<genre>Mystery</genre>" in result
    assert "<actor>" in result
    assert "<name>Actor One</name>" in result
    assert "<role>Protagonist</role>" in result
    assert "<thumb>https://example.com/thumb1.jpg</thumb>" in result

    # Assert video details
    assert "<codec>H.264</codec>" in result
    assert "<micodec>avc1</micodec>" in result
    assert "<bitrate>1500</bitrate>" in result
    assert "<width>1920</width>" in result
    assert "<height>1080</height>" in result
    assert "<aspect>16:9</aspect>" in result
    assert "<aspectratio>16:9</aspectratio>" in result
    assert "<framerate>24</framerate>" in result
    assert "<scantype>progressive</scantype>" in result
    assert "<default>True</default>" in result
    assert "<forced>False</forced>" in result
    assert "<duration>42m 15s</duration>" in result
    assert "<durationinseconds>2535</durationinseconds>" in result

    # Assert audio details
    assert "<codec>AAC</codec>" in result
    assert "<micodec>mp4a</micodec>" in result
    assert "<bitrate>128</bitrate>" in result
    assert "<language>en</language>" in result
    assert "<channels>2</channels>" in result
    assert "<samplingrate>44100</samplingrate>" in result


def test_generate_tvshow_season(mock_season_data: Season):
    """
    Test the generation of an NFO file for a TV show season
    """
    # Initialize the NFO object
    nfo = NFO(data=mock_season_data)

    # Generate the NFO for the season
    result = nfo.generate_tvshow_season()

    # Assert the generated NFO contains expected data
    assert "<title>Season 1 - Season One</title>" in result
    assert "<seasonnumber>1</seasonnumber>" in result
    assert "<plot>An exciting first season of the series.</plot>" in result
    assert "<outline>An exciting first season of the series.</outline>" in result
    assert "<premiered>2023-01-01</premiered>" in result
    assert "<releasedate>2023-01-01</releasedate>" in result
    assert "<dateadded>" in result  # Ensures dateadded is generated

    # Assert actor details
    assert "<actor>" in result
    assert "<name>Actor One</name>" in result
    assert "<role>Protagonist</role>" in result
    assert "<name>Actor Two</name>" in result
    assert "<role>Supporting</role>" in result

    # Assert genre details
    assert "<genre>Drama</genre>" in result
    assert "<genre>Mystery</genre>" in result
