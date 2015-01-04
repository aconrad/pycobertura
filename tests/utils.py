SOURCE_FILE = 'tests/cobertura.xml'


def make_cobertura(xml=SOURCE_FILE, *args, **kwargs):
    from pycobertura import Cobertura
    cobertura = Cobertura(xml, *args, **kwargs)
    return cobertura
