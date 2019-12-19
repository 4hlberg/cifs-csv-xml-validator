from flask import Flask, request, jsonify, Response
import json
import requests
import logging
import os
import sys
from processing.feature import dict_merger, stream_json
from sesamutils import VariablesConfig
from processing.cifs import request_file, request_files
from processing.xml import XmlParser
from processing.csv import parse_csv
from processing.validator import validate_file  

app = Flask(__name__)

## Logic for running program in dev, comment out when hosting as a docker image to sesam
try:
    with open("helpers.json", "r") as stream:
        env_vars = stream.read()
        os.environ['username'] = env_vars[19:41]
        os.environ['password'] = env_vars[61:78]
        os.environ['hostname'] = env_vars[61:78]
        os.environ['host'] = env_vars[61:78]
        os.environ['share'] = env_vars[61:78]
        stream.close()
except Exception as e:
    logging.info("Using env vars defined in SESAM")

## Helpers
required_env_vars = ["username", "password", "hostname", "host", "share"]
optional_env_vars = ["schema_path"]
config = VariablesConfig(required_env_vars, optional_env_vars)
if not config.validate():
    sys.exit(1)


@app.route('/')
def index():
    output = {
        'service': 'cifs csv and xml validator is up and running....',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


@app.route("/file/<path:path>", methods=['GET'])
def get_file(path):
    try:
        if request.args["type"].lower() == "xml":
            if request.args["validate"].lower() == "yes":
                parser = XmlParser(request.args) # This needs the query parameter xml_path to work
                xml_file = request_file(config, path)
                parsed_file = parser.parse(xml_file)
                return Response(stream_json(parsed_file), mimetype='application/json')
            if request.args["validate"].lower() == "no":
                parser = XmlParser(request.args) # This needs the query parameter xml_path to work
                xml_file = request_file(config, path)
                parsed_file = parser.parse(xml_file)
                return Response(stream_json(parsed_file), mimetype='application/json')
            else:
                logging.warning("Please provide the correct options for the query parameter 'validate'. Either 'yes' or 'no'")

        if request.args["type"].lower() == "csv":
            csv_file = request_file(config, path)
            parsed_file = parse_csv(csv_file)
            return Response(stream_json(parsed_file), mimetype='application/json')

        else:
            logging.warning("Please provide the correct options for the query parameter 'type'. Either 'xml' or 'csv'")

    except Exception as e:
        logging.error(f"Failed with error : {e}")
        
    finally:
        return jsonify({"This is an error response": "Error"})


@app.route("/files/<path:path>", methods=['GET'])
def get_files(path):
    try:
        if request.args["type"].lower() == "xml":
            if request.args["validate"].lower() == "yes":
                parser = XmlParser(request.args) # This needs the query parameter xml_path to work
                xml_files = request_files(config, path)
                parsed_xml = []
                for xml_file in xml_files:
                    try:
                        parsed_result = parser.parse(xml_file)
                        parsed_xml.append(parsed_result)
                    except Exception as e:
                        logging.error(f"Skipping xml file with error : {e}")
                
                return Response(stream_json(parsed_xml), mimetype='application/json')
            
            if request.args["validate"].lower() == "no":
                parser = XmlParser(request.args) # This needs the query parameter xml_path to work
                xml_files = request_files(config, path)
                parsed_xml = []
                for xml_file in xml_files:
                    try:
                        parsed_result = parser.parse(xml_file)
                        parsed_xml.append(parsed_result)
                    except Exception as e:
                        logging.error(f"Skipping xml file with error : {e}")
                
                return Response(stream_json(parsed_xml), mimetype='application/json')
            
            else:
                logging.warning("Please provide the correct options for the query parameter 'validate'. Either 'yes' or 'no'")

        if request.args["type"].lower() == "csv":
            csv_files = request_files(config, path)
            parsed_csvs = []
            for csv_file in csv_files:
                try:
                    parsed_file = parse_csv(csv_file)
                    parsed_csvs.append(parsed_file)
                except Exception as e:
                    logging.error(f"Skipping csv file with error : {e}")

            return Response(stream_json(parsed_csvs), mimetype='application/json')
           
        else:
            logging.warning("Please provide the correct options for the query parameter 'type'. Either 'xml' or 'csv'")

    except Exception as e:
        logging.warning(f"Failed with error : {e}")


if __name__ == '__main__':
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger("Steve the logger returns :")

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    logger.info("Logger is ready and waiting...")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)