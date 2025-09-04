import requests
import time

from functools import wraps
from typing import Any, Dict, Tuple

API_URL = "https://api.github.com"

def cached(ttl_attr="_ttl", cache_attr="_cache"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            now = time.time()
            # initialiser le cache si nécessaire
            if not hasattr(self, cache_attr):
                setattr(self, cache_attr, {})
            cache = getattr(self, cache_attr)

            # utiliser le cache si encore valide
            key = func.__name__
            if key in cache:
                data, timestamp = cache[key]
                if now - timestamp < getattr(self, ttl_attr):
                    return data

            # sinon faire la requête réelle
            result = func(self, *args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper
    return decorator

class GitHubClient:
    def __init__(self, token: str, username: str, ttl: int = 600):
        self.token = token
        self.username = username
        self._ttl = ttl  # durée de vie du cache en secondes

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        })
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def rate_limit(self) -> dict[str, int]:
        r = self.session.get(f"{API_URL}/rate_limit")
        r.raise_for_status()
        return r.json()["rate"]

    @cached()
    def user_profile(self) -> dict[str, Any]:
        r = self.session.get(f"{API_URL}/users/{self.username}")
        r.raise_for_status()
        #Debug print(r.json())
        return r.json()

    @cached()
    def user_repos(self) -> list[dict[str, Any]]:
        r = self.session.get(f"{API_URL}/users/{self.username}/repos?per_page=100")
        r.raise_for_status()
        return r.json()

    def user_overview(self) -> dict:
        profile = self.user_profile()
        repos = self.user_repos()

        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        total_forks = sum(repo.get("forks_count", 0) for repo in repos)

        return {
            "login": profile["login"],
            "name": profile.get("name") or profile["login"],
            "bio": profile.get("bio"),
            "avatar_url": profile.get("avatar_url"),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public repos": profile.get("public_repos", 0),
            "public gists": profile.get("public_gists", 0),
            "private repos": profile.get("total_private_repos", 0),
            "private gists": profile.get("public_gists", 0),
            "created_at": profile.get("created_at"),
            "stars": total_stars,
            "forks": total_forks,
        }
