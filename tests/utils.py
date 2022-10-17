from pycobertura import Cobertura
from pycobertura.filesystem import filesystem_factory
from pycobertura.utils import get_dir_from_file_path


def make_cobertura(xml='tests/cobertura.xml', source=None, **kwargs):
    if not source:
        source = get_dir_from_file_path(xml)
    source_filesystem = filesystem_factory(source, **kwargs)
    cobertura = Cobertura(xml, filesystem=source_filesystem)
    return cobertura
