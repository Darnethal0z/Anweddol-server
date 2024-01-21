# Troubleshooting

----

Here is a list of non-exhaustive potential problems that can be encountered while using the Anweddol server : 

## *[...]Libvirt : Permission denied*

*Description* : 

The libvirt API failed to access or create a resource due to the lack of permissions.

*Solution* : 

See the Installation [setup section](installation.md) to learn more.

If the problem persists, try to disable the SELinux enforce feature : 

```
$ sudo setenforce 0
```

Do not forget to re-enable it when unused : 

```
$ sudo setenforce 1
```

## *[...]authentication unavailable: no polkit agent available to authenticate action 'org.libvirt.unix.manage'*

*Description* : 

The user `anweddol` is not on the `libvirt` group.

*Solution* : 

Set the user `anweddol` in the `libvirt` group:

```
$ sudo usermod -aG libvirt anweddol
```

## Interface '[...]' does not exists on system

*Description* : 

The specified network interface does not exists on system.

*Solution* : 

Create it, or if the interface in question is the default `virbr0`, you need to start the `libvirtd` daemon to make in appear : 

```
$ sudo systemctl start libvirtd.service
```

The `virbr0` interface should now exists, check with `ip a`.

## *unsupported configuration: Emulator '[...]' does not support virt type '[...]'*

*Description* : 

Your actual environment cannot run KVM or the actual virt type.

*Solution* : 

By default, the domain type is `'kvm'`. To check if your CPU supports it, you can execute : 

```
$ egrep -c '(vmx|svm)' /proc/cpuinfo
```

If `0` shows up, it means that your actual CPU does not support hardware virtualization: To fix this, you can change the `domain_type` key value in the configuration file (`container` section) to another type, like `qemu`.

Additionally, you can check if virtualization support is enabled in the BIOS.