"""Test for file and directory management."""
from audiopyle import management
import pytest
import shutil
from pathlib import Path


@pytest.fixture(scope="function")
def fx_temp_dir(tmp_path):
    """Creates a temporary directory for testing."""
    d = tmp_path / "test_dir"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("test")
    yield d


@pytest.fixture(
    scope="function",
    params=["non_empty", "empty", "mixed"],
    ids=["non_empty_directory", "empty_directory", "mixed_directories"],
)
def fx_temp_dir_with_subdirs(tmp_path, request):
    """Creates a temporary directory with subdirectories for testing, returns the root directory, the number of empty directories, and the path to the empty directory"""
    empty_directories: int = -1
    _dir = False

    if request.param == "non_empty":
        d = tmp_path / "test_dir"
        d.mkdir()

        _non_empty = d / "bar"
        _non_empty.mkdir()

        p = _non_empty / "foo.txt"
        p.write_text("test")

        empty_directories = 0
        _dir = Path("not_empty")

    elif request.param == "empty":
        d = tmp_path / "test_dir"
        d.mkdir()

        _empty = d / "bar"
        _empty.mkdir()
        _empty2 = d / "baz"
        _empty2.mkdir()
        _dir = _empty

        empty_directories = 2

    elif request.param == "mixed":
        d = tmp_path / "test_dir"
        d.mkdir()

        _empty = d / "bar"
        _empty.mkdir()

        _non_empty = d / "baz"
        _non_empty.mkdir()

        p = _non_empty / "foo.txt"
        p.write_text("test")

        empty_directories = 1
        _dir = _empty

    return d, empty_directories, _dir


@pytest.fixture(
    scope="function",
    params=["root", "subdir", "mixed", "nested", "none"],
    ids=[
        "files_only_in_root",
        "files_only_in_subdir",
        "files_in_both",
        "files_in_nested_subdirs",
        "no_files",
    ],
)
def fx_temp_dir_with_files(tmp_path, request):
    """Creates a temporary directory with files for testing, returns the root directory, the number of files, and the path to the file"""
    num_files = -1
    if request.param == "root":
        d = tmp_path / "test_dir"
        d.mkdir()

        p = d / "foo.txt"
        p.write_text("test")

        _subdir = d / "bar"
        _subdir.mkdir()
        num_files = 1

    elif request.param == "subdir":
        d = tmp_path / "test_dir"
        d.mkdir()

        _subdir = d / "bar"
        _subdir.mkdir()

        p = _subdir / "foo.txt"
        p.write_text("test")

        num_files = 1

    elif request.param == "mixed":
        d = tmp_path / "test_dir"
        d.mkdir()

        p = d / "foo.txt"
        p.write_text("test")

        _subdir = d / "bar"
        _subdir.mkdir()

        p = _subdir / "foo.txt"
        p.write_text("test")

        _subdir2 = d / "baz"
        _subdir2.mkdir()

        p = _subdir2 / "foo.txt"
        p.write_text("test")

        num_files = 3

    elif request.param == "nested":
        d = tmp_path / "test_dir"
        d.mkdir()

        _subdir = d / "bar"
        _subdir.mkdir()

        _subdir2 = _subdir / "baz"
        _subdir2.mkdir()

        p = _subdir2 / "foo.txt"
        p.write_text("test")

        num_files = 1

    elif request.param == "none":
        d = tmp_path / "test_dir"
        d.mkdir()

        num_files = 0

    return d, num_files


@pytest.fixture(scope="function")
def fx_cleanup_temp_dir(fx_temp_dir):
    yield
    generated_dir = str(fx_temp_dir) + "_bak"
    shutil.rmtree(generated_dir)


def test_Directory_from_filepath(fx_temp_dir):
    """Tests the initialization of a Directory object."""
    d = management.Directory._from_filepath(fx_temp_dir)
    assert d._num_files == 1


def test_Directory_from_filepath_raises_FileNotFound():
    """Tests that a Directory raises a FileNotFoundError if the filepath does not exist."""
    with pytest.raises(FileNotFoundError):
        management.Directory._from_filepath("bar")


def test_Directory_from_filepath_raises_NotADirectory():
    """Tests that a Directory raises a NotADirectoryError if the filepath is not a directory."""
    with pytest.raises(NotADirectoryError):
        management.Directory._from_filepath(__file__)


def test_backup_directory(fx_temp_dir, fx_cleanup_temp_dir):
    """Tests that a directory is backed up."""
    d = management.Directory._from_filepath(fx_temp_dir)
    d.backup()
    _d = management.Directory._from_filepath(d._directory_path_str + "_bak")

    assert _d._num_files == 1


def test_get_files(fx_temp_dir_with_files):
    """Tests that the directory object can get files."""
    d, num_files = (
        management.Directory._from_filepath(fx_temp_dir_with_files[0]),
        fx_temp_dir_with_files[1],
    )
    assert len(d.files) == num_files


def test_get_empty_directories(fx_temp_dir_with_subdirs):
    """Tests that the Directory object can get empty directories."""
    d, expected_empty_directories = (
        management.Directory._from_filepath(fx_temp_dir_with_subdirs[0]),
        fx_temp_dir_with_subdirs[1],
    )
    assert len(d._empty_directories) == expected_empty_directories


def test_delete_empty_directories(fx_temp_dir_with_subdirs):
    """Tests that the Directory object can delete empty directories."""
    d, path_to_empty_directory = (
        management.Directory._from_filepath(fx_temp_dir_with_subdirs[0]),
        fx_temp_dir_with_subdirs[2],
    )
    d._delete_empty_directories()

    assert not path_to_empty_directory.exists()


@pytest.mark.parametrize(
    "subdirs",
    [
        ([]),
        (["foo"]),
        (["foo", "bar"]),
    ],
    ids=[
        "no_subdirs",
        "one_subdir",
        "multiple_subdirs",
    ],
)
def test_create_directory(fx_temp_dir, subdirs):
    """Tests that the directory object can create a new directory."""
    d = management.Directory._from_filepath(fx_temp_dir)
    created_directory = d._create_directory(*subdirs)
    assert created_directory.exists()


def test_move_files(fx_temp_dir):
    """Tests that the files in a directory can be moved."""
    d = management.Directory._from_filepath(fx_temp_dir)
    d.move_files()
    assert False
