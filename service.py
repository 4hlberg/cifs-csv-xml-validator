from flask import Flask, request, jsonify, Response
import json
import requests
import logging
import os
import sys
from processing.feature import dict_merger, stream_json
from sesamutils import VariablesConfig
from processing.cifs import request_file, list_files
from processing.xml import parse
from processing.csv import parse_csv

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
    app.logger.info("Using env vars defined in SESAM")

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
            xml_path = request.args["xml_path"] # For the xml parser...
            validate_filename = str(request.args["validate"])
            
            if request.args["validate"].lower() != "no":
                try:
                    app.logger.info(f"Validating against file : {validate_filename}")
                    xml_file = request_file(config, validate_filename, path)
                    app.logger.info("Cifs functionality passed")
                except Exception as e:
                    app.logger.error(f"Cifs failing with error : {e}")
                try:
                    parsed_file = parse(xml_path, xml_file)
                    app.logger.info("Parsing functionality passed")
                except Exception as e:
                    app.logger.error(f"Xml parsing failing with error : {e}")

                return Response(stream_json(parsed_file), mimetype='application/json')
            
            if request.args["validate"].lower() == "no":
                try:
                    xml_file = request_file(config, validate_filename, path)
                    app.logger.info("Cifs functionality passed")
                except Exception as e:
                    app.logger.error(f"Cifs failing with error : {e}")
                try:
                    parsed_file = parse(xml_path, xml_file)
                    app.logger.info("Parsing functionality passed")
                except Exception as e:
                    app.logger.error(f"Xml parsing failing with error : {e}")
                
                return Response(stream_json(parsed_file), mimetype='application/json')
            
            else:
                app.logger.warning("Please provide the correct options for the query parameter 'validate'. Either 'yes' or 'no'")

        if request.args["type"].lower() == "csv":
            validate_filename = str(request.args["validate"])
            csv_file = request_file(config, validate_filename, path)
            app.logger.info("Cifs functionality passed")
            parsed_file = parse_csv(csv_file)
            app.logger.info("Parsing functionality passed")
            return Response(stream_json(parsed_file), mimetype='application/json')

        else:
            app.logger.warning("Please provide the correct options for the query parameter 'type'. Either 'xml' or 'csv'")

    except Exception as e:
        app.logger.error(f"Failed with error : {e}")
        

@app.route("/files/<path:path>", methods=['GET'])
def get_files(path):
    try:
        if request.args["type"].lower() == "xml":
            xml_path = request.args["xml_path"] # For the xml parser...
            validate_filename = request.args["validate"]
            if request.args["validate"].lower() != "no":
                app.logger.info(f"Validating against file : {validate_filename}")
                xml_files = list_files(path, config)
                app.logger.info("Cifs functionality passed")
                parsed_xml = []
                for xml_file in xml_files:
                    if xml_file.filename[-3:] != 'xml':
                        app.logger.info(f"skipping non xml file")
                    else:
                        app.logger.info(f"writing file name to process : {xml_file.filename}")
                        file_path = f"{path}/{xml_file.filename}"
                        xml_file_content = request_file(config, validate_filename, file_path)
                        parsed_result = parse(xml_path, xml_file_content)
                        app.logger.info("Parsing functionality passed")
                        parsed_xml.append(parsed_result)
                   
                return Response(stream_json(parsed_xml), mimetype='application/json')
            
            if request.args["validate"].lower() == "no":
                xml_files = list_files(path, config)
                app.logger.info("Cifs functionality passed")
                parsed_xml = []
                for xml_file in xml_files:
                    if xml_file.filename[-3:] != 'xml':
                        app.logger.info(f"skipping non xml file")
                    else:
                        app.logger.info(f"writing file name to process : {xml_file.filename}")
                        file_path = f"{path}/{xml_file.filename}"
                        xml_file_content = request_file(config, validate_filename, file_path)
                        parsed_result = parse(xml_path, xml_file_content)
                        app.logger.info("Parsing functionality passed")
                        parsed_xml.append(parsed_result)
                    
                return Response(stream_json(parsed_xml), mimetype='application/json')
            
            else:
                app.logger.warning("Please provide the correct options for the query parameter 'validate'. Either 'yes' or 'no'")

        if request.args["type"].lower() == "csv":
            validate_filename = request.args["validate"]
            csv_files = list_files(path, config)
            app.logger.info("Cifs functionality passed")
            parsed_csvs = []
            for csv_file in csv_files:
                if csv_file.filename[-3:] != 'csv':
                    app.logger.info(f"skipping non csv file")
                else:
                    app.logger.info(f"writing file name to process : {csv_file.filename}")
                    file_path = f"{path}/{csv_file.filename}"
                    csv_file_content = request_file(config, validate_filename, file_path)
                    parsed_file = parse_csv(csv_file_content)
                    parsed_csvs.append(parsed_file)
                
            return Response(stream_json(parsed_csvs), mimetype='application/json')
           
        else:
            app.logger.warning("Please provide the correct options for the query parameter 'type'. Either 'xml' or 'csv'")

    except Exception as e:
        app.logger.warning(f"Failed with error : {e}")


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