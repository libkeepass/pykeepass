from __future__ import unicode_literals
from __future__ import absolute_import
import pykeepass.xmlfactory as xmlfactory
import lxml
from datetime import datetime, timedelta
import base64
import dateutil


class BaseElement(object):

    def __init__(self, element=None, version=None, expires=None,
                 expiry_time=None):
        self._element = element
        self._version = version
        self._element.append(xmlfactory.create_uuid_element())
        self._element.append(xmlfactory.create_times_element(expires, expiry_time))

    def _get_subelement_text(self, tag):
        v = self._element.find(tag)
        if v is not None:
            return v.text

    def _set_subelement_text(self, tag, value):
        v = self._element.find(tag)
        if v is not None:
            self._element.remove(v)
        el = xmlfactory.create_element(tag, value)
        self._element.append(el)

    def dump_xml(self, pretty_print=False):
        return lxml.etree.tostring(self._element, pretty_print=pretty_print)

    @property
    def uuid(self):
        return self._get_subelement_text('UUID')

    @uuid.setter
    def uuid(self, value):
        # Ignore the provided value to avoid an uuid collision
        return self._set_subelement_text('UUID', xmlfactory._generate_uuid())

    @property
    def icon(self):
        return self._get_subelement_text('IconID')

    @icon.setter
    def icon(self, value):
        return self._set_subelement_text('IconID', value)


    @property
    def _path(self):
        return self._element.getroottree().getpath(self._element)


    def _get_times_property(self, prop):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                if self._version >= (4, 0):
                    # decode KDBX4 date from b64 format
                    # try:
                    return (
                        datetime(year=1, month=1, day=1) +
                        timedelta(
                            seconds=int.from_bytes(
                                base64.b64decode(prop.text), 'little'
                            )
                        )
                    )
                    # except BinasciiError:
                    #     return dateutil.parser.parse(
                    #         prop.text,
                    #         tzinfos={'UTC':dateutil.tz.gettz('UTC')}
                    #     )
                else:
                    return dateutil.parser.parse(
                        prop.text,
                        tzinfos={'UTC':dateutil.tz.gettz('UTC')}
                    )

    def _set_times_property(self, prop, value):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                if self._version >= (4, 0):
                    # encode KDBX4 date to b64 format
                    diff_seconds = (
                        xmlfactory.datetime_to_utc(value).isoformat() -
                        datetime(year=1, month=1, day=1)
                    ).total_seconds()
                    prop.text = base64.b64encode(
                        struct.pack('<Q', diff_seconds),
                        'big'
                    )
                else:
                    prop.text = xmlfactory.datetime_to_utc(value).isoformat()

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
