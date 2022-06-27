<!-- markdownlint-disable -->

<a href="../pykeepass/pykeepass.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pykeepass`




**Global Variables**
---------------
- **baseelement**
- **group**: # FIXME python2

- **entry**: # FIXME python2

- **exceptions**: # ----- binary parsing exceptions -----

- **attachment**: # FIXME python2

- **kdbx_parsing**
- **xpath**: # FIXME python2

- **pykeepass**: # coding: utf-8

- **version**
- **kdf_uuids**
- **attachment_xp**
- **entry_xp**
- **group_xp**
- **path_xp**
- **BLANK_DATABASE_FILENAME**
- **BLANK_DATABASE_LOCATION**
- **BLANK_DATABASE_PASSWORD**

---

<a href="../pykeepass/pykeepass.py#L902"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_database`

```python
create_database(filename, password=None, keyfile=None, transformed_key=None)
```






---

<a href="../pykeepass/pykeepass.py#L916"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `debug_setup`

```python
debug_setup()
```

Convenience function to quickly enable debug messages 


---

<a href="../pykeepass/pykeepass.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PyKeePass`
Open a KeePass database 



**Args:**
 
 - <b>`filename`</b> (:obj:`str`, optional):  path to database or stream object.  If None, the path given when the database was opened is used. 
 - <b>`password`</b> (:obj:`str`, optional):  database password.  If None,  database is assumed to have no password 
 - <b>`keyfile`</b> (:obj:`str`, optional):  path to keyfile.  If None,  database is assumed to have no keyfile 
 - <b>`transformed_key`</b> (:obj:`bytes`, optional):  precomputed transformed  key. 



**Raises:**
 
 - <b>`CredentialsError`</b>:  raised when password/keyfile or transformed key  are wrong 
 - <b>`HeaderChecksumError`</b>:  raised when checksum in database header is  is wrong.  e.g. database tampering or file corruption 
 - <b>`PayloadChecksumError`</b>:  raised when payload blocks checksum is wrong,  e.g. corruption during database saving 



**Todo:**
 
    - raise, no filename provided, database not open 

<a href="../pykeepass/pykeepass.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(filename, password=None, keyfile=None, transformed_key=None)
```






---

#### <kbd>property</kbd> attachments





---

#### <kbd>property</kbd> binaries





---

#### <kbd>property</kbd> credchange_date





---

#### <kbd>property</kbd> credchange_recommended





---

#### <kbd>property</kbd> credchange_recommended_days

Days until password update should be recommended 

---

#### <kbd>property</kbd> credchange_required





---

#### <kbd>property</kbd> credchange_required_days

Days until password update should be required 

---

#### <kbd>property</kbd> encryption_algorithm

str: encryption algorithm used by database during decryption. Can be one of 'aes256', 'chacha20', or 'twofish'. 

---

#### <kbd>property</kbd> entries

:obj:`list` of :obj:`Entry`: list of all Entry objects in database, excluding history 

---

#### <kbd>property</kbd> groups

:obj:`list` of :obj:`Group`: list of all Group objects in database  



---

#### <kbd>property</kbd> kdf_algorithm

str: key derivation algorithm used by database during decryption. Can be one of 'aeskdf', 'argon2', or 'aeskdf' 

---

#### <kbd>property</kbd> keyfile





---

#### <kbd>property</kbd> password





---

#### <kbd>property</kbd> recyclebin_group

Group: RecycleBin Group of database 

---

#### <kbd>property</kbd> root_group

Group: root Group of database 

---

#### <kbd>property</kbd> transformed_key

bytes: transformed key used in database decryption.  May be cached and passed to `open` for faster database opening 

---

#### <kbd>property</kbd> tree

lxml.etree._ElementTree: database XML payload 

---

#### <kbd>property</kbd> version

tuple: Length 2 tuple of ints containing major and minor versions. Generally (3, 1) or (4, 0). 



---

<a href="../pykeepass/pykeepass.py#L701"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_binary`

```python
add_binary(data, compressed=True, protected=True)
```





---

<a href="../pykeepass/pykeepass.py#L615"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_entry`

```python
add_entry(
    destination_group,
    title,
    username,
    password,
    url=None,
    notes=None,
    expiry_time=None,
    tags=None,
    otp=None,
    icon=None,
    force_creation=False
)
```





---

<a href="../pykeepass/pykeepass.py#L444"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_group`

```python
add_group(destination_group, group_name, icon=None, notes=None)
```





---

<a href="../pykeepass/pykeepass.py#L738"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_binary`

```python
delete_binary(id)
```





---

<a href="../pykeepass/pykeepass.py#L652"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_entry`

```python
delete_entry(entry)
```





---

<a href="../pykeepass/pykeepass.py#L455"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_group`

```python
delete_group(group)
```





---

<a href="../pykeepass/pykeepass.py#L458"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deref`

```python
deref(value)
```





---

<a href="../pykeepass/pykeepass.py#L254"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `dump_xml`

```python
dump_xml(filename)
```

Dump the contents of the database to file as XML 



**Args:**
 
 - <b>`filename`</b> (str):  path to output file 

---

<a href="../pykeepass/pykeepass.py#L505"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty_group`

```python
empty_group(group)
```

Delete the content of a group. 

This does not delete the group itself 



**Args:**
 
 - <b>`group`</b> (:obj:`Group`):  Group to empty 

---

<a href="../pykeepass/pykeepass.py#L671"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_attachments`

```python
find_attachments(recursive=True, path=None, element=None, **kwargs)
```





---

<a href="../pykeepass/pykeepass.py#L520"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries`

```python
find_entries(recursive=True, path=None, group=None, **kwargs)
```





---

<a href="../pykeepass/pykeepass.py#L571"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_notes`

```python
find_entries_by_notes(
    notes,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L549"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_password`

```python
find_entries_by_password(
    password,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L582"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_path`

```python
find_entries_by_path(
    path,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L604"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_string`

```python
find_entries_by_string(
    string,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L527"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_title`

```python
find_entries_by_title(
    title,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L560"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_url`

```python
find_entries_by_url(
    url,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L538"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_username`

```python
find_entries_by_username(
    username,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L593"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_entries_by_uuid`

```python
find_entries_by_uuid(
    uuid,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L395"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_groups`

```python
find_groups(recursive=True, path=None, group=None, **kwargs)
```





---

<a href="../pykeepass/pykeepass.py#L401"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_groups_by_name`

```python
find_groups_by_name(
    group_name,
    regex=False,
    flags=None,
    group=None,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L432"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_groups_by_notes`

```python
find_groups_by_notes(
    notes,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L411"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_groups_by_path`

```python
find_groups_by_path(
    group_path_str=None,
    regex=False,
    flags=None,
    group=None,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L421"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_groups_by_uuid`

```python
find_groups_by_uuid(
    uuid,
    regex=False,
    flags=None,
    group=None,
    history=False,
    first=False
)
```





---

<a href="../pykeepass/pykeepass.py#L655"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `move_entry`

```python
move_entry(entry, destination_group)
```





---

<a href="../pykeepass/pykeepass.py#L481"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `move_group`

```python
move_group(group, destination_group)
```





---

<a href="../pykeepass/pykeepass.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `read`

```python
read(filename=None, password=None, keyfile=None, transformed_key=None)
```

See class docstring. 



**Todo:**
 
    - raise, no filename provided, database not open 

---

<a href="../pykeepass/pykeepass.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `reload`

```python
reload()
```

Reload current database using previous credentials  

---

<a href="../pykeepass/pykeepass.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save(filename=None, transformed_key=None)
```

Save current database object to disk. 



**Args:**
 
 - <b>`filename`</b> (:obj:`str`, optional):  path to database or stream object.  If None, the path given when the database was opened is used.  PyKeePass.filename is unchanged. 
 - <b>`transformed_key`</b> (:obj:`bytes`, optional):  precomputed transformed  key. 

---

<a href="../pykeepass/pykeepass.py#L658"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `trash_entry`

```python
trash_entry(entry)
```

Move an entry to the RecycleBin 



**Args:**
 
 - <b>`entry`</b> (:obj:`Entry`):  Entry to send to the RecycleBin 

---

<a href="../pykeepass/pykeepass.py#L494"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `trash_group`

```python
trash_group(group)
```

Move a group to the RecycleBin 



**Args:**
 
 - <b>`group`</b> (:obj:`Group`):  Group to send to the RecycleBin 

---

<a href="../pykeepass/pykeepass.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `xml`

```python
xml()
```

Get XML part of database as string 



**Returns:**
 
 - <b>`str`</b>:  XML payload section of database. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
