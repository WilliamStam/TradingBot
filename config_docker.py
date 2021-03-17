import os

config = {
    'api': {
        'base': os.environ["API_BASE"],
        'key': os.environ["API_KEY"],
        'secret': os.environ["API_SECRET"]
    },
    'db': {
        'host': os.environ["DB_HOST"],
        'database': os.environ["DB_DATABASE"],
        'username': os.environ["DB_USERNAME"],
        'password': os.environ["DB_PASSWORD"],
        'port': os.environ["DB_PORT"],
    },
}
