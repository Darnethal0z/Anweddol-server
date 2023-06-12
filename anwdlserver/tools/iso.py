"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    Container ISO management features

"""
import requests
import hashlib


# Default values
DEFAULT_CONTAINER_ISO_FILE_NAME = "anweddol_container.iso"
DEFAULT_MD5SUM_FILE_NAME = "md5sum.txt"
DEFAULT_SHA256_FILE_NAME = "sha256sum.txt"
DEFAULT_VERSION_FILE_NAME = "version.txt"


class RemoteISOManager:
    def __init__(
        self,
        permalink_resource_file_url: str = None,
        container_iso_mirror_url: str = None,
    ):
        self.permalink_resource_file_url = permalink_resource_file_url
        self.container_iso_mirror_url = container_iso_mirror_url
        self.downloaded_iso_file_path = None

    def getPermalinkResourceFileURL(self) -> str:
        return self.permalink_resource_file_url

    def getContainerISOMirrorURL(self) -> str:
        return self.permalink_resource_file_url

    def getPermalinkResourceFileURLContent(self) -> str:
        if not self.permalink_resource_file_url:
            raise ValueError("Permalink resource file URL must be set")

        with requests.get(self.permalink_resource_file_url) as req:
            return req.content.decode()

    def getRemoteISOChecksums(self) -> tuple:
        if not self.container_iso_mirror_url:
            raise ValueError("Container ISO mirror URL must be set")

        with requests.get(
            self.container_iso_mirror_url + DEFAULT_MD5SUM_FILE_NAME
        ) as req:
            remote_iso_md5 = req.content.decode()

        with requests.get(
            self.container_iso_mirror_url + DEFAULT_SHA256_FILE_NAME
        ) as req:
            remote_iso_sha256 = req.content.decode()

        return (remote_iso_md5.split(" ")[0], remote_iso_sha256.split(" ")[0])

    def getRemoteISOVersion(self) -> int:
        if not self.container_iso_mirror_url:
            raise ValueError("Container ISO mirror URL must be set")

        with requests.get(
            self.container_iso_mirror_url + DEFAULT_VERSION_FILE_NAME
        ) as req:
            return int(req.content.decode())

    def setPermalinkResourceFileURL(self, permalink_resource_file_url: str) -> None:
        self.permalink_resource_file_url = permalink_resource_file_url

    def setContainerISOMirrorURL(self, container_iso_mirror_url: str) -> None:
        self.container_iso_mirror_url = container_iso_mirror_url

    def downloadRemoteISO(self, output_file: str) -> None:
        if not self.container_iso_mirror_url:
            raise ValueError("Container ISO mirror URL must be set")

        # Download the remote ISO in stream mode with 16384 bytes buffer
        with requests.get(
            self.container_iso_mirror_url + DEFAULT_CONTAINER_ISO_FILE_NAME, stream=True
        ) as req:
            if req.status_code >= 300:
                raise RuntimeError(
                    f"Status {req.status_code} for {self.container_iso_mirror_url + DEFAULT_CONTAINER_ISO_FILE_NAME}"
                )

            with open(output_file, "wb") as fd:
                for buffer in req.iter_content(chunk_size=16 * 1024):
                    fd.write(buffer)

        self.downloaded_iso_file_path = output_file

    def makeISOChecksum(self, iso_path: str = None) -> str:
        hasher = hashlib.sha256()

        with open(
            self.downloaded_iso_file_path if not iso_path else iso_path, "rb"
        ) as fd:
            hasher.update(fd.read())

        return hasher.hexdigest()
