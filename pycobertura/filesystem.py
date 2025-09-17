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
        # Cache submodule paths and commit SHAs for the provided ref
        self._submodules = self._discover_submodules()

    def _git_cat_file_check(self, repo_root, spec):
        """
        Call `git cat-file --batch-check --follow-symlinks` and return existence as bool.
        """
        args = ["git", "cat-file", "--batch-check", "--follow-symlinks"]
        input_data = f"{spec}\n".encode()
        try:
            process = subprocess.Popen(
                args,
                cwd=repo_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output, _ = process.communicate(input=input_data)
            return_code = process.wait()
        except (OSError, subprocess.CalledProcessError):
            return False
        return return_code == 0 and not output.endswith(b"missing\n")

    def _git_cat_file_read(self, repo_root, spec):
        """
        Call `git cat-file --batch --follow-symlinks` and return blob content as bytes.
        Raises FileNotFound if the object is missing or on error.
        """
        args = ["git", "cat-file", "--batch", "--follow-symlinks"]
        input_data = f"{spec}\n".encode()
        try:
            process = subprocess.Popen(
                args,
                cwd=repo_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output, _ = process.communicate(input=input_data)
            return_code = process.wait()
        except (OSError, subprocess.CalledProcessError):
            raise self.FileNotFound(spec)

        if return_code != 0 or output.endswith(b"missing\n"):
            raise self.FileNotFound(spec)
        lines = output.split(b"\n", 1)
        if len(lines) < 2:
            raise self.FileNotFound(spec)
        return lines[1]

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
        # If the file is within a submodule, query the submodule repository
        submodule_ctx = self._resolve_submodule_ctx(filename)
        if submodule_ctx is not None:
            submodule_root, sub_commit, rel_path = submodule_ctx
            return self._git_cat_file_check(submodule_root, f"{sub_commit}:{rel_path}")

        real_filename = self.real_filename(filename)
        return self._git_cat_file_check(self.repository_root, real_filename)

    def _get_root_path(self, repository_folder):
        command = ["git", "rev-parse", "--show-toplevel"]
        try:
            output = subprocess.check_output(command, cwd=repository_folder)
        except (OSError, subprocess.CalledProcessError):
            raise ValueError(
                f"The folder {repository_folder} is not a valid git repository."
            )
        return output.decode("utf-8").rstrip()

    @contextmanager
    def open(self, filename):
        """
        Yield a file-like object for the given filename, following symlinks if necessary.
        """
        # If the file is within a submodule, read from the submodule repository at the pinned commit
        submodule_ctx = self._resolve_submodule_ctx(filename)
        if submodule_ctx is not None:
            submodule_root, sub_commit, rel_path = submodule_ctx
            content = self._git_cat_file_read(
                submodule_root, f"{sub_commit}:{rel_path}"
            )
            yield io.StringIO(content.decode("utf-8"))
            return

        real_filename = self.real_filename(filename)
        content = self._git_cat_file_read(self.repository_root, real_filename)
        yield io.StringIO(content.decode("utf-8"))

    def _discover_submodules(self):
        """
        Discover submodule paths and SHAs for the given ref by inspecting the tree.
        Returns a mapping of submodule path -> commit SHA.
        """
        try:
            output = subprocess.check_output(
                [
                    "git",
                    "ls-tree",
                    "-r",
                    "--full-tree",
                    self.ref,
                ],
                cwd=self.repository_root,
            )
        except (OSError, subprocess.CalledProcessError):
            return {}

        submodules = {}
        for line in output.decode("utf-8", errors="replace").splitlines():
            # Expected format: "160000 commit <sha>\t<path>"
            try:
                meta, path = line.split("\t", 1)
            except ValueError:
                continue
            parts = meta.split()
            if len(parts) < 3:
                continue
            mode, obj_type, sha = parts[0], parts[1], parts[2]
            if mode == "160000" and obj_type == "commit":
                submodules[path] = sha
        return submodules

    def _resolve_submodule_ctx(self, filename):
        """
        If the path points into a submodule, return a tuple of
        (submodule_root_abs_path, submodule_commit_sha, relative_path_inside_submodule).
        Otherwise, return None.
        """
        # Find the longest matching submodule path that prefixes the filename
        matching = [
            p
            for p in self._submodules.keys()
            if filename == p or filename.startswith(p + "/")
        ]
        if not matching:
            return None
        # Use the longest (deepest) match in case of nested submodules
        sub_path = max(matching, key=len)
        sub_sha = self._submodules.get(sub_path)
        if not sub_sha:
            return None

        rel_path = filename.removeprefix(sub_path).lstrip("/")
        submodule_root = os.path.join(self.repository_root, sub_path)
        if not os.path.isdir(submodule_root):
            # Submodule not checked out; we cannot read without local checkout of objects
            return None
        return (submodule_root, sub_sha, rel_path)


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
