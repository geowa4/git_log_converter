#!/usr/bin/env python3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

Base = declarative_base()


def convert_to_datetime(epoch, offset):
    from datetime import timezone, timedelta, datetime
    tz = timezone(timedelta(minutes=offset))
    return datetime.fromtimestamp(epoch, tz=tz)

class Patch(Base):
    __tablename__ = 'patches'

    commit_id = Column(
        String, ForeignKey('commits.commit_id'), primary_key=True
    )
    old_id = Column(String, primary_key=True)
    new_id = Column(String, primary_key=True)
    old_file_path = Column(String, primary_key=True)
    new_file_path = Column(String, primary_key=True)
    status = Column(String)
    similarity = Column(Integer)
    additions = Column(Integer)
    deletions = Column(Integer)

    @staticmethod
    def from_dict(patch_dict):
        return Patch(
            old_file_path=patch_dict['old_file_path'],
            new_file_path=patch_dict['new_file_path'],
            old_id=patch_dict['old_id'],
            new_id=patch_dict['new_id'],
            status=patch_dict['status'],
            similarity=patch_dict['similarity'],
            additions=patch_dict['additions'],
            deletions=patch_dict['deletions'],
        )


class Commit(Base):
    __tablename__ = 'commits'

    commit_id = Column(String, primary_key=True)
    patches = relationship('Patch')
    first_parent_id = Column(String, nullable=True, index=True)
    second_parent_id = Column(String, nullable=True, index=True)
    commit_type = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    author_email = Column(String, nullable=False)
    author_datetime = Column(DateTime(timezone=True), nullable=False)
    committer_name = Column(String, nullable=False)
    committer_email = Column(String, nullable=False)
    committer_datetime = Column(DateTime(timezone=True), nullable=False)
    message = Column(String, nullable=False)
    message_encoding = Column(String)
    commit_datetime = Column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def from_dict(commit_dict):
        parent_ids = commit_dict['parent_ids']
        return Commit(
            commit_id=commit_dict['id'],
            patches=[Patch.from_dict(p) for p in commit_dict['patches']],
            first_parent_id=parent_ids[0] if len(parent_ids) > 0 else None,
            second_parent_id=parent_ids[1] if len(parent_ids) > 1 else None,
            commit_type=commit_dict['type'],
            author_name=commit_dict['author_name'],
            author_email=commit_dict['author_email'],
            author_datetime=convert_to_datetime(
                commit_dict['author_time'],
                commit_dict['author_time_offset'],
            ),
            committer_name=commit_dict['committer_name'],
            committer_email=commit_dict['committer_email'],
            committer_datetime=convert_to_datetime(
                commit_dict['committer_time'],
                commit_dict['committer_time_offset'],
            ),
            message=commit_dict['message'],
            message_encoding=commit_dict['message_encoding'],
            commit_datetime=convert_to_datetime(
                commit_dict['commit_time'],
                commit_dict['commit_time_offset'],
            ),
        )

if __name__ == '__main__':
    import sys
    import argparse
    import json
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    parser = argparse.ArgumentParser(
        description="Write JSON Git log to a database.",
    )
    parser.add_argument(
        "-c", "--connection-string", required=True,
        help="The URI for the database.",
    )
    parser.add_argument(
        "file",
        help="The file to read the JSON; use '-' for STDIN.",
    )
    args = parser.parse_args()

    engine = create_engine(args.connection_string, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    if args.file == "-":
        input_file = sys.stdin
    else:
        input_file = open(args.file, 'r')
    with input_file as f:
        for line in f:
            commit_json = json.loads(str(line))
            commit = Commit.from_dict(commit_json)
            session.add(commit)
            session.commit()
