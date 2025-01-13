import argparse
import sqlite3
import sys
from media_files_organizer.db_connector import DBConnector, DBPerson
from media_files_organizer.pt_scrapper import PTScrapper, ScrapedActor, ScrapedSeason
from rich.table import Table
from rich.console import Console

class PopDB:

    def __init__(self):
        self.db = DBConnector()
        self.console = Console()
        self.scrapper = PTScrapper()
        self.parser = argparse.ArgumentParser(
            prog="PopDB",
            description="Manage the popdb database.",
            #exit_on_error=False
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True, help="Available commands")
        self.args = self._parse_arguments()


    def _parse_arguments(self) -> argparse.Namespace:        
        subparsers = self.subparsers

        # Add 'person' subcommand
        subparsers.add_parser(
            "person",
            help="Manage people in the database",
            #exit_on_error=False
        )
        
        # Add 'series' subcommand
        subparsers.add_parser(
            "tvshow", 
            help="Manage series in the database",
            #exit_on_error=False
        )

        # Add 'movie' subcommand
        subparsers.add_parser(
            "movie",
            help="Manage movies in the database",
            #exit_on_error=False
        )

        ##### SEASON SUBCOMMAND #####
        # Add 'season' subcommand
        season_parser = subparsers.add_parser(
            "season",
            help="Manage seasons in the database",
            #exit_on_error=False
        )

        
        season_subparsers = season_parser.add_subparsers(dest="season_command", help="Season commands")
        
        # Add 'list' subcommand under 'season'
        season_list_subparser = season_subparsers.add_parser(
            "list", 
            help="List all the seasons",
            #exit_on_error=False
        )
        season_list_subparser.add_argument("tvshow_id", type=int, help="The ID of the tvshow in the database. Use 'tvshow list' to get the ID")

        # Add 'create' subcommand under 'season'
        create_parser = season_subparsers.add_parser("scrape", help="Create a new season")
        create_parser.add_argument("url", type=str, help="The URL of the season")
        create_parser.add_argument("tvshow_id", type=int, help="The ID of the tvshow in the database. Use 'tvshow list' to get the ID")
        create_parser.add_argument("season_num", type=str, help="The number of the season")
        create_parser.add_argument(
            "name", 
            type=str, 
            nargs="?",  # Makes the argument optional
            default=None,  # Sets the default value if the argument is not provided
            help="The name of the season (optional)"
        )


        # If no arguments are passed, print the help message and exit
        if len(sys.argv) == 1:
            help = self.parser.format_help()
            self.console.print(help)
            exit(1)

        args = self.parser.parse_args()

        
        # validate the args here, to keep code clean
        # If the user runs 'season' without a subcommand, show 'season' help
        if args.command == "season" and args.season_command is None:
            self.subparsers.choices["season"].print_help()
            exit(1)
        
        # If the user runs 'season list' without 'tvshow_id', show 'list' help
        if args.command == "season" and args.season_command == "list" and not hasattr(args, "tvshow_id"):
            season_list_subparser.print_help()
            exit(1)

        return args
        



    def run(self):
        args = self.args

        # Route to the appropriate function based on the subcommands
        if args.command == "season":
            if args.season_command == "list":
                self.console.print(self.list_seasons(args.tvshow_id))
            elif args.season_command == "scrape":
                self.scrape_season(url=args.url, tvshow_id=args.tvshow_id, season_number=args.season_num, name=args.name)
        elif args.command == "person":
            if args.person_command == "list":

                pass
        elif args.command == "tvshow":
            raise NotImplementedError("Series management is not implemented yet")
        elif args.command == "movie":
            raise NotImplementedError("Movie management is not implemented yet")
        else:
            self.parser.print_help()



    def list_seasons(self, tvshow_id: int):
        seasons = self.db.get_seasons_of_tvshow(tvshow_id)
        if len(seasons) == 0:
            self.console.print("No seasons found in the database for that tvshow", style="bold red")
            return
        
        series_name = self.db.get_tvshow_title(seasons[0]["tv_show_id"])
        
        table = Table(title=f"Seasons of {series_name}")
        table.add_column("ID", style="cyan")
        table.add_column("Season Number", style="magenta")
        table.add_column("Title", style="green")

        for season in seasons:
            table.add_row(str(season["id"]), str(season["season_number"]), str(season["title"]))

        return table
    

    def scrape_season(self, url: str, tvshow_id: int, season_number: int, name: str|None = None):
        scrapper = self.scrapper
        self.console.print(f"Scraping season {season_number} - {name} from {url}...", style="bold blue")
        if not name:
            name = f"Season {season_number}"
        season: ScrapedSeason = scrapper.scrape_season(url=url, name=name)
        
        try:
            season_id = self.db.create_season(title=season["nome"], tvshow_id=tvshow_id, season_number=season_number)
            self.console.print(f"Season {season_number} {name} created successfully in DB!", style="bold green")
        except sqlite3.IntegrityError as e:
            season_id = self.db.get_season_id(tvshow_id, season_number)
            self.console.print(f"Error inserting season {season_number} {name} into database: {e}", style="bold yellow")
        
        for ator in season["atores"]:
            role = ator["role"]
            if ator["url"]:
                ator = self.scrape_person(ator["url"], False)
            
            try:
                dbperson = self._insert_ator_into_db(ator)
                self.console.print(f"{ator['nome']} created successfully!", style="bold green")
            except sqlite3.IntegrityError as e:
                dbperson = self.db.get_person_by_name(ator["nome"])
                self.console.print(f"Error inserting person {ator['nome']} into database: {e}", style="bold yellow")

            if not dbperson:
                raise Exception(f"Error inserting person {ator['nome']} into database")

            try:
                self.db.create_role(type="actor", character=str(role), people_id=dbperson["id"], tv_show_id=tvshow_id, season_id=season_id)
                self.console.print(f"Role {role} created successfully!", style="bold green")
            except Exception as e:
                self.console.print(f"Error inserting role {role} into database: {e}", style="bold red")
                continue

        return season

    def _insert_ator_into_db(self, ator: ScrapedActor)->DBPerson:
        dbperson = self.db.create_person(
            name=ator["nome"],
            full_name=ator["nome_completo"],
            birthday=ator["nascimento"],
            birthday_year=ator["ano_nascimento"],
            birth_place=ator["naturalidade"],
            famous_roles=ator["reconhecimento"],
            biography=ator["biografia"],
            photo_src_url=ator["foto_perfil"]
        )
        if not dbperson:
            raise Exception(f"Error inserting person {ator['nome']} into database")
        return dbperson

    def scrape_person(self, url: str, insert_into_db: bool = True):
        scrapper = self.scrapper
        self.console.print(f"Scraping person from {url}...", style="bold blue")
        person = scrapper.scrape_actor(url=url)
        if insert_into_db:
            self._insert_ator_into_db(person)
            self.console.print("Person created successfully!", style="bold green")
        return person

def main():
    
    popdb = PopDB()
    popdb.run()

    #ptscrapper = PTScrapper()
    #db = DBConnector()
    #if args.type == "season":
    #    season = ptscrapper.scrape_season(url=args.url, name=args.name)
    #    db.create_season(name=season["name"], tvshow_id=season["tvshow_id"], season_number=season["season_number"], start_date=season["start_date"], end_date=season["end_date"], episodes=season["episodes"])

    #    # store information in database

        





if __name__ == "__main__":
    main()
