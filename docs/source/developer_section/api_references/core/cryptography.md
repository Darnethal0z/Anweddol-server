# Cryptography

---

## class *RSAWrapper*

### Definition

```{class} anwdlserver.core.crypto.RSAWrapper(generate_key_pair: bool)
```

Provides [RSA encryption](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) functionality.

**Parameters** :

> ```{attribute} generate_key_pair
> > Type : bool
> 
> `True` to generate RSA key pair on initialization, `False` otherwise. Default is `True`.
> ```

```{note}
When the parameter `generate_key_pair` is set to `True`, a key pair will be generated with the default parameters (see `generateKeyPair()` method definition below).
```

### General usage

```{classmethod} getKeySize()
```

Get the bit length of the local public key modulus.

**Parameters** : 

> None.

**Return value** : 

> The key size exprimed in bytes, or `None` if there is none.

---

```{classmethod} getPublicKey(pem_format)
```

**Description** :

Get the local public key.

**Parameters** :

> ```{attribute} pem_format
> > Type : bool
> 
> `True` to return the local public key in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), `False` to return it as a byte sequence. Default is `True`.
> ```

**Return value** : 

> The local public key, or `None` if there is none.

---

```{classmethod} getPrivateKey(pem_format)
```

Get the local private key.

**Parameters** :

> ```{attribute} pem_format
> > Type : bool
> 
> `True` to return the local public key in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), `False` to return it as a byte sequence. Default is `True`.
> ```

**Return value** : 

> The local private key, or `None` if there is none.

---

```{classmethod} getRemotePublicKey(pem_format)
```

Get the client public key.

**Parameters** :

> ```{attribute} pem_format
> > Type : bool
> 
> `True` to return the local public key in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), `False` to return it as a byte sequence. Default is `True`.
> ```

**Return value** : 

> The client public key, or `None` if there is none.

---

```{classmethod} setPublicKey(public_key, pem_format)
```

Set the local public key.

**Parameters** :

> ```{attribute} public_key
> > Type : str | bytes
> 
> The public key, in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if the parameter `pem_format` is set to `True`, in a byte sequence otherwise.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setPrivateKey(private_key, pem_format, derivate_public_key)
```

Set the local private key.

**Parameters** :

> ```{attribute} private_key
> > Type : str | bytes
> 
> The private key, in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if the parameter `pem_format` is set to `True`, in a byte sequence otherwise.
> ```

> ```{attribute} pem_format
> > Type : bool
> 
> `True` to specify the format of the key in the parameter `private_key` in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), in a byte sequence otherwise. Default is `True`.
> ```

> ```{attribute} derivate_public_key
> > Type : bool
> 
> Derivate the public key out of the private key in the parameter `private_key` or not. Default is `False`.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setRemotePublicKey(remote_public_key, pem_format)
```

Set the remote public key.

**Parameters** :

> ```{attribute} remote_public_key
> > Type : str | bytes
> 
> The remote public key, in [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/) if the parameter `pem_format` is set to `True`, in a byte sequence otherwise.
> ```

> ```{attribute} pem_format
> > Type : bool
> 
> `True` to specify the format of the key in the parameter `remote_public_key` in a [PEM format](https://www.howtogeek.com/devops/what-is-a-pem-file-and-how-do-you-use-it/), in a byte sequence otherwise. Default is `True`.
> ```

**Return value** : 

> `None`.

### Key generation

```{classmethod} generateKeyPair(public_exponent, key_size)
```

Generate the RSA key pair.

**Parameters** :

> ```{attribute} pem_format
> > Type : int
> 
> The public exponent to use. Default is `65537`.
> ```

> ```{attribute} key_size
> > Type : int
> 
> The RSA key size exprimed in bits, must be a multiple of 2. Default is `4096`.
> ```

**Return value** : 

> `None`.

### Encryption and decryption

```{classmethod} encryptData(data, use_local_public_key)
```

Encrypt a buffer of data.

**Parameters** :

> ```{attribute} data
> > Type : str | bytes
> 
> The data to encrypt. It can be a string or a byte sequence.
> ```

> ```{attribute} use_local_public_key
> > Type : bool
> 
> `True` to specify if the local public key must be used for encryption instead of the remote public key, `False` otherwise. Default is `False`.
> ```

**Return value** : 

> The encrypted `data` content as a byte sequence.

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if the local public key or the remote public key is not set.
> ```

---

```{classmethod} decryptData(cipher, decode)
```

Decrypt data.

**Parameters** :

> ```{attribute} cipher
> > Type : bytes
> 
> The encrypted cipher text as a byte sequence.
> ```

> ```{attribute} decode
> > Type : bool
> 
> `True` to specify if the decrypted data should be decoded before being returned, `False` otherwise. Default is `True`.
> ```

**Return value** : 

> The decrypted `data` content as a string or a byte sequence according to the value of `decode`

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if the local private key is not set.
> ```

### Signature and verification

```{classmethod} signData(data)
```

Sign a block of data.

**Parameters** :

> ```{attribute} data
> > Type : str | bytes
> 
> The clear data to sign. It can be a string or a byte sequence.
> ```

**Return value** : 

> The signed data, as a byte sequence.

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if the local private key is not set.
> ```

---

```{classmethod} verifyDataSignature(signature, data)
```

Verify the authenticity of a signed block of data.

**Parameters** :

> ```{attribute} signature
> > Type : bytes
> 
> The signed data, as a byte sequence.
> ```
  
> ```{attribute} data
> > Type : str | bytes
> 
> The clear data to verify. It can be a string or a byte sequence.
> ```

**Return value** : 

> `True` if the data and its signature are authentic, `False` otherwise.

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if the local public key is not set.
> ```

## class *AESWrapper*

### Definition

```{classmethod} anwdlserver.core.crypto.AESWrapper(key_size)
```

Provides [AES encryption](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) functionality.

**Parameters** :

> ```{attribute} key_size
> > Type : int
> 
> The AES key size, exprimed in bits. Default is `256`.
> ```

### General usage

```{classmethod} getKeySize()
```

Get the key size.

**Parameters** : 

> None.

**Return value** : 

> The AES key size exprimed in bits.

---

```{classmethod} getKey()
```

Get the AES key and the IV.

**Parameters** : 

> None.

**Return value** : 

> A tuple representing the actual AES key and the IV : 

> ```
> (
>     KEY,
>     IV,
> )
> ```

> - *KEY*
>   
>   The AES key.
> 
> - *IV*
> 
>   The affiliated IV.

---

```{classmethod} setKey(key, iv)
```

Set the AES key.

**Parameters** :

> ```{attribute} key
> > Type : bytes
> 
> The AES key, as a byte sequence. Must be 16, 24 or 32 bytes long.
> ```

> ```{attribute} iv
> > Type : bytes
> 
> The [Initialisation Vector](https://en.wikipedia.org/wiki/Initialization_vector). Must be 16 bytes long. Default is `None`.
> ```

**Return value** : 

> `None`.

```{note} 
If the parameter `iv` is set to `None`, it will be automatically generated.
```

### Encryption and decryption

```{classmethod} encryptData(data)
```

Encrypt data.

**Parameters** :

> ```{attribute} data
> > Type : str | bytes
> 
> The data to encrypt. It can be a string or a byte sequence.
> ```

**Return value** : 

> The `data` as a byte sequence.

---

```{classmethod} decryptData(cipher, decode)
```

Decrypt data.

**Parameters** :

> ```{attribute} cipher
> > Type : bytes
> 
> The encrypted cipher text as a byte sequence.
> ```

> ```{attribute} decode
> > Type : bytes
> 
> Specify if the decrypted data should be decoded before being returned. Default is `True`
> ```

**Return value** : 

> The decrypted `data` content as a string or a byte sequence according to the value of `decode`.
