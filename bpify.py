import json
from datetime import date, timedelta

import requests as requests
from flask import Flask, escape, request, jsonify, Response
from markets import MARKETS
from listings import LISTINGS
from currencies import CURRENCIES

FLASK_DEBUG = 1
app = Flask(__name__)


@app.route("/test_flask", methods=["GET", "POST"])
def test_flask():
    """Example to show how to use Flask and extract information from the incoming request.
    It is not intended to be the only way to do things with Flask, rather more a way to help you not spend too much time on Flask.

    Ref: http://flask.palletsprojects.com/en/1.1.x/

    Try to make those requests:
    curl "http://localhost:5000/test_flask?first=beyond&last=pricing"
    curl "http://localhost:5000/test_flask" -H "Content-Type: application/json" -X POST -d '{"first":"beyond", "last":"pricing"}'

    """
    # This contains the method used to access the route, such as GET or POST, etc
    method = request.method

    # Query parameters
    # It is a dict like object
    # Ref: https://flask.palletsprojects.com/en/1.1.x/api/?highlight=args#flask.Request.args
    query_params = request.args
    query_params_serialized = ", ".join(f"{k}: {v}" for k, v in query_params.items())

    # Get the data as JSON directly
    # If the mimetype does not indicate JSON (application/json, see is_json), this returns None.
    # Ref: https://flask.palletsprojects.com/en/1.1.x/api/?highlight=get_json#flask.Request.get_json
    data_json = request.get_json()

    return jsonify(
        {
            "method": method,
            "query_params": query_params_serialized,
            "data_json": data_json,
        }
    )


@app.route("/markets")
def markets():
    return jsonify([market.to_dict() for market in MARKETS.get_all()])


@app.route("/listings", methods=["GET", "POST"])
def listings():
    method = request.method

    # get (list)
    if method == "GET":
        query_params = request.args
        return jsonify(LISTINGS.get_all(query_params))
    elif method == "POST":
        # validate data
        required_fields = ["title", "base_price", "currency", "market"]
        error_fields = []
        has_errors = False
        post_data = request.json
        for required_field in required_fields:
            if (
                required_field not in post_data
                or post_data[required_field] is None
                or post_data[required_field] == ""
            ):
                error_fields.append(required_field)
                has_errors = True

        # check if required fields are submitted
        if has_errors:
            return jsonify(
                {
                    "status": False,
                    "errors": f"{', '.join(error_fields)} fields can't be null",
                }
            )

        # validate currency submitted
        if (
            post_data["currency"] not in CURRENCIES.__PER_CODE__
            or post_data["market"] not in MARKETS.__PER_CODE__
        ):
            return jsonify(
                {
                    "status": False,
                    "errors": "One of submitted choices on currency or market is not valid",
                }
            )

        return jsonify(LISTINGS.create_listing(post_data))


@app.route("/listings/<int:id>", methods=["GET", "PUT", "DELETE"])
def listing(id):
    method = request.method
    listing_data = LISTINGS.get_by_id(id)
    if not listing_data:
        return jsonify({"error": f"Listing with id={id} does not exist"}), 404

    if method == "GET":
        return jsonify(listing_data[0])

    elif method == "PUT":
        item_updated = {}
        listings_json = json.load(open("app_data.json"))
        for i in range(len(listings_json)):
            if listings_json[i]["id"] == listing_data[0].get("id"):
                post_data = request.json
                for key in post_data:
                    if (
                        key != "id"
                        and post_data[key] is not None
                        and post_data[key] != ""
                    ):
                        listings_json[i][key] = post_data[key]
                item_updated = listings_json[i]
                break
        open("app_data.json", "w").write(
            json.dumps(listings_json, sort_keys=True, indent=4, separators=(",", ": "))
        )

        return jsonify(item_updated)

    elif method == "DELETE":
        listings_json = json.load(open("app_data.json"))
        for i in range(len(listings_json)):
            if listings_json[i]["id"] == listing_data[0].get("id"):
                listings_json.pop(i)
                break
        open("app_data.json", "w").write(
            json.dumps(listings_json, sort_keys=True, indent=4, separators=(",", ": "))
        )

        return jsonify({"status": True, "message": "Listing deleted"})


@app.route("/listings/<int:id>/calendar", methods=["GET"])
def listing_calendar(id):
    listing_data = LISTINGS.get_by_id(id)
    query_params = request.args

    if listing_data:

        listing_currency = listing_data[0]["currency"]
        listing_base_price = listing_data[0]["base_price"]
        listing_market = listing_data[0]["market"]

        currency_value = ""
        for k, v in query_params.items():
            if v is not None and v != "":
                if "currency" in k:
                    currency_value = v.upper()

        today = date.today()
        calendar_data = []
        converted_price = CURRENCIES.convert_currency(
            listing_base_price=listing_base_price,
            currency_from=listing_currency.upper(),
            currency_to=currency_value.upper(),
        )
        current_listing_currency = listing_currency
        if currency_value is not None and currency_value != "":
            current_listing_currency = currency_value.upper()

        for n in range(365):
            current_day = today + timedelta(days=n)
            current_day_of_week = current_day.weekday()
            calendar_price = converted_price

            if (listing_market == "paris" or listing_market == "lisbon") and (
                current_day_of_week == 5 or current_day_of_week == 6
            ):
                calendar_price = 1.5 * converted_price
            if listing_market == "san-francisco" and current_day_of_week == 2:
                calendar_price = 0.70 * converted_price
            if (
                listing_market not in ["san-francisco", "paris", "lisbon"]
                and current_day_of_week == 4
            ):
                calendar_price = 1.25 * converted_price

            calendar_data.append(
                {
                    "date": current_day.isoformat(),
                    "price": round(calendar_price),
                    "currency": current_listing_currency,
                }
            )

        return jsonify(calendar_data)
    else:
        return jsonify({"error": f"Listing with id={id} does not exist"}), 404
