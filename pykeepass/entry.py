import logging
from copy import deepcopy

from lxml.builder import E
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement

from . import attachment
from .baseelement import BaseElement

logger = logging.getLogger(__name__)
reserved_keys = [
    'Title',
    'UserName',
    'Password',
    'URL',
    'Tags',
    'IconID',
    'Times',
    'History',
    'Notes',
    'otp'
]

class Entry(BaseElement):

    def __init__(self, title=None, username=None, password=None, url=None,
                 notes=None, otp=None, tags=None, expires=False, expiry_time=None,
                 icon=None, autotype_sequence=None, autotype_enabled=True, autotype_window=None,
                 element=None, kp=None):

        self._kp = kp

        if element is None:
            super().__init__(
                element=Element('Entry'),
                kp=kp,
                expires=expires,
                expiry_time=expiry_time,
                icon=icon
            )
            self._element.append(E.String(E.Key('Title'), E.Value(title)))
            self._element.append(E.String(E.Key('UserName'), E.Value(username)))
            self._element.append(
                E.String(E.Key('Password'), E.Value(password, Protected="True"))
            )
            if url:
                self._element.append(E.String(E.Key('URL'), E.Value(url)))
            if notes:
                self._element.append(E.String(E.Key('Notes'), E.Value(notes)))
            if otp:
                self._element.append(
                    E.String(E.Key('otp'), E.Value(otp, Protected="True"))
                )
            if tags:
                self._element.append(
                    E.Tags(';'.join(tags) if isinstance(tags, list) else tags)
                )
            self._element.append(
                E.AutoType(
                    E.Enabled(str(autotype_enabled)),
                    E.DataTransferObfuscation('0'),
                    E.DefaultSequence(str(autotype_sequence) if autotype_sequence else ''),
                    E.Association(
                        E.Window(str(autotype_window) if autotype_window else ''),
                        E.KeystrokeSequence('')
                    )
                )
            )
            # FIXME: include custom_properties in constructor

        else:
            assert type(element) in [_Element, Element, ObjectifiedElement], \
                'The provided element is not an LXML Element, but a {}'.format(
                    type(element)
                )
            assert element.tag == 'Entry', 'The provided element is not an Entry '\
                'element, but a {}'.format(element.tag)
            self._element = element

    def _get_string_field(self, key):
        """Get a string field from an entry

        Args:
            key (str): name of field

        Returns:
            (str or None): field value
        """

        field = self._xpath('String/Key[text()="{}"]/../Value'.format(key), history=True, first=True)
        if field is not None:
            return field.text

    def _set_string_field(self, key, value, protected=None):
        """Create or overwrite a string field in an Entry

        Args:
            key (str): name of field
            value (str): value of field
            protected (bool or None): mark whether the field should be protected in memory
                in other tools.  If None, value is either copied from existing field or field
                is created with protected property unset.

        Note: pykeepass does not support memory protection
        """
        field = self._xpath('String/Key[text()="{}"]/..'.format(key), history=True, first=True)

        protected_str = None
        if protected is None:
            protected_field = self._xpath('String/Key[text()="{}"]/../Value'.format(key), first=True)
            if protected_field is not None:
                protected_str = protected_field.attrib.get("Protected")
        else:
            protected_str = str(protected)

        if field is not None:
            self._element.remove(field)

        if protected_str is None:
            self._element.append(E.String(E.Key(key), E.Value(value)))
        else:
            self._element.append(E.String(E.Key(key), E.Value(value, Protected=protected_str)))

    def _get_string_field_keys(self, exclude_reserved=False):
        results = [x.find('Key').text for x in self._element.findall('String')]
        if exclude_reserved:
            return [x for x in results if x not in reserved_keys]
        else:
            return results

    @property
    def index(self):
        """int: get index of a entry within a group"""
        group = self.group._element
        children = group.getchildren()
        first_index = self.group._first_entry
        index = children.index(self._element)
        return index - first_index

    def reindex(self, new_index):
        """Move entry to a new index within a group
        
        Args:
            new_index (int): new index for the entry starting at 0
        """
        group = self.group._element
        first_index = self.group._first_entry
        group.remove(self._element)
        group.insert(new_index+first_index, self._element)

    @property
    def attachments(self):
        return self._kp.find_attachments(
            element=self,
            filename='.*',
            regex=True,
            recursive=False
        )

    def add_attachment(self, id, filename):
        element = E.Binary(
            E.Key(filename),
            E.Value(Ref=str(id))
        )
        self._element.append(element)

        return attachment.Attachment(element=element, kp=self._kp)

    def delete_attachment(self, attachment):
        attachment.delete()

    def deref(self, attribute):
        return self._kp.deref(getattr(self, attribute))

    @property
    def title(self):
        """str: get or set entry title"""
        return self._get_string_field('Title')

    @title.setter
    def title(self, value):
        return self._set_string_field('Title', value)

    @property
    def username(self):
        """str: get or set entry username"""
        return self._get_string_field('UserName')

    @username.setter
    def username(self, value):
        return self._set_string_field('UserName', value)

    @property
    def password(self):
        """str: get or set entry password"""
        return self._get_string_field('Password')

    @password.setter
    def password(self, value):
        if self.password:
            return self._set_string_field('Password', value)
        else:
            return self._set_string_field('Password', value, True)

    @property
    def url(self):
        """str: get or set entry URL"""
        return self._get_string_field('URL')

    @url.setter
    def url(self, value):
        return self._set_string_field('URL', value)

    @property
    def notes(self):
        """str: get or set entry notes"""
        return self._get_string_field('Notes')

    @notes.setter
    def notes(self, value):
        return self._set_string_field('Notes', value)

    @property
    def icon(self):
        """str: get or set entry icon. See icons.py"""
        return self._get_subelement_text('IconID')

    @icon.setter
    def icon(self, value):
        return self._set_subelement_text('IconID', value)

    @property
    def tags(self):
        """str: get or set entry tags"""
        val = self._get_subelement_text('Tags')
        return val.replace(',', ';').split(';') if val else []

    @tags.setter
    def tags(self, value, sep=';'):
        # Accept both str or list
        v = sep.join(value if isinstance(value, list) else [value])
        return self._set_subelement_text('Tags', v)

    @property
    def otp(self):
        """str: get or set entry OTP text. (defacto standard)"""
        return self._get_string_field('otp')

    @otp.setter
    def otp(self, value):
        if self.otp:
            return self._set_string_field('otp', value)
        else:
            return self._set_string_field('otp', value, True)

    @property
    def history(self):
        """:obj:`list` of :obj:`HistoryEntry`: get entry history"""
        if self._element.find('History') is not None:
            return [HistoryEntry(element=x, kp=self._kp) for x in self._element.find('History').findall('Entry')]
        else:
            return []

    @history.setter
    def history(self, value):
        raise NotImplementedError()

    @property
    def autotype_enabled(self):
        """bool: get or set autotype enabled state.  Determines whether `autotype_sequence` should be used"""
        enabled = self._element.find('AutoType/Enabled')
        if enabled.text is not None:
            return enabled.text == 'True'

    @autotype_enabled.setter
    def autotype_enabled(self, value):
        enabled = self._element.find('AutoType/Enabled')
        if value is not None:
            enabled.text = str(value)
        else:
            enabled.text = None

    @property
    def autotype_sequence(self):
        """str: get or set [autotype string](https://keepass.info/help/base/autotype.html)"""
        sequence = self._element.find('AutoType/DefaultSequence')
        if sequence is None or sequence.text == '':
            return None
        return sequence.text

    @autotype_sequence.setter
    def autotype_sequence(self, value):
        self._element.find('AutoType/DefaultSequence').text = value

    @property
    def autotype_window(self):
        """str: get or set [autotype target window filter](https://keepass.info/help/base/autotype.html#autowindows)"""
        sequence = self._element.find('AutoType/Association/Window')
        if sequence is None or sequence.text == '':
            return None
        return sequence.text

    @autotype_window.setter
    def autotype_window(self, value):
        self._element.find('AutoType/Association/Window').text = value

    @property
    def is_a_history_entry(self):
        """bool: check if entry is History entry"""
        parent = self._element.getparent()
        if parent is not None:
            return parent.tag == 'History'
        return False

    @property
    def path(self):
        """Path to element as list.  List contains all parent group names
        ending with entry title.  List contains strings or NoneTypes."""

        # The root group is an orphan
        if self.parentgroup is None:
            return None
        p = self.parentgroup
        path = [self.title]
        while p is not None and not p.is_root_group:
            if p.name is not None:  # dont make the root group appear
                path.insert(0, p.name)
            p = p.parentgroup
        return path

    def set_custom_property(self, key, value, protect=False):
        assert key not in reserved_keys, '{} is a reserved key'.format(key)
        return self._set_string_field(key, value, protect)

    def get_custom_property(self, key):
        assert key not in reserved_keys, '{} is a reserved key'.format(key)
        return self._get_string_field(key)

    def delete_custom_property(self, key):
        if key not in self._get_string_field_keys(exclude_reserved=True):
            raise AttributeError('No such key: {}'.format(key))
        prop = self._xpath('String/Key[text()="{}"]/..'.format(key), first=True)
        if prop is None:
            raise AttributeError('Could not find property element')
        self._element.remove(prop)

    def is_custom_property_protected(self, key):
        """Whether a custom property is protected.

        Return False if the entry does not have a custom property with the
        specified key.

        Args:
            key (:obj:`str`): key of the custom property to check.

        Returns:
            bool: Whether the custom property is protected.

        """
        assert key not in reserved_keys, '{} is a reserved key'.format(key)
        return self._is_property_protected(key)

    def _is_property_protected(self, key):
        """Whether a property is protected."""
        field = self._xpath('String/Key[text()="{}"]/../Value'.format(key), first=True)
        if field is not None:
            return field.attrib.get("Protected", "False") == "True"
        return False

    @property
    def custom_properties(self):
        keys = self._get_string_field_keys(exclude_reserved=True)
        props = {}
        for k in keys:
            props[k] = self._get_string_field(k)
        return props

    def ref(self, attribute):
        """Create reference to an attribute of this element.

        Args:
            attribute (str): one of 'title', 'username', 'password', 'url', 'notes', or 'uuid'

        Returns:
            str: [field reference][fieldref] to this field of this entry

        [fieldref]: https://keepass.info/help/base/fieldrefs.html
        """
        attribute_to_field = {
            'title': 'T',
            'username': 'U',
            'password': 'P',
            'url': 'A',
            'notes': 'N',
            'uuid': 'I',
        }
        return '{{REF:{}@I:{}}}'.format(attribute_to_field[attribute], self.uuid.hex.upper())

    def save_history(self):
        '''
        Save the entry in its history.  History is not created unless this function is
        explicitly called.
        '''
        archive = deepcopy(self._element)
        hist = archive.find('History')
        if hist is not None:
            archive.remove(hist)
            self._element.find('History').append(archive)
        else:
            history = Element('History')
            history.append(archive)
            self._element.append(history)

    def delete_history(self, history_entry=None, all=False):
        """
        Delete entries from history

        Args:
            history_entry (Entry): history item to delete
            all (bool): delete all entries from history.  Default is False
        """

        if all:
            self._element.remove(self._element.find('History'))
        else:
            self._element.find('History').remove(history_entry._element)

    def __str__(self):
        # filter out NoneTypes and join into string
        pathstr = '/'.join('' if p is None else p for p in self.path)
        return 'Entry: "{} ({})"'.format(pathstr, self.username)


class HistoryEntry(Entry):

    def __str__(self):
        pathstr = super().__str__()
        return 'HistoryEntry: {}'.format(pathstr)

    def __hash__(self):
        # All history items share the same UUID with themselves and their
        # parent, so consider the mtime also
        return hash((self.uuid, self.mtime))
