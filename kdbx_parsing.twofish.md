<!-- markdownlint-disable -->

<a href="../pykeepass/kdbx_parsing/twofish.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `kdbx_parsing.twofish`




**Global Variables**
---------------
- **MODE_ECB**
- **MODE_CBC**
- **MODE_CFB**
- **MODE_OFB**
- **MODE_CTR**
- **MODE_XTS**
- **MODE_CMAC**


---

<a href="../pykeepass/kdbx_parsing/twofish.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BlockCipher`
Base class for all blockciphers  



<a href="../pykeepass/kdbx_parsing/twofish.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(key, mode, IV, counter, cipher_module, segment_size, args={})
```








---

<a href="../pykeepass/kdbx_parsing/twofish.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `decrypt`

```python
decrypt(ciphertext, n='')
```

Decrypt some ciphertext 

 ciphertext  = a string of binary data  n           = the 'tweak' value when the chaining mode is XTS 

The decrypt function will decrypt the supplied ciphertext. The behavior varies slightly depending on the chaining mode. 

ECB, CBC: 
--------- When the supplied ciphertext is not a multiple of the blocksize  of the cipher, then the remaining ciphertext will be cached. The next time the decrypt function is called with some ciphertext,  the new ciphertext will be concatenated to the cache and then  cache+ciphertext will be decrypted. 

CFB, OFB, CTR: 
-------------- When the chaining mode allows the cipher to act as a stream cipher,  the decrypt function will always decrypt all of the supplied  ciphertext immediately. No cache will be kept. 

XTS: 
---- Because the handling of the last two blocks is linked,  it needs the whole block of ciphertext to be supplied at once. Every decrypt function called on a XTS cipher will output  a decrypted block based on the current supplied ciphertext block. 

CMAC: 
----- Mode not supported for decryption as this does not make sense. 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `encrypt`

```python
encrypt(plaintext, n='')
```

Encrypt some plaintext 

 plaintext   = a string of binary data  n           = the 'tweak' value when the chaining mode is XTS 

The encrypt function will encrypt the supplied plaintext. The behavior varies slightly depending on the chaining mode. 

ECB, CBC: 
--------- When the supplied plaintext is not a multiple of the blocksize  of the cipher, then the remaining plaintext will be cached. The next time the encrypt function is called with some plaintext,  the new plaintext will be concatenated to the cache and then  cache+plaintext will be encrypted. 

CFB, OFB, CTR: 
-------------- When the chaining mode allows the cipher to act as a stream cipher,  the encrypt function will always encrypt all of the supplied  plaintext immediately. No cache will be kept. 

XTS: 
---- Because the handling of the last two blocks is linked,  it needs the whole block of plaintext to be supplied at once. Every encrypt function called on a XTS cipher will output  an encrypted block based on the current supplied plaintext block. 

CMAC: 
----- Everytime the function is called, the hash from the input data is calculated. No finalizing needed. The hashlength is equal to block size of the used block cipher. 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `final`

```python
final(style='pkcs7')
```

Finalizes the encryption by padding the cache 

 padfct = padding function  import from CryptoPlus.Util.padding 

For ECB, CBC: the remaining bytes in the cache will be padded and  encrypted. For OFB,CFB, CTR: an encrypted padding will be returned, making the  total outputed bytes since construction of the cipher  a multiple of the blocksize of that cipher. 

If the cipher has been used for decryption, the final function won't do  anything. You have to manually unpad if necessary. 

After finalization, the chain can still be used but the IV, counter etc  aren't reset but just continue as they were after the last step (finalization step). 


---

<a href="../pykeepass/kdbx_parsing/twofish.py#L240"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CBC`
CBC chaining mode  



<a href="../pykeepass/kdbx_parsing/twofish.py#L243"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(codebook, blocksize, IV)
```








---

<a href="../pykeepass/kdbx_parsing/twofish.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update`

```python
update(data, ed)
```

Processes the given ciphertext/plaintext 

Inputs:  data: raw string of any length  ed:   'e' for encryption, 'd' for decryption Output:  processed raw string block(s), if any 

When the supplied data is not a multiple of the blocksize  of the cipher, then the remaining input data will be cached. The next time the update function is called with some data,  the new data will be concatenated to the cache and then  cache+data will be processed and full blocks will be outputted. 


---

<a href="../pykeepass/kdbx_parsing/twofish.py#L287"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `python_Twofish`




<a href="../pykeepass/kdbx_parsing/twofish.py#L288"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(key, mode, IV, counter, segment_size)
```








---

<a href="../pykeepass/kdbx_parsing/twofish.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `decrypt`

```python
decrypt(ciphertext, n='')
```

Decrypt some ciphertext 

 ciphertext  = a string of binary data  n           = the 'tweak' value when the chaining mode is XTS 

The decrypt function will decrypt the supplied ciphertext. The behavior varies slightly depending on the chaining mode. 

ECB, CBC: 
--------- When the supplied ciphertext is not a multiple of the blocksize  of the cipher, then the remaining ciphertext will be cached. The next time the decrypt function is called with some ciphertext,  the new ciphertext will be concatenated to the cache and then  cache+ciphertext will be decrypted. 

CFB, OFB, CTR: 
-------------- When the chaining mode allows the cipher to act as a stream cipher,  the decrypt function will always decrypt all of the supplied  ciphertext immediately. No cache will be kept. 

XTS: 
---- Because the handling of the last two blocks is linked,  it needs the whole block of ciphertext to be supplied at once. Every decrypt function called on a XTS cipher will output  a decrypted block based on the current supplied ciphertext block. 

CMAC: 
----- Mode not supported for decryption as this does not make sense. 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `encrypt`

```python
encrypt(plaintext, n='')
```

Encrypt some plaintext 

 plaintext   = a string of binary data  n           = the 'tweak' value when the chaining mode is XTS 

The encrypt function will encrypt the supplied plaintext. The behavior varies slightly depending on the chaining mode. 

ECB, CBC: 
--------- When the supplied plaintext is not a multiple of the blocksize  of the cipher, then the remaining plaintext will be cached. The next time the encrypt function is called with some plaintext,  the new plaintext will be concatenated to the cache and then  cache+plaintext will be encrypted. 

CFB, OFB, CTR: 
-------------- When the chaining mode allows the cipher to act as a stream cipher,  the encrypt function will always encrypt all of the supplied  plaintext immediately. No cache will be kept. 

XTS: 
---- Because the handling of the last two blocks is linked,  it needs the whole block of plaintext to be supplied at once. Every encrypt function called on a XTS cipher will output  an encrypted block based on the current supplied plaintext block. 

CMAC: 
----- Everytime the function is called, the hash from the input data is calculated. No finalizing needed. The hashlength is equal to block size of the used block cipher. 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `final`

```python
final(style='pkcs7')
```

Finalizes the encryption by padding the cache 

 padfct = padding function  import from CryptoPlus.Util.padding 

For ECB, CBC: the remaining bytes in the cache will be padded and  encrypted. For OFB,CFB, CTR: an encrypted padding will be returned, making the  total outputed bytes since construction of the cipher  a multiple of the blocksize of that cipher. 

If the cipher has been used for decryption, the final function won't do  anything. You have to manually unpad if necessary. 

After finalization, the chain can still be used but the IV, counter etc  aren't reset but just continue as they were after the last step (finalization step). 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L295"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(key, mode=1, IV=None, counter=None, segment_size=None)
```






---

<a href="../pykeepass/kdbx_parsing/twofish.py#L287"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `python_Twofish`




<a href="../pykeepass/kdbx_parsing/twofish.py#L288"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(key, mode, IV, counter, segment_size)
```








---

<a href="../pykeepass/kdbx_parsing/twofish.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `decrypt`

```python
decrypt(ciphertext, n='')
```

Decrypt some ciphertext 

 ciphertext  = a string of binary data  n           = the 'tweak' value when the chaining mode is XTS 

The decrypt function will decrypt the supplied ciphertext. The behavior varies slightly depending on the chaining mode. 

ECB, CBC: 
--------- When the supplied ciphertext is not a multiple of the blocksize  of the cipher, then the remaining ciphertext will be cached. The next time the decrypt function is called with some ciphertext,  the new ciphertext will be concatenated to the cache and then  cache+ciphertext will be decrypted. 

CFB, OFB, CTR: 
-------------- When the chaining mode allows the cipher to act as a stream cipher,  the decrypt function will always decrypt all of the supplied  ciphertext immediately. No cache will be kept. 

XTS: 
---- Because the handling of the last two blocks is linked,  it needs the whole block of ciphertext to be supplied at once. Every decrypt function called on a XTS cipher will output  a decrypted block based on the current supplied ciphertext block. 

CMAC: 
----- Mode not supported for decryption as this does not make sense. 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `encrypt`

```python
encrypt(plaintext, n='')
```

Encrypt some plaintext 

 plaintext   = a string of binary data  n           = the 'tweak' value when the chaining mode is XTS 

The encrypt function will encrypt the supplied plaintext. The behavior varies slightly depending on the chaining mode. 

ECB, CBC: 
--------- When the supplied plaintext is not a multiple of the blocksize  of the cipher, then the remaining plaintext will be cached. The next time the encrypt function is called with some plaintext,  the new plaintext will be concatenated to the cache and then  cache+plaintext will be encrypted. 

CFB, OFB, CTR: 
-------------- When the chaining mode allows the cipher to act as a stream cipher,  the encrypt function will always encrypt all of the supplied  plaintext immediately. No cache will be kept. 

XTS: 
---- Because the handling of the last two blocks is linked,  it needs the whole block of plaintext to be supplied at once. Every encrypt function called on a XTS cipher will output  an encrypted block based on the current supplied plaintext block. 

CMAC: 
----- Everytime the function is called, the hash from the input data is calculated. No finalizing needed. The hashlength is equal to block size of the used block cipher. 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `final`

```python
final(style='pkcs7')
```

Finalizes the encryption by padding the cache 

 padfct = padding function  import from CryptoPlus.Util.padding 

For ECB, CBC: the remaining bytes in the cache will be padded and  encrypted. For OFB,CFB, CTR: an encrypted padding will be returned, making the  total outputed bytes since construction of the cipher  a multiple of the blocksize of that cipher. 

If the cipher has been used for decryption, the final function won't do  anything. You have to manually unpad if necessary. 

After finalization, the chain can still be used but the IV, counter etc  aren't reset but just continue as they were after the last step (finalization step). 

---

<a href="../pykeepass/kdbx_parsing/twofish.py#L295"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(key, mode=1, IV=None, counter=None, segment_size=None)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
