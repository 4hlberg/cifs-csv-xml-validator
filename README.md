# Cifs-csv-xml-validator

## Prerequisites
python3

## API Capabalities
GET

## How to:

*Run program in development*

This repo uses the file ```package.json``` and [yarn](https://yarnpkg.com/lang/en/) to run the required commands.

1. Make sure you have installed yarn.
2. Creata a file called ```helpers.json``` and set username and password in the following format:
```
{
    "username": "some username",
    "password": "some password",
    "hostname": "some hostname",
    "host": "some host",
    "share": "some share"
}
```
3. run:
    ```
        yarn install
    ```
4. execute to run the script:
    ```
        yarn swagger
    ```

*Run program in production*

Make sure the required env variables are defined.

*Use program as a SESAM connector*

#### System config :

```
    {
    "_id": "cifs-xml-csv-validator",
    "type": "system:microservice",
    "docker": {
        "environment": {
        "password": "$SECRET(password)",
        "username": "$ENV(username)",
        "hostname": "$ENV(hostname)",
        "host": "$ENV(host)",
        "share": "$ENV(share)"
        },
        "image": "sesamcommunity/cifs-xml-csv-validator:<some tag>",
        "port": 5000
    },
    "verify_ssl": true
    }
```

#### Example Pipe config :

```
    {
    "_id": "xml-file-foobar",
    "type": "pipe",
    "source": {
        "type": "json",
        "system": "cifs-xml-csv-validator",
        "url": "/file/<url-to-file>?type=xml&validate=yes"
    },
    "transform": {
        "type": "dtl",
        "rules": {
        "default": [
            ["copy", "*"]
            ]
        }
    }
    }
```

## Routes

```
    /file/<path:path>
    /files/<path:path>
```