from flask import Flask, request, jsonify, Response
import json
import requests
import os
import sys
from processing.feature import dict_merger, stream_json
from sesamutils import VariablesConfig, sesam_logger
from processing.cifs import request_file, list_files, create_connection
from processing.xml import parse
from processing.csv import parse_csv

app = Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)

## commonLexicon_4.0.xsd

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
    logger.info("Using env vars defined in SESAM")

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
    logger.info(f"Printing path : {path}")
    try:
        conn = create_connection(config)
        if request.args["type"].lower() == "xml":
            xml_path = request.args["xml_path"] # For the xml parser...
            validate_filename = str(request.args["validate"])
            
            if validate_filename.lower() != "no":
                try:
                    logger.info(f"Validating against file : {validate_filename}")
                    xml_file = request_file(config, validate_filename, path, conn)
                    logger.info("Cifs functionality passed")
                    conn.close()
                except Exception as e:
                    logger.error(f"Cifs failing with error : {e}")
                    conn.close()
                try:
                    parsed_file = parse(xml_path, xml_file)
                    logger.info("Parsing functionality passed")
                except Exception as e:
                    logger.error(f"Xml parsing failing with error : {e}")

                return Response(stream_json(parsed_file), mimetype='application/json')
            
            if validate_filename.lower() == "no":
                try:
                    xml_file = request_file(config, validate_filename, path, conn)
                    logger.info("Cifs functionality passed")
                    conn.close()
                except Exception as e:
                    logger.error(f"Cifs failing with error : {e}")
                    conn.close()
                try:
                    parsed_file = parse(xml_path, xml_file)
                    logger.info("Parsing functionality passed")
                except Exception as e:
                    logger.error(f"Xml parsing failing with error : {e}")
                
                return Response(stream_json(parsed_file), mimetype='application/json')
            
            else:
                conn.close()
                logger.warning("Please provide the correct options for the query parameter 'validate'. Either 'yes' or 'no'")

        if request.args["type"].lower() == "csv":
            validate_filename = str(request.args["validate"])
            csv_file = request_file(config, validate_filename, path, conn)
            logger.info("Cifs functionality passed")
            conn.close()
            parsed_file = parse_csv(csv_file)
            logger.info("Parsing functionality passed")
            return Response(stream_json(parsed_file), mimetype='application/json')

        else:
            conn.close()
            logger.warning("Please provide the correct options for the query parameter 'type'. Either 'xml' or 'csv'")

    except Exception as e:
        conn.close()
        logger.error(f"Failed with error : {e}")
        

@app.route("/files/<path:path>", methods=['GET'])
def get_files(path):
    parsed_content = []
    try:
        conn = create_connection(config)
        if request.args["type"].lower() == "xml":
            xml_path = request.args["xml_path"] # For the xml parser...
            validate_filename = str(request.args["validate"])
            
            if validate_filename.lower() != "no":
                logger.info(f"Validating against file : {validate_filename}")
                xml_files = list_files(path, config, conn)
                logger.info("Cifs functionality passed")
                for xml_file in xml_files:
                    if xml_file.filename[-3:] != 'xml':
                        logger.info(f"skipping non xml file")
                    else:
                        logger.info(f"writing file name to process : {xml_file.filename}")
                        file_path = f"{path}/{xml_file.filename}"
                        xml_file_content = request_file(config, validate_filename, file_path, conn)
                        parsed_result = parse(xml_path, xml_file_content)
                        logger.info("Parsing functionality passed")
                        parsed_content.append(parsed_result)
                
            if validate_filename.lower() == "no":
                xml_files = list_files(path, config, conn)
                logger.info("Cifs functionality passed")
                for xml_file in xml_files:
                    if xml_file.filename[-3:] != 'xml':
                        logger.info(f"skipping non xml file")
                    else:
                        logger.info(f"writing file name to process : {xml_file.filename}")
                        file_path = f"{path}/{xml_file.filename}"
                        xml_file_content = request_file(config, validate_filename, file_path, conn)
                        parsed_result = parse(xml_path, xml_file_content)
                        logger.info("Parsing functionality passed")
                        parsed_content.append(parsed_result)
                
            conn.close()
            logger.info(f"Streaming parsed files {parsed_content} to SESAM")
            return Response(stream_json(parsed_content), mimetype='application/json')      

        if request.args["type"].lower() == "csv":
            validate_filename = str(request.args["validate"])
            csv_files = list_files(path, config, conn)
            logger.info("Cifs functionality passed")
            for csv_file in csv_files:
                if csv_file.filename[-3:] != 'csv':
                    logger.info(f"skipping non csv file")
                else:
                    logger.info(f"writing file name to process : {csv_file.filename}")
                    file_path = f"{path}/{csv_file.filename}"
                    csv_file_content = request_file(config, validate_filename, file_path, conn)
                    parsed_file = parse_csv(csv_file_content)
                    parsed_content.append(parsed_file)

            conn.close()
            logger.info(f"Streaming parsed files {parsed_content} to SESAM")
            return Response(stream_json(parsed_content), mimetype='application/json')      

    except Exception as e:
        logger.warning(f"Failed with error : {e}")
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)