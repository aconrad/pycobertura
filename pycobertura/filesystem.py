import codecs
import os
import io
import zipfile
import subprocess

from contextlib import contextmanager


class FileSystem:
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

        with codecs.open(filename, encoding="utf-8") as f:
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
            with self.zipfile.open(filename) as f:
                with io.TextIOWrapper(f, encoding="utf-8") as t:
                    yield t
        except KeyError:
            raise self.FileNotFound(filename)


class GitFileSystem(FileSystem):
    def __init__(self, repo_folder, ref):
        self.repository = repo_folder
        self.ref = ref
        self.repository_root = self._get_root_path(repo_folder)
        # the report may have been collected in a subfolder of the repository
        # root. Each file path shall thus be completed by the prefix.
        self.prefix = self.repository.replace(self.repository_root, "").lstrip("/")

    def real_filename(self, filename):
        """
        Constructs the Git path for a given filename.
        This method should NOT resolve symlinks on the local disk.
        """
        prefix = f"{self.prefix}/" if self.prefix else ""
        return f"{self.ref}:{prefix}{filename}"

    def has_file(self, filename):
        """
        Check for a file's existence in the specified commit's tree.
        """
        git_path = f"{self.prefix}/{filename}" if self.prefix else filename
        command = ["git", "cat-file", "--batch-check", "--follow-symlinks", "-Z"]
        input_data = f"{self.ref}:{git_path}".encode() + b'\x00'

        process = subprocess.Popen(
            command,
            cwd=self.repository_root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate(input=input_data)
        assert error == b''
        return not output.endswith(b'missing\x00')

    def _get_root_path(self, repository_folder):
        command = ["git", "rev-parse", "--show-toplevel"]
        try:
            output = subprocess.check_output(command, cwd=repository_folder)
        except (OSError, subprocess.CalledProcessError):
            raise ValueError(f"The folder {repository_folder} is not a valid git repository.")
        return output.decode("utf-8").rstrip()

    @contextmanager
    def open(self, filename):
        """
        Yield a file-like object for the given filename, following symlinks if necessary.
        """
        git_path = f"{self.prefix}/{filename}" if self.prefix else filename
        command = ["git", "cat-file", "--batch", "--follow-symlinks", "-Z"]
        input_data = f"{self.ref}:{git_path}".encode() + b'\x00'

        try:
            process = subprocess.Popen(
                command,
                cwd=self.repository_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output, _ = process.communicate(input=input_data)
            return_code = process.wait()

            if return_code != 0 or output.endswith(b'missing\x00'):
                raise self.FileNotFound(self.real_filename(filename))
            lines = output.split(b'\n', 1)
            content = lines[1]
            yield io.StringIO(content.decode("utf-8"))

        except (OSError, subprocess.CalledProcessError):
            raise self.FileNotFound(self.real_filename(filename))


def filesystem_factory(source, source_prefix=None, ref=None):
    """
    The argument `source` is the location of the source code provided as a
    directory path or a file object zip archive containing the source code.

    The optional argument `source` is the location of the source code provided
    as a directory path or a file object zip archive containing the source code.

    The optional argument `ref` will be taken into account when instantiating a
    GitFileSystem, and it shall be a branch name, a commit ID or a git ref ID.
    """
    if zipfile.is_zipfile(source):
        return ZipFileSystem(source, source_prefix=source_prefix)

    if ref:
        return GitFileSystem(source, ref)

    return DirectoryFileSystem(source, source_prefix=source_prefix)
