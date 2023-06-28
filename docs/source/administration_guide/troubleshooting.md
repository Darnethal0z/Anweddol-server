# Troubleshooting

----

Here is a list of non-exhaustive potential problems that can be encountered while using the Anweddol server : 

## [...]`Libvirt : Permission denied`

*Description* : The libvirt API failed to access or create a resource due to the lack of permissions.

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

## [...] `authentication unavailable: no polkit agent available to authenticate action 'org.libvirt.unix.manage'`

*Description* : The user `anweddol` is not on the `libvirt` group.

*Solution* : 

Set the user `anweddol` in the `libvirt` group:

```
$ sudo usermod -aG libvirt anweddol
```