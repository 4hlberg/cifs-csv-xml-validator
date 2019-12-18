from xml.parsers.expat import ExpatError
from sesamutils import Dotdictify
import xmltodict
import logging

class XmlParser:
    def __init__(self, args):
        self._xml_path = args.get("xml_path")
        self._updated_path = args.get("updated_path")
        self._since = args.get("since")

    def parse(self, stream):
        try:
            root_element = xmltodict.parse(stream)
        except ExpatError as e:
            logging.info(f"root element is failing with {e}")

        if self._xml_path is not None:

            if isinstance(list(Dotdictify(root_element).get(self._xml_path))[0], dict):
                l = list(Dotdictify(root_element).get(self._xml_path))
            else:
                l = [Dotdictify(root_element).get(self._xml_path)]
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

        if self._updated_path is not None:
            for entity in l:
                b = Dotdictify(entity)
                entity["_updated"] = b.get(self._updated_path)
        if self._since is not None:
            logging.info("Fetching data since: %s" % self._since)
            return list(filter(l, self._since))
        return l

    def filter(l, since):
        for e in l:
            if e.get("_updated") > since:
                yield e
