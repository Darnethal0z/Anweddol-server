"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module provides the Anweddol server with client 
representation and management features. It includes :

 - RSA / AES key exchange ;
 - Request / response processing ;

"""

import hashlib
import socket
import json
import time

# Intern importation
from .crypto import RSAWrapper, AESWrapper
from .sanitization import makeResponse, verifyRequestContent
from .utilities import isSocketClosed

# Default parameters
DEFAULT_STORE_REQUEST = True
DEFAULT_EXCHANGE_KEYS = True
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
        exchange_keys: bool = DEFAULT_EXCHANGE_KEYS,
    ):
        self.rsa_wrapper = rsa_wrapper if rsa_wrapper else RSAWrapper()
        self.aes_wrapper = aes_wrapper if aes_wrapper else AESWrapper()
        self.stored_request = None
        self.socket = socket

        self.id = hashlib.sha256(
            self.getIP().encode(), usedforsecurity=False
        ).hexdigest()[:7]
        self.creation_timestamp = int(time.time())

        if timeout:
            self.socket.settimeout(timeout)

        if exchange_keys:
            self.exchangeKeys()

    def __del__(self):
        if not self.isClosed():
            self.closeConnection()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not self.isClosed():
            self.closeConnection()

    def isClosed(self) -> bool:
        return isSocketClosed(self.socket)

    def getSocketDescriptor(self) -> socket.socket:
        return self.socket

    def getIP(self) -> str:
        return self.socket.getpeername()[0]

    def getID(self) -> str:
        return self.id

    def getCreationTimestamp(self) -> int:
        return self.creation_timestamp

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
        if self.isClosed():
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
        if self.isClosed():
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
        if self.isClosed():
            raise RuntimeError("Client must be connected to the server")

        aes_key = self.aes_wrapper.getKey()

        self.socket.sendall(self.rsa_wrapper.encryptData(aes_key[0] + aes_key[1]))

        if self.socket.recv(1).decode() is not MESSAGE_OK:
            raise RuntimeError("Peer refused the AES key")

    def recvAESKey(self) -> None:
        try:
            if self.isClosed():
                raise RuntimeError("Client must be connected to the server")

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
        if self.isClosed():
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
        if self.isClosed():
            raise RuntimeError("Client must be connected to the server")

        is_response_valid, response_content, response_errors = makeResponse(
            success, message, data, reason
        )

        if not is_response_valid:
            raise ValueError(f"Error in specified values : {response_errors}")

        encrypted_packet = self.aes_wrapper.encryptData(json.dumps(response_content))

        packet_length = str(len(encrypted_packet))
        self.socket.sendall((packet_length + ("=" * (8 - len(packet_length)))).encode())

        if self.socket.recv(1).decode() != MESSAGE_OK:
            raise RuntimeError("Peer refused the packet")

        self.socket.sendall(encrypted_packet)

    def recvRequest(self, store_request: bool = DEFAULT_STORE_REQUEST) -> tuple:
        if self.isClosed():
            raise RuntimeError("Client must be connected to the server")

        recv_packet_length = int(self.socket.recv(8).decode().split("=")[0])

        if recv_packet_length <= 0:
            self.socket.sendall(MESSAGE_NOK.encode())
            raise ValueError(f"Received bad packet length : {recv_packet_length}")

        self.socket.sendall(MESSAGE_OK.encode())

        decrypted_recv_request = self.aes_wrapper.decryptData(
            self.socket.recv(recv_packet_length)
        )

        is_request_valid, request_content, request_errors = verifyRequestContent(
            json.loads(decrypted_recv_request)
        )

        if is_request_valid and store_request:
            self.stored_request = request_content

        return (is_request_valid, request_content, request_errors)

    def closeConnection(self) -> None:
        self.socket.close()
