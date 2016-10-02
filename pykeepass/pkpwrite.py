#!/usr/bin/env python
# coding: utf-8


from __future__ import print_function
from __future__ import unicode_literals
import argparse
import logging
import pykeepass


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--password',
        help='Password of the KDBX database',
        required=True
    )
    parser.add_argument(
        '-k', '--keyfile',
        help='Keyfile to unlock the KDBX database',
        required=False
    )
    parser.add_argument(
        '-d', '--database',
        # type=argparse.FileType('r'),
        help='Database (KDBX file)',
        required=True
    )
    parser.add_argument(
        '-o', '--outfile',
        # type=argparse.FileType('w'),
        help='File to write the updated database to',
        required=False
    )
    parser.add_argument(
        '-D', '--destination',
        help='Group where to write the new entry to',
        required=False
    )
    parser.add_argument(
        '-f', '--force',
        help='Force the creation of a new entry, even if there already is '\
            'one with the same title',
        action='store_true',
        default=False,
        required=False
    )
    parser.add_argument(
        '-e', '--entry',
        help='Name (title) of the new entry',
        required=True
    )
    parser.add_argument(
        '-U', '--entry-username',
        help='Username to put in the new entry',
        required=True
    )
    parser.add_argument(
        '-P', '--entry-password',
        help='Password to put in the new entry',
        required=True
    )
    parser.add_argument(
        '--entry-url',
        help='URL of the new entry',
        required=False
    )
    parser.add_argument(
        '-N', '--entry-notes',
        help='Notes for the new entry',
        required=False
    )
    parser.add_argument(
        '-T', '--entry-tags',
        help='Tags for the entry',
        action='append',
        required=False
    )
    return parser.parse_args()


def write_entry(kdbx_file, kdbx_password, group_destination_name,
                entry_name, entry_username, entry_password, entry_url,
                entry_notes, entry_tags, kdbx_keyfile=None,
                force_creation=False, outfile=None):
    logging.info(
        'Atempt to write entry "{}: {}:{}" to {}'.format(
            entry_name, entry_username, entry_password, group_destination_name
        )
    )
    with pykeepass.open(
        kdbx_file, password=kdbx_password, keyfile=kdbx_keyfile
    ) as kdb:
        et = kdb.tree
        destination_group = pykeepass.find_group_by_path(et, group_destination_name)
        if not destination_group:
            logging.info(
                'Could not find destination group {}. Create it.'.format(
                    group_destination_name
                )
            )
            destination_group = pykeepass.create_group_path(
                et, group_destination_name
            )
        e = pykeepass.find_entry(destination_group, entry_name)
        if e and not force_creation:
            logger.warning(
                'An entry {} already exists in {}. Update it.'.format(
                    entry_name, group_destination_name
                )
            )
            pykeepass.update_entry(
                e, entry_name, entry_username, entry_password,
                entry_url, entry_notes, entry_tags
            )
        else:
            pykeepass.create_entry(
                et, destination_group, entry_name, entry_username,
                entry_password, entry_notes, entry_url, entry_tags
            )
        outstream = open(
            kdbx_file if not outfile else outfile, 'w+'
        ).__enter__()
        kdb.write_to(outstream)
        logging.info('Wrote database to {}'.format(outstream.name))


def main():
    args = parse_args()
    write_entry(
        kdbx_file=args.database,
        kdbx_password=args.password,
        kdbx_keyfile=args.keyfile,
        outfile=args.outfile,
        group_destination_name=args.destination,
        force_creation=args.force,
        entry_name=args.entry,
        entry_username=args.entry_username,
        entry_password=args.entry_password,
        entry_url=args.entry_url,
        entry_notes=args.entry_notes,
        entry_tags=args.entry_tags,
    )


if __name__ == '__main__':
    main()
