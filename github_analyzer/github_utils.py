import aiohttp
from typing import List
import requests
import logging


class GitHubAnalyzer:
    """
    Class to interact with the GitHub API and fetch data
    all functions work asynchronously to avoid blocking the main thread
    """

    def __init__(self, token, repo_name):
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json"}
        self.logger = logging.getLogger(__name__)

    async def fetch_repo(self, session: aiohttp.ClientSession) -> dict:
        url = f"https://api.github.com/repos/{self.repo_name}"
        try:
            self.logger.debug(f"Fetching repo data from {url}")
            async with session.get(url) as response:
                response.raise_for_status()
                repo_data = await response.json()
            return repo_data
        except Exception as e:
            self.logger.error(f"Failed to retrieve repo data: {e}")
            return {}

    async def fetch_releases(self, session: aiohttp.ClientSession, limit_releases=3) -> List[dict]:
        url = f"https://api.github.com/repos/{self.repo_name}/releases"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                releases = await response.json()
                self.logger.info(f"Latest {limit_releases} releases retrieved successfully")
                self.logger.debug(f"Releases data: {releases}")
            return [release['tag_name'] for release in releases[:limit_releases]]
        except Exception as e:
            self.logger.error(f"Failed to retrieve latest releases: {e}")
            return []

    async def fetch_contributors(self, session: aiohttp.ClientSession) -> int:
        """
        Fetches contributors from github and include anonymous contributors
        """
        url = f"https://api.github.com/repos/{self.repo_name}/contributors"
        contributors = []
        try:
            while True:
                async with session.get(url, params={'anon': 'true'}) as response:
                    response.raise_for_status()
                    contributors.extend(await response.json())
                    if 'next' in response.links.keys():
                        url = response.links['next']['url']
                    else:
                        break
            self.logger.info(f"Contributors retrieved successfully")
            self.logger.debug(f"Contributors data: {contributors}")
        except Exception as e:
            self.logger.error(f"Failed to retrieve contributors: {e}")
        return contributors

    async def fetch_pulls(self, session: aiohttp.ClientSession, params=None) -> int:
        if params is None:
            params = {"state": "all"}
        url = f"https://api.github.com/repos/{self.repo_name}/pulls"
        pulls = []
        try:
            while True:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    pulls.extend(await response.json())
                    if 'next' in response.links.keys():
                        url = response.links['next']['url']
                    else:
                        break
            self.logger.info(f"Contributors retrieved successfully")
            self.logger.debug(f"Contributors data: {pulls}")
        except Exception as e:
            self.logger.error(f"Failed to retrieve contributors: {e}")
        return pulls

    @staticmethod
    def process_contributors(pulls):
        contributors = {}
        for pull in pulls:
            user = pull['user']['login']
            if contributors.get(user, None) is None:
                contributors[user] = 1
            else:
                contributors[user] += 1
        return sorted(contributors.items(), key=lambda usr: usr[1], reverse=True)

    def get_commits_of_pull(self, pull_number):
        url = f"{self.base_url}/repos/{self.repo_name}/pulls/{pull_number}/commits"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"GitHub API request failed with status code {response.status_code}")
        return response.json()
