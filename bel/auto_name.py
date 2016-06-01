_NAME_NEXT_OFFSET = {}

def auto_name(prefix):
    if prefix not in _NAME_NEXT_OFFSET:
        _NAME_NEXT_OFFSET[prefix] = 0

    name = '{}{}'.format(prefix, _NAME_NEXT_OFFSET[prefix])
    _NAME_NEXT_OFFSET[prefix] += 1

    return name
