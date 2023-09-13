# Installation

----

This section covers the prerequisites needed for the system before the Anweddol server installation.

## Anweddol server installation

Install the Anweddol server by the sources :

```
$ git clone https://github.com/the-anweddol-project/Anweddol-server.git
$ cd Anweddol-server
$ sudo pip install .
```

The nessessary files and users will be created during the installation.

```{warning}
If the pip installation is launched with non-root permissions, only the `anwdlserver` package will be installed : the full setup will be skipped.
```

### Libvirt

[Libvirt](https://libvirt.org/) is a toolkit to manage virtualization platforms that the server is using to manage container domains.

#### Installation

Libvirt and qemu must be installed via your package manager : 

Apt : 

```
$ sudo apt-get update
$ sudo apt-get install libvirt-daemon-system python-libvirt
```

DNF :

```
$ sudo dnf install libvirt python-libvirt
```

Yum :

```
$ sudo yum install libvirt python-libvirt
```

#### Setup

You need to modify the `/etc/libvirt/qemu.conf` file to give libvirt appropriate rights.

Edit the `/etc/libvirt/qemu.conf` file : 

```
$ sudo nano /etc/libvirt/qemu.conf
```

Find the `user` and `group` directives. By default, both are set to `root` :

```
[...] 
Some examples of valid values are:
#
user = "qemu"   # A user named "qemu"
user = "+0"     # Super user (uid=0)
user = "100"    # A user named "100" or a user with uid=100
#
#user = "root"
The group for QEMU processes run by the system instance. It can be
specified in a similar way to user.
#group = "root"
[...]
```

Uncomment both lines and replace `root` with `anweddol` and the group with `libvirt` as shown below:

```
[...] 
Some examples of valid values are:
#
user = "qemu"   # A user named "qemu"
user = "+0"     # Super user (uid=0)
user = "100"    # A user named "100" or a user with uid=100
#
user = "anweddol"
The group for QEMU processes run by the system instance. It can be
specified in a similar way to user.
group = "libvirt"
[...]
```

Then restart the libvirtd daemon :

``` 
$ sudo systemctl restart libvirtd.service
```

```{note}
If you want to use the Anweddol server API for external programming, you can replace `anweddol` with the user of your choice. Also make sure that this user is part of the `libvirt` group.
```

(source : [ostechnix](https://ostechnix.com/solved-cannot-access-storage-file-permission-denied-error-in-kvm-libvirt/))

### Networking

To enable clients to communicate with containers, the server includes a port forwarding system that will be managed with [socat](https://linux.die.net/man/1/socat).

If not already installed, install `socat` via your local package manager : 

Apt : 

```
$ sudo apt-get install socat
```

DNF :

```
$ sudo dnf install socat
```

Yum :

```
$ sudo yum install socat
```

Containers will use a bridge interface called `virbr0` as internal NIC which is affiliated to the `libvirtd` daemon.

To create the `virbr0` interface, you need to start the `libvirtd` daemon (previously installed) : 

```
$ sudo systemctl start libvirtd.service
```

The containers should now have a functional interface at disposal.

Note that you can modify the port forwarding feature behaviour on the [configuration file](configuration_file.md), `port_forwarding` section.

### Container ISO

Before using the server, you need to download a specific ISO image for the container domains in order to provide a functional service. 

See the [Container ISO](container_iso.md) section to learn more.

## Getting started

At this point, you should be able to start the server. See the [Server usage section](server_usage.md) to do so.

## Anweddol server uninstallation

To uninstall the Anweddol server, an `uninstall.sh` script exists on the root of the package, execute it as root to delete any files and everything associated with the Anweddol server.