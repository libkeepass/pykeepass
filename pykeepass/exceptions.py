# ----- binary parsing exceptions -----

class CredentialsError(Exception):
    pass

class PayloadChecksumError(Exception):
    pass

class HeaderChecksumError(Exception):
    pass

# ----- pykeepass exceptions -----

class BinaryError(Exception):
    pass

# ----- Entry exceptions -----

# ----- Group exceptions -----

# ----- RecycleBin exceptions -----

class UnableToSendToRecycleBin(Exception):
    pass