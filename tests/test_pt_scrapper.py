import pytest
from unittest.mock import Mock
from bs4 import BeautifulSoup
import requests
from media_files_organizer.pt_scrapper import PTScrapper  # Import your class here

@pytest.fixture
def mock_response_flora():
    # Load the HTML content from a test file
    with open("tests/mocks/pt_scrapper.all_info.flora_miranda.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Create a mock response
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

@pytest.fixture
def mock_response_isabel_nunes():
    # Load the HTML content from a different test file for another case
    with open("tests/mocks/pt_scrapper.missing_bio.isabel_nunes.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

def test_scrape_full_bio(mock_response_flora, mocker):
    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_flora)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape("http://example.com")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["nome"] == "Flora Miranda"
    assert data["nome_completo"] == "Maria Flora Granja Miranda"
    assert data["naturalidade"] == "Porto, Portugal"
    assert data["nascimento"] == "1983-12-18"
    assert data["reconhecimento"] == "Diamante Azul, Mallow, Frida, WilyKit"
    assert "Cantora e atriz de profissão" in data["biography"]
    assert data["profile_photo"] == "https://static.wikia.nocookie.net/vozesportuguesas/images/3/31/Flora_miranda_2.jpg/revision/latest/scale-to-width-down/1000?cb=20201124004416&path-prefix=pt"


def test_scrape_partial_bio(mock_response_isabel_nunes, mocker):
    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_isabel_nunes)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape("http://example.com")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["nome"] == "Isabel Nunes"
    assert data["nome_completo"] == "Isabel Cristina Nunes Rodrigues"
    assert data["naturalidade"] == "Vila Nova de Gaia, Porto, Portugal"
    assert data["nascimento"] == None
    assert data["reconhecimento"] == "Finn, Joana, Sophocles, Carmen Sandiego"
    assert data["biography"] == None
    assert data["profile_photo"] == "https://static.wikia.nocookie.net/vozesportuguesas/images/7/7e/Isabel_Nuneshd.png/revision/latest/scale-to-width-down/1000?cb=20220609070250&path-prefix=pt"
