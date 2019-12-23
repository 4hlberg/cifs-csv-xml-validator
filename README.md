# Cifs-csv-xml-validator
Connector for smb connection, csv and xml parsing and xml validation

## Prerequisites
python3

## API Capabalities
GET


## Caveats :
When parsing xml files, remember to provide the query parameter `xml_path=<parent-element>` to make sure the xml_parser function defined in /processing/xml.py parses from the right dimension in the provided file. 

*Working functionality*
- xml file reading works. Validation needs to be validated and csv aswell.


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
        "schema_path": "$ENV(<path to schema folder>)",
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
        "url": "/file/<url-to-file>?type=xml&validate=no&xml_path=<parent-element>"
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