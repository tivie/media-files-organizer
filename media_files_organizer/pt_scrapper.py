from typing import TypedDict, Optional
from datetime import datetime
import locale
import re
from bs4 import BeautifulSoup
import requests

class ScrapeResult(TypedDict):
    """
    A dictionary containing the scraped data from a Portuguese
    dubber's Fandom wiki page.
    """
    nome: str
    nome_completo: Optional[str]
    naturalidade: Optional[str]
    nascimento: Optional[str]
    ano_nascimento: Optional[int]
    reconhecimento: Optional[str]
    foto_perfil: Optional[str]
    biografia: Optional[str]


class PTScrapper:
    """
    A webscraper for portugues dubs on the Fandom wiki.

    Attributes:
    None

    Methods:
    scrape(url: str) -> ScrapeResult: Scrape data from the given URL.
    """

    def __init__(self):
        # Set the locale to Portuguese (Portugal) for date parsing
        try:
            locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')  # Use 'pt_PT' for Portuguese (Portugal)
        except locale.Error:
            print("Locale not available. Ensure Portuguese locale is installed on your system.")
        

    def scrape(self, url: str) -> ScrapeResult:
        """
        Scrape data from the given URL.

        Returns:
        A dictionary containing keys like 'nome', 'nome_completo', etc., and their values.
        """

        # Send an HTTP request to the URL
        response = requests.get(url, timeout=10)

        # Parse the webpage content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main container of interest
        aside_section = soup.find('aside', class_='portable-infobox')

        # Extracting data
        data = {}

        # Nome
        nome = aside_section.find('h2', class_='pi-title')
        data['nome'] = nome.text.strip()
        if not nome:
            raise ValueError("Nome não encontrado")

        # Nome Completo
        nome_completo = aside_section.find('div', {'data-source': 'nome'})
        data['nome_completo'] = nome_completo.find('div', class_='pi-data-value').text.strip() if nome_completo else None

        # Naturalidade
        naturalidade = aside_section.find('div', {'data-source': 'naturalidade'})
        data['naturalidade'] = naturalidade.find('div', class_='pi-data-value').text.strip() if naturalidade else None

        # Nascimento (if exists)
        nascimento = aside_section.find('div', {'data-source': 'nascimento'})
        if nascimento:
            nascimento_text = nascimento.find('div', class_='pi-data-value').text.strip()
            # Remove the age part and parse the date
            nascimento_cleaned = nascimento_text.split('(')[0].strip()
            try:
                parsed_date = datetime.strptime(nascimento_cleaned, '%d de %B de %Y')
                data['nascimento'] = parsed_date.strftime('%Y-%m-%d')  # Convert to 'yyyy-mm-dd'
                data["ano_nascimento"] = parsed_date.year
            except ValueError:
                data['nascimento'] = nascimento_cleaned  # Keep original if parsing fails
        else:
            data['nascimento'] = None
            data["ano_nascimento"] = None


        # Reconhecimento
        reconhecimento = aside_section.find('div', {'data-source': 'reconhecimento'})
        if reconhecimento:
            reconhecimento_value = reconhecimento.find('div', class_='pi-data-value')
            # Create a list of items by splitting on <br> tags
            reconhecimentos = [item.strip() for item in reconhecimento_value.stripped_strings]
            # Join the list into a comma-separated string
            data['reconhecimento'] = ", ".join(reconhecimentos)
        else:
            data['reconhecimento'] = None


        # Profile Photo
        profile_photo = aside_section.find('figure', {'data-source': 'image'})
        if profile_photo:
            img_tag = profile_photo.find('img')
            if img_tag:
                img_src = img_tag.get('src')
                # Replace transformations
                if img_src:
                    img_src = img_src.replace('&amp;', '&')
                    img_src = re.sub(r'scale-to-width-down/\d+', 'scale-to-width-down/1000', img_src)
                data['foto_perfil'] = img_src
        else:
            data['foto_perfil'] = None

        # Extracting Biography
        biography_section = soup.find('span', id='Biografia')  # Find the "Biografia" section
        if biography_section:
            biography = []
            for sibling in biography_section.parent.find_next_siblings():
                if sibling.name == 'h2':  # Stop if another header is encountered
                    break
                if sibling.name == 'p':  # Add paragraphs to the biography list
                    biography.append(sibling.text.strip())
            data['biografia'] = "\n".join(biography)  # Combine all paragraphs into a single string
        else:
            data['biografia'] = None
        
        return data



