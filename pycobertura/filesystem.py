import codecs
import os
import io
import zipfile
import subprocess
import shlex

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


class GitFileSystem(FileSystem):
    def __init__(self, repo_folder, ref):
        self.repository = repo_folder
        self.ref = ref
        self.repository_root = self._get_root_path(repo_folder)
        self.prefix = self.repository.replace(self.repository_root, "").lstrip("/")

    def real_filename(self, filename):
        prefix = "{}/".format(self.prefix) if self.prefix else ""
        return "{ref}:{prefix}{filename}".format(
            prefix=prefix, ref=self.ref, filename=filename
        )

    def has_file(self, filename):
        command = "git --no-pager show {}".format(self.real_filename(filename))
        return_code = subprocess.call(
            command,
            cwd=self.repository,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return not bool(return_code)

    def _get_root_path(self, repository_folder):
        command = "git rev-parse --show-toplevel"
        output = subprocess.check_output(shlex.split(command), cwd=repository_folder)
        return output.decode("utf-8").rstrip()

    @contextmanager
    def open(self, filename):
        """
        Yield a file-like object for file `filename`.

        This function is a context manager.
        """
        filename = self.real_filename(filename)

        command = "git --no-pager show {}".format(filename)

        try:
            output = subprocess.check_output(shlex.split(command), cwd=self.repository)
        except OSError:
            raise self.FileNotFound(filename)

        output = output.decode("utf-8").rstrip()
        yield io.StringIO(output)
