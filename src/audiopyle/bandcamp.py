"""Helpers for resolving Bandcamp URLs and scraping tag lists."""

from __future__ import annotations

import re
import unicodedata

import requests
from bs4 import BeautifulSoup


def _slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ASCII", "ignore").decode("utf-8")
    cleaned = re.sub(r"\s+", "-", re.sub(r"[^a-zA-Z0-9\s\'\.]", "-", normalized)).lower()
    cleaned = re.sub(r"\'", "", cleaned)
    cleaned = re.sub(r"\d+(\.)\d?", "", cleaned)
    cleaned = re.sub(r"\.", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned)
    return re.sub(r"^-|-$", "", cleaned)


def build_url_path(album: str | None = None, track: str | None = None) -> str | None:
    """Return a relative Bandcamp path for an album or track title.

    Args:
        album: Album title (preferred when both are supplied).
        track: Track title (used when ``album`` is ``"N/A"`` or missing).

    Returns:
        ``"album/<slug>"`` or ``"track/<slug>"``, or ``None`` if neither
        title is usable.
    """
    if album is not None and album != "N/A":
        return f"album/{_slugify(album)}"
    if track is not None and track != "N/A":
        return f"track/{_slugify(track)}"
    return None


def build_link(origin: str, url_path: str) -> str:
    """Join an origin URL and a relative path into a full Bandcamp URL."""
    return f"{origin}/{url_path}"


def get_tags(url: str, recurse: bool = True) -> list[str]:
    """Return tags scraped from a Bandcamp album or track page.

    Args:
        url: The page URL.
        recurse: If True, retry with a ``-2`` suffix once on HTTP failure
            (Bandcamp sometimes uses this for collisions).

    Returns:
        A list of tag strings; empty on failure.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return get_tags(url + "-2", recurse=False) if recurse else []

    soup = BeautifulSoup(response.content, features="html.parser")
    return [tag.get_text(strip=True) for tag in soup.find_all("a", class_="tag")]


def clean_tags(tags: list[str]) -> list[str]:
    """Return ``tags`` deduplicated, capitalized, and sorted."""
    unique = {tag.replace("-", " ") for tag in tags}
    capitalized = [" ".join(word.capitalize() for word in tag.split()) for tag in unique]
    return sorted(capitalized)
