import asyncio
from system import *
from system.db import *


app = Application()

def CreateApp(config=dict()):
    try:
        from config import config
    except:
        from config_docker import config

    default_config = {
        'db': {
            'host': None,
            'database': None,
            'username': None,
            'password': None,
            'port': None,
            'charset': 'utf8',
            'collation': 'utf8_general_ci',
            'connection_timeout': 900
        },
        'api': {
            'base': "...",
            'key': "...",
            'secret': "..."
        },
        'ticker_interval': 30,
        'ticker_key': "%%Y%%m%%d%%H%%i%%S",
        'symbol': {
            'interval':30,
            'test': {
                'test1':3,
                'test2':5
            }
        }
    }
    app.load_config(default_config,config)



    app.db = Mysql(
        app=app,
        host=app.config.get("db.host"),
        database=app.config.get("db.database"),
        user=app.config.get("db.username"),
        password=app.config.get("db.password"),
        port=app.config.get("db.port"),
        charset=app.config.get("db.charset"),
        connect_timeout=app.config.get("db.connection_timeout ") or 900,

    )

    app.exchange = Requests()


    return app


