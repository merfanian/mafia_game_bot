def find_type_in_list(instance, l):
    return next(filter(lambda m: isinstance(m, instance), l), None)
