"""
ptdub_metadata.py
This module provides the PTDubMetadata class for fetching metadata related to Portuguese dubbed media.
It utilizes the PTScrapper class to scrape actor and season information from specified URLs.

Classes:
    PTDubMetadata: A class to fetch metadata for Portuguese dubbed media.

Usage example:
    scrapper = PTScrapper()
    metadata = PTDubMetadata(scrapper)
    actor = metadata.fetch_actor("http://example.com/actor")
    actors = metadata.fetch_actors("http://example.com/season", "Season 1")
"""

from media_files_organizer.pt_scrapper import PTScrapper, ScrapedActor, ScrapedSeason
from media_files_organizer.metadata_types import Actor

class PTDubMetadata:
    """
    A class to fetch metadata for Portuguese dubbed media.
    
    Attributes:
        scrapper (PTScrapper): The PTScrapper object to use for scraping.
        
    Methods:
        fetch_actor(url: str, role: str = "Unknown") -> Actor: Fetch actor information from the given URL.
        fetch_actors(url: str, season_name: str) -> List[Actor]: Fetch actors from the given URL.
        
    """

    def __init__(self, scrapper: PTScrapper | None = None):
        if scrapper is None:
            scrapper = PTScrapper()
        self.scrapper = scrapper


    def fetch_actor(self, url: str, role: str = "Unknown") -> Actor:
        """
        Fetch actor information from the given URL.

        Parameters:
            url (str): The URL to scrape.

        Returns:
            ScrapedActor: The scraped data for the actor.
        """
        data: ScrapedActor = self.scrapper.scrape_actor(url)

        parsed_actor: Actor = {
            "name": data["nome"],
            "original_name": data["nome_completo"],
            "type": "actor",
            "role": role,
            "photo": data["foto_perfil"],
            "thumb": f"/config/data/metadata/People/{data['nome'][0].upper()}/{data['nome']}/folder.jpg"
        }

        return parsed_actor

    def fetch_actors(self, url: str, season_name: str):
        """
        Fetch actors from the given URL.

        Parameters:
            url (str): The URL to scrape.

        Returns:
            List[ScrapedActor]: A list of scraped data for each actor.
        """
        data: ScrapedSeason = self.scrapper.scrape_season(url, season_name)

        parsed_actors: list[Actor] = []

        for actor in data["atores"]:
            role = actor.get("role")
            if role is None:
                role = "Unknown"

            if actor["url"] is not None:
                p_actor: Actor = self.fetch_actor(actor["url"], role)

            else:
                p_actor: Actor = {
                    "name": actor["nome"],
                    "original_name": None,
                    "type": "actor",
                    "role": role,
                    "photo": None,
                    "thumb": f"/config/data/metadata/People/{actor['nome'][0].upper()}/{actor['nome']}/folder.jpg"
                }

            parsed_actors.append(p_actor)

        return parsed_actors
