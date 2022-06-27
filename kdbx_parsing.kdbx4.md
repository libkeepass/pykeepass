<!-- markdownlint-disable -->

<a href="../pykeepass/kdbx_parsing/kdbx4.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `kdbx_parsing.kdbx4`




**Global Variables**
---------------
- **kdf_uuids**

---

<a href="../pykeepass/kdbx_parsing/kdbx4.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `compute_transformed`

```python
compute_transformed(context)
```

Compute transformed key for opening database 


---

<a href="../pykeepass/kdbx_parsing/kdbx4.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `compute_header_hmac_hash`

```python
compute_header_hmac_hash(context)
```

Compute HMAC-SHA256 hash of header. Used to prevent header tampering. 


---

<a href="../pykeepass/kdbx_parsing/kdbx4.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `compute_payload_block_hash`

```python
compute_payload_block_hash(this)
```

Compute hash of each payload block. Used to prevent payload corruption and tampering. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
