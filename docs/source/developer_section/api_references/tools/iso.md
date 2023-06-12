# Container ISO management

----

> Container ISO management features

> Package `anwdlserver.tools.iso`

## Constants

Default values :

| Name                            | Value                    | Description                                          |
| ------------------------------- | ------------------------ | ---------------------------------------------------- |
| DEFAULT_CONTAINER_ISO_FILE_NAME | "anweddol_container.iso" | The default remote ISO file name                     |
| DEFAULT_MD5SUM_FILE_NAME        | "md5sum.txt"             | The default remote ISO MD5 checksum file name        |
| DEFAULT_SHA256_FILE_NAME        | "sha256sum.txt"          | The default remote ISO SHA256 checksum file name     |
| DEFAULT_VERSION_FILE_NAME       | "version.txt"            | The default remote ISO version file name             |

## Classes

### `RemoteISOManager`

#### Definition

```
class RemoteISOManager(permalink_resource_file_url: str = None, container_iso_mirror_url: str = None)
```

> Provides remote container ISO management features

_Parameters_ : 

- `permalink_resource_file_url` : The [permalink resource file](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html#tokens) URL to use
- `container_iso_mirror_url` : The container ISO mirror URL to interact with. Must point to the root of the mirror

#### Methods

```
getPermalinkResourceFileURL() -> str
```

> Get the permalink resource file URL

_Parameters_ : 

- None

_Return value_ : 

- The instance [permalink resource file](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html#tokens) URL

---

```
getContainerISOMirrorURL() -> str
```

> Get the container ISO mirror URL

_Parameters_ : 

- None

_Return value_ : 

- The instance [container ISO mirror](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html#tokens) URL

---

```
getPermalinkResourceFileURLContent() -> str
```

> Get the remote permalink resource file URL content

_Parameters_ : 

- None

_Return value_ : 

- The remote permalink resource file URL content, leading to the actual official container ISO mirror URL (see the technical specifications [ISO management](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html#tokens) section for more)

```
getRemoteISOChecksums() -> tuple
```

> Get the remote ISO MD5 and SHA256 checksums

_Parameters_ : 

- None

_Return value_ : 

- A tuple : 

```
(
	iso_md5,
	iso_sha256
)
```

- `iso_md5` : The remote ISO MD5 checksum
- `iso_sha256` : The remote ISO SHA256 checksum

---
```
getRemoteISOVersion() -> int
```

> Get the remote ISO version

_Parameters_ : 

- None

_Return value_ : 

- The remote ISO version, as an integer

---
```
setPermalinkResourceFileURL(permalink_resource_file_url: str) -> None
```

> Set the permalink resource file URL content

_Parameters_ : 

- `permalink_resource_file_url` : The permalink resource file URL to set

_Return value_ : 

- None

---
```
setContainerISOMirrorURL(container_iso_mirror_url: str) -> None 
```

> Set the container ISO mirror URL

_Parameters_ : 

- `container_iso_mirror_url` : The container ISO mirror URL to set

_Return value_ : 

- None

---
```
downloadRemoteISO(output_file: str) -> None
```

> Download the remote ISO

_Parameters_ : 

- `output_file` : The output file

_Return value_ : 

- None

**NOTE** : When this methods ends, the parameter `output_file` content is stored on the instance for the `makeISOChecksum` method

---
```
makeISOChecksum(iso_path: str = None) -> str
```

> Make the ISO SHA256 checksum

_Parameters_ : 

- `iso_path` : The ISO path

_Return value_ : 

- The SHA256 checksum of the specified ISO

**NOTE** : If the parameter `iso_path` is `None`, the stored output file from the `downloadRemoteISO` method will be used