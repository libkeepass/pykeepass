from datetime import datetime
from lxml.etree import Element
import base64
import uuid


def __generate_uuid(self, tree=None):
    if not tree:
        tree = self.kdb.tree
    uuids = [str(x) for x in tree.xpath('//UUID')]
    while True:
        rand_uuid = base64.b64encode(uuid.uuid1().bytes)
        if rand_uuid not in uuids:
            return rand_uuid

def create_uuid_element(tree=None):
    uuid_el = Element('UUID')
    uuid_el.text = __generate_uuid(tree)
    # logger.info('New UUID: {}'.format(uuid_el.text))
    return uuid_el

def create_title_element(title):
    return __create_string_element('Title', title)


def __create_string_element(self, key, value):
    string_el = Element('String')
    key_el = Element('Key')
    key_el.text = key
    value_el = Element('Value')
    value_el.text = value
    string_el.append(key_el)
    string_el.append(value_el)
    return string_el


def __dateformat(self, time=None):
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    if not time:
        time = datetime.utcnow()
    else:
        # Convert local datetime to utc
        UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.now()
        time = time + UTC_OFFSET_TIMEDELTA
    return datetime.strftime(time, format=dformat)
