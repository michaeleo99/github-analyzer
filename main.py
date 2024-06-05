import argparse
from github_analyzer.logger_config import setup_logger
from github_analyzer.graph_utils import GraphGenerator
import asyncio, aiohttp
from github_analyzer.github_utils import GitHubAnalyzer
import logging


async def fetch_data(github_api: GitHubAnalyzer):
    """
    Fetches data from the GitHub API
    """
    async with aiohttp.ClientSession(headers=github_api.headers) as session:
        repo_data, releases, contributors, pulls = await asyncio.gather(
            github_api.fetch_repo(session),
            github_api.fetch_releases(session),
            github_api.fetch_contributors(session),
            github_api.fetch_pulls(session)
        )
        contributors_sorted_by_pr = github_api.process_contributors(
            pulls)
    return (repo_data, releases, repo_data['forks'],
            repo_data['stargazers_count'], contributors, pulls, contributors_sorted_by_pr)


if __name__ == "__main__":
    # parsing the args from the command line
    parser = argparse.ArgumentParser(description="GitHub Analyzer")
    parser.add_argument("--token", required=True, help="GitHub API token")
    parser.add_argument("--log_to_file", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    # setting up logger
    setup_logger(args.debug, args.log_to_file)
    logger = logging.getLogger(__name__)
    # creating an instance of the GitHubAnalyzer class
    github_client = GitHubAnalyzer(args.token, "CTFd/CTFd")
    logger.info("Starting GitHub Extractor")
    loop = asyncio.get_event_loop()
    (repo, releases, forks, stars,
     contributors, pulls, contributors_sorted_by_pr) = loop.run_until_complete(fetch_data(github_client))
    loop.close()
    logger.info(f"3 Latest Releases: {releases}")
    logger.info(f"Forks: {forks}")
    logger.info(f"Stars: {stars}")
    logger.info(f"Contributors: {len(contributors)}")
    logger.info(f"Pulls: {len(pulls)}")
    logger.info(f"Contributors per Pull Request: {contributors_sorted_by_pr}")
    # draw the graph
    graph_maker = GraphGenerator(github_client)
    graph_maker.create_graph("mark-3.7.1", "master", pulls)
    logger.info("GitHub Extractor Finished")
