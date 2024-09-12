from typing import Any

import psycopg2


class DBManager:
    """Класс для получения данных о компаниях и вакансиях из БД"""

    def __init__(self, db_name: str, params: dict) -> None:
        """Инициализация класса"""
        self.__db_name = db_name
        self.__params = params

    def __execute_query(self, query: str) -> list[dict] | Any:
        """Выполнения запроса"""
        conn = psycopg2.connect(dbname=self.__db_name, **self.__params)
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                # result = cur.fetchall()
                columns = [column[0] for column in cur.description]
                result = cur.fetchall()
                result_in_dict = [dict(zip(columns, i)) for i in result]
        conn.close()
        return result_in_dict

    def get_employers(self) -> Any:
        """Получает данные об компаниях из БД"""
        return self.__execute_query("SELECT * FROM employer")

    def get_companies_and_vacancies_count(self) -> Any:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        return self.__execute_query("""
                                    SELECT employer.employer_name, COUNT(*) AS vacancies_count
                                    FROM vacancy
                                    JOIN employer USING(employer_id)
                                    GROUP BY employer.employer_name
                                    """)

    def get_all_vacancies(self) -> Any:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        return self.__execute_query("""
                                    SELECT employer.employer_name, vacancy_name, salary_from, salary_to, vacancy_url
                                    FROM vacancy
                                    JOIN employer USING(employer_id)
                                    """)

    def get_avg_salary(self) -> Any:
        """Получает среднюю зарплату по вакансиям"""
        return round(self.__execute_query("""
                                    SELECT AVG (salary_from)
                                    FROM vacancy
                                    WHERE salary_to > 0
                                    """)[0]["avg"], 2)

    def get_vacancies_with_higher_salary(self) -> Any:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        return self.__execute_query("""
                                    SELECT employer.employer_name, vacancy_name, salary_from, salary_to, vacancy_url
                                    FROM vacancy
                                    JOIN employer USING(employer_id)
                                    WHERE salary_from > (
                                    SELECT AVG (salary_from)
                                    FROM vacancy
                                    WHERE salary_to > 0)
                                    """)

    def get_vacancies_with_keyword(self, word: str) -> Any:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        return self.__execute_query(f"""
                                    SELECT employer.employer_name, vacancy_name, salary_from, salary_to, vacancy_url
                                    FROM vacancy
                                    JOIN employer USING(employer_id)
                                    WHERE vacancy_name ILIKE '%{word}%'
                                    """)
