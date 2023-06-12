# Networking

----

## Server

In order to let clients and containers communicate, the server needs a specific interface.

A bridge interface `anwdlbr0` must be created on the server, with its current physical network interface configured as a slave on it. Containers will connect via TAP on this bridge, ensuring full-bridged networking for the container.

> Read the 'Administration guide' for more info.

## Container

Each container have two network interfaces : 
- A NAT interface ;
- A bridged interface ;

-> The NAT interface is used for server administration.  
It is an interface based on the `virbr0` libvirt virtual bridge.

-> The bridged interface is used to receive client traffic. 
It is based on the manually created bridge on the system (see above), thus providing full-bridged networking.
