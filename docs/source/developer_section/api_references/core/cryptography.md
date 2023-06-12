# Cryptography

---

> RSA / AES encryption features.

> Package `anwdlserver.core.crypto`

## Constants

Default values :

| Name                          | Value   | Description                                               |
| ----------------------------- | ------- | --------------------------------------------------------- |
| `DEFAULT_RSA_KEY_SIZE`        | `4096`  | The default RSA key size                                  |
| `DEFAULT_AES_KEY_SIZE`        | `256`   | The default AES key size                                  |
| `DEFAULT_PEM_FORMAT`          | `True`  | Specify key in a PEM format by default                    |
| `DEFAULT_GENERATE_KEY_PAIR`   | `True`  | Generate key pair on initialization by default            |
| `DEFAULT_DERIVATE_PUBLIC_KEY` | `False` | Derivate the public key out of the private key by default |

## Classes

### `RSAWrapper`

#### Definition

```
class RSAWrapper(
    key_size: int = DEFAULT_RSA_KEY_SIZE,
    generate_key_pair: bool = DEFAULT_GENERATE_KEY_PAIR
)
```

> Provides [RSA encryption](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) functionality

_Parameters_ :

- `key_size` : The RSA key size, exprimed in bits. Must be a multiple of 2
- `generate_key_pair` : Generate RSA key pair on initialization or not

#### Methods

    generateKeyPair(self) -> None

> Generate the RSA key pair

_Parameters_ :

- None

_Return value_ :

- None

---

    getKeySize() -> int

> Get the local key size

_Parameters_ :

- None

_Return value_ :

- The key size exprimed in bytes

---

    getPublicKey(pem_format: bool = True) -> str | bytes

> Get the local public key

_Parameters_ :

- `pem_format` : `True` to return the local public key in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), `False` to return it as a byte sequence

_Return value_ :

- The local public key

---

    getPrivateKey(pem_format: bool = True) -> str | bytes

> Get the local private key

_Parameters_ :

- `pem_format` : `True` to return the local key in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), `False` to return it as a byte sequence

_Return value_ :

- The local private key

---

    getRemotePublicKey(pem_format: bool = True) -> None | str | bytes

> Get the client public key

_Parameters_ :

- `pem_format` : `True` to return the client public key in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), `False` to return it as a byte sequence

_Return value_ :

- The client public key, or `None` if there is none

---

    setPublicKey(public_key: str | bytes, pem_format: bool = True) -> None

> Set the local public key

_Parameters_ :

- `public_key` : The public key, in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if the parameter `pem_format` is set to `True`, in a byte sequence otherwise
- `pem_format` : Specify the format of the key in the parameter `public_key`. The key must be in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if set to `True`, in a byte sequence otherwise

_Return value_ :

- None

**NOTE** : The intern private key will be deleted in the process, you must use `setPrivateKey` to set the affiliated private key.

---

    setPrivateKey(
        private_key: str | bytes,
        pem_format: bool = DEFAULT_PEM_FORMAT,
        derivate_public_key: bool = DEFAULT_DERIVATE_PUBLIC_KEY
    ) -> None

> Set the local private key

_Parameters_ :

- `private_key` : The private key, in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if the parameter `pem_format` is set to `True`, in a byte sequence otherwise
- `pem_format` : Specify the format of the key in the parameter `private_key`. The key must be in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if set to `True`, in a byte sequence otherwise
- `derivate_public_key` : Derivate the public key out of the private key or not

_Return value_ :

- None

---

    setRemotePublicKey(
        remote_public_key: str | bytes,
        pem_format: bool = DEFAULT_PEM_FORMAT,
    ) -> None

> Set the client public key

_Parameters_ :

- `remote_public_key` : The remote public key, in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if the parameter `pem_format` is set to `True`, in a byte sequence otherwise
- `pem_format` : Specify the format of the key in the parameter `private_key`. The key must be in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if set to `True`, in a byte sequence otherwise

_Return value_ :

- None

---

    encryptData(
        data: str | bytes,
        encode: bool = True,
        use_local_public_key: bool = False
    ) -> bytes

> Encrypt data

_Parameters_ :

- `data` : The data to encrypt. It can be a string or a byte sequence
- `encode` : Specify if the content in parameter `data` must be encoded before being processed (mus be set to `True` only if the parameter `data` is a string)
- `use_local_public_key` : Specify if the local public key must be used for encryption instead of the remote public key

_Return value_ :

- The encrypted `data` content as a byte sequence

_Possible raise classes_ :

- `RuntimeError`

**NOTE** : If the parameter `use_local_public_key` is set to `False`, the remote public key must be set (`RuntimeError` will be raised otherwise)

---

    decryptData(cipher: bytes, decode: bool = True) -> str | bytes

> Decrypt data

_Parameters_ :

- `cipher` : The encrypted cipher text as a byte sequence
- `decode` : Specify if the decrypted data should be decoded before being returned

_Return value_

- The decrypted `data` content as a string or a byte sequence according to the value of `decode`

---

```
signData(data: str | bytes, encode: bool = True) -> bytes
```

> Sign a block of data

_Parameters_ :

- `data` : The data to sign
- `encode` : Specify if the content in parameter `data` must be encoded before being processed (set to `True` only if the parameter `data` is a string)

_Peturn value_ :

- The signed data, as a byte sequence

---

```
verifyDataSignature(
    signature: bytes,
    data: str | bytes,
    encode: bool = True
) -> bool
```

> Verify the authenticity of a signed block of data

_Parameters_ :

- `signature` : The signed data, as a byte sequence
- `data` : The data to verify
- `encode` : Specify if the content in parameter `data` must be encoded before being processed (set to `True` only if the parameter `data` is a string)

_Peturn value_ :

- A boolean value : `True` if the data and its signature are authentic, `False` otherwise

### `AESWrapper`

#### Definition

    class AESWrapper(key_size: int = DEFAULT_AES_KEY_SIZE)

> Provides [AES encryption](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) functionality

_Parameters_ :

- `key_size` : The AES key size, exprimed in bytes. Must be 16, 24 or 32 bytes long

#### Methods

    getKeySize() -> int

> Get the key size

_Parameters_ :

- None

_Return value_ :

- The AES key size exprimed in bytes, as an integer

---

    getKey() -> bytes

> Get the AES key

_Parameters_ :

- None

_Return value_ :

- The AES key as a byte sequence

---

    getIv() -> bytes

> Get the [Initialisation Vector](https://en.wikipedia.org/wiki/Initialization_vector) (Iv)

_Parameters_ :

- None

_Return value_ :

- The IV as a 16 byte sequence

---

    setKey(key: bytes, iv: bytes = None) -> None

> Set the AES key

_Parameters_ :

- `key` : The AES key, as a byte sequence. Must be 16, 24 or 32 bytes long
- `iv` : The [Initialisation Vector](https://en.wikipedia.org/wiki/Initialization_vector). Must be 16 bytes long

_Return value_ :

- None

**NOTE** : If the parameter `iv` is not set, it will be automatically generated

---

    encryptData(data: str | bytes, encode: bool = True) -> bytes

> Encrypt data

_Parameters_ :

- `data` : The data to encrypt. It can be a string or a byte sequence
- `encode` : Specify if the content in parameter `data` must be encoded before being processed (set to `True` only if the parameter `data` is a string)

_Return value_ :

- The `data` as a byte sequence

---

    decryptData(self, cipher: bytes, decode: bool = True) -> str | bytes

> Decrypt data

_Parameters_:

- `cipher`: The encrypted cipher text as a byte sequence
- `decode`: Specify if the decrypted data should be decoded before being returned

_Return value_

- The decrypted `data` content as a string or a byte sequence according to the value of `decode`
