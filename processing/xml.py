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
            imbedded_xml = xmltodict.parse(
                "<html>" + root_element["ichicsr"]["safetyreport"]["patient"]["parent"]["parentmedicalrelevanttext"] + "</html>")
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
    xml = dicttoxml.dicttoxml(
        json_response, attr_type=False, item_func=lambda x: x)

    formatet_xml = parseString(xml)
    return formatet_xml.toprettyxml()


def json2xml(json_obj, line_padding=""):
    result_list = list()
    json_obj_type = type(json_obj)

    if json_obj_type is list:
        if not json_obj:
            json_obj == "empty"
        else:
            for sub_elem in json_obj:
                result_list.append(json2xml(sub_elem, line_padding))
            return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            if str(sub_obj) == "None" or len(str(sub_obj)) == 0 or sub_obj == "empty":
                pass
            else:
                if tag_name == "animalsigns" or tag_name == "animalsuspectdrug":
                    for item in sub_obj:
                        result_list.append("%s<%s>" %
                                           (line_padding, tag_name))
                        result_list.append(json2xml(item, "\t" + line_padding))
                        result_list.append("%s</%s>" %
                                           (line_padding, tag_name))
                else:
                    if type(sub_obj) is list:
                        if not sub_obj:
                            pass

                        else:
                            result_list.append("%s<%s>" %
                                               (line_padding, tag_name))
                            result_list.append(
                                json2xml(sub_obj, "\t" + line_padding))
                            result_list.append("%s</%s>" %
                                               (line_padding, tag_name))
                    else:
                        result_list.append("%s<%s>" % (line_padding, tag_name))
                        result_list.append(
                            json2xml(sub_obj, "\t" + line_padding))
                        result_list.append("%s</%s>" %
                                           (line_padding, tag_name))

        return "\n".join(result_list)

    if json_obj == "empty":
        pass

    else:
        return "%s%s" % (line_padding, json_obj)
