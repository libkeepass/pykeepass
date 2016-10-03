#!/usr/bin/env python
# coding: utf-8


from __future__ import print_function
from __future__ import unicode_literals
from copy import deepcopy
from datetime import datetime
from lxml.etree import Element
import base64
import libkeepass
import logging
import os
import uuid


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# KeePass DB
kdb = None
kdb_filename = None


def read(filename, password=None, keyfile=None):
    global kdb
    global kdb_filename
    logger.info('Open file {}'.format(filename))
    kdb_filename = filename
    kdb = libkeepass.open(
        filename, password=password, keyfile=keyfile
    ).__enter__()
    return kdb


def save(filename=None):
    if not filename:
        filename = kdb_filename
    outfile = open(filename, 'w+').__enter__()
    kdb.write_to(outfile)
    return outfile


def dump_xml(outfile):
    '''
    Dump the content of the database to a file
    NOTE The file is unencrypted!
    '''
    with open(outfile, 'w+') as f:
        f.write(kdb.pretty_print())


def __xpath(xpath_str, first_match_only=True, tree=None):
    if not tree:
        tree = kdb.tree
    result = tree.xpath(xpath_str)
    if first_match_only:
        # FIXME This raises a FutureWarning:
        # kpwrite.py:217: FutureWarning: The behavior of this method will change in
        # future versions. Use specific 'len(elem)' or 'elem is not None' test
        # instead.
        if len(result) > 0:
            return result[0]
    else:
        return result


def find_group_by_path(group_path_str=None, tree=None):
    if not tree:
        tree = kdb.tree
    xp = '/KeePassFile/Root/Group'
    # if group_path_str is not set, assume we look for root dir
    if group_path_str:
        for s in group_path_str.split('/'):
            xp += '/Group/Name[text()="{}"]/..'.format(s)
    return __xpath(xp, tree=tree)


def get_root_group(tree=None):
    return find_group_by_path(tree=tree)


def find_group_by_name(group_name, tree=None):
    '''
    '''
    return __xpath(tree, '//Group/Name[text()="{}"]/..'.format(group_name))


def find_group(group_name, tree=None):
    gname = os.path.dirname(group_name) if group_name.contains('/') else group_name
    return find_group_by_name(gname)


def __generate_uuid(tree=None):
    if not tree:
        tree = kdb.tree
    uuids = [str(x) for x in tree.xpath('//UUID')]
    while True:
        rand_uuid = base64.b64encode(uuid.uuid1().bytes)
        if rand_uuid not in uuids:
            return rand_uuid


def create_uuid_element(tree=None):
    uuid_el = Element('UUID')
    uuid_el.text = __generate_uuid(tree)
    logger.info('New UUID: {}'.format(uuid_el.text))
    return uuid_el


def create_name_element(name):
    name_el = Element('Name')
    name_el.text = name
    return name_el


def create_tags_element(tags):
    tags_el = Element('Tags')
    if type(tags) is list:
        tags_el.text = ';'.join(tags)
    return tags_el


def __create_string_element(key, value):
    string_el = Element('String')
    key_el = Element('Key')
    key_el.text = key
    value_el = Element('Value')
    value_el.text = value
    string_el.append(key_el)
    string_el.append(value_el)
    return string_el


def create_title_element(title):
    return __create_string_element('Title', title)


def create_username_element(username):
    return __create_string_element('UserName', username)


def create_password_element(password):
    string_el = Element('String')
    key_el = Element('Key')
    key_el.text = 'Password'
    value_el = Element('Value')
    value_el.text = password
    value_el.set('Protected', 'False')
    # TODO FIXME
    value_el.set('ProtectedValue', '???')
    string_el.append(key_el)
    string_el.append(value_el)
    return string_el


def create_url_element(url):
    return __create_string_element('URL', url)


def create_notes_element(notes):
    return __create_string_element('Notes', notes)


def dateformat(time=None):
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    if not time:
        time = datetime.utcnow()
    else:
        # Convert local datetime to utc
        UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.now()
        time = time + UTC_OFFSET_TIMEDELTA
    return datetime.strftime(time, format=dformat)


def create_time_element(expires=False, expiry_time=None):
    now_str = dateformat()
    expiry_time_str = dateformat(expiry_time)

    times_el = Element('Times')
    ctime_el = Element('CreationTime')
    mtime_el = Element('LastModificationTime')
    atime_el = Element('LastAccessTime')
    etime_el = Element('ExpiryTime')
    expires_el = Element('Expires')
    usage_count_el = Element('UsageCount')
    location_changed_el = Element('LocationChanged')

    ctime_el.text = now_str
    atime_el.text = now_str
    mtime_el.text = now_str
    etime_el.text = expiry_time_str
    location_changed_el.text = now_str
    expires_el.text = str(expires)
    usage_count_el.text = str(0)

    times_el.append(ctime_el)
    times_el.append(mtime_el)
    times_el.append(atime_el)
    times_el.append(etime_el)
    times_el.append(expires_el)
    times_el.append(location_changed_el)

    return times_el


def create_group_path(group_path, tree):
    logger.info('Create group {}'.format(group_path))
    group = get_root_group(tree)
    path = ''
    for gn in group_path.split('/'):
        group = __create_group_at_path(tree, path.rstrip('/'), gn)
        path += gn + '/'
    return group


def __create_group_at_path(tree, group_path, group_name):
    logger.info(
        'Create group {} at {}'.format(
            group_name,
            group_path if group_path else 'root dir'
        )
    )
    parent_group = find_group_by_path(group_path, tree)
    if parent_group:
        group_el = Element('Group')
        name_el = create_name_element(group_name)
        uuid_el = create_uuid_element(tree)
        group_el.append(uuid_el)
        group_el.append(name_el)
        parent_group.append(group_el)
        return group_el
    else:
        logger.error('Could not find group at {}'.format(group_path))


def find_entry(tree, entry_name):
    xp = '//Entry/String/Key[text()="Title"]/../Value[text()="{}"]/../..'.format(
        entry_name
    )
    return __xpath(xp, tree=tree)


def find_entries_by_username(tree, username):
    xp = '//Entry/String/Key[text()="Username"]/../Value[text()="{}"]/../..'.format(
        username
    )
    return __xpath(tree, xp, False)


def create_entry(group, entry_title, entry_username, entry_password,
                 entry_notes=None, entry_url=None, entry_tags=None,
                 entry_expires=False, entry_expiration_date=None, tree=None):
    if not tree:
        tree = kdb.tree
    entry_el = Element('Entry')
    title_el = create_title_element(entry_title)
    uuid_el = create_uuid_element(tree)
    username_el = create_username_element(entry_username)
    password_el = create_password_element(entry_password)
    times_el = create_time_element(entry_expires, entry_expiration_date)
    if entry_url:
        url_el = create_url_element(entry_url)
        entry_el.append(url_el)
    if entry_notes:
        notes_el = create_notes_element(entry_notes)
        entry_el.append(notes_el)
    if entry_tags:
        tags_el = create_tags_element(entry_tags)
        entry_el.append(tags_el)
    entry_el.append(title_el)
    entry_el.append(uuid_el)
    entry_el.append(username_el)
    entry_el.append(password_el)
    entry_el.append(times_el)
    group.append(entry_el)
    return entry_el


def touch_entry(entry):
    '''
    Update last access time of an entry
    '''
    entry.Times.LastAccessTime = dateformat()


def __get_entry_string_field(entry, key):
    return __xpath(tree=entry, xpath_str='String/Key[text()="{}"]/..'.format(key))


def get_entry_title_field(entry):
    return __get_entry_string_field(entry, 'Title')


def get_entry_password_field(entry):
    return __get_entry_string_field(entry, 'Password')


def get_entry_username_field(entry):
    return __get_entry_string_field(entry, 'UserName')


def get_entry_notes_field(entry):
    return __get_entry_string_field(entry, 'Notes')


def get_entry_url_field(entry):
    return __get_entry_string_field(entry, 'URL')


def archive_entry(entry):
    '''
    Save the entry in its history
    '''
    archive = deepcopy(entry)
    if getattr(entry, 'History'):
        archive.remove(archive.History)
        entry.History.append(archive)
    else:
        history = Element('History')
        history.append(archive)
        entry.append(history)


def update_entry(entry, entry_title=None, entry_username=None,
                 entry_password=None, entry_url=None, entry_notes=None,
                 entry_tags=None,
                 entry_expires=None, entry_expiration_date=None):
    archive_entry(entry)
    if entry_title:
        get_entry_title_field(entry).Value = entry_title
    if entry_username:
        get_entry_username_field(entry).Value = entry_username
    if entry_password:
        get_entry_password_field(entry).Value = entry_password
    if entry_url:
        get_entry_url_field(entry).Value = entry_url
    if entry_notes:
        get_entry_notes_field(entry).Value = entry_notes
    if entry_expires is not None:
        entry.Times.Expires = str(entry_expires)
    if entry_expiration_date:
        entry.Times.ExpiryTime = entry_expiration_date
    if entry_tags:
        entry.Tags = ';'.join(entry_tags)
    entry.Times.LastModificationTime = dateformat()


def add_entry(group_path, entry_title, entry_username,
              entry_password, entry_url=None, entry_notes=None,
              entry_tags=None, force_creation=False):
    destination_group = find_group_by_path(group_path)
    if not destination_group:
        logging.info(
            'Could not find destination group {}. Create it.'.format(
                group_path
            )
        )
        destination_group = create_group_path(group_path)
    e = find_entry(destination_group, entry_title)
    if e and not force_creation:
        logger.warning(
            'An entry {} already exists in {}. Update it.'.format(
                entry_title, group_path
            )
        )
        update_entry(
            e,
            entry_title=entry_title,
            entry_username=entry_username,
            entry_password=entry_password,
            entry_url=entry_url,
            entry_notes=entry_notes,
            entry_tags=entry_tags
        )
    else:
        create_entry(
            destination_group,
            entry_title=entry_title,
            entry_username=entry_username,
            entry_password=entry_password,
            entry_notes=entry_notes,
            entry_url=entry_url,
            entry_tags=entry_tags
        )
