"""Rough UID module."""

_NAME_NEXT_OFFSET = {}

def auto_name(prefix):
    """Create unique name of the form prefixN, where N is an int."""
    if prefix not in _NAME_NEXT_OFFSET:
        _NAME_NEXT_OFFSET[prefix] = 0

    name = '{}{}'.format(prefix, _NAME_NEXT_OFFSET[prefix])
    _NAME_NEXT_OFFSET[prefix] += 1

    return name
