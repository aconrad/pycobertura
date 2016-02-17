import codecs
import os
import zipfile

from contextlib import contextmanager


class FileSystem(object):
    class FileNotFound(Exception):
        def __init__(self, path):
            super(self.__class__, self).__init__(path)
            self.path = path


class DirectoryFileSystem(FileSystem):
    def __init__(self, source_dir, source_prefix=None):
        self.source_dir = source_dir
        self.source_prefix = source_prefix

    def real_filename(self, filename):
        if self.source_prefix is not None:
            filename = os.path.join(self.source_prefix, filename)
        return os.path.join(self.source_dir, filename)

    def has_file(self, filename):
        # FIXME: make this O(1)
        filename = self.real_filename(filename)
        return os.path.isfile(filename)

    @contextmanager
    def open(self, filename):
        """
        Yield a file-like object for file `filename`.

        This function is a context manager.
        """
        filename = self.real_filename(filename)

        if not os.path.exists(filename):
            raise self.FileNotFound(filename)

        with codecs.open(filename, encoding='utf-8') as f:
            yield f


class ZipFileSystem(FileSystem):
    def __init__(self, zip_file, source_prefix=None):
        self.zipfile = zipfile.ZipFile(zip_file)
        self.source_prefix = source_prefix

    def real_filename(self, filename):
        if self.source_prefix is not None:
            filename = os.path.join(self.source_prefix, filename)

        return filename

    def has_file(self, filename):
        # FIXME: make this O(1)
        return self.real_filename(filename) in self.zipfile.namelist()

    @contextmanager
    def open(self, filename):
        filename = self.real_filename(filename)

        try:
            f = self.zipfile.open(filename)
            yield f
            f.close()
        except KeyError:
            raise self.FileNotFound(filename)
