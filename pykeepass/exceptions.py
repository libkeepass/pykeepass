# ----- binary parsing exceptions -----

# ----- pykeepass exceptions -----
class BinaryError(Exception):
    pass

# raised on invalid credentials, header corruption, payload corruption
# this may be split into multiple exceptions when python-construct supports it
class CredentialsIntegrityError(Exception):
    def __init__(self, msg='Credentials are wrong or integrity check failed'):
        super(Exception, self).__init__(msg)

# ----- Entry exceptions -----

# ----- Group exceptions -----
