"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    RSA/AES encryption features.

    Provided encryption scheme is RSA with a default 4096 key size,
    and AES 256 CBC utilities.

"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import cryptography.hazmat.primitives.padding as symetric_padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
import os


# Default parameters
DEFAULT_RSA_EXPONENT = 65537
DEFAULT_RSA_KEY_SIZE = 4096
DEFAULT_AES_KEY_SIZE = 256

DEFAULT_PEM_FORMAT = True
DEFAULT_GENERATE_KEY_PAIR = True
DEFAULT_DERIVATE_PUBLIC_KEY = False


class RSAWrapper:
    def __init__(
        self,
        public_exponent: int = DEFAULT_RSA_EXPONENT,
        key_size: int = DEFAULT_RSA_KEY_SIZE,
        generate_key_pair: bool = DEFAULT_GENERATE_KEY_PAIR,
    ):
        self.remote_public_key = None
        self.private_key = None
        self.public_key = None

        if generate_key_pair:
            self.generateKeyPair(public_exponent, key_size)

    def generateKeyPair(
        self,
        public_exponent: int = DEFAULT_RSA_EXPONENT,
        key_size: int = DEFAULT_RSA_KEY_SIZE,
    ) -> None:
        self.private_key = rsa.generate_private_key(
            public_exponent=public_exponent, key_size=key_size
        )
        self.public_key = self.private_key.public_key()

    def getKeySize(self) -> None | int:
        return self.public_key.key_size if self.public_key else None

    def getPublicKey(self, pem_format: bool = DEFAULT_PEM_FORMAT) -> None | str | bytes:
        return (
            self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            if pem_format and self.public_key
            else self.public_key
        )

    def getPrivateKey(
        self, pem_format: bool = DEFAULT_PEM_FORMAT
    ) -> None | str | bytes:
        return (
            self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            if pem_format and self.private_key
            else self.private_key
        )

    def getRemotePublicKey(
        self, pem_format: bool = DEFAULT_PEM_FORMAT
    ) -> None | str | bytes:
        return (
            self.remote_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            if pem_format and self.remote_public_key
            else self.remote_public_key
        )

    def setPublicKey(
        self, public_key: str | bytes, pem_format: bool = DEFAULT_PEM_FORMAT
    ) -> None:
        self.public_key = (
            serialization.load_pem_public_key(public_key) if pem_format else public_key
        )

    def setPrivateKey(
        self,
        private_key: str | bytes,
        pem_format: bool = DEFAULT_PEM_FORMAT,
        derivate_public_key: bool = DEFAULT_DERIVATE_PUBLIC_KEY,
    ) -> None:
        self.private_key = (
            serialization.load_pem_private_key(private_key, password=None)
            if pem_format
            else private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

        if derivate_public_key:
            self.public_key = self.private_key.public_key()

    def setRemotePublicKey(
        self, remote_public_key: str | bytes, pem_format: bool = DEFAULT_PEM_FORMAT
    ) -> None:
        self.remote_public_key = (
            serialization.load_pem_public_key(remote_public_key)
            if pem_format
            else remote_public_key
        )

    def encryptData(
        self, data: str | bytes, use_local_public_key: bool = False
    ) -> bytes:
        if not self.remote_public_key and not use_local_public_key:
            raise ValueError("Remote public key is not set")

        else:
            if not self.public_key:
                raise ValueError("Local public key is not set")

        encoded_data = data.encode() if type(data) is str else data

        return (
            self.remote_public_key.encrypt(
                encoded_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            if not use_local_public_key
            else self.public_key.encrypt(
                encoded_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        )

    def decryptData(self, cipher: bytes, decode: bool = True) -> str | bytes:
        if not self.private_key:
            raise ValueError("Local private key is not set")

        decrypted_data = self.private_key.decrypt(
            cipher,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return decrypted_data.decode() if decode else decrypted_data

    def signData(self, data: str | bytes) -> bytes:
        if not self.private_key:
            raise ValueError("Local private key is not set")

        encoded_data = data.encode() if type(data) is str else data

        return self.private_key.sign(
            encoded_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

    # `signature` is the signed data, `data` is the data itself
    def verifyDataSignature(self, signature: bytes, data: str | bytes) -> bool:
        if not self.public_key:
            raise ValueError("Local public key is not set")

        encoded_data = data.encode() if type(data) is str else data

        try:
            self.public_key.verify(
                signature,
                encoded_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return True

        except InvalidSignature:
            return False


class AESWrapper:
    def __init__(self, key_size: int = DEFAULT_AES_KEY_SIZE):
        self.key = os.urandom(int(key_size / 8))
        self.iv = os.urandom(16)

        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))

    def getKeySize(self) -> int:
        return len(self.key) * 8

    def getKey(self) -> bytes:
        return (self.key, self.iv)

    def setKey(self, key: bytes, iv: bytes = None) -> None:
        self.key = key
        self.iv = iv if iv else os.urandom(16)

        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))

    def encryptData(self, data: str | bytes) -> bytes:
        encryptor = self.cipher.encryptor()
        encoded_data = data.encode() if type(data) is str else data

        return encryptor.update(self.__pad_data(encoded_data)) + encryptor.finalize()

    def decryptData(self, cipher: bytes, decode: bool = True) -> str | bytes:
        decryptor = self.cipher.decryptor()
        decrypted_data = self.__unpad_data(
            decryptor.update(cipher) + decryptor.finalize()
        )

        return decrypted_data.decode() if decode else decrypted_data

    def __pad_data(self, data, size=128):
        padder = symetric_padding.PKCS7(size).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()

        return padded_data

    def __unpad_data(self, data, size=128):
        padder = symetric_padding.PKCS7(size).unpadder()
        unpadded_data = padder.update(data)
        unpadded_data += padder.finalize()

        return unpadded_data
