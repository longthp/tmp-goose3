from __future__ import annotations

import datetime
import zoneinfo
import urllib.parse

from typing import Protocol

from goose3 import Article
from goose3 import Configuration
from goose3 import Goose

from tinydb import TinyDB
from tinydb import Query


URLS = [
    "https://apnews.com/article/south-korea-martial-law-3210438b8663fe609bfe4cb8b748a114",
    "https://www.npr.org/2024/12/11/1218506698/code-switch-black-utopians",
    "https://www.npr.org/2024/12/09/nx-s1-5200587/mina-new-album-gassa-damante-italy"
]


def datetime_to_gmt_str(dt: datetime.datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def parse_url_domain(url: str) -> str:
    parsed = urllib.parse.urlparse(url)

    return parsed.netloc.replace(".", "_")


class Storage(Protocol):
    def __init__(self, uri: str) -> None:
        pass

    def insert(self, document: dict) -> str | int:
        ...


class TinyDBStorage:
    def __init__(
        self,
        uri: str,
    ) -> None:
        self.db = TinyDB(uri)
        self.query = Query()
        self._collection_name = "default"

    @property
    def collection(self) -> str:
        return self._collection_name

    @collection.setter
    def collection(self, name: str) -> None:
        self._collection_name = name

    def insert(self, document: dict) -> int:
        return self.db.table(self._collection_name).insert(document)


def extract_article(
    goose: Goose,
    url: str,
    attrs: list[str] | None = None
) -> dict:
    article: Article = goose.extract(url=url)

    a = set()

    if attrs is not None:
        for attr in attrs:
            if attr in GOOSE3_ARTICLE_DEFAULT_ATTRS:
                a.add(attr)

            else:
                continue

    elif attrs is None:
        a.add("infos")

    d = {
        attr: getattr(article, attr)
        for attr in a
    }

    return d


def setup_goose() -> Goose:
    c = Configuration()
    c.browser_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2)"

    g = Goose(config=c)

    return g


def main() -> int:
    g = setup_goose()

    tinydb_storage = TinyDBStorage("/tmp/documents.json")

    for url in URLS:
        domain = parse_url_domain(url)

        tinydb_storage.collection = domain

        d = extract_article(
            goose=g,
            url=url
        )

        extracted_at = datetime.datetime.now()

        d["extracted_at"] = datetime_to_gmt_str(extracted_at)

        tinydb_storage.insert(d)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
