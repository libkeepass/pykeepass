<!-- markdownlint-disable -->

<a href="../pykeepass/entry.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `entry`




**Global Variables**
---------------
- **reserved_keys**


---

<a href="../pykeepass/entry.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Entry`




<a href="../pykeepass/entry.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    title=None,
    username=None,
    password=None,
    url=None,
    notes=None,
    otp=None,
    tags=None,
    expires=False,
    expiry_time=None,
    icon=None,
    autotype_sequence=None,
    autotype_enabled=True,
    element=None,
    kp=None
)
```






---

#### <kbd>property</kbd> atime





---

#### <kbd>property</kbd> attachments





---

#### <kbd>property</kbd> autotype_enabled





---

#### <kbd>property</kbd> autotype_sequence





---

#### <kbd>property</kbd> ctime





---

#### <kbd>property</kbd> custom_properties





---

#### <kbd>property</kbd> expired





---

#### <kbd>property</kbd> expires





---

#### <kbd>property</kbd> expiry_time





---

#### <kbd>property</kbd> group





---

#### <kbd>property</kbd> history





---

#### <kbd>property</kbd> icon





---

#### <kbd>property</kbd> is_a_history_entry





---

#### <kbd>property</kbd> mtime





---

#### <kbd>property</kbd> notes





---

#### <kbd>property</kbd> otp





---

#### <kbd>property</kbd> parentgroup





---

#### <kbd>property</kbd> password





---

#### <kbd>property</kbd> path

Path to element as list.  List contains all parent group names ending with entry title.  List may contain strings or NoneTypes. 

---

#### <kbd>property</kbd> tags





---

#### <kbd>property</kbd> title





---

#### <kbd>property</kbd> url





---

#### <kbd>property</kbd> username





---

#### <kbd>property</kbd> uuid

Returns uuid of this element as a uuid.UUID object 



---

<a href="../pykeepass/entry.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_attachment`

```python
add_attachment(id, filename)
```





---

<a href="../pykeepass/entry.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_attachment`

```python
delete_attachment(attachment)
```





---

<a href="../pykeepass/entry.py#L259"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_custom_property`

```python
delete_custom_property(key)
```





---

<a href="../pykeepass/entry.py#L301"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_history`

```python
delete_history(history_entry=None, all=False)
```

Delete entries from history 



**Args:**
 
 - <b>`history_entry`</b> (Entry):  history item to delete 
 - <b>`all`</b> (bool):  delete all entries from history.  Default is False 

---

<a href="../pykeepass/entry.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deref`

```python
deref(attribute)
```





---

<a href="../pykeepass/entry.py#L255"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_custom_property`

```python
get_custom_property(key)
```





---

<a href="../pykeepass/entry.py#L275"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ref`

```python
ref(attribute)
```

Create reference to an attribute of this element. 

---

<a href="../pykeepass/entry.py#L287"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_history`

```python
save_history()
```

Save the entry in its history 

---

<a href="../pykeepass/entry.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_custom_property`

```python
set_custom_property(key, value)
```






---

<a href="../pykeepass/entry.py#L321"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HistoryEntry`




<a href="../pykeepass/entry.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    title=None,
    username=None,
    password=None,
    url=None,
    notes=None,
    otp=None,
    tags=None,
    expires=False,
    expiry_time=None,
    icon=None,
    autotype_sequence=None,
    autotype_enabled=True,
    element=None,
    kp=None
)
```






---

#### <kbd>property</kbd> atime





---

#### <kbd>property</kbd> attachments





---

#### <kbd>property</kbd> autotype_enabled





---

#### <kbd>property</kbd> autotype_sequence





---

#### <kbd>property</kbd> ctime





---

#### <kbd>property</kbd> custom_properties





---

#### <kbd>property</kbd> expired





---

#### <kbd>property</kbd> expires





---

#### <kbd>property</kbd> expiry_time





---

#### <kbd>property</kbd> group





---

#### <kbd>property</kbd> history





---

#### <kbd>property</kbd> icon





---

#### <kbd>property</kbd> is_a_history_entry





---

#### <kbd>property</kbd> mtime





---

#### <kbd>property</kbd> notes





---

#### <kbd>property</kbd> otp





---

#### <kbd>property</kbd> parentgroup





---

#### <kbd>property</kbd> password





---

#### <kbd>property</kbd> path

Path to element as list.  List contains all parent group names ending with entry title.  List may contain strings or NoneTypes. 

---

#### <kbd>property</kbd> tags





---

#### <kbd>property</kbd> title





---

#### <kbd>property</kbd> url





---

#### <kbd>property</kbd> username





---

#### <kbd>property</kbd> uuid

Returns uuid of this element as a uuid.UUID object 



---

<a href="../pykeepass/entry.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_attachment`

```python
add_attachment(id, filename)
```





---

<a href="../pykeepass/entry.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_attachment`

```python
delete_attachment(attachment)
```





---

<a href="../pykeepass/entry.py#L259"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_custom_property`

```python
delete_custom_property(key)
```





---

<a href="../pykeepass/entry.py#L301"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_history`

```python
delete_history(history_entry=None, all=False)
```

Delete entries from history 



**Args:**
 
 - <b>`history_entry`</b> (Entry):  history item to delete 
 - <b>`all`</b> (bool):  delete all entries from history.  Default is False 

---

<a href="../pykeepass/entry.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deref`

```python
deref(attribute)
```





---

<a href="../pykeepass/entry.py#L255"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_custom_property`

```python
get_custom_property(key)
```





---

<a href="../pykeepass/entry.py#L275"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ref`

```python
ref(attribute)
```

Create reference to an attribute of this element. 

---

<a href="../pykeepass/entry.py#L287"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_history`

```python
save_history()
```

Save the entry in its history 

---

<a href="../pykeepass/entry.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_custom_property`

```python
set_custom_property(key, value)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
