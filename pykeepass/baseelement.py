import base64
import uuid
from datetime import datetime, timezone


from lxml import etree
from lxml.builder import E


class BaseElement:
    """Entry and Group inherit from this class"""

    def __init__(self, element, kp=None, icon=None, expires=False,
                 expiry_time=None):

        self._element = element
        self._element.append(
            E.UUID(base64.b64encode(uuid.uuid1().bytes).decode('utf-8'))
        )
        if icon:
            self._element.append(E.IconID(icon))
        current_time_str = self._kp._encode_time(datetime.now(timezone.utc))
        if expiry_time:
            expiry_time_str = self._kp._encode_time(expiry_time.astimezone(timezone.utc))
        else:
            expiry_time_str = current_time_str

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

    def _xpath(self, xpath, **kwargs):
        return self._kp._xpath(xpath, tree=self._element, **kwargs)

    def _get_subelement_text(self, tag):
        v = self._element.find(tag)
        if v is not None:
            return v.text

    def _set_subelement_text(self, tag, value):
        v = self._element.find(tag)
        if v is not None:
            self._element.remove(v)
        self._element.append(getattr(E, tag)(value))

    @property
    def group(self):
        return self._xpath(
            '(ancestor::Group)[last()]',
            first=True,
            cast=True
        )

    parentgroup = group

    def dump_xml(self, pretty_print=False):
        return etree.tostring(self._element, pretty_print=pretty_print)

    @property
    def uuid(self):
        """Returns uuid of this element as a uuid.UUID object"""
        b64_uuid = self._get_subelement_text('UUID')
        return uuid.UUID(bytes=base64.b64decode(b64_uuid))

    @uuid.setter
    def uuid(self, uuid):
        """Set element uuid. `uuid` is a uuid.UUID object"""
        b64_uuid = base64.b64encode(uuid.bytes).decode('utf-8')
        return self._set_subelement_text('UUID', b64_uuid)

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
            if prop is not None and prop.text is not None:
                return self._kp._decode_time(prop.text)

    def _set_times_property(self, prop, value):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                prop.text = self._kp._encode_time(value)

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
        if self.expires:
            return (
                datetime.now(timezone.utc) >
                self.expiry_time
            )

        return False

    @property
    def expiry_time(self):
        return self._get_times_property('ExpiryTime')

    @expiry_time.setter
    def expiry_time(self, value):
        self._set_times_property('ExpiryTime', value)

    @property
    def ctime(self):
        """(datetime.datetime): Creation time."""
        return self._get_times_property('CreationTime')

    @ctime.setter
    def ctime(self, value):
        self._set_times_property('CreationTime', value)

    @property
    def atime(self):
        """(datetime.datetime): Access time. Update with touch()"""
        return self._get_times_property('LastAccessTime')

    @atime.setter
    def atime(self, value):
        self._set_times_property('LastAccessTime', value)

    @property
    def mtime(self):
        """(datetime.datetime): Access time. Update with touch(modify=True)"""
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

    def __hash__(self):
        return hash((self.uuid,))

    def __eq__(self, other):
        if isinstance(other, BaseElement):
            return hash(self) == hash(other)
        return NotImplemented

    def touch(self, modify=False):
        """
        Update last access time of an entry/group

        Args:
            modify (bool): update access time as well a modification time
        """
        now = datetime.now(timezone.utc)
        self.atime = now
        if modify:
            self.mtime = now
