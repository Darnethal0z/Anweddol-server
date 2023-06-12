# ISO management

----

In order to provice a valid service, containers domains needs to run with a specific ISO image.

This ISO image is actually a custom live Debian image, with pre-installed utility softwares (text editors, programming environment, network tools, ...) for the user.
See the [ISO factory repository](https://github.com/the-anweddol-project/Anweddol-ISO-factory) to get the script that creates these ISO images.

## Official mirror

Containers ISO images are actually provided via a mirror URL that you can retrieve on the official website [permalink resource file](https://the-anweddol-project.github.io/resources/mirror.txt).

This resource file contains a container ISO mirror URL with this file tree : 

```
.
├── anweddol_container.iso
├── md5sum.txt
├── sha256sum.txt
└── version.txt
```

- `anweddol_container.iso` is the actual container ISO image.
- `md5sum.txt` contains the MD5 checksum of `anweddol_container.iso`
- `sha256sum.txt` contains the SHA256 checksum of `anweddol_container.iso`
- `version.txt` is the version of the ISO. It contains an integer  which is incremented by 1 each updates.

**NOTE** : Always use the container ISO mirror URL specified in the permalink resource file, since it can be modified at any moment.