from sesamutils import Dotdictify
import xmltodict
from service import logger

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
            logger.info(f"None imbedded xml defined. Failing with error: {e}")
        except ExpatError as e:
            logger.info(f"None imbedded xml defined. Failing with error: {e}")
        except KeyError as e:
            logger.info(f"None imbedded xml element of {e}")
        except UnboundLocalError as e:
            logger.info(f"None imbedded xml element of {e}")

        l = [root_element]

    return l
