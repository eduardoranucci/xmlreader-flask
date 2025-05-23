from utils import get_text, parse_date
from lxml import etree

def nfe_parser(xml_data):
    root = etree.fromstring(xml_data)
    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
    nfe = root.find(".//nfe:NFe/nfe:infNFe", namespaces=ns)
    return {
        "Número da NF-e": get_text(nfe, './/nfe:ide/nfe:nNF', ns),
        "Data de Emissão": parse_date(get_text(nfe, './/nfe:ide/nfe:dhEmi', ns)),
        "Valor Total": get_text(nfe, './/nfe:total/nfe:ICMSTot/nfe:vNF', ns)
    }
