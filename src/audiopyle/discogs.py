"""Discogs API client and search helpers."""

from __future__ import annotations

import os
import re
import time
from dataclasses import asdict, dataclass
from typing import Self

import requests

from audiopyle.audio import Audio

DEFAULT_BASE_URL = "https://api.discogs.com"
DEFAULT_USER_AGENT = "audiopyle/0.2 (+https://github.com/CoolCatMona/audiopyle)"


@dataclass
class DiscogsSearchParameters:
    """Parameters for the Discogs ``/database/search`` endpoint.

    Each attribute maps to a named query parameter as documented at
    https://www.discogs.com/developers#page:database,header:database-search.
    """

    query: str | None = None
    type: str | None = None
    title: str | None = None
    release_title: str | None = None
    credit: str | None = None
    artist: str | None = None
    anv: str | None = None
    label: str | None = None
    genre: str | None = None
    style: str | None = None
    country: str | None = None
    year: str | None = None
    format: str | None = None
    catno: str | None = None
    barcode: str | None = None
    track: str | None = None
    submitter: str | None = None
    contributor: str | None = None

    @property
    def search_string(self) -> str:
        """Return the parameters joined into a query-string fragment."""
        parts = [
            f"{key}={value.replace(' ', '+')}"
            for key, value in asdict(self).items()
            if value is not None
        ]
        return "&?".join(parts)

    @classmethod
    def from_audio(cls, audio: Audio) -> Self:
        """Construct a parameter set from an :class:`Audio` instance."""
        return cls(
            release_title=_clean_album_name(audio.album),
            artist=_clean_artist_name(audio.artist),
        )


def _clean_album_name(album: str) -> str:
    return re.sub(r"[\(\[].*?[\)\]]", "", album).strip()


def _clean_artist_name(artist: str) -> str:
    return re.sub(r",.*", "", artist)


class DiscogsClient:
    """Thin wrapper around the Discogs database-search endpoint."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        """Initialize the client.

        Args:
            token: Discogs API token. If ``None``, read from the
                ``DISCOGS_TOKEN`` environment variable at call time.
            base_url: Override for the API base URL (for testing).
            user_agent: ``User-Agent`` header sent with each request.
        """
        self._token = token
        self._base_url = base_url
        self._user_agent = user_agent

    def _headers(self) -> dict[str, str]:
        token = self._token or os.getenv("DISCOGS_TOKEN")
        headers = {"User-Agent": self._user_agent}
        if token:
            headers["Authorization"] = f"Discogs token={token}"
        return headers

    def search_styles(self, params: DiscogsSearchParameters, retries: int = 2) -> list[str]:
        """Search Discogs and return the ``style`` tags of the first match.

        Args:
            params: Search parameters.
            retries: How many times to retry on HTTP 429.

        Returns:
            A list of style tags, or an empty list on failure.
        """
        url = f"{self._base_url}/database/search?{params.search_string}"
        for _ in range(retries):
            response = requests.get(url, headers=self._headers(), timeout=10)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                if response.status_code == 429:
                    time.sleep(10)
                    continue
                return []
            return _parse_style_tags(params, response.json())
        return []


def _parse_style_tags(params: DiscogsSearchParameters, payload: dict[str, object]) -> list[str]:
    target = (params.release_title or "").lower()
    results = payload.get("results") or []
    if not isinstance(results, list):
        return []
    for result in results:
        if not isinstance(result, dict):
            continue
        title = result.get("title", "")
        if not isinstance(title, str):
            continue
        if target and target in title.lower():
            styles = result.get("style") or []
            return list(styles) if isinstance(styles, list) else []
    return []
