import socket
import os
import sys
import tempfile
import logging
from smb.SMBConnection import SMBConnection
from processing.validator import validate_file


def create_connection(config):
    connection = SMBConnection(config.username, config.password, socket.gethostname(),
                         config.hostname, is_direct_tcp=True, use_ntlm_v2=True)

    if not connection.connect(config.host, 445):
        logging.error("Failed to authenticate with the provided credentials")
        connection.close()
        return "Invalid credentials provided for fileshare", 500

    logging.info("Successfully connected to SMB host.")
    return connection


def request_file(config, val_file_name, path, conn):
    try:
        if config.schema_path:
            schema_path = config.schema_path
    except AttributeError:
        schema_path = 'Denmark'
    
    logging.info(f"Processing request for path '{path}'.")

    logging.info("Successfully connected to SMB host.")

    logging.info("Listing available shares:")
    share_list = conn.listShares()
    for share in share_list:
        logging.info(f"Share: {share.name}  {share.type}    {share.comments}")

    try:
        xml_content = None
        file_obj = tempfile.NamedTemporaryFile()
        conn.retrieveFile(config.share, path, file_obj)
        logging.info("Completed file downloading...")
        if val_file_name != "no":
            logging.info('Validator initiated...')     
            file_obj.seek(0)
            xml_content = file_obj.read().decode()    
            schema_obj = tempfile.NamedTemporaryFile()
            conn.retrieveFile(config.share, f"{schema_path}/{val_file_name}", schema_obj)
            schema_obj.seek(0)
            schema_content = schema_obj.read().decode()
            validation_resp = validate_file(xml_content, schema_content)
            #logging.debug(f"This is the response from validation func : {validation_resp}")
            file_obj.close()
            schema_obj.close()
            if validation_resp == "Your file was validated :)":
                return xml_content
            else:
                logging.error('Validation unsuccessfull! :(')
                sys.exit(1)
        else:  
            file_obj.seek(0)
            xml_content = file_obj.read().decode()
            file_obj.close()   
            return xml_content           
    except Exception as e:
        logging.error(f"Failed to get file from fileshare. Error: {e}")
        logging.debug("Files found on share:")
        file_list = conn.listPath(os.environ.get("share"), "/")
        for f in file_list:
            logging.debug('file: %s (FileSize:%d bytes, isDirectory:%s)' % (f.filename, f.file_size, f.isDirectory))


def list_files(path, config, conn):
    logging.info(f"Processing request for path '{path}'.")

    share_list = conn.listShares()
    for share in share_list:
        if share.name == os.environ.get("share"):
            target_share = share.name

    # Defined share of interest..
    logging.info(f"Writing target share from which we start : {target_share}")
    file_list = conn.listPath(target_share, f"/{path}")

    return file_list
