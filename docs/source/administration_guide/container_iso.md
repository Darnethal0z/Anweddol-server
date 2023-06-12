# Container ISO

----

In order to provice a valid service, containers domains needs to run with a specific ISO image.

## Download the ISO image

This ISO image is actually a custom live Debian image that you can retrieve on the official mirror, you can download it from the CLI by executing : 

```
$ sudo anwdlserver dl-iso
```

By default, the downloaded ISO is stored on `/etc/anweddol/iso/anweddol_container.iso`, you can change this by editing the `container_iso_path` field on the configuration file.

You can also specify a custom ISO mirror URL it with the `-u` parameter  

```
$ sudo anwdlserver dl-iso -u https://example.com/url/of/the/mirror/root
```

Learn more about the container ISO on the technical specifications [ISO management section](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/iso_management.html#official-mirror).
