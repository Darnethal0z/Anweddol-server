# Virtualization

----

## API

The Anweddol server uses the Libvirt API to manage containers.
You'll retrieve the full documentation on the [libvirt python binding](https://www.libvirt.org/docs/libvirt-appdev-guide-python/en-US/html/) documentation website.

A *container* is a libvirt domain wrapper utility running with a live debian image (see below).

The domain XML used for container domain definition is : 

```
<domain type='kvm'>
	<name>container_uuid</name>
	<memory unit='MiB'>memory</memory>
	<currentMemory unit='MiB'>memory</currentMemory>
	<vcpu placement='static'>vcpus/vcpu>
	<uuid>container_uuid</uuid>
	<os>
		<type arch='x86_64' machine='pc'>hvm</type>
		<boot dev='hd'/>
		<boot dev='cdrom'/>
	</os>
	<features>
		<acpi/>
		<apic/>
		<vmport state='off'/>
	</features>
	<clock offset='utc'>
		<timer name='rtc' tickpolicy='catchup'/>
		<timer name='pit' tickpolicy='delay'/>
		<timer name='hpet' present='no'/>
	</clock>
	<pm>
		<suspend-to-mem enabled='yes'/>
		<suspend-to-disk enabled='yes'/>
	</pm>
	<devices>
		<disk type='file' device='cdrom'>
			<driver name='qemu' type='raw'/>
			<source file='iso_path'/>
			<target dev='hda' bus='ide'/>
			<address type='drive' controller='0' bus='0' target='0' unit='0'/>
		</disk>
		<interface type='bridge'>
	        <start mode='onboot'/>
	        <source bridge='nat_interface_name'/> 
	        <model type='virtio'/>
	    </interface>
        <interface type='bridge'>
            <start mode='onboot'/>
            <source bridge='bridge_interface_name'/>
            <model type='virtio'/>
        </interface>
        <memballoon model='virtio'>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
		</memballoon>
	</devices>
</domain>
```

- `container_uuid` : The container UUID
- `memory` : The container domain memory amount
- `vcpus` : The container domain virtual CPUs amount
- `iso_path` : The ISO file path that will be used by the container domain
- `nat_interface_name` : The NAT interface name that will be used by the container domain
- `bridge_interface_name` : The bridge interface name that will be used by the container domain

## Container OS

In order to provice a valid service, containers domains needs to run with a specific ISO image.

The operating system running on containers is a custom live Debian to ensure as little data remanence as possible on the virtual domain : All basic tools like text editors, network interactions, development environment are already pre-installed to bring comfortable usage for the client.

See the [ISO factory repository](https://github.com/the-anweddol-project/Anweddol-ISO-factory) to get the script that creates these ISO images.
You can retrieve a copy of this container ISO on the [official mirror](https://mega.nz/folder/BTFyVCLB#DNC2K8Lmhgbk6QWrVpeznw).

This mirror URL contains this file tree : 

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

## Management

During a server runtime, running container coordinates created for clients are stored in memory to manage them.

If a container is shut down, a routine will detect that its domain is not active, and will delete the container's presence in memory and database to prevent ghosted credentials.

Containers are identified with an UUID4 format string, and their [libvirt domains UUID](https://libvirt.gitlab.io/libvirt-appdev-guide-python/libvirt_application_development_guide_using_python-Guest_Domains-Information-UUID.html) are the same one.

## Administration

When a container is started, the server first waits for the network to be available inside.
Then, the server generates new user coordinates and a new listen port that the container will use for client service.

On every container a specific user is defined called **endpoint**. 

This is a user dedicated to container administration that the server will interact via SSH to administrate it (it is actually calling a bash script inside that you can retrieve on the ISO factory [github repository](https://github.com/the-anweddol-project/Anweddol-ISO-factory)). Its default password is `endpoint`, and the container default SSH server is listening on the conventional port (80).

The bash script executes 3 tasks : 

- Create the new specified user that the client will use ;
- Set up the new SSH listen port ;
- Disabling the endpoint user once its task is executed ;

The username is in the format `user_NUM`, where NUM is a random number between 10000 and 90000.
The user password is a 120 character string.
The new listen port is a random port between 10000 and 15000, whose bindability is checked before assignation.

When the script will be called, the container will only accept SSH connections with the newly created user, since the endpoint user will be disabled in the process.