import requests

class APIHandler:
    __API_URL = 'https://api.exchangerate-api.com/v4/latest/'

    def check_server_state(self):
        response = self.__go_to_API()
        self.__check_response(response)

    def __check_response(self, response):
        if response.status_code != 200:
            raise ServerError
    def get_rate_from_API(self, from_currency: str, to_currency: str) -> float:
        rates = self.get_rates_from_API(from_currency)
        return rates.get(to_currency)

    def get_rates_from_API(self, currency_code: str = 'USD') -> dict:
        response = self.__go_to_API(currency_code).json()
        return response.get('rates')

    def get_list_of_currencies(self) -> list[str]:
        response = self.__go_to_API().json()
        return list(response.get('rates').keys())

    def __go_to_API(self, currency_code: str = 'USD') -> requests.Response:
        self.set_session()
        return self.session.get(
            self.__get_link_to_API(currency_code)
        )

    def set_session(self):
        if not hasattr(self, 'session'):
            setattr(self, 'session', requests.Session())

    def __get_link_to_API(self, currency_code: str = 'USD') -> str:
        return self.__API_URL + currency_code.upper()