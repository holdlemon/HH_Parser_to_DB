from typing import Any

import requests


class HHParser:
    """ Класс для работы с API HeadHunter """

    def __init__(self) -> None:
        """Инициализатор класса"""
        self.__url: str = ""
        self.__params: dict[str, Any] = {}

    def __connection_to_api(self) -> list[dict[str, Any]] | Any:
        """Приватный метод для подключения к API"""
        response = requests.get(self.__url, self.__params)
        if response.status_code != 200:
            raise requests.RequestException
        return response.json()["items"]

    def load_employers(self) -> list[dict[str, Any]]:
        """Метод для получения списка компаний, отсортированных по количеству открытых вакансий"""
        self.__url = "https://api.hh.ru/employers"
        self.__params = {
            "sort_by": "by_vacancies_open",
            "per_page": 10
        }
        return self.__connection_to_api()

    def load_vacancies(self, employer_id: int) -> list[dict[str, Any]]:
        """Метод для получения списка вакансий"""
        self.__url = "https://api.hh.ru/vacancies"
        self.__params = {
            "employer_id": employer_id,
            "per_page": 50
        }
        return self.__connection_to_api()
