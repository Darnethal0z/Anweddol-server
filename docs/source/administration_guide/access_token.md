# Access token

----

The Anweddol server implementation can restrict its utilization by using the `tools` [Access token feature](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html) for client authentication.

An access token is a url-safe 124 characters long used on the implementation to restrict access.
These tokens are stored in a SQLite database file on the system.

```{note}
There is one token for one client, since a client cannot store 2 tokens for one same server.
```

## Prerequisites

This feature can be enabled or disabled.

Being disabled by default, you can enable it in the configuration file `/etc/anweddol/config.yaml` by changing the affiliated `enabled` field value for `True` : 

```
[...]
# ---
# Access token parameters.
access_token:

  # Enable this feature or not.
  enabled: False <----- here

  # Access token database file path.
  access_token_database_file_path: /etc/anweddol/credentials/access_token.db

[...]
```

Then restart the server.

```{warning} 
If this feature is enabled but no tokens are in the database, nobody will be able to use the server. 
```

## Add / delete a token

To add a token to the database, execute : 

```
$ anwdlserver access-tk -a
```

It will result with the created token and its entry ID on the standard output.

On the client-side, you need to record this token in order to be able to authenticate.
See the [Client usage guide](https://anweddol-client.readthedocs.io/en/latest/usage_guide/index.html) to learn more.

```{warning}
Since the access tokens are hashed in the database (see the technical specifications [Access token](../technical_specifications/tools/access_token.md) section to learn more), there's no way to see them again in plain text : Store this plain token somewhere safe in order to use it for further operations.
```

If you want to delete a token, execute : 

```
$ anwdlserver access-tk -r <entry_id>
```

## Enable / Disable a token

You have the possibility to enable or disable recorded tokens to temporarily disable its usage.

To disable a token, execute : 

```
$ anwdlserver access-tk -d <entry_id>
```

And to re-enable it : 

```
$ anwdlserver access-tk -e <entry_id>
```