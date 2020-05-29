SOURCE_FILE = 'tests/cobertura.xml'


def make_cobertura(xml=SOURCE_FILE, **kwargs):
    from pycobertura import Cobertura
    from pycobertura.filesystem import filesystem_factory
    source_filesystem = filesystem_factory(xml, **kwargs)
    cobertura = Cobertura(xml, filesystem=source_filesystem)
    return cobertura
