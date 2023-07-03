# CLI JSON output

----

In order to communicate with other programs in an easy way, the Anweddol server CLI provides a JSON output feature that allows [inter-program communication](https://clig.dev/#simple-parts-that-work-together.

## Global structure

Each commands with the `--json` parameter results on a single JSON structure printed on `stdout` : 

```
{
	"status": STATUS
	"message": MESSAGE
	"data": DATA
}
```

- `STATUS` : The result status, it can be `"OK"` if there was no errors during the process, `"ERROR"` otherwise.
- `MESSAGE` : The message according to the command purpose.
- `DATA` : A dictionary containing every exploitable informations that a command can generate.

The `DATA` dictionary content changes according to the command context (see below).

**NOTE** : Configuration file related errors arent produced in a JSON format.

## Specific result JSON structures

### Errors

When an error is raised during the process with any `--json` parameter set with subcommands, the output JSON will be : 

```
{
	"status": "ERROR",
	"message": "An error occured",
	"data": {
		"error": ERROR
	}
}
```

- `ERROR` : The error message that occured

### `start` sub-command

`anwdlserver start` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Server is started",
	"data": {}
}
```

**NOTE** : If the option `-d` is set, no output will be displayed.

If the option `-c` is set : 

```
{
	"status": "OK",
	"message": "Check done",
	"data": {
		"errors_recorded": ERRORS_RECORDED, 
		"errors_list": ERRORS_LIST
	}
}
```

If an error occured during server environment verification, the JSON structure looks like this : 

```
{
	"status": "ERROR",
	"message": "Errors detected on server environment",
	"data": {
		"errors_recorded": ERRORS_RECORDED, 
		"errors_list": ERRORS_LIST
	}
}
```

- `ERRORS_RECORDED` : The amount of errors recorded
- `ERRORS_LIST` : The errors messages list

### `stop` sub-command

`anwdlserver stop` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Server is stopped",
	"data": {}
}
```

### `restart` sub-command

`anwdlserver restart` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Server is started",
	"data": {}
}
```

### `dl-iso` sub-command

`anwdlserver dl-iso` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "ISO image was successfully downloaded",
	"data": {
		"checksums": CHECKSUMS,
		"version": VERSION,
		"file_path": FILE_PATH
	}
}
```

- `CHECKSUMS` : The downloaded ISO MD5 and SHA256 checksums, in a list
- `VERSION` : The downloaded [ISO version](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/iso_management.html#official-mirror)
- `FILE_PATH` : The downloaded ISO file path

if the option `-m` is set : 

```
{
	"status": "OK",
	"message": "Remote ISO metadata",
	"data": {
		"checksums": CHECKSUMS,
		"version": VERSION,
	}
}
``` 

- `CHECKSUMS` : The downloaded ISO MD5 and SHA256 checksums, in a list
- `VERSION` : The downloaded [ISO version](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/iso_management.html#official-mirror)

### `access-tk` sub-command

`anwdlserver access-tk -a` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "New access token created",
	"data": {
		"entry_id": ENTRY_ID,
		"access_token": ACCESS_TOKEN,
	}
}
``` 

- `ENTRY_ID` : The created entry ID
- `ACCESS_TOKEN` : The new access token, in plain text

`anwdlserver access-tk -l` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Recorded entries ID",
	"data": {
		"entry_list": ENTRY_LIST
	}
}
``` 

- `ENTRY_LIST` : The recorded entries list

`anwdlserver access-tk -r` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Entry ID was deleted",
	"data": {}
}
``` 

`anwdlserver access-tk -e` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Entry ID was enabled",
	"data": {}
}
``` 

`anwdlserver access-tk -d` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "Entry ID was disabled",
	"data": {}
}
```

### `regen-rsa` sub-command

`anwdlserver regen-rsa` with the `--json` parameter will result in :

```
{
	"status": "OK",
	"message": "RSA keys re-generated",
	"data": {
		"fingerprint": FINGERPRINT
	}
}
```

- `FINGERPRINT` : The new generated public key's SHA256 digest