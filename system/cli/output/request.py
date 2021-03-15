from .style import Style
from . import Line, Item
class Request():
    def __init__( self, response ):
        self.response = response


    def __repr__( self ):
        parts = list()

        parts.append("")

        return ": ".join(parts)

