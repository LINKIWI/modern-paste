"""
This script creates and drops all tables in the current database, as specified by config.BUILD_ENVIRONMENT.
"""

import sys
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', help='Create the database and all tables', action='store_true')
    parser.add_argument('--drop', help='Drop the database and all tables', action='store_true')
    args = parser.parse_args()

    from modern_paste import db
    if args.create and args.drop:
        print 'Requested action ambiguous; exiting'
        sys.exit(1)
    elif args.create:
        print 'Creating database and all tables'
        db.create_all()
    elif args.drop:
        print 'Dropping database and all tables'
        db.drop_all()
    else:
        print 'Call this script with either the --create or --drop flag to create or drop the database, respectively'
        sys.exit(1)
