from collections.abc import Sequence
import json
class Collection(Sequence):
    def __init__(self,include_data=list(),schema=None):
        self.data = list()
        self.schema = schema
        for item in include_data:
            self.data.append(item)
    def add(self,item):
        self.data.append(item)

    def __getitem__(self, index):
        return self.data[index]
    def __len__(self):
        return len(self.data)
    def __bool__(self):
        return bool(self.__cursor)
    def __str__(self):
        return json.dumps(self.data)
    
    def toList(self):
        ret = list()
        for item in self.data:
            ret.append(item.toDict())
        return ret

    def toDict(self,key=None,schema=None):
        ret = dict()
        if key is None:
            return self.toList()

        if schema is not None:
            return self.toSchema(schema=schema)

        ret = dict()
        for item in self.data:
            key_fld = getattr(item,key)
            ret[key_fld] = item.toDict()
        

        return ret

    def toSchema(self,schema=None):
        
        ret = list()
        for item in self.data:
            if schema is not None:
                ret.append(schema(item).toDict())
            else:
                ret.append(item.toDict(schema))
        
        return ret

    def getLastId(self):
        return self.__cursor.lastrowid

    # def toIdDict(self):
    #     ret = dict()