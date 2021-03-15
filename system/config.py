from .utils.dict import merge_dicts as utils_dict_merge_dicts
class Config(dict):
    def __init__(self):
        self.config = dict()
        self.default = dict()
        self._config = dict()
    def load(self,default=dict(),config=dict()):
        self.config = config
        self.default = default
        self._config = (self.merge_dicts(self.default,self.config))
        # return self.merge_dicts(self.default,self.config)
        return self
    def get( self,key=None,default=None ):
        if key is None:
            return self._config
        parts = key.split(".")
        val = self._config
        for p in parts:
            if isinstance(val,dict) and val.get(p):
                val = val[p]
            else:
                val = default
                break
        return val
    def merge_dicts(self, base_dict,other_dict ):
        return utils_dict_merge_dicts(base_dict,other_dict)
