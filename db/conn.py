import psycopg2 as pg
import os
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    return pg.connect(
        database=os.getenv("DB_NAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USERNAME"),
    )
