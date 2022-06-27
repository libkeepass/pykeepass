<!-- markdownlint-disable -->

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `kdbx_parsing.pytwofish`




**Global Variables**
---------------
- **block_size**
- **key_size**
- **WORD_BIGENDIAN**
- **tab_5b**
- **tab_ef**
- **ror4**
- **ashx**
- **qt0**
- **qt1**
- **qt2**
- **qt3**

---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `rotr32`

```python
rotr32(x, n)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `rotl32`

```python
rotl32(x, n)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `byteswap32`

```python
byteswap32(x)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `byte`

```python
byte(x, n)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `qp`

```python
qp(n, x)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L198"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `gen_qtab`

```python
gen_qtab(pkey)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L203"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `gen_mtab`

```python
gen_mtab(pkey)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L218"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `gen_mk_tab`

```python
gen_mk_tab(pkey, key)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `h_fun`

```python
h_fun(pkey, x, key)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L263"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `mds_rem`

```python
mds_rem(p0, p1)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `set_key`

```python
set_key(pkey, in_key, key_len)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L314"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `encrypt`

```python
encrypt(pkey, in_blk)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L354"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `decrypt`

```python
decrypt(pkey, in_blk)
```






---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Twofish`




<a href="../pykeepass/kdbx_parsing/pytwofish.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(key=None)
```

Twofish. 




---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `decrypt`

```python
decrypt(block)
```

Decrypt blocks. 

---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L99"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `encrypt`

```python
encrypt(block)
```

Encrypt blocks. 

---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_block_size`

```python
get_block_size()
```

Get cipher block size in bytes. 

---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_key_size`

```python
get_key_size()
```

Get cipher key size in bytes. 

---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_name`

```python
get_name()
```

Return the name of the cipher. 

---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_key`

```python
set_key(key)
```

Init. 


---

<a href="../pykeepass/kdbx_parsing/pytwofish.py#L156"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TWI`




<a href="../pykeepass/kdbx_parsing/pytwofish.py#L157"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__()
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
