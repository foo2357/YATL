from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import requests


class ContentFormat(StrEnum):
    """Unified enumeration for content formats.

    Combines both format names and their corresponding MIME types.
    """

    JSON = "json"
    XML = "xml"
    TEXT = "text"

    @property
    def mime_type(self) -> str:
        """Returns the MIME type for this format."""
        mapping = {
            self.JSON: "application/json",
            self.XML: "application/xml",
            self.TEXT: "text/plain",
        }
        return mapping[self]

    @classmethod
    def from_mime_type(cls, mime_type: str) -> "ContentFormat":
        """Determines the format from a MIME type.

        Args:
            mime_type: The MIME type string (e.g., "application/json").

        Returns:
            The corresponding ContentFormat enum value.

        Raises:
            ValueError: If the MIME type is not supported.
        """
        normalized = mime_type.split(";")[0].strip().lower()
        mapping = {
            "application/json": cls.JSON,
            "application/xml": cls.XML,
            "text/plain": cls.TEXT,
            "text/html": cls.TEXT,
        }
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(f"Unsupported content type: {mime_type}")


@dataclass
class BodyExpectation:
    format: ContentFormat
    spec: dict[str, Any] | str


@dataclass
class ExpectSpec:
    status: int | None
    headers: dict[str, str] | None
    body: BodyExpectation | None


@dataclass
class ExtractSpec:
    mappings: dict[str, str]


@dataclass
class JsonBody:
    data: Any

    def to_requests_kwargs(self, headers: dict[str, str]) -> dict[str, Any]:
        headers.setdefault("Content-Type", "application/json")
        return {"json": self.data}


@dataclass
class XmlBody:
    data: str

    def to_requests_kwargs(self, headers: dict[str, str]) -> dict[str, Any]:
        headers.setdefault("Content-Type", "application/xml")
        return {"data": self.data}


@dataclass
class FormBody:
    data: dict[str, str]

    def to_requests_kwargs(self, headers: dict[str, str]) -> dict[str, Any]:
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        return {"data": self.data}


@dataclass
class FilesBody:
    data: dict[str, Any]

    def to_requests_kwargs(self, headers: dict[str, str]) -> dict[str, Any]:
        return {"files": self.data}


@dataclass
class TextBody:
    data: str

    def to_requests_kwargs(self, headers: dict[str, str]) -> dict[str, Any]:
        headers.setdefault("Content-Type", "text/plain")
        return {"data": self.data}


type Body = JsonBody | XmlBody | FormBody | FilesBody | TextBody


@dataclass
class HttpRequest:
    url: str
    method: str
    headers: dict[str, str]
    params: dict[str, str]
    cookies: dict[str, str]
    timeout: float | None
    body: Body | None


@dataclass
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes
    content_type: ContentFormat


def adapt_response(raw: requests.Response) -> HttpResponse:
    """Converts a requests. Response into a domain Response.

    Args:
        raw: The raw HTTP response from the requests library.

    Returns:
        A domain Response object with extracted status, headers, body,
        and content type.
    """

    content_type = ContentFormat.from_mime_type(
        raw.headers.get("Content-Type", "text/plain")
    )
    return HttpResponse(
        status_code=raw.status_code,
        headers=dict(raw.headers),
        body=raw.content,
        content_type=content_type,
    )
