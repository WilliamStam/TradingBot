def merge_dicts( base_dict, other_dict ):
    if other_dict is None:
        return base_dict
    t = type(base_dict)
    if not issubclass(t, dict):
        return other_dict
    return {k: merge_dicts(v, other_dict.get(k)) for k, v in base_dict.items()}