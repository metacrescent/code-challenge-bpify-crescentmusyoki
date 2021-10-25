import json
from dataclasses import dataclass, asdict

import requests

openexchange_id = "b99551be68ff46cd819b46704c63dd7a"
openexchange_rates_url = "https://openexchangerates.org/api/latest.json"


@dataclass
class Currency:
    code: str
    name: str
    symbol: str

    def to_dict(self):
        return asdict(self)


class CURRENCIES:
    # Codes
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    ILS = "ILS"
    AUD = "AUD"

    # Define all currencies
    __ALL__ = [
        Currency(USD, "United States Dollar", "$"),
        Currency(EUR, "Euro", "€"),
        Currency(JPY, "Japanese Yen", "¥"),
        Currency(ILS, "Israeli shekel", "₪"),
        Currency(AUD, "Australian Dollar", "A$"),
    ]
    # Organize per code for convenience
    __PER_CODE__ = {currency.code: currency for currency in __ALL__}

    @classmethod
    def get_all(cls):
        return cls.__ALL__

    @classmethod
    def get_by_code(cls, code):
        if code not in cls.__PER_CODE__:
            raise Exception(f"Currency with code={code} does not exist")
        return cls.__PER_CODE__[code]

    @classmethod
    def convert_currency(cls, listing_base_price, currency_from, currency_to):
        converted_price = listing_base_price
        if currency_from != currency_to:
            openexchange_rates = requests.get(
                openexchange_rates_url, params={"app_id": openexchange_id}
            )
            rates = json.loads(openexchange_rates.content).get("rates")
            if currency_to in rates:
                rate_to_usd = rates.get(currency_to)
                if currency_to == "USD":
                    converted_price = rates.get(currency_from) * listing_base_price
                else:
                    first_price_to_usd = rates.get(currency_from) * listing_base_price
                    converted_price = rates.get(currency_to) * first_price_to_usd
        return converted_price
