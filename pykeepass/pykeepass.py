#!/usr/bin/env python
# coding: utf-8


from __future__ import print_function
from __future__ import unicode_literals
from copy import deepcopy
from datetime import datetime
from lxml.etree import Element
import base64
import logging
import os
import uuid


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def dump_to_file(kdb, outfile):
    '''
    Dump the content of the database to a file
    NOTE The file is unencrypted!
    '''
    with open(outfile, 'w+') as f:
        f.write(kdb.pretty_print())


def __xpath(tree, xpath_str, first_match_only=True):
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


def find_group_by_path(etree, group_path_str=None):
    xp = '/KeePassFile/Root/Group'
    # if group_path_str is not set, assume we look for root dir
    if group_path_str:
        for s in group_path_str.split('/'):
            xp += '/Group/Name[text()="{}"]/..'.format(s)
    return __xpath(etree, xp)


def get_root_group(etree):
    return find_group_by_path(etree)


def find_group_by_name(etree, group_name):
    '''
    '''
    return __xpath(etree, '//Group/Name[text()="{}"]/..'.format(group_name))


def find_group(etree, group_name):
    gname = os.path.dirname(group_name) if group_name.contains('/') else group_name
    return find_group_by_name(gname)


def generate_unique_uuid(etree):
    uuids = [str(x) for x in etree.xpath('//UUID')]
    while True:
        rand_uuid = base64.b64encode(uuid.uuid1().bytes)
        if rand_uuid not in uuids:
            return rand_uuid


def get_uuid_element(etree):
    uuid_el = Element('UUID')
    uuid_el.text = generate_unique_uuid(etree)
    logger.info('New UUID: {}'.format(uuid_el.text))
    return uuid_el


def get_name_element(name):
    name_el = Element('Name')
    name_el.text = name
    return name_el


def get_tags_element(tags):
    tags_el = Element('Tags')
    if type(tags) is list:
        tags_el.text = ';'.join(tags)
    return tags_el


def __get_string_element(key, value):
    string_el = Element('String')
    key_el = Element('Key')
    key_el.text = key
    value_el = Element('Value')
    value_el.text = value
    string_el.append(key_el)
    string_el.append(value_el)
    return string_el

def get_title_element(title):
    return __get_string_element('Title', title)


def get_username_element(username):
    return __get_string_element('UserName', username)


def get_password_element(password):
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


def get_url_element(url):
    return __get_string_element('URL', url)


def get_notes_element(notes):
    return __get_string_element('Notes', notes)


def dateformat(time=None):
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    if not time:
        time = datetime.utcnow()
    else:
        # Convert local datetime to utc
        UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.now()
        time = time + UTC_OFFSET_TIMEDELTA
    return datetime.strftime(time, format=dformat)


def get_time_element(expires=False, expiry_time=None):
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


def create_group_path(etree, group_path):
    logger.info('Create group {}'.format(group_path))
    group = get_root_group(etree)
    path = ''
    for gn in group_path.split('/'):
        group = __create_group_at_path(etree, path.rstrip('/'), gn)
        path += gn + '/'
    return group


def __create_group_at_path(etree, group_path, group_name):
    logger.info(
        'Create group {} at {}'.format(
            group_name,
            group_path if group_path else 'root dir'
        )
    )
    parent_group = find_group_by_path(etree, group_path)
    if parent_group:
        group_el = Element('Group')
        name_el = get_name_element(group_name)
        uuid_el = get_uuid_element(etree)
        group_el.append(uuid_el)
        group_el.append(name_el)
        parent_group.append(group_el)
        return group_el
    else:
        logger.error('Could not find group at {}'.format(group_path))


def find_entry(etree, entry_name):
    xp = '//Entry/String/Key[text()="Title"]/../Value[text()="{}"]/../..'.format(
        entry_name
    )
    return __xpath(etree, xp)


def find_entries_by_username(etree, username):
    xp = '//Entry/String/Key[text()="Username"]/../Value[text()="{}"]/../..'.format(
        username
    )
    return __xpath(etree, xp, False)


def create_entry(etree, group, entry_name, entry_username, entry_password,
                 entry_notes=None, entry_url=None, entry_tags=None,
                 entry_expires=False, entry_expiration_date=None):
    entry_el = Element('Entry')
    title_el = get_title_element(entry_name)
    uuid_el = get_uuid_element(etree)
    username_el = get_username_element(entry_username)
    password_el = get_password_element(entry_password)
    times_el = get_time_element(entry_expires, entry_expiration_date)
    if entry_url:
        url_el = get_url_element(entry_url)
        entry_el.append(url_el)
    if entry_notes:
        notes_el = get_notes_element(entry_notes)
        entry_el.append(notes_el)
    if entry_tags:
        tags_el = get_tags_element(entry_tags)
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
    return __xpath(entry, 'String/Key[text()="{}"]/..'.format(key))


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
