from __future__ import unicode_literals
from __future__ import absolute_import
from lxml import etree
from lxml.etree import Element
from lxml.builder import E
from datetime import datetime, timedelta
import base64
from dateutil import parser, tz
import uuid
import struct


class BaseElement(object):
    """Entry and Group inherit from this class"""

    def __init__(self, element=None, version=None, icon=None, expires=False,
                 expiry_time=None):

        self._element = element
        self._element.append(
            E.UUID(base64.b64encode(uuid.uuid1().bytes).decode('utf-8'))
        )
        if icon:
            self._element.append(E.IconID(icon))
        current_time_str = self._encode_time(datetime.utcnow())
        if expiry_time:
            expiry_time_str = self._encode_time(
                self._datetime_to_utc(expiry_time)
            )
        else:
            expiry_time_str = self._encode_time(datetime.utcnow())

        self._element.append(
            E.Times(
                E.CreationTime(current_time_str),
                E.LastModificationTime(current_time_str),
                E.LastAccessTime(current_time_str),
                E.ExpiryTime(expiry_time_str),
                E.Expires(str(expires if expires is not None else False)),
                E.UsageCount(str(0)),
                E.LocationChanged(current_time_str)
            )
        )

    def _get_subelement_text(self, tag):
        v = self._element.find(tag)
        if v is not None:
            return v.text

    def _set_subelement_text(self, tag, value):
        v = self._element.find(tag)
        if v is not None:
            self._element.remove(v)
        self._element.append(getattr(E, tag)(value))

    def dump_xml(self, pretty_print=False):
        return etree.tostring(self._element, pretty_print=pretty_print)

    @property
    def uuid(self):
        return self._get_subelement_text('UUID')

    @uuid.setter
    def uuid(self, value):
        return self._set_subelement_text('UUID', value)

    @property
    def icon(self):
        return self._get_subelement_text('IconID')

    @icon.setter
    def icon(self, value):
        return self._set_subelement_text('IconID', value)

    @property
    def _path(self):
        return self._element.getroottree().getpath(self._element)

    def _datetime_to_utc(self, dt):
        """Convert naive datetimes to UTC"""
        
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=tz.gettz())
        return dt.astimezone(tz.gettz('UTC'))

    def _encode_time(self, value):
        """Convert datetime to base64 or plaintext string"""

        if self._version >= (4, 0):
            diff_seconds = int(
                (value - datetime(year=1, month=1, day=1)).total_seconds()
            )
            return base64.b64encode(
                struct.pack('<Q', diff_seconds)
            ).decode('utf-8')
        else:
            return self._datetime_to_utc(value).isoformat()

    def _decode_time(self, text):
        """Convert base64 time or plaintext time to datetime"""

        if self._version >= (4, 0):
            # decode KDBX4 date from b64 format
            try:
                return (
                    datetime(year=1, month=1, day=1) +
                    timedelta(
                        seconds=int.from_bytes(
                            base64.b64decode(text), 'little'
                        )
                    )
                )
            except BinasciiError:
                return parser.parse(
                    text,
                    tzinfos={'UTC':tz.gettz('UTC')}
                )
        else:
            return parser.parse(
                text,
                tzinfos={'UTC':tz.gettz('UTC')}
            )


    def _get_times_property(self, prop):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                return self._decode_time(prop.text)

    def _set_times_property(self, prop, value):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                prop.text = self._encode_time(value)

    @property
    def expires(self):
        times = self._element.find('Times')
        d = times.find('Expires').text
        if d is not None:
            return d == 'True'

    @expires.setter
    def expires(self, value):
        d = self._element.find('Times').find('Expires')
        d.text = 'True' if value else 'False'

    @property
    def expired(self):
        return self.expires and (datetime.utcnow() > self.expiry_time)


    @property
    def expiry_time(self):
        return self._get_times_property('ExpiryTime')

    @expiry_time.setter
    def expiry_time(self, value):
        self._set_times_property('ExpiryTime', value)

    @property
    def ctime(self):
        return self._get_times_property('CreationTime')

    @ctime.setter
    def ctime(self, value):
        self._set_times_property('CreationTime', value)

    @property
    def atime(self):
        return self._get_times_property('LastAccessTime')

    @atime.setter
    def atime(self, value):
        self._set_times_property('LastAccessTime', value)

    @property
    def mtime(self):
        return self._get_times_property('LastModificationTime')

    @mtime.setter
    def mtime(self, value):
        self._set_times_property('LastModificationTime', value)

    def delete(self):
        self._element.getparent().remove(self._element)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
