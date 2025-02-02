"""
DBConnector Module

This module provides a `DBConnector` class that interacts with an SQLite3 database to perform operations
on a `people` table. It includes methods for inserting individual person records and bulk insertion 
of multiple records.

Classes:
    - DBConnector: A class to manage database operations for the `people` table.

Dependencies:
    - sqlite3: Python's built-in library for SQLite database operations.
    - ScrapeResult: A custom data structure for handling bulk person data.

Usage Example:
    from db_connector import DBConnector
    from pt_scrapper import ScrapeResult

    db_connector = DBConnector()

    # Add a single person record
    db_connector.create_person(
        name="John Doe",
        full_name="Jonathan Doe",
        birth_place="New York",
        birthday="1980-01-01",
        famous_roles="Actor",
        biography="Known for various roles in movies.",
        photo_src_url="http://example.com/photo.jpg"
    )

    # Add multiple person records in bulk
    data = ScrapeResult([...])  # Example list of person records
    db_connector.create_person_bulk(data)
"""
import sqlite3
from typing import TypedDict, Optional
from pt_scrapper import ScrapedActor

class DBSeason(TypedDict):
    id: int
    tv_show_id: int
    title: str
    season_number: int
    year: int
    plot: str
    writer: str
    rating: str
    premiered: str
    releasedate: str

class DBTvShow(TypedDict):
    id: int
    tmdb_id: int
    title: str
    original_title: Optional[str]
    year: Optional[int]
    plot: Optional[str]
    rating: Optional[str]
    mpaa: Optional[str]
    seasons: Optional[int]

class DBPerson(TypedDict):
    id: int
    name: str
    full_name: Optional[str]
    birthday: Optional[str]
    birthday_year: Optional[int]
    birth_place: Optional[str]
    biography: Optional[str]
    famous_roles: Optional[str]
    photo_src_url: Optional[str]

class DBActorWithRole(DBPerson):
    role: str
    type: Optional[str]

class DBRole(TypedDict):
    id: int
    type: str
    character: Optional[str]
    people_id: int
    tv_show_id: int
    season_id: int

class DBConnector:
    """
    A class to handle database operations related to people.

    Attributes:
        db_name (str): The name of the SQLite database file.

    Methods:
        create_person(name: str, full_name: str = None, birth_place: str = None, birthday: str = None, birthday_year: str = None, famous_roles: str = None, biography: str = None, photo_src_url: str = None) -> None:
            Inserts a single person's information into the database.
        create_person_bulk(data: ScrapeResult) -> None:
            Inserts multiple people's information into the database in bulk.
    """

    def __init__(self, db_path: str = "database/pt_database.sqlite3"):
        """
        Initializes the database connector with the name of the SQLite database file.

        Args:
            db_path (str): The path of the SQLite database file. Defaults to "database/pt_database.sqlite3".
        """
        self.db_name = db_path
    

    def create_person(
            self,
            name: str,
            full_name: str|None = None,
            birth_place: str|None = None,
            birthday: str|None =None,
            birthday_year: int|None = None,
            famous_roles: str|None =None,
            biography: str|None =None,
            photo_src_url: str|None =None
    ) -> DBPerson:
        """
        Inserts a single person's information into the database.
        
        Args:
            name (str): The name of the person.
            full_name (str, optional): The full name of the person. Defaults to None.
            birth_place (str, optional): The birth place of the person. Defaults to None.
            birthday (str, optional): The birthday of the person. Defaults to None.
            birthday_year (str, optional): The birth year of the person. Defaults to None.
            famous_roles (str, optional): The famous roles of the person. Defaults to None.
            biography (str, optional): The biography of the person. Defaults to None.
            photo_src_url (str, optional): The URL of the person's photo. Defaults to

        Returns:
            DBPerson

        """

        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO people (name, full_name, birthday, birthday_year, birth_place, famous_roles, biography, photo_src_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                (name, full_name, birthday, birthday_year, birth_place, famous_roles, biography, photo_src_url))
            connection.commit()

            person_id = cursor.lastrowid
            if not person_id:
                raise Exception("Error inserting person")

            return DBPerson({
                "id": person_id,
                "name": name,
                "full_name": full_name,
                "birthday": birthday,
                "birthday_year": birthday_year,
                "birth_place": birth_place,
                "famous_roles": famous_roles,
                "biography": biography,
                "photo_src_url": photo_src_url
            })


    def create_role(self, type: str, character: str, people_id: int, tv_show_id: int, season_id: int) -> int:
        """
        Inserts a single role's information into the database.
        
        Args:
            type (str): The type of role.
            character (str): The character name.
            people_id (int): The ID of the person.
            tv_show_id (int): The ID of the TV show.
            season_id (int): The ID of the season.

        Returns:
            int: The ID of the inserted role.

        """

        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO role (type, character, people_id, tv_show_id, season_id) VALUES (?, ?, ?, ?, ?)", 
                (type, character, people_id, tv_show_id, season_id))
            connection.commit()
            role_id = cursor.lastrowid
            if not role_id:
                raise Exception("Error inserting role")

            return role_id

    def create_season(self, tvshow_id: int, title: str, season_number: int) -> int:
        """
        Inserts a single season's information into the database.
        
        Args:
            tvshow_id (int): The ID of the TV show.
            title (str): The title of the season.
            season_number (int): The season number.

        Returns:
            int: The ID of the inserted season.

        """

        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO season (tv_show_id, title, season_number) VALUES (?, ?, ?)", 
                (tvshow_id, title, season_number))
            connection.commit()
            season_id = cursor.lastrowid
            if not season_id:
                raise Exception("Error inserting season")

            return season_id


    def create_person_bulk(self, data: ScrapedActor) -> None:
        """
        Inserts multiple people's information into the database in bulk.

        Args:
            data (ScrapeResult): An object containing the scraped data of multiple people.

        Returns:
            None
        """
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.executemany(
                "INSERT INTO people (name, full_name, birthday, birthday_year, birth_place, famous_roles, biography, photo_src_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                data)
            connection.commit()
    
    def get_season_of_tvshow_by_tmdb_id(self, tmdb_id: int, season_number: int)->DBSeason|None:
        """
        Get the season number of a TV show by its TMDB ID.

        Args:
            tmdb_id (int): The TMDB ID of the TV show.

        Returns:
            int: The season number of the TV show.
        """
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            query = """
                SELECT season.*
                FROM season
                JOIN tv_show ON tv_show.id = season.tv_show_id
                WHERE tv_show.tmdb_id = ? AND season.season_number = ?;
                """
            cursor.execute(query, (tmdb_id, season_number))
            result = cursor.fetchone()

        return DBSeason(result) if result else None
    
    def get_season_id_of_tvshow_by_tmdb_id(self, tmdb_id: int, season_number: int)->int|None:
        """
        Get the season number of a TV show by its TMDB ID.

        Args:
            tmdb_id (int): The TMDB ID of the TV show.

        Returns:
            int: The season number of the TV show.
        """
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            query = """
                SELECT season.id
                FROM season
                JOIN tv_show ON tv_show.id = season.tv_show_id
                WHERE tv_show.tmdb_id = ? AND season.season_number = ?;
                """
            cursor.execute(query, (tmdb_id, season_number))
            result = cursor.fetchone()

        return result[0] if result else None

    def get_season_id(self, tv_show_id: int, season_number: int)->int:
        """
        Get the season number of a TV show by its TMDB ID.

        Args:
            tmdb_id (int): The TMDB ID of the TV show.

        Returns:
            int: The season number of the TV show.
        """
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            query = """
                SELECT id
                FROM season
                WHERE tv_show_id = ? AND season_number = ?;
                """
            cursor.execute(query, (tv_show_id, season_number))
            result = cursor.fetchone()

        return result[0]

    def get_person_by_name(self, name: str)->DBPerson|None:
        """
        Get a person by their name.

        Args:
            name (str): The name of the person.

        Returns:
            DBPerson: The person's information.
        """
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            query = "SELECT * FROM people WHERE name = ?"
            cursor.execute(query, (name,))
            result = cursor.fetchone()
        
        if result is None:
            return None  # Handle case when no matching record is found

        return DBPerson({
            "id": result["id"],
            "name": result["name"],
            "full_name": result["full_name"],
            "birthday": result["birthday"],
            "birthday_year": result["birthday_year"],
            "birth_place": result["birth_place"],
            "biography": result["biography"],
            "famous_roles": result["famous_roles"],
            "photo_src_url": result["photo_src_url"]
        })
    

    def get_seasons(self)->list[DBSeason]:
        """
        Get all seasons from the database.

        Returns:
            list: A list of seasons.
        """
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM season")
            result = cursor.fetchall()

        store: list[DBSeason] = []

        for rr in result:
            store.append(DBSeason({
                "id": rr[0],
                "tv_show_id": rr[1],
                "title": rr[2],
                "season_number": rr[3],
                "year": rr[4],
                "plot": rr[5],
                "writer": rr[6],
                "rating": rr[7],
                "premiered": rr[8],
                "releasedate": rr[9]
            }))
        
        return store
    
    def get_seasons_of_tvshow(self, tv_show_id: int)->list[DBSeason]:
        """
        Get all seasons of a TV show.

        Args:
            tv_show_id (int): The ID of the TV show.

        Returns:
            list: A list of seasons.
        """
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM season WHERE tv_show_id = ? ORDER BY season_number"
            cursor.execute(query, (tv_show_id,))
            result = cursor.fetchall()

        store: list[DBSeason] = []

        for rr in result:
            store.append(DBSeason({
                "id": rr[0],
                "tv_show_id": rr[1],
                "title": rr[2],
                "season_number": rr[3],
                "year": rr[4],
                "plot": rr[5],
                "writer": rr[6],
                "rating": rr[7],
                "premiered": rr[8],
                "releasedate": rr[9]
            }))
        
        return store

    def get_tvshow_title(self, series_id: int)->str:
        """
        Get the name of a series.

        Args:
            series_id (int): The ID of the series.

        Returns:
            str: The name of the series.
        """
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            query = "SELECT title FROM tv_show WHERE id = ?"
            cursor.execute(query, (series_id,))
            result = cursor.fetchone()

        return result[0]

    def get_actors_of_season(self, season_id: int)->list[DBActorWithRole]:
        """
        Get the actors of a season.

        Args:
            season_id (int): The ID of the season.

        Returns:
            list: A list of actors in the season.
        """
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            query = """
                SELECT 
                    people.id AS id,
                    people.name AS name,
                    people.full_name AS full_name,
                    people.birthday AS birthday,
                    people.birthday_year AS birthday_year,
                    people.birth_place AS birth_place,
                    people.biography AS biography,
                    people.famous_roles AS famous_roles,
                    people.photo_src_url AS photo_src_url,
                    role.type AS type,
                    role.character AS role
                FROM 
                    role
                JOIN 
                    people ON role.people_id = people.id
                WHERE 
                    role.season_id = ?;
                """
            cursor.execute(query, (season_id,))
            result = cursor.fetchall()
        foo: list[DBActorWithRole] = []
        for rr in result:
            foo.append(DBActorWithRole({
                "id": rr["id"],
                "name": rr["name"],
                "full_name": rr["full_name"],
                "birthday": rr["birthday"],
                "birthday_year": rr["birthday_year"],
                "birth_place": rr["birth_place"],
                "biography": rr["biography"],
                "famous_roles": rr["famous_roles"],
                "photo_src_url": rr["photo_src_url"],
                "type": rr["type"],
                "role": rr["role"]
            }))

        return foo
