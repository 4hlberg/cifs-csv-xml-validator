import logging
from smb.SMBConnection import SMBConnection

def create_connection(config):
    return SMBConnection(config.username, config.password, socket.gethostname(),
                         config.hostname, is_direct_tcp=True, use_ntlm_v2=True)

def request_file(config, path):
    try:
        if config.schema_path:
            schema_path = config.schema_path
    except AttributeError:
        schema_path = 'Denmark'
    
    logging.info(f"Processing request for path '{path}'.")

    conn = create_connection(config)
    if not conn.connect(config.host, 445):
        logging.error("Failed to authenticate with the provided credentials")
        conn.close()
        return "Invalid credentials provided for fileshare", 500

    logging.info("Successfully connected to SMB host.")

    logging.info("Listing available shares:")
    share_list = conn.listShares()
    for share in share_list:
        logging.info(f"Share: {share.name}  {share.type}    {share.comments}")

    path_parts = path.split("/")
    file_name = path_parts[len(path_parts)-1]

    try:
        file_obj = tempfile.NamedTemporaryFile()
        conn.retrieveFile(config.share, path, file_obj)
        logging.info("Completed file downloading...")
        if schema_path != "Denmark":
            logging.info('Validator initiated...')     
            file_obj.seek(0)
            xml_content = file_obj.read().decode()    
            schema_obj = tempfile.NamedTemporaryFile()
            conn.retrieveFile(config.share, schema_path, schema_obj)
            schema_obj.seek(0)
            schema_content = schema_obj.read().decode()
            validation_resp = validate_file(xml_content, schema_content)
            logging.debug(f"This is the response from validation func : {validation_resp}")
            #file_obj.close()
            schema_obj.close()
            if validation_resp == "Your file was validated :)":
                return file_obj
            else:
                logging.error('Validation unsuccessfull! :(')
        else:    
            return file_obj           
    except Exception as e:
        logging.error(f"Failed to get file from fileshare. Error: {e}")
        logging.debug("Files found on share:")
        file_list = conn.listPath(os.environ.get("share"), "/")
        for f in file_list:
            logging.debug('file: %s (FileSize:%d bytes, isDirectory:%s)' % (f.filename, f.file_size, f.isDirectory))
    finally:
        conn.close()

def request_files(config, path):
    try:
        if config.schema_path:
            schema_path = config.schema_path
    except AttributeError:
        schema_path = 'Denmark'

    logging.info(f"Processing request for path '{path}'.")

    conn = create_connection(config)
    if not conn.connect(config.host, 445):
        logging.error("Failed to authenticate with the provided credentials")
        conn.close()
        return "Invalid credentials provided for fileshare", 500

    logging.info("Successfully connected to SMB host.")

    share_list = conn.listShares()
    for share in share_list:
        if share.name == os.environ.get("share"):
            target_share = share.name

    # Defined share of interest..
    logging.info(f"Writing target share from which we start : {target_share}")
    file_list = conn.listPath(target_share, f"/{path}")

    # Files to write to :
    files_to_send = []

    logging.info("Listing files found : %s" % file_list)
    for file_name in file_list:
        file_obj = tempfile.NamedTemporaryFile()
        path_to_file = f"/{path}/{file_name.filename}"
        try:
            conn.retrieveFile(target_share, path_to_file, file_obj)
            file_obj.seek(0)
            file_temp = file_obj.read().decode()
            if schema_path != "Denmark":
                logging.info('Validator initiated...')
                schema_obj = tempfile.NamedTemporaryFile()
                conn.retrieveFile(target_share, schema_path, schema_obj)
                schema_obj.seek(0)
                schema_content = schema_obj.read().decode()
                validation_resp = validate_file(file_temp, schema_content)
                logging.debug(f"This is the response from validation func : {validation_resp}")
                if validation_resp == "Your file was validated :)":
                    files_to_send.append(file_temp)
                else:
                    logging.error('Validation unsuccessfull! :(')
                    
                logging.info("Finished appending file to list")
                file_obj.close()
                schema_obj.close()
            else:
                files_to_send.append(file_temp)
                logging.info("Finished appending file to list")
                file_obj.close()
        except Exception as e:
            logging.error(f"Failed to get file from fileshare. Error: {e}")
    
    conn.close()
    logging.info(f"Finished appending files... ;)")
    return files_to_send