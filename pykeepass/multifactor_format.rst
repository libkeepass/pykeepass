KeePass Multifactor Authentication File Format
==============================================

The KeePass file format is a reasonably complex thing. This page describes how KeePass
files, version 4.0, can support multi-factor authentication.

Design Goals
------------
Design goals of the multifactor solution:

- Extensible to support a wide variety of authentication factors (ideally anything that can
  produce keying material)
- Allow 1-of-N unlocking (spare/backup authenticators)
- Support clean future changes to cryptographic algorithms
- Allow de-authorizing authenticators
- Require minimal changes to existing database format
- Describe necessary authentication factors in the database itself (no guessing for the user)
- Avoid needing to present/activate authenticators more than once per read/save cycle

Non-goals:

- Allow a database with multifactor authentication enabled to be unlocked by an application not
  implementing this specification
- Allow de-authorizing authenticators without requiring the presence of a remaining authenticator
- Minimal storage size of disk
- Provide a replacement for the KDBX key derivation block (PBKDF2 or Argon2id)

Background
----------
A KeePass file has an "inner" and an "outer" header. The "outer" header is stored
unencrypted, and thus accessible before the database is opened. It is a series of TLV-encoded
values.

One of those values (number 12) is "public_custom_data", intended for storing arbitrary
information outside the encrypted contents blob. `public_custom_data` is a `VariantDict`, a
binary representation of a key-value map with a defined set of allowed value types.

File Format
===========
Only the KDBX 4.0 file (and up) are supported by this standard.

Within the `public_custom_data` outer header, a single dictionary entry is defined. This
entry shall has key `authentication_factors`. It has type `0x18`, a UTF-8 encoded string.
If this entry is present, the database uses multifactor authentication.

`authentication_factors` describes an ordered list of factor-groups. Each
group provides one binary part of the composite key that unlocks the KeePass database.
Within each group there may be multiple factors. For every factor, a differently-encrypted
copy of the composite key part is stored in such a way that it can only be
decrypted with the aid of that factor.

The value of the `authentication_factors` dict item is string-encoded XML. All binary elements within
the XML are base64-encoded. An example follows (with whitespace added for legibility):

.. code:: xml

    <FactorInfo>
        <CompatVersion>1</CompatVersion>
        <Comprehensive>true</Comprehensive>
        <Group>
            <ValidationType>HMAC-SHA512</ValidationType>
            <ValidationIn>fYB7M/IgSIMXAUDRyohObKbTp2GdJEGopyMJup7xTdg=</ValidationIn>
            <ValidationOut>4/dIKGkVeXp9fvjH0K7bEU3tywlfpMYiINYYuK55SRb2OglxBnLDWZb/nJl39+X9vbh10sIT5ZJC4ej64dlJqg==</ValidationOut>
            <Challenge>rXRnGOtIIWLz8xN1xWPqrw3opjoCFCJO29AXij6Bt8g=</Challenge>
            <Factor>
                <Name>Some Password</Name>
                <TypeUUID>c127a67f-be51-4bba-ac6f-7351e8a70ba0</TypeUUID>
                <KeyType>AES-CBC</KeyType>
                <KeySalt>R9vW1f329uh/7HMaqtCdIQ==</KeySalt>
                <WrappedKey>B4pHAoQomD8728UKeST2HOxglrjzwyq2M/IPEOV4xo8=</WrappedKey>
            </Factor>
            <Factor>
                <Name>Some Password</Name>
                <TypeUUID>15f77f9d-a65c-4a2e-b2b5-171f7b2df41a</TypeUUID>
                <KeyType>AES-CBC</KeyType>
                <KeySalt>hdJxBLk4Ln0T6lLIVguW3w==</KeySalt>
                <WrappedKey>o1Ysop7tBPjQe8WBwAGbF60QhZ0mHfMkEFbgaKj07Jk=</WrappedKey>
                <CredentialID>5iQ/yXVRCPwrLmNnLzKXktN0XM1Tdjn9u+GwpJnNj3fiztbtlEsCkYZ/b6Jy+dn8dQUewIayd4kJ/Bgrx9Kdfg==</CredentialID>
            </Factor>
        </Group>
    </FactorInfo>

The top element, `FactorInfo`, contanis the mandatory `CompatVersion` element.
The contents of `CompatVersion` must be the string `1` in this version of the specification.

The element `Comprehensive` may be present with contents `true`. If it is not, or
it is present with any other contents, then the groups' contribution to the composite key
will be concatenated onto an outside password, keyfile, and/or yubikey challenge-response.
In other words, if `Comprehensive` is `true`, the additional factors will together comprise everything
necessary to unlock the database.

Within each group there is a chunk to check that the correct composite key part has been derived. Three
properties are involved:

- `ValidationType`, defining the algorithm used to validate the key part
- `ValidationIn`, whose contents are used as input to the algorithm selected by `ValidationType`
- `ValidationOut`, whose contents must be produced as output of the algorithm selected by `ValidationType` with the correct key part

All Validation properties are OPTIONAL. When any are omitted, the validity of the factor response for that particular
`Group` cannot be determined in isolation, and incorrect input will result in a later failure using the database
composite key. When there is a factor present within the group susceptible to brute force, such as a bare password,
the Validation properties SHOULD be omitted for that group.

A fourth *OPTIONAL* member, `Challenge`, defines what value is sent as input to any and all challenge-response factors
within the group.

Within the group is an unordered list of `Factor` elements. Each one has a human-readable `Name` element, and a `TypeUUID`
defining what type of authenticator it is. They each also contain `WrappedKey`, an encrypted representation of the composite key
part for the group. In order to unwrap `WrappedKey`, the algorithm specified by the factor's `KeyType` is applied.

Additional elements may be present within the Factor depending on its `TypeUUID` and/or `KeyType`.

Pseudo-algorithm
----------------
- Iterate through each Group entry
- Within the Group, if Validation properties are present iterate through each Factor. Otherwise have the user select a Factor
- If the Factor type (defined by `TypeUUID`) is unknown, continue
- If the Key storage type (defined by `KeyType`) is unknown, continue
- Apply the algorithm from `KeyType` to `WrappedKey`, using `KeySalt` as appropriate. This produces a candidate key part
- If the user chose this Factor explicitly (ie Validation properties are absent), skip the next four steps
- Apply the algorithm from the group's `ValidationType` to the group's `ValidationIn`, using the candidate key part
- Compare the result with the group's `ValidationOut`
- If no match, discard this Factor and continue. If a match, stop iterating through Factors within this Group
- If the end of the Group is reached without a match, error
- Concatenate the candidate key parts from each Group, in the order in which the Groups are defined
- If the `FactorInfo` element has `Comprehensive` set to `true`, stop: the concatenated result is the final key
- Concatenate the obtained key to the end of any outside-provided key parts such as passwords and/or keyfiles

Defined Key Algorithm Types
===========================

AES-CBC
-------
Identifier: `AES-CBC`

This algorithm applies AES with a 128-bit block size in the Cipher Block Chaining mode. It requires
a 16-byte-long `KeySalt`. The input and output are unpadded, and so must be a
multiple of 16 bytes in length.

The key length used depends on the factor type, but must be either 128 bits or 256 bits.

Defined Validation Algorithm Types
==================================

HMAC-SHA512
-----------
Identifier: `HMAC-SHA512`

This applies an HMAC-SHA512 to `ValidationIn` to produce `ValidationOut`.

Defined Factor Types
====================
Each factor type has a UUID, to avoid ambiguity in implementation compatibility.

Password-SHA256
---------------
UUID: `c127a67f-be51-4bba-ac6f-7351e8a70ba0`

This performs a SHA-256 hash of a raw password. As such, it provides no
resistance against brute-force attacks and is generally insecure. It exists
only for compatibility with databases already encrypted with passwords.

Key File
--------
UUID: `6b9746c7-ca8d-430b-986d-1afaf689c4e4`

This opens a user-specified file. If the file contains valid UTF-8 XML, then
a `Meta/Version` element is located. In the event it contains the string `1.0`,
the base64-decoded contents of a `Key/Data` element are used as the key part.
If the version element contains `2.0`, the `Key/Data` element is whitespace-stripped,
hex-decoded, and then used as the key.

Otherwise, if the file is 32 bytes long, its contents are used as the key.

Otherwise, if the file is 64 bytes long and contains only hexadecimal data, its
contents are hex-decoded and used as the key.

Otherwise, the SHA-256 of the file contents is used as the key.

FIDO2-ES256
-----------
UUID: `15f77f9d-a65c-4a2e-b2b5-171f7b2df41a`

This allows the use of FIDO2 authenticators supporting both the `hmac-secret` and
the `credProtect` extensions to produce keying material.

When adding a FIDO2 authenticator, a new credential is created with:

- Relying Party ID set to `fido2.keepass.nodomain`
- The `hmac-secret` extension enabled
- `credProtect` set to `3` (required)
- A random, non-colliding user ID
- The `ES256` (256-bit ECDSA) algorithm

The resulting credential ID is stored (base64-encoded) within the `CredentialID`
member of the `Factor`.

To generate key material, the `Group` element's `Challenge` member is base64-decoded
and used as a salt to a FIDO2 get-assertion call. The result is used as the composite key
part.

Yubikey Challenge-Response
--------------------------
UUID: `0e6803a0-915e-4ebf-95ee-f9ddd8c97eea`

Placeholder, to be implemented.

Null
----
UUID: `618636bf-e202-4e0b-bb7c-e2514be00f5a`

This factor contributes nothing to the key, and is useful only for testing.
