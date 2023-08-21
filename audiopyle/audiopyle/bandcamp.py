"""Methods and functions related to bandcamp scraping and parsing"""
from bs4 import BeautifulSoup
import requests
import re


def _build_url_path(album: str | None = None, track: str | None = None) -> str:
    """Given either an album title or track title, attempt to build a valid bandcamp url."""
    raise NotImplementedError


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
