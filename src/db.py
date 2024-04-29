import os
from flask import current_app, g
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_db():
    if "db" not in g:
        uri = os.environ.get("MONGODB_CONN_STRING")
        password = os.environ.get("MONGODB_PASSWORD")
        uri = uri.split("<password>")
        uri = uri[0] + password + uri[1]
        print(uri)
        max_attempt = 5
        for attempt in range(0, max_attempt):
            try:
                print("Trying to connect to MongoDB")
                db = MongoClient(uri, server_api=ServerApi("1"))
                g.db = db["ContentForge"]
                print("Connection Successful")
                break
            except Exception as e:
                if attempt < max_attempt:
                    print(f"Attempt {attempt + 1} failed. Error {str(e)}")
                else:
                    print(
                        f"Failed to connect to database. Exiting. Last error : {str(e)}"
                    )
                    raise
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        print("Closed connection")
        db.close()
