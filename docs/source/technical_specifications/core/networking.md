# Networking

----

## Server

In order to let clients and containers domains communicate, the server will forward ports to these containers domains via `socat` pipes.

The ports that the server process can use with these pipes are predefined to control which port range can be assigned on the server machine.

## Container

Each container domains have an ethernet interface linked to a NAT bridge on the server, based on the `virbr0` libvirt interface by default.