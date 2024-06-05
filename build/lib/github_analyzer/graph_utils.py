import pydot
from github_analyzer.github_utils import GitHubAnalyzer
import logging


class GraphGenerator:
    """
    Class to generate a graph of commits given a merged branch
    """
    def __init__(self, github_client: GitHubAnalyzer):
        self.api = github_client
        self.logger = logging.getLogger(__name__)

    def create_graph(self, branch, main_branch, pulls):
        dot = pydot.Dot(graph_type='digraph')
        for pull in pulls:
            if pull['head']['ref'] == branch and pull['base']['ref'] == main_branch:
                merge_commit_sha = pull['merge_commit_sha']
                merge_commit_msg = pull['body']
                commits = self.api.get_commits_of_pull(pull['number'])
                self._add_commits_to_graph(dot, commits,
                                           {'sha': merge_commit_sha[:7], 'message': merge_commit_msg[:50]})
                break
        dot.write(f'graph_{main_branch}_{branch}.dot')

    @staticmethod
    def _add_commits_to_graph(dot, commits, merge_commit):
        parent_node = None
        merge_commit_node = pydot.Node(merge_commit['sha'], label=f'Merge:\n'
                                                                  f'{merge_commit["sha"]}:{merge_commit["message"]}')
        dot.add_node(merge_commit_node)
        for commit in commits:
            sha = commit['sha'][:7]
            message = commit['commit']['message']
            node = pydot.Node(sha, label=f'{sha}: {message}')
            dot.add_node(node)
            for parent in commit['parents']:
                parent_sha = parent['sha'][:7]
                if parent_node is None:
                    parent_node = pydot.Node(parent_sha, label=f'{parent_sha}')
                    dot.add_edge(pydot.Edge(parent_node, merge_commit_node))
                edge = pydot.Edge(parent_sha, sha)
                dot.add_edge(edge)
        dot.add_edge(pydot.Edge(node, merge_commit_node))
