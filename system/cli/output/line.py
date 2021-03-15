from .item import Item


class Line:
    def __init__( self ):
        self.__list = dict()

    def add( self, output: Item, key=None ):
        if key is None:
            key = f"_{len(self.__list) + 1}"
        self.__list[key] = output
        return self.__list[key]

    def add_list( self, Items, key=None ):
        if key is None:
            key_prefix = f"_{len(self.__list) + 1}"
        else:
            key_prefix = key
        for row in Items:
            item = Items[row]
            key = f"{key_prefix}_{row}"
            self.add(item, key=key)

    def update( self, key, **kwargs ):
        obj = self.__list[key]
        for row in kwargs:
            setattr(obj, row, kwargs[row])

        return obj

    def fetch( self ):
        return self.__list

    def toDict( self ):
        return [str(self.__list[x]) for x in self.__list]

    def print( self, separator=" | " ):
        print(separator.join(self.toDict()))
