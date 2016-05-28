import logging

def configure(name, level):
    fmt = ('%(asctime)s %(levelname)s {} '
           '[%(filename)s:%(lineno)d] %(message)s').format(name)
    logging.basicConfig(level=level, format=fmt)
