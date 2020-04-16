# Cifs-csv-xml-validator
Connector for smb connection, csv and xml parsing and xml validation

## Prerequisites
python3

## API Capabalities
GET
POST


## Caveats :
When parsing xml files, remember to provide the query parameter `xml_path=<parent-element>` to make sure the xml_parser function defined in /processing/xml.py parses from the right dimension in the provided file. 

*Working functionality*
- xml /file/ and /files/ reading works.
- Single file reading of csv file works '/file/' 
- Multiple csv file reading needs to be validated '/files'
- /send_file/ works. Use in pipe that gets a URL from a sink pipe (http_endpoint).
- Validation needs to be validated.


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
    "share": "some share",
    "schema_path": "schema path",
    "target_folder": "your folder",
    "sesam_jwt": "sesam jwt",
    "ms_access_token":"some access token for microservice if needed",
    "ms_url": "some microservice base url if needed"
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
        "share": "$ENV(share)",
        "schema_path": "$ENV(schema path)",
        "target_folder": "$ENV(your folder)",
        "sesam_jwt": "$SECRET(sesam jwt)",
        "ms_access_token":"$SECRET(some access token for microservice if needed)",
        "ms_url": "$ENV(some microservice base url if needed)"
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

#### Example Pipe config for csv :

```
    {
    "_id": "csv-file-foobar",
    "type": "pipe",
    "source": {
        "type": "csv",
        "system": "cifs-xml-csv-validator",
        "auto_dialect": true,
        "delimiter": ";",
        "dialect": "excel",
        "encoding": "utf-8-sig",
        "has_header": true,
        "preserve_empty_strings": false,
        "primary_key": "This is awesome",
        "url": "/file/Folder_with_file/this_is_a_csv.csv?type=csv&validate=no"
    },
    "transform": {
        "type": "dtl",
        "rules": {
        "default": [
            ["copy", "*"],
            ["add", "rdf:type",
            ["ni", "some_ni"]
            ]
        ]
        }
    },
    "add_namespaces": true
    }
```


## Routes

```
    /file/<path:path>
    /files/<path:path>
    /send_file/<path:path>
```