# Configuration file

----

The Anweddol server implementation is using a YAML file for configuration.

It is stored in `/etc/anweddol/config.yaml` after installation, read its header to learn about it.

```{tip}
If you need to get the default configuration file back, you can retrieve it in the `resource` folder at the root of the downloaded package.
```

> ```{note}
> While setting up the Anweddol server, if a previous configuration file is found during environment setup, it will be automatically renamed as `config.yaml.old` to preserve potential old modifications.
> 
> Note that this `config.yaml.old` file is supposed to be temporary, and will be ignored if the installation process is launched a second time.
> ```