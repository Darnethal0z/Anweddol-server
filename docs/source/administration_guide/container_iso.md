# Container ISO

----

In order to provice a valid service, containers domains needs to run with a specific ISO image.

## Download the ISO image

This ISO image is actually a custom live Debian image that you can retrieve on the [official mirror](https://mega.nz/folder/BTFyVCLB#DNC2K8Lmhgbk6QWrVpeznw).

```{tip}
You can easily download files via the CLI with the [MEGAcmd tool](https://github.com/meganz/MEGAcmd). See its [Usage guide](https://github.com/meganz/MEGAcmd/blob/master/UserGuide.md) for more informations.
```

You'll need to copy the downloaded `anweddol_container.iso` file on the `/etc/anweddol/iso/` folder by default, or you can specify the ISO path in the configuration file, in the `container_iso_path` key.

```{note}
This ISO image is meant to be replaced at each update announced
```

Learn more about the container ISO on the technical specifications [Container OS section](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#container-os).
