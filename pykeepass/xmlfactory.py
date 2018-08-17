from datetime import datetime
import dateutil.parser, dateutil.tz as tz
from lxml.etree import Element
import base64
import uuid


def create_element(tag, value):
    element = Element(tag)
    element.text = value
    return element


def create_name_element(name):
    name_el = Element('Name')
    name_el.text = name
    return name_el


def create_icon_element(icon):
    icon_el = Element('IconID')
    icon_el.text = str(icon)
    return icon_el


def create_customicon_element(customicon):
    customicon_el = Element('CustomIconUUID')
    customicon_el.text = str(customicon)
    return customicon_el


def create_tags_element(tags):
    tags_el = Element('Tags')
    str_tags = ';'.join(tags) if type(tags) is list else tags
    tags_el.text = str_tags
    return tags_el


def create_username_element(username):
    return _create_string_element('UserName', username)


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
    return _create_string_element('URL', url)


def create_notes_element(notes):
    return _create_string_element('Notes', notes)


def create_times_element(expires=False, expiry_time=None):
    now_str = datetime.utcnow().isoformat()
    if expiry_time:
        # add timezone info if it doesnt exist
        expiry_time_str = datetime_to_utc(expiry_time).isoformat()
    else:
        expiry_time_str = datetime.utcnow().isoformat()

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
    expires_el.text = str(expires) if expires is not None else None
    usage_count_el.text = str(0)

    times_el.append(ctime_el)
    times_el.append(mtime_el)
    times_el.append(atime_el)
    times_el.append(etime_el)
    times_el.append(expires_el)
    times_el.append(location_changed_el)

    return times_el


def _generate_uuid():
    # FIXME
    return base64.b64encode(uuid.uuid1().bytes)
    # uuids = [str(x) for x in tree.xpath('//UUID')]
    # while True:
    #     rand_uuid = base64.b64encode(uuid.uuid1().bytes)
    #     if rand_uuid not in uuids:
    #         return rand_uuid


def create_uuid_element():
    uuid_el = Element('UUID')
    uuid_el.text = _generate_uuid()
    # logger.info('New UUID: {}'.format(uuid_el.text))
    return uuid_el


def create_title_element(title):
    return _create_string_element('Title', title)


def _create_string_element(key, value):
    string = Element('String')
    key_el = Element('Key')
    key_el.text = key
    value_el = Element('Value')
    value_el.text = value
    string.append(key_el)
    string.append(value_el)
    return string

# convert naive datetimes to utc
# use current timezone if timezone not set
def datetime_to_utc(dt):
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=tz.gettz())
    return dt.astimezone(tz.gettz('UTC'))
