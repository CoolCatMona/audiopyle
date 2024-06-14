"""Methods and functions related to bandcamp scraping and parsing"""

import re
import unicodedata

import requests
from bs4 import BeautifulSoup


def _build_url_path(album: str | None = None, track: str | None = None) -> str:
    """Given either an album title or track title, attempt to build a valid bandcamp url."""

    def __get_url_path(title):
        # Remove unicode characters
        normalized = (
            unicodedata.normalize("NFKD", title)
            .encode("ASCII", "ignore")
            .decode("utf-8")
        )
        # Replace non alphanumeric characters
        cleaned = re.sub(
            r"\s+", "-", re.sub(r"[^a-zA-Z0-9\s\'\.]", "-", normalized)
        ).lower()
        cleaned = re.sub(r"\'", "", cleaned)
        cleaned = re.sub(r"\d+(\.)\d?", "", cleaned)
        cleaned = re.sub(r"\.", "-", cleaned)
        # Combine sequential -
        cleaned = re.sub(r"[-]+", "-", cleaned)
        # Remove trailing -
        cleaned = re.sub(r"^[-]|[-]$", "", cleaned)

        return cleaned

    url_path = None

    if album != "N/A":
        url_path = f"album/{__get_url_path(album)}"
    elif track != "N/A":
        url_path = f"track/{__get_url_path(track)}"

    return url_path


def build_link(origin, url):
    return f"{origin}/{url}"


def get_tags(url: str, recurse: bool = True) -> list:
    """Gets tags from bandcamp given a url

    Returns:
        list: List of tags
    """
    tags = []
    r = requests.get(url)
    try:
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        _tags = soup.findAll("a", class_="tag")
        tags = [tag.get_text(strip=True) for tag in _tags]
    except requests.exceptions.HTTPError as e:
        if recurse:
            tags = get_tags(url + "-2", recurse=False)

    return tags
