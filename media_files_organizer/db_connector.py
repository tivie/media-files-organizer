import sqlite3
from pt_scrapper import ScrapeResult

class DBConnector:

    db_name = "pt_database.sqlite3"

    def create_person(self, name: str, full_name: str = None, birth_place: str = None, birthday: str =None, birthday_year: str = None, famous_roles: str =None, biography: str =None, photo_src_url: str =None ) -> None:

        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO people (name, full_name, birthday, birthday_year, birth_place, famous_roles, biography, photo_src_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                (name, full_name, birthday, birthday_year, birth_place, famous_roles, biography, photo_src_url))
            connection.commit()
            connection.close()

    
    def create_person_bulk(self, data: ScrapeResult) -> None:
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.executemany(
                "INSERT INTO people (name, full_name, birthday, birthday_year, birth_place, famous_roles, biography, photo_src_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                data)
            connection.commit()
            connection.close()
