"""
A webscraper for Portuguese dubs on the Fandom wiki.

Attributes:
None

Methods:
scrape(url: str) -> ScrapeResult: Scrape data from the given URL.
"""

from typing import TypedDict, Optional
from datetime import datetime
import locale
import re
from bs4 import BeautifulSoup, Tag, NavigableString
import requests


class ScrapedActor(TypedDict):
    """
    A dictionary containing the scraped data from a Portuguese
    dubber's Fandom wiki page.
    """
    url: Optional[str]
    nome: str
    nome_completo: Optional[str]
    naturalidade: Optional[str]
    nascimento: Optional[str]
    ano_nascimento: Optional[int]
    reconhecimento: Optional[str]
    foto_perfil: Optional[str]
    biografia: Optional[str]
    role: Optional[str]
    dbid: Optional[int]

class ScrapedSeason(TypedDict):
    """
    A dictionary containing the scraped data from
    a Portuguese dub season's Fandom wiki page.
    """
    url: str
    nome: str
    nome_portugues: Optional[str]
    outline: Optional[str]
    overview: Optional[str]
    atores: list[ScrapedActor]
    dbid: Optional[int]

class PTScrapper:
    """
    A webscraper for Portuguese dubs on the Fandom wiki.

    Attributes:
    _base_url (str): The base URL of the Fandom wiki. PRIVATE

    Methods:
    scrape_season(url: str, name: str) -> ScrapedSeason: Scrape data from the given URL.
    scrape_actor(url: str) -> ScrapedActor: Scrape data from the given URL.
    """

    _base_url: str = "https://wikidobragens.fandom.com"

    def __init__(self):
        """
        Initialize the scraper and set the locale to Portuguese (Portugal)
        for date parsing. Falls back if locale setting fails.
        """
        try:
            locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')  # Use 'pt_PT' for Portuguese (Portugal)
        except locale.Error:
            print("Locale not available. Ensure Portuguese locale is installed on your system.")

    def _validate_tag(self, result: Tag | NavigableString | int | None, identifier: str = "Unkown")-> Tag:

        tag: Optional[Tag] = result if isinstance(result, Tag) else None

        if not tag :
            raise ValueError(f"No '{identifier}' found in the page, but it was expected.")

        return tag

    def _clean_text(self, text: str) -> str:
        """Cleans up the given text by removing unnecessary spaces around punctuation and parentheses.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: The cleaned text with spaces removed before punctuation, after opening parentheses or quotes, and before closing parentheses or quotes.
        """

        # Remove spaces before punctuation
        text = re.sub(r'\s([,.!?;:])', r'\1', text)
        # Remove spaces after opening parentheses or quotes
        text = re.sub(r'([\(\[\{])\s', r'\1', text)
        # Remove spaces before closing parentheses or quotes
        text = re.sub(r'\s([\)\]\}])', r'\1', text)
        return text

    def scrape_season(self, url: str, name: str) -> ScrapedSeason:
        """
        Scrape data from the given URL.

        Parameters:
            url (str): The URL of the Fandom wiki page.
            name (str): The name of the season/series

        Returns:
            ScrapedSeason: A dictionary containing keys like 'nome', 'nome_completo', etc., and their values.
        """
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse the webpage content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting data
        data: ScrapedSeason = {
            "url": url,
            "nome": name,
            "nome_portugues": None,
            "outline": None,
            "overview": None,
            "atores": [],
            "dbid": None
        }

        # Extract Portuguese title
        first_heading = soup.find("h1", id="firstHeading")
        if first_heading:
            data["nome_portugues"] = first_heading.get_text(strip=True)

        # Extract outline
        content_text = soup.find("div", id="mw-content-text")
        if content_text:
            content_text = self._validate_tag(content_text, "Content Text")
            parser_output = content_text.find("div", class_="mw-parser-output")
            if parser_output:
                aside_tag = parser_output.find("aside")
                if aside_tag:
                    siblings_between: list[str] = []
                    aside_tag = self._validate_tag(aside_tag, "Aside")
                    for sibling in aside_tag.next_siblings:
                        # Stop at the first table
                        if isinstance(sibling, Tag) and sibling.name == "table":
                            break
                        # Include both text nodes and tags, skip empty strings
                        if isinstance(sibling, str) and sibling.strip():
                            siblings_between.append(sibling.strip())
                        elif isinstance(sibling, Tag):
                            siblings_between.append(sibling.get_text(strip=True))
                    data["outline"] = self._clean_text(" ".join([text.strip() for text in siblings_between if text.strip()]))

        # Extract overview
        target_tr = None
        for tr in soup.find_all("tr"):
            if tr.get_text(strip=True) == "Sinopse":
                target_tr = tr
                break

        if target_tr:
            next_sibling = target_tr.find_next_sibling("tr")
            if next_sibling:
                data["overview"] = next_sibling.get_text(strip=True)

        # Extract Portuguese dub cast (atores)
        versao_portuguesa_header = soup.find("span", id="Versão_Portuguesa")
        if not versao_portuguesa_header:
            return data

        h2_tag = versao_portuguesa_header.find_parent("h2")
        if not h2_tag:
            return data

        actors_table = h2_tag.find_next_sibling("table", class_="article-table")
        if not actors_table:
            return data

        actors_table = self._validate_tag(actors_table, "Actors Table")
        role = "" # initialize role here because of rowspan cases
        i=0

        for row in actors_table.find_all("tr")[1:]:  # Skip the header row
            columns = row.find_all("td")

            if not columns or columns == []:
                continue

            # Only one column means the previous it's a merged cell with the role name
            if len(columns) == 1:
                # let's check if it has a th sibling, for some stupid reason
                col: Tag = columns[0]
                th = col.find_previous_sibling("th")
                if th:
                    role = th.get_text(strip=True)

                actor = self._parse_actor_column(columns[0], role=role)

            else:
                role = columns[0].get_text(strip=True)
                actor = self._parse_actor_column(columns[1], role=role)

            if not actor:
                continue

            data["atores"].append(actor)

            i = i + 1

        return data

    def _parse_actor_column(self, column: Tag, role: str) -> ScrapedActor|None:
        """
        Parse the actor column in the table and return the scraped data.

        Parameters:
        column (Tag): The column tag containing the actor data.

        Returns:
        ScrapedActor: A dictionary containing the scraped data for the actor.
        """
        actor_name: str = column.get_text(strip=True)
        if not actor_name or actor_name == "" or actor_name == "—":
            return None

        actor_name = re.sub(r'\(.+\)', '', actor_name).strip()  # Remove any role info in parentheses
        if actor_name in ('N/A', 'N/D'):
            return None

        actor_link = column.find("a")
        actor_url: str|None = None

        if actor_link:
            actor_link = self._validate_tag(actor_link, "Actor Link")
            actor_url = self._base_url + str(actor_link["href"])
        else:
            actor_url = None

        actor_obj: ScrapedActor = {
            "nome": actor_name,
            "role": role,
            "url": actor_url,
            "nome_completo": None,
            "naturalidade": None,
            "nascimento": None,
            "ano_nascimento": None,
            "reconhecimento": None,
            "foto_perfil": None,
            "biografia": None,
            "dbid": None
        }

        return actor_obj


    def scrape_actor(self, url: str) -> ScrapedActor:
        """
        Scrape data from the given URL.

        Parameters:
        url (str): The URL of the Fandom wiki page.

        Returns:
        ScrapeResult: A dictionary containing keys like 'nome', 'nome_completo', etc., and their values.
        """
        # Send an HTTP request to the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse the webpage content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main container of interest
        result = soup.find('aside', class_='portable-infobox')
        aside_section: Tag = self._validate_tag(result, "aside")

        # Extracting data
        data: ScrapedActor = {
            "url": url,
            "nome": "",
            "nome_completo": None,
            "naturalidade": None,
            "nascimento": None,
            "ano_nascimento": None,
            "reconhecimento": None,
            "foto_perfil": None,
            "biografia": None,
            "role": None,
            "dbid": None
        }

        # Nome
        nome = aside_section.find('h2', class_='pi-title')
        if nome and nome.text:
            data['nome'] = nome.text.strip()
        else:
            raise ValueError("Nome não encontrado")

        # Nome Completo
        nome_completo = aside_section.find('div', {'data-source': 'nome'})
        if nome_completo:
            nome_completo = self._validate_tag(nome_completo, "Nome Completo div")
            nome_completo_value = nome_completo.find('div', class_='pi-data-value')
            data['nome_completo'] = nome_completo_value.text.strip() if nome_completo_value else None

        # Naturalidade
        naturalidade = aside_section.find('div', {'data-source': 'naturalidade'})
        if naturalidade:
            naturalidade = self._validate_tag(naturalidade, "Naturalidade div")
            naturalidade_value = naturalidade.find('div', class_='pi-data-value')
            data['naturalidade'] = naturalidade_value.text.strip() if naturalidade_value else None

        # Nascimento
        nascimento = aside_section.find('div', {'data-source': 'nascimento'})
        if nascimento:
            nascimento = self._validate_tag(nascimento, "Nascimento div")
            nascimento_value = nascimento.find('div', class_='pi-data-value')
            if nascimento_value and nascimento_value.text:
                nascimento_text = nascimento_value.text.strip()
                nascimento_cleaned = nascimento_text.split('(')[0].strip()  # Remove age part if present
                try:
                    parsed_date = datetime.strptime(nascimento_cleaned, '%d de %B de %Y')
                    data['nascimento'] = parsed_date.strftime('%Y-%m-%d')  # Convert to 'yyyy-mm-dd'
                    data["ano_nascimento"] = parsed_date.year
                except ValueError:
                    data['nascimento'] = nascimento_cleaned  # Fallback to raw text

        # Reconhecimento
        reconhecimento = aside_section.find('div', {'data-source': 'reconhecimento'})
        if reconhecimento:
            reconhecimento = self._validate_tag(reconhecimento, "Reconhecimento div")
            reconhecimento_value = reconhecimento.find('div', class_='pi-data-value')
            if reconhecimento_value:
                reconhecimentos = [item.strip() for item in reconhecimento_value.stripped_strings]
                data['reconhecimento'] = ", ".join(reconhecimentos)

        # Profile Photo
        profile_photo = aside_section.find('figure', {'data-source': 'image'})
        if profile_photo:
            img_tag = profile_photo.find('img')
            if img_tag:
                img_tag = self._validate_tag(img_tag, "Profile Photo img")
                img_src = img_tag.get('src')
                if img_src:
                    if isinstance(img_src, str):
                        img_src = img_src.replace('&amp;', '&')
                        img_src = re.sub(r'scale-to-width-down/\d+', 'scale-to-width-down/1000', img_src)
                        data['foto_perfil'] = img_src

        # Extracting Biography
        biography_section = soup.find('span', id='Biografia')
        if biography_section:
            biography: list[str] = []
            if biography_section.parent:
                for sibling in biography_section.parent.find_next_siblings():
                    if isinstance(sibling, Tag):
                        if sibling.name == 'h2':  # Stop at the next header
                            break
                        if sibling.name == 'p':  # Include paragraphs
                            biography.append(sibling.text.strip())
                data['biografia'] = "\n".join(biography)

        return data
