import json
from pathlib import Path
from flask import g

from flask import jsonify


class DATASTORE:
    file_name = "app_data.json"

    @classmethod
    def open_datastore(cls):
        if not Path(cls.file_name).exists():
            with open(cls.file_name, "w") as new_data_file:
                json.dump([], new_data_file)

    @classmethod
    def add_datastore(cls, data):
        # check if created
        cls.open_datastore()

        # save data
        with open(cls.file_name, "r+") as file_to_update:
            # First we load existing data into a dict.
            file_data = json.load(file_to_update)
            # Join new_data with file_data inside emp_details
            file_data.append(data)
            # Sets file's current position at offset.
            file_to_update.seek(0)
            # convert back to json.
            json.dump(file_data, file_to_update, indent=4)

    @classmethod
    def read_datastore(cls):
        # check if created
        cls.open_datastore()

        # add store to context
        if "db" not in g:
            g.db = json.load(open(cls.file_name))

        return g.db
