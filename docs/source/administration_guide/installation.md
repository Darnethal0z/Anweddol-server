# Installation

----

## Nessessary packages

1. Install every needed dependancies with your package manager : 

> Apt : 
> 
> ```
> $ sudo apt-get update
> $ sudo apt-get install libvirt-daemon-system python-libvirt socat python-pip
> ```

> DNF :
> 
> ```
> $ sudo dnf install libvirt python-libvirt socat python-pip
> ```

> Yum :
> 
> ```
> $ sudo yum install libvirt python-libvirt socat python-pip
> ```

2. Install the Anweddol server python package:

> ```
> $ git clone https://github.com/the-anweddol-project/Anweddol-server.git
> $ cd Anweddol-server
> $ sudo pip install .
> ```

> The nessessary files and users will be created during the installation.

> ```{warning}
> If the pip installation is launched with non-root permissions, only the `anwdlserver` package will be installed : the full environment setup will be skipped.
> ```

> ```{note}
> If a previous configuration file is found during environment setup, it will be automatically renamed as `config.yaml.old` to preserve potential old modifications.
> ```

## Setup and configuration

After that, you need to modify the `/etc/libvirt/qemu.conf` file to give libvirt appropriate rights.

3. Edit the `/etc/libvirt/qemu.conf` file : 

> ```
> $ sudo nano /etc/libvirt/qemu.conf
> ```
> 
> Find the `user` and `group` directives. By default, both are set to `root` :
> 
> ```
> [...] 
> # Some examples of valid values are:
> #
> # 	user = "qemu"   # A user named "qemu"
> # 	user = "+0"     # Super user (uid=0)
> # 	user = "100"    # A user named "100" or a user with uid=100
> #
> #user = "root"
> # The group for QEMU processes run by the system instance. It can be
> # specified in a similar way to user.
> #group = "root"
> [...]
> ```
> 
> Uncomment both lines and replace `root` with `anweddol` and the group with `libvirt` as shown below:
> 
> ```
> [...] 
> # Some examples of valid values are:
> #
> # 	user = "qemu"   # A user named "qemu"
> # 	user = "+0"     # Super user (uid=0)
> # 	user = "100"    # A user named "100" or a user with uid=100
> #
> user = "anweddol"
> # The group for QEMU processes run by the system instance. It can be
> # specified in a similar way to user.
> group = "libvirt"
> [...]
> ```
> 
> (source : [ostechnix](https://ostechnix.com/solved-cannot-access-storage-file-permission-denied-error-in-kvm-libvirt/))
> 
> ```{note}
> If you want to use the Anweddol server API for external programming, you can replace `anweddol` with the user of your choice. Also make sure that this user is part of the `libvirt` group.
> ```

## Container ISO

Before using the server, you need to download a specific ISO image for the container domains in order to provide a functional service. 

See the [Container ISO](container_iso.md) section to learn more.

## Getting started

At this point you should be able to start the server, see the [Server usage](server_usage.md) section to do so.
