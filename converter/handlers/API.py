import requests

class APIHandler:
    __API_URL = 'https://api.exchangerate-api.com/v4/latest/'

    def check_server_state(self):
        response = self.__go_to_API()
        self.__check_response(response)

    def __check_response(self, response):
        if response.status_code != 200:
            raise ServerError

    def get_rates_from_api(self, currency_code: str = 'USD') -> dict:
        response = self.__go_to_API(currency_code).json()
        return response.get('rates')

    def get_list_of_currencies(self) -> list[str]:
        response = self.__go_to_API().json()
        return list(response.get('rates').keys())

    def __go_to_API(self, currency_code: str = 'USD') -> requests.Response:
        return requests.get(
            self.__get_link_to_API(currency_code)
        )

    def __get_link_to_API(self, currency_code: str = 'USD') -> str:
        return self.__API_URL + currency_code.upper()