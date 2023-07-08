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

**NOTE** : If the pip installation is launched with non-root permissions, only the `anwdlserver` package will be installed : the full setup will be skipped.

## Environment setup

### Libvirt

[Libvirt](https://libvirt.org/) is a toolkit to manage virtualization platforms that the server is using to manage container domains.

#### Installation

Libvirt must be installed via your package manager : 

Apt : 

```
$ sudo apt-get update
$ sudo apt-get install python-libvirt
```

DNF :

```
$ sudo dnf install python-libvirt
```

Yum :

```
$ sudo yum install python-libvirt
```

**NOTE** : You can also install it from pip by executing : 

```
$ pip install libvirt-python
```

But you need to install build dependencies manually, and this topic is not covered in this documentation.

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

(source : [ostechnix](https://ostechnix.com/solved-cannot-access-storage-file-permission-denied-error-in-kvm-libvirt/))

### Networking

For the containers to be able to communicate with the outside, the host system must have a bridge interface linking the main network interface to the container domain's interface.

It consists of a bridge interface with the main network interface set as a slave to the bridge : 
the container domain's interface will connect to it on the runtime via TAP link.

> If the server is using a WI-FI interface as the main network interface, a more specific setup must be done before continuing (see the [debian documentation](https://wiki.debian.org/BridgeNetworkConnections#Bridging_with_a_wireless_NIC) for more).

Follow the steps below according to your system : 

#### Debian-based systems

First, you need to stop the networking service : 

```
$ service network stop
```

Then you can create the `anwdlbr0` bridge interface, replacing `MASTER_INTERFACE_NAME` by your actual master interface name : 

```
$ brctl addbr anwdlbr0
$ brctl addif anwdlbr0 MASTER_INTERFACE_NAME
```

Create persistent configuration files for your interfaces : 

```
$ printf "iface MASTER_INTERFACE_NAME inet manual" >> /etc/network/interfaces
$ printf "iface anwdlbr0 inet dhcp\n\tbridge_ports MASTER_INTERFACE_NAME" >> /etc/network/interfaces
```

Enable the `anwdlbr0` interface, and restart the networking service : 

```
$ ifup anwdlbr0
$ service network start
```
 

#### Redhat-based systems

Disable NetworkManager : 

```
$ sudo chkconfig NetworkManager off
$ sudo chkconfig network on
$ sudo service NetworkManager stop
$ sudo service network start
```

Define the main network interface in networks-script, replacing `MASTER_INTERFACE_NAME` by your actual master interface name  : 

```
$ sudo printf "DEVICE=MASTER_INTERFACE_NAME\nHWADDR=$(ifconfig MASTER_INTERFACE_NAME | grep -o -E ..:..:..:..:..:..)\nONBOOT=yes\nBRIDGE=anwdlbr0\nNM_CONTROLLED=no" /etc/sysconfig/networks-script/MASTER_INTERFACE_NAME
```

Create the `anwdlbr0` bridge interface in networks-script : 

```
$ sudo printf "DEVICE=anwdlbr0\nTYPE=Bridge\nBOOTPROTO=dhcp\nONBOOT=yes\nDELAY=0\nNM_CONTROLLED=no" /etc/sysconfig/networks-script/ifcfg-anwdlbr0
```

Add sysctl rules to enable packet forwarding : 

```
$ sudo printf "net.bridge.bridge-nf-call-ip6tables = 0\nnet.bridge.bridge-nf-call-iptables = 0\nnet.bridge.bridge-nf-call-arptables = 0" >> /etc/sysctl.conf
$ sudo sysctl -p /etc/sysctl.conf
```

Add iptables rules to accept packet forwarding from bridged interfaces : 

```
$ sudo printf "-I FORWARD -m physdev --physdev-is-bridged -j ACCEPT" /etc/sysconfig/anweddol-iptables-forward-rules
$ sudo lokkit --custom-rules=ipv4:filter:/etc/sysconfig/anweddol-iptables-forward-rules
```

Restart the network service : 

```
$ sudo service network restart
```

### Container ISO

Before using the server, you need to download a specific ISO image for the container domains in order to provide a functional service. 

See the [Container ISO](container_iso.md) section to learn more.

## Getting started

At this point, you should be able to start the server. See the [Server usage section](server_usage.md) to do so.

## Anweddol server uninstallation

To uninstall the Anweddol server, execute : 

```
$ sudo anwdlserver-uninstall
```

The script will delete any files and everything associated with the Anweddol server.