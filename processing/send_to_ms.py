import requests
import tempfile


def sending_file_to_ms(xml_file_name, file_obj, header, ms_url):
    return_string = None
    _id = str(xml_file_name).split(".")[0]
    files = {
        'Data': (f"{xml_file_name}", file_obj.read(), "application/xml")
    }
    payload = {
        'RapportId': _id
    }
    response = requests.post(ms_url, headers=header,
                             verify=False, files=files, data=payload)

    if response.status_code == 200:
        return_string = "Yes, I've send your file!"
    else:
        return_string = f"Something went wrong when sending file. Response code is {response.status_code}"

    return return_string
