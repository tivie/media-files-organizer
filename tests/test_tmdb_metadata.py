import os
import pytest
from unittest.mock import patch
from media_files_organizer.tmdb_metadata import TMDBMetadata
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# load mock files
mocks = {}
with open("tests/mocks/tv_general_info.json") as f:
    mocks.update({"tv_general_info": json.load(f)})

with open("tests/mocks/tv_cast.json") as f:
    mocks.update({"tv_cast": json.load(f)})

with open("tests/mocks/tv_season_info.json") as f:
    mocks.update({"tv_season_info": json.load(f)})

with open("tests/mocks/tv_episode_1.json") as f:
    mocks.update({"tv_ep_1": json.load(f)})


@pytest.fixture
def tmdb_instance():
    """Fixture to initialize the TMDBMetadata class."""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        pytest.fail("TMDB_API_KEY is not set in the environment variables.")
    return TMDBMetadata(api_key)

def test_get_tv_general_info(tmdb_instance):
    """Test the _get_tv_general_info method."""
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = mocks["tv_general_info"]
        result = tmdb_instance._get_tv_general_info(media_id=1396)
        assert result["series_name"] == "Breaking Bad"
        assert "Drama" in result["genres"]

def test_get_tv_cast(tmdb_instance):
    """Test the _get_tv_cast method."""
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = mocks["tv_cast"]
        result = tmdb_instance._get_tv_cast(media_id=12345)
        assert len(result) == 348
        assert result[0]["name"] == "Bryan Cranston"
        assert result[0]["role"] == "Walter White"
        assert result[0]["type"] == "actor"
        assert result[0]["thumb"] == "/config/data/metadata/People/B/Bryan Cranston/folder.jpg"
        assert result[1]["name"] == "Aaron Paul"
        assert result[1]["role"] == "Jesse Pinkman"
        assert result[1]["type"] == "actor"
        assert result[1]["thumb"] == "/config/data/metadata/People/A/Aaron Paul/folder.jpg"

def test_get_tv_season_info(tmdb_instance):
    """Test the _get_tv_season_info method."""
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = mocks["tv_season_info"]
        result = tmdb_instance._get_tv_season_info(media_id=1396, season=1)
        assert result["season_name"] == "Season 1"
        assert result["season_number"] == 1
        # assert that overview starts with "Walter White, a high school chemistry teacher, learns he has terminal lung cancer."
        assert result["overview"] == "High school chemistry teacher Walter White's life is suddenly transformed by a dire medical diagnosis. Street-savvy former student Jesse Pinkman \"teaches\" Walter a new trade."
        assert result["community_rating"] == 8.3
        assert result["episode_count"] == 7
        assert result["release_date"] == "2008-01-20"
        assert result["poster_url"] == "https://image.tmdb.org/t/p/original/1BP4xYv9ZG4ZVHkL7ocOziBbSYH.jpg"
        assert len(result["episodes"]) == 0


def test__parse_crew(tmdb_instance):
    result = tmdb_instance._parse_crew(mocks["tv_ep_1"]["credits"]["crew"])
    assert len(result) == 6
    assert result[0]["name"] == "Vince Gilligan"
    assert result[0]["original_name"] == "Vince Gilligan"
    assert result[0]["type"] == "Writer"
    assert result[0]["photo"] == "https://image.tmdb.org/t/p/original/z3E0DhBg1V1PZVEtS9vfFPzOWYB.jpg"
    assert result[0]["thumb"] == "/config/data/metadata/People/V/Vince Gilligan/folder.jpg"

def test___parse_actors(tmdb_instance):
    result = tmdb_instance._parse_actors(mocks["tv_ep_1"]["credits"]["guest_stars"], type="GuestStar")
    assert len(result) == 16
    assert result[0]["name"] == "Steven Michael Quezada"
    assert result[0]["type"] == "GuestStar"
    assert result[0]["role"] == "Steven Gomez"
    assert result[0]["photo"] == "https://image.tmdb.org/t/p/original/pVYrDkwI6GWvCNL2kJhpDJfBFyd.jpg"
    assert result[0]["thumb"] == "/config/data/metadata/People/S/Steven Michael Quezada/folder.jpg"

    result = tmdb_instance._parse_actors(mocks["tv_ep_1"]["credits"]["cast"], type="actor")
    assert len(result) == 6
    assert result[0]["name"] == "Bryan Cranston"
    assert result[0]["role"] == "Walter White"
    assert result[0]["type"] == "actor"
    assert result[0]["photo"] == "https://image.tmdb.org/t/p/original/7Jahy5LZX2Fo8fGJltMreAI49hC.jpg"
    assert result[0]["thumb"] == "/config/data/metadata/People/B/Bryan Cranston/folder.jpg"

def test_fetch_with_invalid_media_type(tmdb_instance):
    """Test fetch method with an invalid media type."""
    with pytest.raises(ValueError):
        tmdb_instance.fetch(media_type="invalid_type", media_id=12345)


# Functional tests that requires an internet connection and a valid API key.
# They connect to the real API and so are skipped by default.
@pytest.mark.skip(reason="Functional tests that require a valid API key.")
def test_fetch_tv_series(tmdb_instance):
    """Test the fetch method with a valid TV series ID."""
    media_id = 1396  # Breaking Bad TV series ID
    season = 1
    metadata = tmdb_instance.fetch(media_type="tv", media_id=media_id, season=season)
    assert metadata["series_name"] == "Breaking Bad"
    assert "Drama" in metadata["genres"]
    assert len(metadata["actors"]) > 0
    assert any(
        cast_member["name"] == "Bryan Cranston" and cast_member["role"] == "Walter White"
        for cast_member in metadata["actors"]
    )
