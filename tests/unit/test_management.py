"""Tests for the ``Directory`` class."""

from pathlib import Path

import pytest

from audiopyle import management


@pytest.fixture
def fx_temp_dir(tmp_path: Path) -> Path:
    d = tmp_path / "test_dir"
    d.mkdir()
    (d / "test_file.txt").write_text("test")
    return d


@pytest.fixture(scope="function", params=["non_empty", "empty", "mixed"])
def fx_temp_dir_with_subdirs(tmp_path: Path, request):
    d = tmp_path / "test_dir"
    d.mkdir()

    if request.param == "non_empty":
        sub = d / "bar"
        sub.mkdir()
        (sub / "foo.txt").write_text("test")
        return d, 0, Path("not_empty")
    if request.param == "empty":
        empty = d / "bar"
        empty.mkdir()
        (d / "baz").mkdir()
        return d, 2, empty
    sub = d / "bar"
    sub.mkdir()
    other = d / "baz"
    other.mkdir()
    (other / "foo.txt").write_text("test")
    return d, 1, sub


def test_directory_from_filepath(fx_temp_dir: Path) -> None:
    d = management.Directory._from_filepath(fx_temp_dir)
    assert d._num_files == 1


def test_directory_from_filepath_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        management.Directory._from_filepath("bar")


def test_directory_from_filepath_raises_not_a_directory() -> None:
    with pytest.raises(NotADirectoryError):
        management.Directory._from_filepath(__file__)


def test_backup_creates_sibling(fx_temp_dir: Path) -> None:
    d = management.Directory._from_filepath(fx_temp_dir)
    backup = d.backup()
    try:
        assert backup.exists()
        assert (backup / "test_file.txt").read_text() == "test"
    finally:
        import shutil

        shutil.rmtree(backup)


def test_empty_subdirectories(fx_temp_dir_with_subdirs) -> None:
    root, expected, _ = fx_temp_dir_with_subdirs
    d = management.Directory._from_filepath(root)
    assert len(d.empty_subdirectories) == expected


def test_delete_empty_subdirectories(fx_temp_dir_with_subdirs) -> None:
    root, _, to_delete = fx_temp_dir_with_subdirs
    d = management.Directory._from_filepath(root)
    d.delete_empty_subdirectories()
    if to_delete != Path("not_empty"):
        assert not to_delete.exists()


def test_files_is_lazy(fx_temp_dir: Path) -> None:
    d = management.Directory._from_filepath(fx_temp_dir)
    assert d.files == [fx_temp_dir / "test_file.txt"]


def test_move_files_is_not_implemented(fx_temp_dir: Path) -> None:
    d = management.Directory._from_filepath(fx_temp_dir)
    with pytest.raises(NotImplementedError):
        d.move_files()
