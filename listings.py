import random
import string
from dataclasses import dataclass, asdict

from currencies import Currency
from datastore import DATASTORE


@dataclass
class Listing:
    id: int
    title: str
    base_price: float
    currency: Currency
    market: str
    host_name: str

    def to_dict(self):
        return asdict(self)


class LISTINGS:
    # Open datafile
    DATASTORE.open_datastore()

    # Fetch all listings
    __ALL__ = []

    # Organize per code for convenience
    __PER_CODE__ = {market.code: market for market in __ALL__}

    @classmethod
    def get_all(cls, query_params):
        all_listings = DATASTORE.read_datastore()
        for k, v in query_params.items():
            if v is not None and v != "":
                if "base_price" not in k:
                    all_listings = [
                        x for x in all_listings if x[k].lower() == v.lower()
                    ]
                else:
                    math_operation = k.split(".")[1]
                    if math_operation == "e":
                        all_listings = [
                            x for x in all_listings if x["base_price"] == int(v)
                        ]
                    elif math_operation == "lt":
                        all_listings = [
                            x for x in all_listings if x["base_price"] < int(v)
                        ]
                    elif math_operation == "lte":
                        all_listings = [
                            x for x in all_listings if x["base_price"] <= int(v)
                        ]
                    elif math_operation == "gt":
                        all_listings = [
                            x for x in all_listings if x["base_price"] > int(v)
                        ]
                    elif math_operation == "gte":
                        all_listings = [
                            x for x in all_listings if x["base_price"] >= int(v)
                        ]

        return all_listings

    @classmethod
    def get_by_id(cls, listing_id):
        all_listings = DATASTORE.read_datastore()
        return [x for x in all_listings if x["id"] == listing_id]

    @classmethod
    def create_listing(cls, data):
        data["id"] = int("".join(random.choice(string.digits) for _ in range(8)))
        DATASTORE.add_datastore(data)
        return data
