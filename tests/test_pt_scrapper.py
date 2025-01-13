"""

This module contains test cases for the PTScrapper class.
"""
from unittest.mock import Mock
import pytest
from media_files_organizer.pt_scrapper import PTScrapper  # Import your class here

@pytest.fixture(name="mock_response_flora")
def mock_response_flora_fixture():
    """
    A fixture to return a mock response object with the HTML content of a test file.
    For the case of Flora Miranda, the page has all the information.
    """
    # Load the HTML content from a test file
    with open("tests/mocks/pt_scrapper.all_info.flora_miranda.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Create a mock response
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

@pytest.fixture(name="mock_response_isabel_nunes")
def mock_response_isabel_nunes_fixture():
    """
    A fixture to return a mock response object with the HTML content of a test file.
    For the case of Isabel Nunes, the page is missing the biography and birth date.
    """
    # Load the HTML content from a different test file for another case
    with open("tests/mocks/pt_scrapper.missing_bio.isabel_nunes.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

@pytest.fixture(name="mock_response_season_pokemon_alola")
def mock_response_season_alola_fixture():
    """
    A fixture to return a mock response object with the HTML content of a test file.
    For the case of a season page, the page has all the information.
    """
    # Load the HTML content from a test file
    with open("tests/mocks/seasons/pt_scrapper.pokemon_sol_e_lua_pt_dobragens.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Create a mock response
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

@pytest.fixture(name="mock_response_season_evangelion")
def mock_response_season_evangelion_fixture():
    """
    A fixture to return a mock response object with the HTML content of a test file.
    For the case of a season page, the page has all the information.
    """
    # Load the HTML content from a test file
    with open("tests/mocks/seasons/pt_scrapper.evangelion.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Create a mock response
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

@pytest.fixture(name="mock_response_season_cinderela")
def mock_response_season_cinderela_fixture():
    """
    A fixture to return a mock response object with the HTML content of a test file.
    For the case of a season page, the page has all the information.
    """
    # Load the HTML content from a test file
    with open("tests/mocks/seasons/pt_scrapper.cinderela.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Create a mock response
    mock_resp = Mock()
    mock_resp.content = html_content
    return mock_resp

def test_scrape_full_bio(mock_response_flora: Mock, mocker: Mock):
    """
    Test the scrape method of the PTScrapper class to ensure it correctly parses and returns the expected data.

    Args:
        mock_response_flora (Mock): A mock response object to simulate the HTTP response.
        mocker (Mock): A mocker object to patch the requests.get call.

    Asserts:
        The returned data dictionary contains the expected values for the following keys:
        - "nome": "Flora Miranda"
        - "nome_completo": "Maria Flora Granja Miranda"
        - "naturalidade": "Porto, Portugal"
        - "nascimento": "1983-12-18"
        - "reconhecimento": "Diamante Azul, Mallow, Frida, WilyKit"
        - "biografia": Contains specific substrings indicating biographical details.
        - "foto_perfil": URL to the profile picture.
    """
    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_flora)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape_actor("http://example.com/flora")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["url"] == "http://example.com/flora"
    assert data["nome"] == "Flora Miranda"
    assert data["nome_completo"] == "Maria Flora Granja Miranda"
    assert data["naturalidade"] == "Porto, Portugal"
    assert data["nascimento"] == "1983-12-18"
    assert data["reconhecimento"] == "Diamante Azul, Mallow, Frida, WilyKit"
    assert data["biografia"] is not None
    assert isinstance(data["biografia"], str)
    assert "Cantora e atriz de profissão" in data["biografia"] # pylint: disable=unsupported-membership-test
    assert "Frequentou escolas como o Hot Club de Lisboa ou a Escola de Jazz do Porto." in data["biografia"] # pylint: disable=unsupported-membership-test
    assert "Neste momento é vocalista dos projetos Fado em Trio e Fauna & Flora. É também atriz e cantora no projeto infantil Panda e os Caricas do Canal Panda" in data["biografia"] # pylint: disable=unsupported-membership-test
    assert data["foto_perfil"] == "https://static.wikia.nocookie.net/vozesportuguesas/images/3/31/Flora_miranda_2.jpg/revision/latest/scale-to-width-down/1000?cb=20201124004416&path-prefix=pt"


def test_scrape_partial_bio(mock_response_isabel_nunes: Mock, mocker: Mock):
    """
    Test the PTScrapper's scrape method for a partial biography.
    This test mocks the requests.get call to return a predefined response and
    verifies that the PTScrapper correctly parses the data.
    Args:
        mock_response_isabel_nunes (Mock): A mock response object containing the HTML to be scraped.
        mocker (Mock): A mocker object to patch the requests.get call.
    Assertions:
        Asserts that the parsed data contains the expected values for:
        - nome
        - nome_completo
        - naturalidade
        - nascimento
        - reconhecimento
        - biografia
        - foto_perfil
    """

    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_isabel_nunes)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape_actor("http://example.com/isabel_nunes")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["url"] == "http://example.com/isabel_nunes"
    assert data["nome"] == "Isabel Nunes"
    assert data["nome_completo"] == "Isabel Cristina Nunes Rodrigues"
    assert data["naturalidade"] == "Vila Nova de Gaia, Porto, Portugal"
    assert data["nascimento"] is None
    assert data["reconhecimento"] == "Finn, Joana, Sophocles, Carmen Sandiego"
    assert data["biografia"] is None
    assert data["foto_perfil"] == "https://static.wikia.nocookie.net/vozesportuguesas/images/7/7e/Isabel_Nuneshd.png/revision/latest/scale-to-width-down/1000?cb=20220609070250&path-prefix=pt"

def test_scrape_season_with_evangelion(mock_response_season_evangelion: Mock, mocker: Mock):
    """
    Test the PTScrapper's scrape method for a season page.
    mock_response_season (Mock): A mock response object containing the HTML to be scraped.
    """
    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_season_evangelion)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape_season("http://example.com/eva", "Evangelion")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["url"] == "http://example.com/eva"
    assert data["nome"] == "Evangelion"
    assert data["nome_portugues"] is not None
    assert data["nome_portugues"] == "Evangelion"
    assert data["outline"] is not None
    assert data["outline"] == "Evangelion (Shinseiki Evangelion, no original) é uma série de animação japonesa produzida pelos estúdios Gainax e Tatsunoko Production."
    assert data["overview"] is not None
    assert data["overview"] == "A série de ação pós-apocalíptica gira em torno de uma organização paramilitar chamada NERV, criada para combater seres monstruosos chamados Anjos, utilizando seres gigantes chamados Unidades Evangelion (ou EVAs)."
    assert len(data["atores"]) == 42

def test_scrape_season_with_cinderela(mock_response_season_cinderela: Mock, mocker: Mock):
    """
    Test the PTScrapper's scrape method for a season page.
    mock_response_season (Mock): A mock response object containing the HTML to be scraped.
    """
    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_season_cinderela)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape_season("http://example.com/cinderela", "Cinderela")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["url"] == "http://example.com/cinderela"
    assert data["nome"] == "Cinderela"
    assert data["nome_portugues"] is not None
    assert data["nome_portugues"] == "A Cinderela"
    assert data["outline"] is not None
    assert data["outline"] == "A Cinderela (Cinderella Monogatari, no original) é uma série de animação nipo-italiana produzida pelos estúdios Tatsunoko e a Mondo TV."
    assert data["overview"] is not None
    assert data["overview"] == "Cinderela é uma rapariga doce ingénua. Depois de o seu pai partir em viagem, a sua Madrasta e as suas filhas ordenam que Cinderela faça as tarefas domésticas da casa."
    assert len(data["atores"]) == 37

    assert data["atores"][0]["nome"] == "Zélia Santos" # Zélia Santos
    assert data["atores"][0]["role"] == "Cinderela" # Zélia Santos
    assert data["atores"][0]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Z%C3%A9lia_Santos" # Zélia Santos

    assert data["atores"][1]["nome"] == "Raul Constante Pereira" # Raul Constante Pereira
    assert data["atores"][1]["role"] == "Príncipe Charles" # Raul Constante Pereira
    assert data["atores"][1]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raul_Constante_Pereira" # Raul Constante Pereira

    assert data["atores"][2]["nome"] == "Sissa Afonso" # Sissa Afonso
    assert data["atores"][2]["role"] == "Madame Paulette" # Sissa Afonso
    assert data["atores"][2]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Sissa_Afonso" # Sissa Afonso

    assert data["atores"][3]["nome"] == "Raquel Rosmaninho" # Raquel Rosmaninho
    assert data["atores"][3]["role"] == "Madrasta" # Raquel Rosmaninho
    assert data["atores"][3]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho" # Raquel Rosmaninho

    assert data["atores"][4]["nome"] == "Margarida Machado" # Margarida Machado
    assert data["atores"][4]["role"] == "Catherine" # Margarida Machado
    assert data["atores"][4]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Margarida_Machado" # Margarida Machado

    assert data["atores"][5]["nome"] == "Sissa Afonso" # Sissa Afonso
    assert data["atores"][5]["role"] == "Jane" # Sissa Afonso
    assert data["atores"][5]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Sissa_Afonso" # Sissa Afonso

    assert data["atores"][6]["nome"] == "Raul Constante Pereira" # Raul Constante Pereira
    assert data["atores"][6]["role"] == "Poly" # Raul Constante Pereira
    assert data["atores"][6]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raul_Constante_Pereira" # Raul Constante Pereira

    assert data["atores"][7]["nome"] == "Sissa Afonso" # Sissa Afonso
    assert data["atores"][7]["role"] == "Papy" # Sissa Afonso
    assert data["atores"][7]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Sissa_Afonso" # Sissa Afonso

    assert data["atores"][8]["nome"] == "Zélia Santos" # Zélia Santos
    assert data["atores"][8]["role"] == "Chouchou" # Zélia Santos
    assert data["atores"][8]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Z%C3%A9lia_Santos" # Zélia Santos

    assert data["atores"][9]["nome"] == "João Cardoso" # João Cardoso
    assert data["atores"][9]["role"] == "Bingo" # João Cardoso
    assert data["atores"][9]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Cardoso" # João Cardoso

    assert data["atores"][10]["nome"] == "Rui Oliveira" # Rui Oliveira
    assert data["atores"][10]["role"] == "Bingo" # Rui Oliveira
    assert data["atores"][10]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira" # Rui Oliveira

    assert data["atores"][11]["nome"] == "Jorge Paupério" # Jorge Paupério
    assert data["atores"][11]["role"] == "Bingo" # Jorge Paupério
    assert data["atores"][11]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Paup%C3%A9rio" # Jorge Paupério

    assert data["atores"][12]["nome"] == "Rui Oliveira" # Rui Oliveira
    assert data["atores"][12]["role"] == "Misha" # Rui Oliveira
    assert data["atores"][12]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira" # Rui Oliveira

    assert data["atores"][13]["nome"] == "Jorge Paupério" # Jorge Paupério
    assert data["atores"][13]["role"] == "Misha" # Jorge Paupério
    assert data["atores"][13]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Paup%C3%A9rio" # Jorge Paupério

    assert data["atores"][14]["nome"] == "Sissa Afonso" # Sissa Afonso
    assert data["atores"][14]["role"] == "Misha" # Sissa Afonso
    assert data["atores"][14]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Sissa_Afonso" # Sissa Afonso

    assert data["atores"][15]["nome"] == "Jorge Pinto" # Jorge Pinto
    assert data["atores"][15]["role"] == "Duque Zara" # Jorge Pinto
    assert data["atores"][15]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Pinto" # Jorge Pinto

    assert data["atores"][16]["nome"] == "Jorge Paupério" # Jorge Paupério
    assert data["atores"][16]["role"] == "Duque Zara" # Jorge Paupério
    assert data["atores"][16]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Paup%C3%A9rio" # Jorge Paupério

    assert data["atores"][17]["nome"] == "João Cardoso" # João Cardoso
    assert data["atores"][17]["role"] == "Duque Zara" # João Cardoso
    assert data["atores"][17]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Cardoso" # João Cardoso

    assert data["atores"][18]["nome"] == "Jorge Vasques" # Jorge Vasques
    assert data["atores"][18]["role"] == "Duque Zara" # Jorge Vasques
    assert data["atores"][18]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Vasques" # Jorge Vasques

    assert data["atores"][19]["nome"] == "Sissa Afonso" # Sissa Afonso
    assert data["atores"][19]["role"] == "Isabelle" # Sissa Afonso
    assert data["atores"][19]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Sissa_Afonso" # Sissa Afonso

    assert data["atores"][20]["nome"] == "Raquel Rosmaninho" # Raquel Rosmaninho
    assert data["atores"][20]["role"] == "Alex" # Raquel Rosmaninho
    assert data["atores"][20]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho" # Raquel Rosmaninho

    assert data["atores"][21]["nome"] == "João Cardoso" # João Cardoso
    assert data["atores"][21]["role"] == "Rei" # João Cardoso
    assert data["atores"][21]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Cardoso" # João Cardoso

    assert data["atores"][22]["nome"] == "Rui Oliveira" # Rui Oliveira
    assert data["atores"][22]["role"] == "Rei" # Rui Oliveira
    assert data["atores"][22]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira" # Rui Oliveira

    assert data["atores"][23]["nome"] == "Jorge Paupério" # Jorge Paupério
    assert data["atores"][23]["role"] == "Rei" # Jorge Paupério
    assert data["atores"][23]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Paup%C3%A9rio" # Jorge Paupério

    assert data["atores"][24]["nome"] == "Jorge Vasques" # Jorge Vasques
    assert data["atores"][24]["role"] == "Rei" # Jorge Vasques
    assert data["atores"][24]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Vasques" # Jorge Vasques

    assert data["atores"][25]["nome"] == "Margarida Machado" # Margarida Machado
    assert data["atores"][25]["role"] == "Rainha" # Margarida Machado
    assert data["atores"][25]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Margarida_Machado" # Margarida Machado

    assert data["atores"][26]["nome"] == "Jorge Paupério" # Jorge Paupério
    assert data["atores"][26]["role"] == "Pai da Cinderela" # Jorge Paupério
    assert data["atores"][26]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Paup%C3%A9rio" # Jorge Paupério

    assert data["atores"][27]["nome"] == "Rui Oliveira" # Rui Oliveira
    assert data["atores"][27]["role"] == "Pai da Cinderela" # Rui Oliveira
    assert data["atores"][27]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira" # Rui Oliveira

    assert data["atores"][28]["nome"] == "João Cardoso" # João Cardoso
    assert data["atores"][28]["role"] == "Pierre, o Cocheiro" # João Cardoso
    assert data["atores"][28]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Cardoso" # João Cardoso

    assert data["atores"][29]["nome"] == "Jorge Paupério" # Jorge Paupério
    assert data["atores"][29]["role"] == "Hans, o Precetor" # Jorge Paupério
    assert data["atores"][29]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Paup%C3%A9rio" # Jorge Paupério

    assert data["atores"][30]["nome"] == "João Cardoso" # João Cardoso
    assert data["atores"][30]["role"] == "Hans, o Precetor" # João Cardoso
    assert data["atores"][30]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Cardoso" # João Cardoso

    assert data["atores"][31]["nome"] == "Rui Oliveira" # Rui Oliveira
    assert data["atores"][31]["role"] == "Ian" # Rui Oliveira
    assert data["atores"][31]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira" # Rui Oliveira

    assert data["atores"][32]["nome"] == "Jorge Vasques" # Jorge Vasques
    assert data["atores"][32]["role"] == "Ian" # Jorge Vasques
    assert data["atores"][32]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jorge_Vasques" # Jorge Vasques

    assert data["atores"][33]["nome"] == "Raquel Rosmaninho" # Raquel Rosmaninho
    assert data["atores"][33]["role"] == "Ian" # Raquel Rosmaninho
    assert data["atores"][33]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho" # Raquel Rosmaninho

    assert data["atores"][34]["nome"] == "Raquel Rosmaninho" # Raquel Rosmaninho
    assert data["atores"][34]["role"] == "Marcel" # Raquel Rosmaninho
    assert data["atores"][34]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho" # Raquel Rosmaninho

    assert data["atores"][35]["nome"] == "João Cardoso" # João Cardoso
    assert data["atores"][35]["role"] == "Marcel" # João Cardoso
    assert data["atores"][35]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Cardoso" # João Cardoso

    assert data["atores"][36]["nome"] == "Sissa Afonso" # Sissa Afonso
    assert data["atores"][36]["role"] == "Marcel" # Sissa Afonso
    assert data["atores"][36]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Sissa_Afonso" # Sissa Afonso



def test_scrape_season_with_pokemon_alola(mock_response_season_pokemon_alola: Mock, mocker: Mock):
    """
    Test the PTScrapper's scrape method for a season page.
    mock_response_season (Mock): A mock response object containing the HTML to be scraped.
    """
    # Mock the requests.get call to return the mock response
    mocker.patch("requests.get", return_value=mock_response_season_pokemon_alola)

    # Create an instance of the scrapper
    scrapper = PTScrapper()

    # Call the scrape method
    data = scrapper.scrape_season("http://example.com/pokemon_sol_e_lua_pt_dobragens", "Pokémon: Sol e Lua")  # URL doesn't matter since it's mocked

    # Assertions to validate the data
    assert data["url"] == "http://example.com/pokemon_sol_e_lua_pt_dobragens"
    assert data["nome"] == "Pokémon: Sol e Lua"
    assert data["nome_portugues"] is not None
    assert data["nome_portugues"] == "Pokémon, A Série: Sol e Lua"
    assert data["outline"] is not None
    assert data["outline"] == "Pokémon, A Série: Sol e Lua (Pocket Monsters Sun & Moon, no original) é uma série de animação japonesa produzida pelo estúdio OLM. É a 20ª temporada da série Pokémon e a 1ª da saga Sol e Lua."
    assert data["overview"] is not None
    assert data["overview"].startswith("Os desafios não param de chegar, e o Ash agradece! ")
    assert len(data["atores"]) == 27

    assert data["atores"][0]["nome"] == "Raquel Rosmaninho"
    assert data["atores"][1]["nome"] == "Bernardo Gavina"
    assert data["atores"][2]["nome"] == "Flora Miranda"
    assert data["atores"][3]["nome"] == "Isabel Nunes"
    assert data["atores"][4]["nome"] == "Isabel Queirós"
    assert data["atores"][5]["nome"] == "Raquel Pereira"
    assert data["atores"][6]["nome"] == "Raquel Rosmaninho"
    assert data["atores"][7]["nome"] == "Pedro Mendonça"
    assert data["atores"][8]["nome"] == "Mário Santos"
    assert data["atores"][9]["nome"] == "Ivo Bastos"
    assert data["atores"][10]["nome"] == "Pedro Frias"
    assert data["atores"][11]["nome"] == "Rui Oliveira"
    assert data["atores"][12]["nome"] == "Rodrigo Santos"
    assert data["atores"][13]["nome"] == "Ângela Marques"
    assert data["atores"][14]["nome"] == "Ivo Bastos"
    assert data["atores"][15]["nome"] == "Helena Montez"
    assert data["atores"][16]["nome"] == "Pedro Almendra"
    assert data["atores"][17]["nome"] == "Pedro Manana"
    assert data["atores"][18]["nome"] == "Tiago Araújo"
    assert data["atores"][19]["nome"] == "Joana Africano"
    assert data["atores"][20]["nome"] == "Mário Santos"
    assert data["atores"][21]["nome"] == "Ricardo Oliveira"
    assert data["atores"][22]["nome"] == "Roberto Madalena"
    assert data["atores"][23]["nome"] == "Vânia Blubird"
    assert data["atores"][24]["nome"] == "Zélia Santos"
    assert data["atores"][25]["nome"] == "Ana Regueiras"
    assert data["atores"][26]["nome"] == "João Guimarães"

    assert data["atores"][0]["role"] == "Ash"
    assert data["atores"][1]["role"] == "Kiawe"
    assert data["atores"][2]["role"] == "Mallow"
    assert data["atores"][3]["role"] == "Sophocles"
    assert data["atores"][4]["role"] == "Lana"
    assert data["atores"][5]["role"] == "Lillie"
    assert data["atores"][6]["role"] == "Jessie"
    assert data["atores"][7]["role"] == "James"
    assert data["atores"][8]["role"] == "Meowth"
    assert data["atores"][9]["role"] == "Rotom Dex"
    assert data["atores"][10]["role"] == "Prof. Kukui"
    assert data["atores"][11]["role"] == "Diretor Oak"
    assert data["atores"][12]["role"] == "Giovanni"
    assert data["atores"][13]["role"] == "Delia Ketchum"
    assert data["atores"][14]["role"] == "Prof. Oak"
    assert data["atores"][15]["role"] == "Misty"
    assert data["atores"][16]["role"] == "Brock"
    assert data["atores"][17]["role"] == "Tupp"
    assert data["atores"][18]["role"] == "Zipp"
    assert data["atores"][19]["role"] == "Tipp"
    assert data["atores"][20]["role"] == "Narrador"
    assert data["atores"][21]["role"] == "Vozes Adicionais"
    assert data["atores"][22]["role"] == "Vozes Adicionais"
    assert data["atores"][23]["role"] == "Vozes Adicionais"
    assert data["atores"][24]["role"] == "Vozes Adicionais"
    assert data["atores"][25]["role"] == "Tema de Abertura"
    assert data["atores"][26]["role"] == "Tema de Abertura"

    assert data["atores"][0]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho" # Raquel Rosmaninho
    assert data["atores"][1]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Bernardo_Gavina" # Bernardo Gavina
    assert data["atores"][2]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Flora_Miranda" # Flora Miranda
    assert data["atores"][3]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Isabel_Nunes" # Isabel Nunes
    assert data["atores"][4]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Isabel_Queir%C3%B3s" # Isabel Queirós
    assert data["atores"][5]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Pereira" # Raquel Pereira
    assert data["atores"][6]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho" # Raquel Rosmaninho
    assert data["atores"][7]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Pedro_Mendon%C3%A7a" # Pedro Mendonça
    assert data["atores"][8]["url"] == "https://wikidobragens.fandom.com/pt/wiki/M%C3%A1rio_Santos" # Mário Santos
    assert data["atores"][9]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Ivo_Bastos" # Ivo Bastos
    assert data["atores"][10]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Pedro_Frias" # Pedro Frias
    assert data["atores"][11]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira" # Rui Oliveira
    assert data["atores"][12]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Rodrigo_Santos" # Rodrigo Santos
    assert data["atores"][13]["url"] == "https://wikidobragens.fandom.com/pt/wiki/%C3%82ngela_Marques" # Ângela Marques
    assert data["atores"][14]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Ivo_Bastos" # Ivo Bastos
    assert data["atores"][15]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Helena_Montez" # Helena Montez
    assert data["atores"][16]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Pedro_Almendra" # Pedro Almendra
    assert data["atores"][17]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Pedro_Manana" # Pedro Manana
    assert data["atores"][18]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Tiago_Ara%C3%BAjo" # Tiago Araújo
    assert data["atores"][19]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Joana_Africano" # Joana Africano
    assert data["atores"][20]["url"] == "https://wikidobragens.fandom.com/pt/wiki/M%C3%A1rio_Santos" # Mário Santos
    assert data["atores"][21]["url"] is None # Ricardo Oliveira
    assert data["atores"][22]["url"] is None # Roberto Madalena
    assert data["atores"][23]["url"] == "https://wikidobragens.fandom.com/pt/wiki/V%C3%A2nia_Blubird" # Vânia Blubird
    assert data["atores"][24]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Z%C3%A9lia_Santos" # Zélia Santos
    assert data["atores"][25]["url"] is None # Ana Regueiras
    assert data["atores"][26]["url"] == "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Guimar%C3%A3es" # João Guimarães
