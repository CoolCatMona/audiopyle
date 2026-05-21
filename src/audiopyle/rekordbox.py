"""Parsing helpers for Rekordbox XML exports."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from audiopyle.core import File


@dataclass
class RekordboxXML(File):
    """Wraps a parsed Rekordbox XML export."""

    tree: ET.ElementTree[ET.Element[str]] | None = field(default=None, repr=False, compare=False)
    collection: ET.Element[str] | None = field(default=None, repr=False, compare=False)

    @classmethod
    def _from_filepath(cls, filepath: str | Path) -> Self:
        """Parse a Rekordbox XML file and return a populated instance."""
        path = Path(filepath)
        _, year, month = File.date_components(path)
        tree = ET.parse(path)
        collection = tree.find("COLLECTION")
        return cls(
            filename=path.name,
            filepath=str(path.resolve()),
            download_year=year,
            download_month=month,
            tree=tree,
            collection=collection,
        )


class Field:
    """A single text field on a Rekordbox track entry.

    Supports cleaning a separated list of values (e.g. tags) by
    deduplicating, capitalizing, and resorting them.
    """

    def __init__(self, content: str) -> None:
        self._content: str = content

    @property
    def content(self) -> str:
        """Return the raw text content of the field."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value

    def clean_content(self, sep: str) -> None:
        """Sort, deduplicate, and capitalize the field's separated values."""
        if not self._content:
            return
        items = [
            item.strip().replace("-", " ") for item in self._content.split(sep) if item.strip()
        ]
        unique = {item: None for item in items}
        capitalized = [" ".join(w.capitalize() for w in item.split()) for item in unique]
        self._content = " ".join(sep + entry for entry in sorted(capitalized))
