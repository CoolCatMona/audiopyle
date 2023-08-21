"""Test for file and directory management."""
from audiopyle import management
import pytest
import shutil


@pytest.fixture(scope="function")
def fx_temp_dir(tmp_path):
    """Creates a temporary directory for testing."""
    d = tmp_path / "test_dir"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("test")
    yield d


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
