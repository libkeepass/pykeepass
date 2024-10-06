import hashlib
import hmac
import logging
import random
from io import BytesIO

from Cryptodome.Cipher import AES
from lxml import etree
from base64 import b64encode, b64decode

from pykeepass.exceptions import CredentialsError
from pykeepass.fido2 import fido2_get_key_material, fido2_enroll
from pykeepass.kdbx_parsing.common import compute_keyfile_part_of_composite

FACTOR_TYPE_FIDO_2 = "15f77f9d-a65c-4a2e-b2b5-171f7b2df41a"
FACTOR_TYPE_KEY_FILE = "6b9746c7-ca8d-430b-986d-1afaf689c4e4"
FACTOR_TYPE_YK_CHALRESP = "0e6803a0-915e-4ebf-95ee-f9ddd8c97eea"
FACTOR_TYPE_PASSWORD = "c127a67f-be51-4bba-ac6f-7351e8a70ba0"
FACTOR_TYPE_EMPTY = "618636bf-e202-4e0b-bb7c-e2514be00f5a"

factor_types_to_names = {
    FACTOR_TYPE_FIDO_2: 'FIDO2',
    FACTOR_TYPE_KEY_FILE: 'key file',
    FACTOR_TYPE_YK_CHALRESP: 'YK challenge-response',
    FACTOR_TYPE_PASSWORD: 'password',
    FACTOR_TYPE_EMPTY: 'null (for testing)'
}

FACTOR_ALG_AES_CBC = "AES-CBC"

FACTOR_VALIDATE_HMAC_SHA512 = "HMAC-SHA512"

log = logging.getLogger(__name__)


class FactorInfo:
    def __init__(self, compat_version="1", comprehensive=False, factor_groups=None):
        if factor_groups is None:
            factor_groups = []
        self.compat_version = compat_version
        self.comprehensive = comprehensive
        self.factor_groups = factor_groups

    def encode(self, user_supplied_info):
        root_element = etree.Element("FactorInfo")

        version = etree.SubElement(root_element, "CompatVersion")
        version.text = str(self.compat_version)

        if self.comprehensive:
            inclusive = etree.SubElement(root_element, "Comprehensive")
            inclusive.text = "true"

        for group in self.factor_groups:
            factor_group = etree.SubElement(root_element, "Group")

            group.encode(factor_group, user_supplied_info)

        return etree.tostring(root_element, encoding='utf-8').decode()

    @staticmethod
    def decode(given_bytes):
        parser = etree.XMLParser(remove_blank_text=True)
        parsed = etree.parse(BytesIO(given_bytes.encode('utf-8')), parser)

        comprehensive_el = parsed.xpath("/FactorInfo/Comprehensive")
        comprehensive = True if len(comprehensive_el) == 1 and comprehensive_el[0].text == "true" else False

        ret = FactorInfo(
            compat_version=parsed.xpath("/FactorInfo/CompatVersion")[0].text,
            comprehensive=comprehensive
        )

        for group in parsed.xpath("/FactorInfo/Group"):
            ret.factor_groups.append(FactorGroup.decode(group))

        return ret


class FactorGroup:
    def __init__(self, validation_type=FACTOR_VALIDATE_HMAC_SHA512, validation_in=None, validation_out=None, challenge=None, factors=None):
        self.factors = []
        self.validation_type = validation_type
        self.validation_in = validation_in
        self.validation_out = validation_out
        self.challenge = challenge
        self.cached_key_part = None

        if factors is not None:
            for factor in factors:
                self.add_factor(factor)

    def add_factor(self, factor):
        self.factors.append(factor)
        factor.group = self
        if isinstance(factor, FIDO2Factor) and self.challenge is None:
            self.challenge = random.randbytes(32)

    def generate_validation(self, user_supplied_info):
        if self.validation_in is None:
            # Generate validation info
            if len(self.factors) == 0:
                raise CredentialsError("Cannot save a FactorGroup with no factors and unset validation info")
            self.validation_in = random.randbytes(32)
            # Arbitrarily get some factor - they should all create the same validation output
            wrapping_key = None
            for factor in self.factors:
                wrapping_key = factor.get_wrapping_key(user_supplied_info=user_supplied_info)
                if wrapping_key is not None:
                    break
            if wrapping_key is None:
                raise CredentialsError("Cannot find a factor to generate validation info")
            _, self.validation_out = factor.unwrap_key_part(user_supplied_info=user_supplied_info, unwrapping_key=wrapping_key)

        assert self.validation_in is not None and self.validation_out is not None

    def encode(self, group_element, user_supplied_info):
        if self.validation_in is not None:
            key_validation_type = etree.SubElement(group_element, "ValidationType")
            key_validation_type.text = self.validation_type

            key_validation_in = etree.SubElement(group_element, "ValidationIn")
            key_validation_in.text = b64encode(self.validation_in)

            key_validation_out = etree.SubElement(group_element, "ValidationOut")
            key_validation_out.text = b64encode(self.validation_out)

        if self.challenge is not None:
            challenge = etree.SubElement(group_element, "Challenge")
            challenge.text = b64encode(self.challenge)

        for factor in self.factors:
            factor_element = etree.SubElement(group_element, "Factor")
            factor.encode(factor_element)

    @staticmethod
    def decode(group_element):
        key_validation_type = None
        key_validation_in = None
        key_validation_out = None

        validation_element = group_element.xpath("ValidationType")
        if validation_element:
            key_validation_type = validation_element[0].text
            key_validation_in = b64decode(group_element.xpath("ValidationIn")[0].text)
            key_validation_out = b64decode(group_element.xpath("ValidationOut")[0].text)

        challenge = None
        challenges = group_element.xpath("Challenge")
        if challenges:
            challenge = b64decode(challenges[0].text)

        factors = []
        for factor in group_element.xpath("Factor"):
            factors.append(Factor.decode(factor))
        return FactorGroup(
            validation_type=key_validation_type,
            validation_in=key_validation_in,
            validation_out=key_validation_out,
            challenge=challenge,
            factors=factors
        )

    def unwrap_key_part(self, user_supplied_info):
        if self.cached_key_part is not None and user_supplied_info == self.cached_key_part[0]:
            return self.cached_key_part[1]

        fido2_factors = [x for x in self.factors if isinstance(x, FIDO2Factor)]
        other_factors = [x for x in self.factors if not isinstance(x, FIDO2Factor)]

        for factor in other_factors:
            # Try non-FIDO factors first
            try:
                unwrapped_part, _ = factor.unwrap_key_part(user_supplied_info=user_supplied_info)
                if unwrapped_part is not None:
                    self.cached_key_part = (user_supplied_info, unwrapped_part)
                    return unwrapped_part
            except CredentialsError as e:
                log.error("Factor failed: {}".format(e))
                continue

        next_challenge = random.randbytes(32)

        if len(fido2_factors) > 0:
            # Do all the FIDO2 factors in the group "in one go" to avoid prompting for authenticators repeatedly
            pin_data = user_supplied_info.get("factor_data", {}).get("fido2_pin", {})

            fido2_credentials_in_group = [x.credential_id for x in fido2_factors]

            result1, result2 = self.get_fido2_key_material(fido2_credentials_in_group, next_challenge, pin_data)

            for factor in fido2_factors:
                try:
                    unwrapped_part, _ = factor.unwrap_key_part(user_supplied_info=user_supplied_info, unwrapping_key=result1)
                    if unwrapped_part is not None:

                        # Success with FIDO2! Rotate the challenge if we can (if there's just one authenticator)
                        if len(fido2_factors) == 1:
                            self.rotate_fido2(factor, unwrapped_part, next_challenge=next_challenge, next_key_material=result2)

                        self.cached_key_part = (user_supplied_info, unwrapped_part)
                        return unwrapped_part
                except CredentialsError as e:
                    log.error("Factor failed: {}".format(e))
                    continue

        raise CredentialsError("Unable to derive key part for a required 2FA group")

    def get_fido2_key_material(self, fido2_credentials_in_group, next_challenge, pin_data):
        return fido2_get_key_material(pin_data,
                                      fido2_credentials_in_group,
                                      salt1=self.challenge,
                                      salt2=next_challenge,
                                      verify_user=True
                                      )

    def rotate_fido2(self, fido2_factor, key_part, next_challenge, next_key_material):
        if len(self.factors) == 1:
            # We really only have one factor: rotate the validation randomness too
            self.validation_in = random.randbytes(32)

        self.challenge = next_challenge
        wrapped_part = fido2_factor.wrap_key_part({}, key_part, next_key_material)
        fido2_factor.wrapped_key_part, new_validation_out = wrapped_part

        if len(self.factors) == 1:
            self.validation_out = new_validation_out


class Factor:
    def __init__(self, name, uuid, key_salt=None, key_type=FACTOR_ALG_AES_CBC, wrapped_key_part=None):
        if key_salt is None:
            key_salt = random.randbytes(16)
        self.name = name
        self.uuid = uuid
        self.key_salt = key_salt
        self.key_type = key_type
        self.wrapped_key_part = wrapped_key_part
        self.group = None

    def encode(self, factor_element):
        name = etree.SubElement(factor_element, "Name")
        name.text = self.name
        uuid = etree.SubElement(factor_element, "TypeUUID")
        uuid.text = self.uuid
        salt = etree.SubElement(factor_element, "KeySalt")
        salt.text = b64encode(self.key_salt)
        key_type = etree.SubElement(factor_element, "KeyType")
        key_type.text = self.key_type
        assert self.wrapped_key_part is not None
        key_part = etree.SubElement(factor_element, "WrappedKey")
        key_part.text = b64encode(self.wrapped_key_part)

    @staticmethod
    def decode(factor_element):
        name = factor_element.xpath("Name")[0].text
        uuid = factor_element.xpath("TypeUUID")[0].text

        key_salt = b64decode(factor_element.xpath("KeySalt")[0].text)
        key_type = factor_element.xpath("KeyType")[0].text
        key_part = b64decode(factor_element.xpath("WrappedKey")[0].text)
        ret = Factor(
            name=name,
            uuid=uuid,
            key_salt=key_salt,
            key_type=key_type,
            wrapped_key_part=key_part
        )

        if uuid == FACTOR_TYPE_FIDO_2:
            return FIDO2Factor.decode(ret, factor_element)
        elif uuid == FACTOR_TYPE_PASSWORD:
            return PasswordFactor.decode(ret, factor_element)
        elif uuid == FACTOR_TYPE_KEY_FILE:
            return KeyFileFactor.decode(ret, factor_element)
        elif uuid == FACTOR_TYPE_EMPTY:
            return NopFactor.decode(ret, factor_element)

        return ret

    def wrap_key_part(self, user_supplied_info, key_part, wrapping_key = None):
        factor_name = factor_types_to_names.get(self.uuid, self.uuid)
        if wrapping_key is None:
            wrapping_key = self.get_wrapping_key(user_supplied_info=user_supplied_info)

        encrypted_key = None
        if self.key_type == FACTOR_ALG_AES_CBC:
            cipher = AES.new(wrapping_key, AES.MODE_CBC, iv=self.key_salt)
            encrypted_key = cipher.encrypt(key_part)

        if encrypted_key is None:
            raise NotImplementedError(
                "Cannot wrap a key part for unknown alg {} on factor type {}".format(self.key_type, factor_name)
            )

        validation_out = None
        if self.group.validation_type == FACTOR_VALIDATE_HMAC_SHA512:
            validation_out = hmac.new(key_part, self.group.validation_in, 'SHA-512').digest()
        else:
            raise NotImplementedError(
                "Cannot verify a key part for unknown alg {} on factor type {}".format(self.group.verify_type,
                                                                                       factor_name)
            )

        return encrypted_key, validation_out

    def get_unwrapping_key(self, user_supplied_info):
        unwrapping_key = self.get_wrapping_key(user_supplied_info=user_supplied_info)
        if unwrapping_key is None:
            factor_name = factor_types_to_names.get(self.uuid, self.uuid)
            raise CredentialsError("Could not get key part for factor type {}".format(factor_name))
        return unwrapping_key

    def generate_key_if_necessary(self, user_supplied_info, unwrapping_key=None):
        if self.wrapped_key_part is None:
            # Generate wholly new key part
            if unwrapping_key is None:
                unwrapping_key = self.get_unwrapping_key(user_supplied_info=user_supplied_info)
            cipher = AES.new(unwrapping_key, AES.MODE_CBC, iv=self.key_salt)
            new_generated_key = random.randbytes(32)
            self.wrapped_key_part = cipher.encrypt(new_generated_key)

    def unwrap_key_part(self, user_supplied_info, unwrapping_key=None):
        factor_name = factor_types_to_names.get(self.uuid, self.uuid)

        self.generate_key_if_necessary(user_supplied_info=user_supplied_info, unwrapping_key=unwrapping_key)

        if unwrapping_key is None:
            unwrapping_key = self.get_unwrapping_key(user_supplied_info=user_supplied_info)

        decrypted_key = None

        if self.key_type == FACTOR_ALG_AES_CBC:
            # Salt forms the AES-CBC IV
            cipher = AES.new(unwrapping_key, AES.MODE_CBC, iv=self.key_salt)

            # Decrypt wrapped key part
            decrypted_key = cipher.decrypt(self.wrapped_key_part)

        if decrypted_key is None:
            raise NotImplementedError(
                "Cannot unwrap a key part for unknown alg {} on factor type {}".format(self.key_type, factor_name)
            )

        digest = None
        if self.group.validation_type == FACTOR_VALIDATE_HMAC_SHA512:
            digest = hmac.new(decrypted_key, self.group.validation_in, 'SHA-512').digest()
        else:
            # Can't verify, we don't know how or there's no validation type set for this Group
            pass

        if self.group.validation_out is not None and digest is not None and digest != self.group.validation_out:
            raise CredentialsError("Factor type {} did not return a valid key part".format(factor_name))

        # All good - return the key part
        return decrypted_key, digest

    def get_wrapping_key(self, user_supplied_info):
        factor_name = factor_types_to_names.get(self.uuid, self.uuid)

        raise NotImplementedError(
            "Cannot get unwrapping key part for factor type {}".format(factor_name)
        )

    def _get_relevant_user_info(self, user_supplied_info, section_name, factor_name=None):
        if user_supplied_info is None:
            return None
        if factor_name is None:
            factor_name = self.name
        section = user_supplied_info.get('factor_data', {}).get(section_name, None)
        if isinstance(section, str):
            return section
        return section.get(self.name, section.get("*", None))


class FIDO2Factor(Factor):
    def __init__(self, credential_id=None, *args, **kwargs):
        for prop_name in ['credential_id']:
            setattr(self, prop_name, locals()[prop_name])

        self.rotated_salt = None
        self.rotated_key = None

        super(FIDO2Factor, self).__init__(
            uuid=FACTOR_TYPE_FIDO_2,
            **kwargs
        )

    def encode(self, factor_element):
        super(FIDO2Factor, self).encode(factor_element)

        credential_id = etree.SubElement(factor_element, "CredentialID")
        credential_id.text = b64encode(self.credential_id)

    @staticmethod
    def decode(partial_factor, factor_element):
        credential_id = b64decode(factor_element.xpath("CredentialID")[0].text)

        return FIDO2Factor(
            name=partial_factor.name,
            key_salt=partial_factor.key_salt,
            key_type=partial_factor.key_type,
            wrapped_key_part=partial_factor.wrapped_key_part,
            credential_id=credential_id
        )

    def _enroll_if_necessary(self, user_supplied_info):
        if self.credential_id is None:
            existing_creds = [x for x in self.group.factors if isinstance(x, FIDO2Factor) and x.credential_id is not None]
            self.credential_id = fido2_enroll(user_supplied_info.get("factor_data", {}).get("fido2_pin", {}), existing_creds)

    def wrap_key_part(self, user_supplied_info, key_part, wrapping_key = None):
        self._enroll_if_necessary(user_supplied_info)
        return super(FIDO2Factor, self).wrap_key_part(user_supplied_info, key_part, wrapping_key)

    def get_wrapping_key(self, user_supplied_info):
        # Basically only used when creating a new group with a new FIDO2 factor in it
        self._enroll_if_necessary(user_supplied_info)
        pin_data = user_supplied_info.get("factor_data", {}).get("fido2_pin", {})
        hmac1, hmac2 = fido2_get_key_material(pin_data,
                                      [self.credential_id],
                                      salt1=self.group.challenge,
                                      salt2=self.group.challenge,
                                      verify_user=True
                                      )
        return hmac1


class PasswordFactor(Factor):
    def __init__(self, *args, **kwargs):
        super(PasswordFactor, self).__init__(
            uuid=FACTOR_TYPE_PASSWORD,
            *args,
            **kwargs
        )

    def get_wrapping_key(self, user_supplied_info):
        password = self._get_relevant_user_info(user_supplied_info, "password")

        # The unwrapping alg will do something more advanced, but we hash the password once just in case
        hashed_password = hashlib.sha256(password.encode('utf-8')).digest()

        return hashed_password

    @staticmethod
    def decode(partial_factor, factor_element):
        return PasswordFactor(
            name=partial_factor.name,
            key_salt=partial_factor.key_salt,
            key_type=partial_factor.key_type,
            wrapped_key_part=partial_factor.wrapped_key_part,
        )

    def change_password(self, old_password, new_password):
        unwrapped_part, _ = self.unwrap_key_part({"factor_data": {"password": old_password}})
        self.key_salt = random.randbytes(16)
        self.wrapped_key_part, _ = self.wrap_key_part({"factor_data": {"password": new_password}}, unwrapped_part)
        self.group.cached_key_part = None


class NopFactor(Factor):
    def __init__(self, *args, **kwargs):
        super(NopFactor, self).__init__(
            uuid=FACTOR_TYPE_EMPTY,
            *args,
            **kwargs
        )

    def get_wrapping_key(self, user_supplied_info):
        return b''

    def unwrap_key_part(self, user_supplied_info):
        return b'', self.group.validation_out

    @staticmethod
    def decode(partial_factor, factor_element):
        return NopFactor(
            name=partial_factor.name,
            key_salt=partial_factor.key_salt,
            key_type=partial_factor.key_type,
            wrapped_key_part=partial_factor.wrapped_key_part,
        )


class KeyFileFactor(Factor):
    def __init__(self, *args, **kwargs):
        super(KeyFileFactor, self).__init__(
            uuid=FACTOR_TYPE_KEY_FILE,
            *args,
            **kwargs
        )

    def get_wrapping_key(self, user_supplied_info):
        if user_supplied_info is None:
            user_supplied_info = {}
        keyfile = self._get_relevant_user_info(user_supplied_info, "keyfile")
        if keyfile is None:
            return None

        return compute_keyfile_part_of_composite(keyfile)

    @staticmethod
    def decode(partial_factor, factor_element):
        return KeyFileFactor(
            name=partial_factor.name,
            key_salt=partial_factor.key_salt,
            key_type=partial_factor.key_type,
            wrapped_key_part=partial_factor.wrapped_key_part,
        )
