"""Database setup and seed script."""

from __future__ import annotations

from typing import Dict

from connector import BaseModel, db_session, get_engine
from models.article import Article
from models.region import Region
from models.author import Author  # noqa: F401  # Ensure mapper is configured


REGION_SEEDS = {
    "AU": "Australia",
    "UK": "United Kingdom",
    "US": "United States of America",
}

ARTICLE_SEEDS = [
    {
        "title": "Post 1",
        "content": "This is a post body",
        "regions": ("AU", "UK"),
    },
    {
        "title": "Post 2",
        "content": "This is the second post body",
        "regions": ("AU", "US"),
    },
]


def ensure_regions(session) -> Dict[str, Region]:
    """Create region records if they do not already exist."""
    region_map: Dict[str, Region] = {}

    for code, name in REGION_SEEDS.items():
        region = session.query(Region).filter(Region.code == code).one_or_none()
        if region is None:
            region = Region(code=code, name=name)
            session.add(region)
        region_map[code] = region

    session.flush()  # Ensure IDs are available for relationship assignment
    return region_map


def ensure_articles(session, regions: Dict[str, Region]) -> None:
    """Create demo articles if they do not already exist."""
    for seed in ARTICLE_SEEDS:
        article = session.query(Article).filter(Article.title == seed["title"]).one_or_none()
        if article is not None:
            continue

        article = Article(
            title=seed["title"],
            content=seed["content"],
            regions=[regions[code] for code in seed["regions"]],
        )
        session.add(article)


def main() -> None:
    """Ensure schema exists and seed baseline lookup data."""
    engine = get_engine()
    BaseModel.metadata.create_all(engine)

    with db_session() as session:
        regions = ensure_regions(session)
        ensure_articles(session, regions)

    print("✓ Database schema initialized and seed data ensured.")


if __name__ == "__main__":
    main()
