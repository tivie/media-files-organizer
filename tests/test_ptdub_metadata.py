"""
Module: test_ptdub_metadata
===========================

This module contains unit tests for the `PTDubMetadata` class, which is responsible for fetching metadata related to Portuguese dubbed media. The tests validate the functionality of methods that fetch actor and season data using a mocked `PTScrapper` object.

Fixtures:
---------
- `mock_scrapper`: Provides a mocked `PTScrapper` instance that simulates the behavior of the real web scraper.
- `metadata`: Initializes a `PTDubMetadata` instance with the mocked `PTScrapper`.

Tests:
------
- `test_fetch_actor`: Verifies that the `fetch_actor` method correctly processes actor data fetched from a given URL.
- `test_fetch_actors`: Validates that the `fetch_actors` method handles multiple actors, including cases where actor URLs are missing.
- `test_fetch_actor_with_default_role`: Ensures that the `fetch_actor` method assigns the default role "Unknown" when no role is specified.
- `test_fetch_actors_with_empty_data`: Confirms that the `fetch_actors` method returns an empty list when no actors are present in the scraped season data.

Purpose:
--------
These tests ensure the robustness and correctness of the `PTDubMetadata` class, focusing on its integration with the `PTScrapper` and its ability to handle various edge cases.

Usage:
------
Run the tests using pytest:
    $ pytest test_ptdub_metadata.py
"""
from unittest.mock import MagicMock
import pytest
from media_files_organizer.ptdub_metadata import PTDubMetadata
from media_files_organizer.pt_scrapper import PTScrapper, ScrapedActor, ScrapedSeason

@pytest.fixture(name="mock_scrapper")
def mock_scrapper_fixture():
    """
    Fixture that creates a mocked PTScrapper instance.
    
    Returns:
        MagicMock: A mocked PTScrapper object with the same interface as the real class.
    """
    return MagicMock(spec=PTScrapper)

@pytest.fixture(name="ptdub_metadata")
def metadata(mock_scrapper: MagicMock):
    """
    Fixture that initializes the PTDubMetadata class with a mocked scrapper.
    
    Args:
        mock_scrapper (MagicMock): The mocked PTScrapper instance.
    
    Returns:
        PTDubMetadata: An instance of PTDubMetadata initialized with the mocked scrapper.
    """
    return PTDubMetadata(scrapper=mock_scrapper)

def test_fetch_actor(ptdub_metadata: PTDubMetadata, mock_scrapper: MagicMock):
    """
    Test the fetch_actor method of the PTDubMetadata class.
    
    Ensures that:
    - The method correctly fetches and processes actor data from a given URL.
    - The scrapper's scrape_actor method is called with the correct arguments.
    
    Args:
        metadata (PTDubMetadata): The test instance of PTDubMetadata.
        mock_scrapper (MagicMock): The mocked PTScrapper instance.
    """
    # Configurar o mock para o scrapper
    mock_scrapper.scrape_actor.return_value = ScrapedActor(
        url="http://example.com/actor",
        nome="João Silva",
        nome_completo="João Pedro da Silva",
        naturalidade="Lisboa",
        nascimento="1980-01-01",
        ano_nascimento=1980,
        reconhecimento="Dublador principal",
        foto_perfil="http://example.com/profile.jpg",
        biografia="Ator experiente.",
        role="Protagonist"
    )

    # Chamar o método
    actor = ptdub_metadata.fetch_actor("http://example.com/actor", role="Protagonist")

    # Verificar o resultado
    assert actor["name"] == "João Silva"
    assert actor["original_name"] == "João Pedro da Silva"
    assert actor["type"] == "actor"
    assert actor["role"] == "Protagonist"
    assert actor["photo"] == "http://example.com/profile.jpg"
    assert actor["thumb"] == "/config/data/metadata/People/J/João Silva/folder.jpg"

    # Verificar se o método do scrapper foi chamado corretamente
    mock_scrapper.scrape_actor.assert_called_once_with("http://example.com/actor")

def test_fetch_actors(ptdub_metadata: PTDubMetadata, mock_scrapper: MagicMock):
    """
    Test the fetch_actors method of the PTDubMetadata class.
    
    Ensures that:
    - The method correctly processes multiple actors from a season's URL.
    - Actors with missing URLs are handled appropriately.
    - The scrapper's scrape_season and scrape_actor methods are called with the correct arguments.
    
    Args:
        metadata (PTDubMetadata): The test instance of PTDubMetadata.
        mock_scrapper (MagicMock): The mocked PTScrapper instance.
    """
    # Configurar o mock para o scrapper
    mock_scrapper.scrape_season.return_value = ScrapedSeason(
        url="http://example.com/season",
        nome="Temporada 1",
        nome_portugues="Season 1",
        outline="Descrição da temporada.",
        overview="Resumo detalhado da temporada.",
        atores=[
            ScrapedActor(
                url="http://example.com/actor1",
                nome="Maria Costa",
                nome_completo="Maria dos Anjos Costa",
                naturalidade="Porto",
                nascimento=None,
                ano_nascimento=None,
                reconhecimento=None,
                foto_perfil="http://example.com/maria.jpg",
                biografia=None,
                role="Villain"
            ),
            ScrapedActor(
                url=None,
                nome="Carlos Santos",
                nome_completo=None,
                naturalidade=None,
                nascimento=None,
                ano_nascimento=None,
                reconhecimento=None,
                foto_perfil=None,
                biografia=None,
                role=None
            )
        ]
    )

    # Configurar o mock para fetch_actor
    mock_scrapper.scrape_actor.return_value = ScrapedActor(
        url="http://example.com/actor1",
        nome="Maria Costa",
        nome_completo="Maria dos Anjos Costa",
        naturalidade="Porto",
        nascimento=None,
        ano_nascimento=None,
        reconhecimento=None,
        foto_perfil="http://example.com/maria.jpg",
        biografia=None,
        role="Villain"
    )

    # Chamar o método
    actors = ptdub_metadata.fetch_actors("http://example.com/season", "Season 1")

    # Verificar o resultado
    assert len(actors) == 2

    # Verificar o primeiro ator (com URL)
    assert actors[0]["name"] == "Maria Costa"
    assert actors[0]["original_name"] == "Maria dos Anjos Costa"
    assert actors[0]["role"] == "Villain"
    assert actors[0]["photo"] == "http://example.com/maria.jpg"
    assert actors[0]["thumb"] == "/config/data/metadata/People/M/Maria Costa/folder.jpg"

    # Verificar o segundo ator (sem URL)
    assert actors[1]["name"] == "Carlos Santos"
    assert actors[1]["original_name"] is None
    assert actors[1]["role"] == "Unknown"
    assert actors[1]["photo"] is None
    assert actors[1]["thumb"] == "/config/data/metadata/People/C/Carlos Santos/folder.jpg"

    # Verificar chamadas aos métodos do scrapper
    mock_scrapper.scrape_season.assert_called_once_with("http://example.com/season", "Season 1")
    mock_scrapper.scrape_actor.assert_called_once_with("http://example.com/actor1")

def test_fetch_actor_with_default_role(ptdub_metadata: PTDubMetadata, mock_scrapper: MagicMock):
    """
    Test the fetch_actor method when no role is specified.

    Ensures that:
    - The default role 'Unknown' is assigned correctly.
    
    Args:
        metadata (PTDubMetadata): The test instance of PTDubMetadata.
        mock_scrapper (MagicMock): The mocked PTScrapper instance.
    """
    # Configurar o mock
    mock_scrapper.scrape_actor.return_value = ScrapedActor(
        url="http://example.com/actor",
        nome="Pedro Silva",
        nome_completo="Pedro Miguel da Silva",
        naturalidade=None,
        nascimento=None,
        ano_nascimento=None,
        reconhecimento=None,
        foto_perfil="http://example.com/pedro.jpg",
        biografia=None,
        role=None
    )

    # Chamar o método
    actor = ptdub_metadata.fetch_actor("http://example.com/actor")

    # Verificar o resultado
    assert actor["role"] == "Unknown"

def test_fetch_actors_with_empty_data(ptdub_metadata: PTDubMetadata, mock_scrapper: MagicMock):
    """
    Test the fetch_actors method with an empty season data response.
    
    Ensures that:
    - An empty list is returned when no actors are present.
    - The scrapper's scrape_season method is called correctly.
    
    Args:
        metadata (PTDubMetadata): The test instance of PTDubMetadata.
        mock_scrapper (MagicMock): The mocked PTScrapper instance.
    """
    # Configurar o mock
    mock_scrapper.scrape_season.return_value = ScrapedSeason(
        url="http://example.com/season",
        nome="Temporada 1",
        nome_portugues="Season 1",
        outline=None,
        overview=None,
        atores=[]
    )

    # Chamar o método
    actors = ptdub_metadata.fetch_actors("http://example.com/season", "Season 1")

    # Verificar o resultado
    assert actors == []

    # Verificar chamadas ao scrapper
    mock_scrapper.scrape_season.assert_called_once_with("http://example.com/season", "Season 1")
