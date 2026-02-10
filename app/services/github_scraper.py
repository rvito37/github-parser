import re

import httpx
from bs4 import BeautifulSoup

from app.models.profile import ContributionStats, PinnedRepo


class GitHubScraper:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def scrape_profile(self, username: str) -> dict:
        """Scrape GitHub profile page for data not available via REST API."""
        try:
            resp = await self._client.get(
                f"https://github.com/{username}",
                headers={"User-Agent": "Mozilla/5.0 (compatible; GitHubParser/1.0)"},
                follow_redirects=True,
            )
            if resp.status_code != 200:
                return {"pinned_repos": [], "contribution_stats": None, "achievements": []}

            soup = BeautifulSoup(resp.text, "lxml")

            return {
                "pinned_repos": self._parse_pinned_repos(soup),
                "contribution_stats": self._parse_contributions(soup),
                "achievements": self._parse_achievements(soup),
            }
        except Exception:
            return {"pinned_repos": [], "contribution_stats": None, "achievements": []}

    def _parse_pinned_repos(self, soup: BeautifulSoup) -> list[PinnedRepo]:
        pinned = []
        for item in soup.select(".pinned-item-list-item-content"):
            name_el = item.select_one("a.text-bold span")
            name = name_el.get_text(strip=True) if name_el else None
            if not name:
                continue

            desc_el = item.select_one("p.pinned-item-desc")
            description = desc_el.get_text(strip=True) if desc_el else None

            lang_el = item.select_one("[itemprop='programmingLanguage']")
            language = lang_el.get_text(strip=True) if lang_el else None

            stars = 0
            star_el = item.select_one("a[href$='/stargazers']")
            if star_el:
                star_text = star_el.get_text(strip=True).replace(",", "")
                stars = int(star_text) if star_text.isdigit() else 0

            pinned.append(PinnedRepo(name=name, description=description, language=language, stars=stars))
        return pinned

    def _parse_contributions(self, soup: BeautifulSoup) -> ContributionStats | None:
        heading = soup.select_one("h2.f4.text-normal.mb-2")
        if not heading:
            return None
        text = heading.get_text(strip=True)
        match = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", text)
        if not match:
            return None
        count = int(match.group(1).replace(",", ""))
        return ContributionStats(total_contributions_last_year=count)

    def _parse_achievements(self, soup: BeautifulSoup) -> list[str]:
        achievements = []
        for badge in soup.select("img.achievement-badge-sidebar"):
            alt = badge.get("alt", "")
            if alt and alt not in ("", "Achievement"):
                name = alt.replace("Achievement: ", "")
                if name not in achievements:
                    achievements.append(name)
        return achievements
