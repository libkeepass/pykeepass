<!-- markdownlint-disable -->

<a href="../pykeepass/kdbx_parsing/common.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `kdbx_parsing.common`





---

<a href="../pykeepass/kdbx_parsing/common.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `Reparsed`

```python
Reparsed(subcon_out)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `aes_kdf`

```python
aes_kdf(key, rounds, key_composite)
```

Set up a context for AES128-ECB encryption to find transformed_key 


---

<a href="../pykeepass/kdbx_parsing/common.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `compute_key_composite`

```python
compute_key_composite(password=None, keyfile=None)
```

Compute composite key. Used in header verification and payload decryption. 


---

<a href="../pykeepass/kdbx_parsing/common.py#L164"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `compute_master`

```python
compute_master(context)
```

Computes master key from transformed key and master seed. Used in payload decryption. 


---

<a href="../pykeepass/kdbx_parsing/common.py#L260"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `Unprotect`

```python
Unprotect(protected_stream_id, protected_stream_key, subcon)
```

Select stream cipher based on protected_stream_id 


---

<a href="../pykeepass/kdbx_parsing/common.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HeaderChecksumError`








---

<a href="../pykeepass/kdbx_parsing/common.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CredentialsError`








---

<a href="../pykeepass/kdbx_parsing/common.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PayloadChecksumError`








---

<a href="../pykeepass/kdbx_parsing/common.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DynamicDict`
ListContainer <---> Container Convenience mapping so we dont have to iterate ListContainer to find the right item 

FIXME: lump kwarg was added to get around the fact that InnerHeader is not truly a dict.  We lump all 'binary' InnerHeaderItems into a single list 

<a href="../pykeepass/kdbx_parsing/common.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(key, subcon, lump=[])
```









---

<a href="../pykeepass/kdbx_parsing/common.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `XML`
Bytes <---> lxml etree 





---

<a href="../pykeepass/kdbx_parsing/common.py#L189"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UnprotectedStream`
lxml etree <---> unprotected lxml etree Iterate etree for Protected elements and decrypt using cipher provided by get_cipher 

<a href="../pykeepass/kdbx_parsing/common.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(protected_stream_key, subcon)
```









---

<a href="../pykeepass/kdbx_parsing/common.py#L233"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ARCFourVariantStream`




<a href="../pykeepass/kdbx_parsing/common.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(protected_stream_key, subcon)
```








---

<a href="../pykeepass/kdbx_parsing/common.py#L234"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cipher`

```python
get_cipher(protected_stream_key)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Salsa20Stream`




<a href="../pykeepass/kdbx_parsing/common.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(protected_stream_key, subcon)
```








---

<a href="../pykeepass/kdbx_parsing/common.py#L240"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cipher`

```python
get_cipher(protected_stream_key)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChaCha20Stream`




<a href="../pykeepass/kdbx_parsing/common.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(protected_stream_key, subcon)
```








---

<a href="../pykeepass/kdbx_parsing/common.py#L250"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cipher`

```python
get_cipher(protected_stream_key)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L275"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Concatenated`
Data Blocks <---> Bytes 





---

<a href="../pykeepass/kdbx_parsing/common.py#L293"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DecryptedPayload`
Encrypted Bytes <---> Decrypted Bytes 





---

<a href="../pykeepass/kdbx_parsing/common.py#L326"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AES256Payload`







---

<a href="../pykeepass/kdbx_parsing/common.py#L327"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cipher`

```python
get_cipher(master_key, encryption_iv)
```





---

<a href="../pykeepass/kdbx_parsing/common.py#L329"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pad`

```python
pad(data)
```





---

<a href="../pykeepass/kdbx_parsing/common.py#L331"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `unpad`

```python
unpad(data)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L335"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChaCha20Payload`







---

<a href="../pykeepass/kdbx_parsing/common.py#L336"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cipher`

```python
get_cipher(master_key, encryption_iv)
```





---

<a href="../pykeepass/kdbx_parsing/common.py#L338"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pad`

```python
pad(data)
```





---

<a href="../pykeepass/kdbx_parsing/common.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `unpad`

```python
unpad(data)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L344"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TwoFishPayload`







---

<a href="../pykeepass/kdbx_parsing/common.py#L345"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cipher`

```python
get_cipher(master_key, encryption_iv)
```





---

<a href="../pykeepass/kdbx_parsing/common.py#L347"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pad`

```python
pad(data)
```





---

<a href="../pykeepass/kdbx_parsing/common.py#L349"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `unpad`

```python
unpad(data)
```






---

<a href="../pykeepass/kdbx_parsing/common.py#L353"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Decompressed`
Compressed Bytes <---> Decompressed Bytes 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
