<!-- markdownlint-disable -->

# API Overview

## Modules

- [`attachment`](./attachment.md#module-attachment)
- [`baseelement`](./baseelement.md#module-baseelement)
- [`entry`](./entry.md#module-entry)
- [`exceptions`](./exceptions.md#module-exceptions)
- [`group`](./group.md#module-group)
- [`icons`](./icons.md#module-icons)
- [`kdbx_parsing`](./kdbx_parsing.md#module-kdbx_parsing)
- [`kdbx_parsing.common`](./kdbx_parsing.common.md#module-kdbx_parsingcommon)
- [`kdbx_parsing.kdbx`](./kdbx_parsing.kdbx.md#module-kdbx_parsingkdbx)
- [`kdbx_parsing.kdbx3`](./kdbx_parsing.kdbx3.md#module-kdbx_parsingkdbx3)
- [`kdbx_parsing.kdbx4`](./kdbx_parsing.kdbx4.md#module-kdbx_parsingkdbx4)
- [`kdbx_parsing.pytwofish`](./kdbx_parsing.pytwofish.md#module-kdbx_parsingpytwofish)
- [`kdbx_parsing.twofish`](./kdbx_parsing.twofish.md#module-kdbx_parsingtwofish)
- [`pykeepass`](./pykeepass.md#module-pykeepass)
- [`setters`](./setters.md#module-setters)
- [`version`](./version.md#module-version)
- [`xpath`](./xpath.md#module-xpath)

## Classes

- [`attachment.Attachment`](./attachment.md#class-attachment)
- [`baseelement.BaseElement`](./baseelement.md#class-baseelement): Entry and Group inherit from this class
- [`entry.Entry`](./entry.md#class-entry)
- [`entry.HistoryEntry`](./entry.md#class-historyentry)
- [`exceptions.BinaryError`](./exceptions.md#class-binaryerror)
- [`exceptions.CredentialsError`](./exceptions.md#class-credentialserror)
- [`exceptions.HeaderChecksumError`](./exceptions.md#class-headerchecksumerror)
- [`exceptions.PayloadChecksumError`](./exceptions.md#class-payloadchecksumerror)
- [`exceptions.UnableToSendToRecycleBin`](./exceptions.md#class-unabletosendtorecyclebin)
- [`group.Group`](./group.md#class-group)
- [`common.AES256Payload`](./kdbx_parsing.common.md#class-aes256payload)
- [`common.ARCFourVariantStream`](./kdbx_parsing.common.md#class-arcfourvariantstream)
- [`common.ChaCha20Payload`](./kdbx_parsing.common.md#class-chacha20payload)
- [`common.ChaCha20Stream`](./kdbx_parsing.common.md#class-chacha20stream)
- [`common.Concatenated`](./kdbx_parsing.common.md#class-concatenated): Data Blocks <---> Bytes
- [`common.CredentialsError`](./kdbx_parsing.common.md#class-credentialserror)
- [`common.Decompressed`](./kdbx_parsing.common.md#class-decompressed): Compressed Bytes <---> Decompressed Bytes
- [`common.DecryptedPayload`](./kdbx_parsing.common.md#class-decryptedpayload): Encrypted Bytes <---> Decrypted Bytes
- [`common.DynamicDict`](./kdbx_parsing.common.md#class-dynamicdict): ListContainer <---> Container
- [`common.HeaderChecksumError`](./kdbx_parsing.common.md#class-headerchecksumerror)
- [`common.PayloadChecksumError`](./kdbx_parsing.common.md#class-payloadchecksumerror)
- [`common.Salsa20Stream`](./kdbx_parsing.common.md#class-salsa20stream)
- [`common.TwoFishPayload`](./kdbx_parsing.common.md#class-twofishpayload)
- [`common.UnprotectedStream`](./kdbx_parsing.common.md#class-unprotectedstream): lxml etree <---> unprotected lxml etree
- [`common.XML`](./kdbx_parsing.common.md#class-xml): Bytes <---> lxml etree
- [`pytwofish.TWI`](./kdbx_parsing.pytwofish.md#class-twi)
- [`pytwofish.Twofish`](./kdbx_parsing.pytwofish.md#class-twofish)
- [`twofish.BlockCipher`](./kdbx_parsing.twofish.md#class-blockcipher): Base class for all blockciphers
- [`twofish.CBC`](./kdbx_parsing.twofish.md#class-cbc): CBC chaining mode
- [`twofish.python_Twofish`](./kdbx_parsing.twofish.md#class-python_twofish)
- [`twofish.python_Twofish`](./kdbx_parsing.twofish.md#class-python_twofish)
- [`pykeepass.PyKeePass`](./pykeepass.md#class-pykeepass): Open a KeePass database

## Functions

- [`common.Reparsed`](./kdbx_parsing.common.md#function-reparsed)
- [`common.Unprotect`](./kdbx_parsing.common.md#function-unprotect): Select stream cipher based on protected_stream_id
- [`common.aes_kdf`](./kdbx_parsing.common.md#function-aes_kdf): Set up a context for AES128-ECB encryption to find transformed_key
- [`common.compute_key_composite`](./kdbx_parsing.common.md#function-compute_key_composite): Compute composite key.
- [`common.compute_master`](./kdbx_parsing.common.md#function-compute_master): Computes master key from transformed key and master seed.
- [`kdbx3.compute_transformed`](./kdbx_parsing.kdbx3.md#function-compute_transformed): Compute transformed key for opening database
- [`kdbx4.compute_header_hmac_hash`](./kdbx_parsing.kdbx4.md#function-compute_header_hmac_hash): Compute HMAC-SHA256 hash of header.
- [`kdbx4.compute_payload_block_hash`](./kdbx_parsing.kdbx4.md#function-compute_payload_block_hash): Compute hash of each payload block.
- [`kdbx4.compute_transformed`](./kdbx_parsing.kdbx4.md#function-compute_transformed): Compute transformed key for opening database
- [`pytwofish.byte`](./kdbx_parsing.pytwofish.md#function-byte)
- [`pytwofish.byteswap32`](./kdbx_parsing.pytwofish.md#function-byteswap32)
- [`pytwofish.decrypt`](./kdbx_parsing.pytwofish.md#function-decrypt)
- [`pytwofish.encrypt`](./kdbx_parsing.pytwofish.md#function-encrypt)
- [`pytwofish.gen_mk_tab`](./kdbx_parsing.pytwofish.md#function-gen_mk_tab)
- [`pytwofish.gen_mtab`](./kdbx_parsing.pytwofish.md#function-gen_mtab)
- [`pytwofish.gen_qtab`](./kdbx_parsing.pytwofish.md#function-gen_qtab)
- [`pytwofish.h_fun`](./kdbx_parsing.pytwofish.md#function-h_fun)
- [`pytwofish.mds_rem`](./kdbx_parsing.pytwofish.md#function-mds_rem)
- [`pytwofish.qp`](./kdbx_parsing.pytwofish.md#function-qp)
- [`pytwofish.rotl32`](./kdbx_parsing.pytwofish.md#function-rotl32)
- [`pytwofish.rotr32`](./kdbx_parsing.pytwofish.md#function-rotr32)
- [`pytwofish.set_key`](./kdbx_parsing.pytwofish.md#function-set_key)
- [`pykeepass.create_database`](./pykeepass.md#function-create_database)
- [`pykeepass.debug_setup`](./pykeepass.md#function-debug_setup): Convenience function to quickly enable debug messages
- [`setters.get_text`](./setters.md#function-get_text)
- [`setters.get_time`](./setters.md#function-get_time)
- [`setters.set_text`](./setters.md#function-set_text)
- [`setters.set_time`](./setters.md#function-set_time)


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
