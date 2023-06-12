"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    Client management features

"""
import hashlib
import socket
import json
import time

# Intern importation
from .crypto import RSAWrapper, AESWrapper
from .sanitize import makeResponse, verifyRequestContent

# Default parameters
DEFAULT_STORE_REQUEST = True
DEFAULT_AUTO_EXCHANGE_KEYS = True
DEFAULT_RECEIVE_FIRST = True

# Constants definition
MESSAGE_OK = "1"
MESSAGE_NOK = "0"


# Class representing a established client connexion
class ClientInstance:
    def __init__(
        self,
        socket: socket.socket,
        timeout: int = None,
        rsa_wrapper: RSAWrapper = None,
        aes_wrapper: AESWrapper = None,
        auto_exchange_key: bool = DEFAULT_AUTO_EXCHANGE_KEYS,
    ):
        self.rsa_wrapper = rsa_wrapper if rsa_wrapper else RSAWrapper()
        self.aes_wrapper = aes_wrapper if aes_wrapper else AESWrapper()
        self.stored_request = None
        self.is_closed = False
        self.socket = socket

        self.id = hashlib.sha256(
            self.getIP().encode(), usedforsecurity=False
        ).hexdigest()[:7]
        self.timestamp = int(time.time())

        if timeout:
            self.socket.settimeout(timeout)

        if auto_exchange_key:
            self.exchangeKeys()

    def __del__(self):
        if not self.is_closed:
            self.closeConnection()

    def isClosed(self) -> bool:
        return self.is_closed

    def getSocketDescriptor(self) -> socket.socket:
        return self.socket

    def getIP(self) -> str:
        return self.socket.getpeername()[0]

    def getID(self) -> str:
        return self.id

    def getTimestamp(self) -> int:
        return self.timestamp

    def getStoredRequest(self) -> None | dict:
        return self.stored_request

    def getRSAWrapper(self) -> RSAWrapper:
        return self.rsa_wrapper

    def getAESWrapper(self) -> AESWrapper:
        return self.aes_wrapper

    def setRSAWrapper(self, rsa_wrapper: RSAWrapper) -> None:
        self.rsa_wrapper = rsa_wrapper

    def setAESWrapper(self, aes_wrapper: AESWrapper) -> None:
        self.aes_wrapper = aes_wrapper

    def sendPublicRSAKey(self) -> None:
        if self.is_closed:
            raise RuntimeError("Client must be connected to the server")

        rsa_public_key = self.rsa_wrapper.getPublicKey()
        rsa_public_key_length = str(len(rsa_public_key))

        # Send the key size
        self.socket.sendall(
            (rsa_public_key_length + ("=" * (8 - len(rsa_public_key_length)))).encode()
        )

        if self.socket.recv(1).decode() is not MESSAGE_OK:
            raise RuntimeError("Peer refused the packet")

        self.socket.sendall(rsa_public_key)

        if self.socket.recv(1).decode() is not MESSAGE_OK:
            raise RuntimeError("Peer refused the RSA key")

    def recvPublicRSAKey(self) -> None:
        if self.is_closed:
            raise RuntimeError("Client must be connected to the server")

        try:
            recv_key_length = int(self.socket.recv(8).decode().split("=")[0])

            if recv_key_length <= 0:
                self.socket.sendall(MESSAGE_NOK.encode())
                raise ValueError(f"Received bad key length : {recv_key_length}")

            self.socket.sendall(MESSAGE_OK.encode())
            recv_packet = self.socket.recv(recv_key_length)

            self.rsa_wrapper.setRemotePublicKey(recv_packet)
            self.socket.sendall(MESSAGE_OK.encode())

        except Exception as E:
            self.socket.sendall(MESSAGE_NOK.encode())
            raise E

    def sendAESKey(self) -> None:
        if self.is_closed:
            raise RuntimeError("Client must be connected to the server")

        if not self.rsa_wrapper:
            raise ValueError("RSA cipher is not set")

        aes_key = self.aes_wrapper.getKey()
        aes_iv = self.aes_wrapper.getIv()

        self.socket.sendall(
            self.rsa_wrapper.encryptData(aes_key + aes_iv, encode=False)
        )

        if self.socket.recv(1).decode() is not MESSAGE_OK:
            raise RuntimeError("Peer refused the AES key")

    def recvAESKey(self) -> None:
        try:
            if self.is_closed:
                raise RuntimeError("Client must be connected to the server")

            if not self.rsa_wrapper:
                raise ValueError("RSA cipher is not set")

            # Key size is divided by 8 to get the maximum supported block size
            recv_packet = self.rsa_wrapper.decryptData(
                self.socket.recv(int(self.rsa_wrapper.getKeySize() / 8)),
                decode=False,
            )

            self.aes_wrapper.setKey(recv_packet[:-16], recv_packet[-16:])

            self.socket.sendall(MESSAGE_OK.encode())

        except Exception as E:
            self.socket.sendall(MESSAGE_NOK.encode())
            raise E

    def exchangeKeys(self, receive_first: bool = DEFAULT_RECEIVE_FIRST) -> None:
        if self.is_closed:
            raise RuntimeError("Client must be connected to the server")

        if receive_first:
            self.recvPublicRSAKey()
            self.sendPublicRSAKey()
            self.recvAESKey()
            self.sendAESKey()

        else:
            self.sendPublicRSAKey()
            self.recvPublicRSAKey()
            self.sendAESKey()
            self.recvAESKey()

    def sendResponse(
        self, success: bool, message: str, data: dict = {}, reason: str = None
    ) -> None:
        if self.is_closed:
            raise RuntimeError("Client must be connected to the server")

        if not self.aes_wrapper:
            raise ValueError("AES cipher is not set")

        response_tuple = makeResponse(success, message, data, reason)

        if not response_tuple[0]:
            raise ValueError(f"Error in specified values : {response_tuple[1]}")

        encrypted_packet = self.aes_wrapper.encryptData(json.dumps(response_tuple[1]))

        packet_length = str(len(encrypted_packet))
        self.socket.sendall((packet_length + ("=" * (8 - len(packet_length)))).encode())

        if self.socket.recv(1).decode() != MESSAGE_OK:
            raise RuntimeError("Peer refused the packet")

        self.socket.sendall(encrypted_packet)

    def recvRequest(self, store_request: bool = DEFAULT_STORE_REQUEST) -> tuple:
        if self.is_closed:
            raise RuntimeError("Client must be connected to the server")

        if not self.aes_wrapper:
            raise ValueError("AES cipher is not set")

        recv_packet_length = int(self.socket.recv(8).decode().split("=")[0])

        if recv_packet_length <= 0:
            self.socket.sendall(MESSAGE_NOK.encode())
            raise ValueError(f"Received bad packet length : {recv_packet_length}")

        self.socket.sendall(MESSAGE_OK.encode())

        decrypted_recv_request = self.aes_wrapper.decryptData(
            self.socket.recv(recv_packet_length)
        )

        verification_result = verifyRequestContent(json.loads(decrypted_recv_request))

        if verification_result[0]:
            if store_request:
                self.stored_request = verification_result[1]

        return verification_result

    def closeConnection(self) -> None:
        self.socket.close()
        self.is_closed = True
