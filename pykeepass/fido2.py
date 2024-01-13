import logging
import random

from fido2.cose import ES256
from fido2.ctap import CtapError
from fido2.ctap2.extensions import HmacSecretExtension, CredProtectExtension
from fido2.hid import CtapHidDevice
from fido2.client import Fido2Client, UserInteraction
from fido2.webauthn import PublicKeyCredentialCreationOptions, PublicKeyCredentialRpEntity, \
    PublicKeyCredentialUserEntity, PublicKeyCredentialParameters, PublicKeyCredentialType, \
    PublicKeyCredentialDescriptor, PublicKeyCredentialRequestOptions, UserVerificationRequirement

log = logging.getLogger(__name__)

try:
    from fido2.pcsc import CtapPcscDevice
except ImportError:
    CtapPcscDevice = None

FIDO2_FACTOR_RPID = "fido2.keepass.nodomain"


class NonInteractive(UserInteraction):

    def __init__(self, fixed_pin):
        self.fixed_pin = fixed_pin

    def request_pin(self, permissions, rp_id):
        return self.fixed_pin


def _get_all_authenticators():
    for dev in CtapHidDevice.list_devices():
        yield dev
    if CtapPcscDevice:
        for dev in CtapPcscDevice.list_devices():
            yield dev


def _get_suitable_clients(pin_data):
    for authenticator in _get_all_authenticators():
        authenticator_path_string = repr(authenticator)

        if isinstance(pin_data, str):
            pin_to_use = pin_data
        else:
            pin_to_use = pin_data.get(authenticator_path_string, pin_data.get("*", None))

        client = Fido2Client(
            authenticator,
            "https://{}".format(FIDO2_FACTOR_RPID),
            user_interaction=NonInteractive(pin_to_use),
            extension_types=[
                HmacSecretExtension,
                CredProtectExtension
            ]
        )

        if "hmac-secret" in client.info.extensions and "credProtect" in client.info.extensions:
            yield client


class FIDOException(Exception):
    pass


def fido2_enroll(pin_data, already_enrolled_credentials):
    log.info("Enrolling new FIDO2 authenticator")

    # We don't care about the user ID
    # So long as it doesn't collide with another one for the same authenticator, it's all good
    user_id = random.randbytes(16)

    chosen_client = next(_get_suitable_clients(pin_data), None)
    if chosen_client is None:
        raise FIDOException("Could not find an authenticator supporting the hmac-secret and credProtect extensions")

    credential = chosen_client.make_credential(PublicKeyCredentialCreationOptions(
        rp=PublicKeyCredentialRpEntity(
            name="pykeepass",
            id=FIDO2_FACTOR_RPID
        ),
        user=PublicKeyCredentialUserEntity(
            name="keepass",
            id=user_id,
            display_name="KeePass"
        ),
        challenge=random.randbytes(32),
        pub_key_cred_params=[
            PublicKeyCredentialParameters(
                type=PublicKeyCredentialType.PUBLIC_KEY,
                alg=ES256.ALGORITHM
            )
        ],
        exclude_credentials=[
            PublicKeyCredentialDescriptor(
                type=PublicKeyCredentialType.PUBLIC_KEY,
                id=credential_id
            ) for credential_id in already_enrolled_credentials
        ],
        extensions={
            "hmacCreateSecret": True,
            "credentialProtectionPolicy": CredProtectExtension.POLICY.REQUIRED,
            "enforceCredentialProtectionPolicy": True
        }
    ))

    if not credential.extension_results.get("hmacCreateSecret", False):
        raise FIDOException("Authenticator didn't create an HMAC secret!")

    return credential.attestation_object.auth_data.credential_data.credential_id


def fido2_get_key_material(pin_data, credential_ids, salt1, salt2, verify_user=True):
    log.info("Getting keying material from FIDO2 authenticator (with {} potential credentials)".format(len(credential_ids)))

    user_verification = UserVerificationRequirement.REQUIRED if verify_user else UserVerificationRequirement.DISCOURAGED
    for client in _get_suitable_clients(pin_data):
        try:
            assertion_response = client.get_assertion(
                PublicKeyCredentialRequestOptions(
                    challenge=random.randbytes(32),
                    rp_id=FIDO2_FACTOR_RPID,
                    allow_credentials=[
                        PublicKeyCredentialDescriptor(
                            type=PublicKeyCredentialType.PUBLIC_KEY,
                            id=credential_id
                        ) for credential_id in credential_ids
                    ],
                    user_verification=user_verification,
                    extensions={
                        "hmacGetSecret": {
                            "salt1": salt1,
                            "salt2": salt2
                        }
                    }
                )
            )
            assertion = assertion_response.get_response(0)
            hmac_response = assertion.extension_results.get("hmacGetSecret", None)
            if hmac_response is not None:
                return hmac_response.get("output1", None), hmac_response.get("output2", None)
        except CtapError as e:
            if e.code != CtapError.ERR.NO_CREDENTIALS:
                raise e

    raise FIDOException("No authenticator provided key material")
