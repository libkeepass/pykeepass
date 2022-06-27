<!-- markdownlint-disable -->

<a href="../pykeepass/baseelement.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `baseelement`






---

<a href="../pykeepass/baseelement.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BaseElement`
Entry and Group inherit from this class 

<a href="../pykeepass/baseelement.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(element, kp=None, icon=None, expires=False, expiry_time=None)
```






---

#### <kbd>property</kbd> atime





---

#### <kbd>property</kbd> ctime





---

#### <kbd>property</kbd> expired





---

#### <kbd>property</kbd> expires





---

#### <kbd>property</kbd> expiry_time





---

#### <kbd>property</kbd> group





---

#### <kbd>property</kbd> icon





---

#### <kbd>property</kbd> mtime





---

#### <kbd>property</kbd> parentgroup





---

#### <kbd>property</kbd> uuid

Returns uuid of this element as a uuid.UUID object 



---

<a href="../pykeepass/baseelement.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete`

```python
delete()
```





---

<a href="../pykeepass/baseelement.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `dump_xml`

```python
dump_xml(pretty_print=False)
```





---

<a href="../pykeepass/baseelement.py#L175"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `touch`

```python
touch(modify=False)
```

Update last access time of an entry/group 



**Args:**
 
 - <b>`modify`</b> (bool):  update access time as well a modification time 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
