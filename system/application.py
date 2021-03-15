import asyncio
from system.config import Config
class Application:
    def __init__(self):
        self.config = Config()
    def load_config( self, default_config=dict(),config=dict() ):
        self.config.load(default_config,config)

    @property
    def loop( self ):
        return asyncio.get_event_loop()
    @loop.setter
    def loop( self, loop=None ):
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()
    # def longest_job_id( self ):
    #     return self.db.exec("SELECT ")


