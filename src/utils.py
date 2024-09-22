import psycopg2
from src.hh_parser import HHParser


def create_database(db_name: str, params: dict) -> None:
    """Создание БД"""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        f"""SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '{db_name}' AND pid <> pg_backend_pid()"""
    )
    cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")
    cur.close()
    conn.close()


def create_tables(db_name: str, params: dict) -> None:
    """Создание таблиц"""
    conn = psycopg2.connect(dbname=db_name, **params)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE employer (
            employer_id INTEGER PRIMARY KEY,
            employer_name VARCHAR(255) NOT NULL UNIQUE,
            open_vacancies INT)""")

            cur.execute("""CREATE TABLE vacancy (
                        vacancy_id INTEGER PRIMARY KEY,
                        vacancy_name VARCHAR(255) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        vacancy_url VARCHAR(255),
                        employer_id INTEGER,
                        CONSTRAINT fk_vacancies_employer FOREIGN KEY (employer_id) REFERENCES employer(employer_id))"""
                        )
    conn.close()


def insert_data(db_name: str, params: dict) -> None:
    """Добавление данных в таблицу"""
    conn = psycopg2.connect(dbname=db_name, **params)
    with conn:
        with conn.cursor() as cur:
            hh = HHParser()
            employers = hh.load_employers()
            for employer in employers:
                employer_id = employer["id"]
                cur.execute("INSERT INTO employer VALUES (%s, %s, %s)",
                            (employer_id, employer["name"], employer["open_vacancies"]))
                vacancies = hh.load_vacancies(employer_id)
                for vacancy in vacancies:
                    if not vacancy["salary"]:
                        salary_from = 0
                        salary_to = 0
                    else:
                        salary_from = vacancy["salary"]["from"] if vacancy["salary"]["from"] else 0
                        salary_to = vacancy["salary"]["to"] if vacancy["salary"]["to"] else 0
                    cur.execute("INSERT INTO vacancy VALUES (%s, %s, %s, %s, %s, %s)",
                                (vacancy["id"], vacancy["name"], salary_from, salary_to,
                                 vacancy["alternate_url"], employer_id))
    conn.close()
