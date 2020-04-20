from sesamutils import Dotdictify
import xmltodict
import logging
import json
import dicttoxml
from xml.dom.minidom import parseString

def parse(xml_path, stream):
    
    root_element = xmltodict.parse(stream)

    if xml_path is not None:

        if isinstance(list(Dotdictify(root_element).get(xml_path))[0], dict):
            l = list(Dotdictify(root_element).get(xml_path))
        else:
            l = [Dotdictify(root_element).get(xml_path)]
    else:
        try:
            imbedded_xml = xmltodict.parse("<html>" + root_element["ichicsr"]["safetyreport"]["patient"]["parent"]["parentmedicalrelevanttext"] + "</html>")
            root_element["ichicsr"]["safetyreport"]["patient"]["parent"]["parentmedicalrelevanttext"] = imbedded_xml["html"]
        except TypeError as e:
            logging.info(f"None imbedded xml defined. Failing with error: {e}")
        except ExpatError as e:
            logging.info(f"None imbedded xml defined. Failing with error: {e}")
        except KeyError as e:
            logging.info(f"None imbedded xml element of {e}")
        except UnboundLocalError as e:
            logging.info(f"None imbedded xml element of {e}")

        l = [root_element]

    return l

def convert_to_xml(json_response):
    xml = dicttoxml.dicttoxml(json_response, attr_type=False, item_func=lambda x: x)
    formatet_xml = parseString(xml)
    return formatet_xml.toprettyxml()
