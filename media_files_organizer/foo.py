import os
import io
from tmdb_metadata import TMDBMetadata
from dotenv import load_dotenv
from rich.console import Console
from nfo_generator import NFO
from db_connector import DBConnector
from pt_scrapper import PTScrapper
from rich.console import Console



ep_base = "Pokémon Sun and Moon.S20E"
#filebase = "\\192.168.0.23\\Media\\Anime\\Pokémon\\Season 20.Sun and Moon\\"
filebase = "D:/DOWNLOADS/Season 20.Sun and Moon/"



def main():
    #create_metadata()
    url_list = [
        "https://wikidobragens.fandom.com/pt/wiki/Raquel_Rosmaninho",
        "https://wikidobragens.fandom.com/pt/wiki/Bernardo_Gavina",
        "https://wikidobragens.fandom.com/pt/wiki/Flora_Miranda",
        "https://wikidobragens.fandom.com/pt/wiki/Isabel_Nunes",
        "https://wikidobragens.fandom.com/pt/wiki/Isabel_Queir%C3%B3s",
        "https://wikidobragens.fandom.com/pt/wiki/Raquel_Pereira",
        "https://wikidobragens.fandom.com/pt/wiki/Pedro_Mendon%C3%A7a",
        "https://wikidobragens.fandom.com/pt/wiki/M%C3%A1rio_Santos",
        "https://wikidobragens.fandom.com/pt/wiki/Ivo_Bastos",
        "https://wikidobragens.fandom.com/pt/wiki/Pedro_Frias",
        "https://wikidobragens.fandom.com/pt/wiki/Rui_Oliveira",
        "https://wikidobragens.fandom.com/pt/wiki/Rodrigo_Santos",
        "https://wikidobragens.fandom.com/pt/wiki/%C3%82ngela_Marques",
        "https://wikidobragens.fandom.com/pt/wiki/Helena_Montez",
        "https://wikidobragens.fandom.com/pt/wiki/Pedro_Almendra",
        "https://wikidobragens.fandom.com/pt/wiki/Pedro_Manana",
        "https://wikidobragens.fandom.com/pt/wiki/Tiago_Ara%C3%BAjo",
        "https://wikidobragens.fandom.com/pt/wiki/Joana_Africano",
        "https://wikidobragens.fandom.com/pt/wiki/V%C3%A2nia_Blubird",
        "https://wikidobragens.fandom.com/pt/wiki/Z%C3%A9lia_Santos",
        "https://wikidobragens.fandom.com/pt/wiki/Jo%C3%A3o_Guimar%C3%A3es"
    ]
    scrape_pt_wiki(url_list)


def scrape_pt_wiki(url_list):
    console = Console()

    scrapper = PTScrapper()
    db = DBConnector()
    data = []

    for url in url_list:
        prs = scrapper.scrape(url)
        data.append(prs)
        try:
            db.create_person(nome_completo=prs["nome_completo"], naturalidade=prs["naturalidade"], nascimento=prs["nascimento"], reconhecimento=prs["reconhecimento"], profile_photo=prs["profile_photo"], biography=prs["biography"])
        except Exception as e:
            console.print(f"Error inserting data: {e}", style="bold red")
            continue
    
    console.print("Data inserted successfully!", style="bold green")


def create_metadata():
    # Load environment variables from .env file
    load_dotenv()
    console = Console()
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

    media_id = 60572
    season = 20 # Season 21 sun & moon ultra adventures

    tmdb = TMDBMetadata(TMDB_API_KEY, console)
    data = tmdb.fetch("tv", media_id, season)
    
    nfo = NFO(data, type="tvshow")
    nfo_season = nfo.generate_tvshow_season()

    # write this to a file
    with io.open(f"{filebase}/season.nfo", "w", encoding='utf-8-sig') as f:
        f.write(nfo_season)


    
    

    for episode in data["episodes"]:
        ep_num = episode["episode_number"]
        ep_num = str(ep_num)
        if ep_num and len(ep_num) < 2:
            ep_num = f"0{ep_num}"

        episode_name = episode["episode_name"]
        filename = f"{ep_base}{ep_num}.{episode_name}"
        
        nfo_episode = nfo.generate_tvshow_episode(ep_num, episode, f"{filebase}{filename}.mkv")


        # write this to a file
        with io.open(f"{filebase}{filename}.nfo", "w", encoding='utf-8-sig') as f:
            f.write(nfo_episode)

        

if __name__ == "__main__":
    main()
