import codecs
import os
import zipfile

from contextlib import contextmanager


class FileSystem(object):
    class FileNotFound(Exception):
        def __init__(self, path):
            self.path = path


class DirectoryFileSystem(FileSystem):
    def __init__(self, source_dir):
        self.source_dir = source_dir

    @contextmanager
    def open(self, filename):
        """
        Yield a file-like object for file `filename`.

        This function is a context manager.
        """
        filepath = os.path.join(self.source_dir, filename)

        if not os.path.exists(filepath):
            raise self.FileNotFound(filepath)

        with codecs.open(filepath, encoding='utf-8') as f:
            yield f


class ZipFileSystem(FileSystem):
    def __init__(self, zip_file):
        self.zipfile = zipfile.ZipFile(zip_file)

    @contextmanager
    def open(self, filename):
        try:
            f = self.zipfile.open(filename)
            yield f
            f.close()
        except KeyError:
            raise self.FileNotFound(filename)
