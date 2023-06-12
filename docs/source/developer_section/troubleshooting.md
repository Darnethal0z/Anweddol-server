# Troubleshooting

----

Here is a list of non-exhaustive potential problems that can be encountered while using the Anweddol server API :

## `libvirt:  error : Cannot get interface MTU on 'virbr0'`[...]

*Description* : The libvirt daemon is not started.

*Solution* : 

Start the libvirtd daemon : 

```
$ sudo systemctl start libvirtd.service
```

Then restart your script.