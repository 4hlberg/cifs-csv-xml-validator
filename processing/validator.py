from lxml import etree, objectify
from lxml.etree import XMLSyntaxError
from service import logger

def validate_file(xml_file, xsd_file):
    try:
        try:
            xmlschema = etree.XMLSchema(file=xsd_file)
            logger.info(f"This is the xmlschema : {xmlschema}")
            parser = objectify.makeparser(schema=xmlschema)
            logger.info(f"Next step...")
            objectify.fromstring(xml_file, parser)
        except Exception as e:
            return f"Failed with error : {e}"
        return "Your xml file was validated :)"
    except XMLSyntaxError:
        return "Your xml file couldn't be validiated... :("