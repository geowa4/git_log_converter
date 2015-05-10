#!/usr/bin/env python

import json
import sys
from pygit2 import Repository, GIT_SORT_TOPOLOGICAL


class GitLogConverter(object):
    def __init__(self, path):
        self.repo = Repository('%s/.git' % path)

    def get_commits(self):
        return self.repo.walk(
            self.repo.head.target,
            GIT_SORT_TOPOLOGICAL
        )

    def commits_as_dicts(self):
        return (self.commit_to_dict(commit) for commit in self.get_commits())

    def commit_to_dict(self, commit):
        commit_dict = {
            "id": str(commit.id),
            "type": commit.type,
            "author_name": commit.author.name,
            "author_email": commit.author.email,
            "author_time": commit.author.time,
            "author_time_offset": commit.author.offset,
            "committer_name": commit.committer.name,
            "committer_email": commit.committer.email,
            "committer_time": commit.committer.time,
            "committer_time_offset": commit.committer.offset,
            "message": commit.message,
            "message_encoding": commit.message_encoding,
            "patches": [],
            "parent_ids": [str(id) for id in commit.parent_ids],
            "commit_time": commit.commit_time,
            "commit_time_offset": commit.commit_time_offset,
        }
        patches = commit_dict["patches"]
        diffs = [
            commit.tree.diff_to_tree(parent.tree)
            for parent in commit.parents
        ]
        merged_diff = None
        for diff in diffs:
            if merged_diff is None:
                merged_diff = diff
            else:
                merged_diff.merge(diff)
        if merged_diff is not None:
            for patch in merged_diff:
                patch_dict = {
                    "old_file_path": patch.old_file_path,
                    "new_file_path": patch.new_file_path,
                    "old_id": str(patch.old_id),
                    "new_id": str(patch.new_id),
                    "status": patch.status,
                    "similarity": patch.similarity,
                    "additions": patch.additions,
                    "deletions": patch.deletions,
                }
                patches.append(patch_dict)
        return commit_dict

    def print_commits_as_json(self, file=sys.stdout):
        try:
            for commit_dict in self.commits_as_dicts():
                print(json.dumps(commit_dict), file=file, flush=True)
        except (BrokenPipeError, KeyboardInterrupt):
            pass

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a Git log to lines of JSON.",
    )
    parser.add_argument(
        "--repo", required=True,
        help="The path to the Git repository.",
    )
    parser.add_argument(
        "file",
        help="The file to print the JSON; use '-' for STDOUT.",
    )
    args = parser.parse_args()

    if args.file == "-":
        output = sys.stdout
    else:
        output = open(args.file, mode='w')

    converter = GitLogConverter(args.repo)
    converter.print_commits_as_json(output)
    sys.stderr.close()
