from parser.utils import get_text, parse_date
from lxml import etree

def parse_nfe(xml_data):
    root = etree.fromstring(xml_data)
    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
    nfe = root.find(".//nfe:NFe/nfe:infNFe", namespaces=ns)
    ide = nfe.find('.//nfe:ide', namespaces=ns)
    emit = nfe.find('.//nfe:emit', namespaces=ns)
    dest = nfe.find('.//nfe:dest', namespaces=ns)
    det_list = nfe.findall('.//nfe:det', namespaces=ns)
    total = nfe.find('.//nfe:total', namespaces=ns)
    ICMSTot = total.find('.//nfe:ICMSTot', namespaces=ns)
    ISSQNtot = total.find('.//nfe:ISSQNtot', namespaces=ns)
    transp = nfe.find('.//nfe:transp', namespaces=ns)

    def get_document(element):
        if element is None:
            return None
        doc = element.find('.//nfe:CNPJ', namespaces=ns)
        if doc is None:
            doc = element.find('.//nfe:CPF', namespaces=ns)
        return doc.text if doc is not None else None

    def get_modalidade_frete(transp):
        val = get_text(transp, './/nfe:modFrete', ns)
        if val is None:
            return None
        val = int(val)
        return {
            0: 'Por conta do Emitente/Remetente',
            1: 'Por conta do Destinatário',
            2: 'por conta de terceiros',
            9: 'Sem frete'
        }.get(val, val)

    def get_purpose(ide):
        val = get_text(ide, './/nfe:finNFe', ns)
        if val is None:
            return None
        val = int(val)
        return {
            1: 'Normal',
            2: 'Complementar',
            3: 'Ajuste',
            4: 'Devolução'
        }.get(val, val)

    summary = {
        "Número": get_text(ide, './/nfe:nNF', ns),
        "Série": get_text(ide, './/nfe:serie', ns),
        "Emissão": parse_date(get_text(ide, './/nfe:dhEmi', ns)),
        "Tipo": 'Saída' if get_text(ide, './/nfe:tpNF', ns) == '1' else 'Entrada',
        "Finalidade": get_purpose(ide),
        "Natureza": get_text(ide, './/nfe:natOp', ns),
        "CNPJ/CPF Emitente": get_document(emit),
        "Emitente": get_text(emit, './/nfe:xNome', ns),
        "Município Emitente": get_text(emit, './/nfe:enderEmit/nfe:xMun', ns),
        "UF Emitente": get_text(emit, './/nfe:enderEmit/nfe:UF', ns),
        "IE Emitente": get_text(emit, './/nfe:IE', ns),
        "CRT Emitente": get_text(emit, './/nfe:CRT', ns),
        "CNPJ/CPF Destinatário": get_document(dest),
        "Destinatário": get_text(dest, './/nfe:xNome', ns),
        "Município Destinatário": get_text(dest, './/nfe:enderDest/nfe:xMun', ns),
        "UF Destinatário": get_text(dest, './/nfe:enderDest/nfe:UF', ns),
        "IE Destinatário": get_text(dest, './/nfe:IE', ns),
        "Valor Total": get_text(ICMSTot, './/nfe:vNF', ns),
        "Valor Total Produtos": get_text(ICMSTot, './/nfe:vProd', ns),
        "Frete": get_text(transp, './/nfe:vFrete', ns),
        "Desconto": get_text(ICMSTot, './/nfe:vDesc', ns),
        "Outras Despesas": get_text(ICMSTot, './/nfe:vOutro', ns),
        "Seguro": get_text(ICMSTot, './/nfe:vSeg', ns),
        "BC": get_text(ICMSTot, './/nfe:vBC', ns),
        "ICMS": get_text(ICMSTot, './/nfe:vICMS', ns),
        "ICMS Desonerado": get_text(ICMSTot, './/nfe:vICMSDeson', ns),
        "BCST": get_text(ICMSTot, './/nfe:vBCST', ns),
        "ST": get_text(ICMSTot, './/nfe:vST', ns),
        "IPI": get_text(ICMSTot, './/nfe:vIPI', ns),
        "IPI Devolvido": get_text(ICMSTot, './/nfe:vIPIDevol', ns),
        "PIS": get_text(ICMSTot, './/nfe:vPIS', ns),
        "COFINS": get_text(ICMSTot, './/nfe:vCOFINS', ns),
        "Imposto Importação": get_text(ICMSTot, './/nfe:vII', ns),
        "Valor Total Serviços": get_text(ISSQNtot, './/nfe:vServ', ns) if ISSQNtot is not None else None,
        "Desconto Incondicionado": get_text(ISSQNtot, './/nfe:vDescIncond', ns) if ISSQNtot is not None else None,
        "Desconto Condicionado": get_text(ISSQNtot, './/nfe:vDescCond', ns) if ISSQNtot is not None else None,
        "Serviço BC": get_text(ISSQNtot, './/nfe:vBC', ns) if ISSQNtot is not None else None,
        "Serviço ISS": get_text(ISSQNtot, './/nfe:vISS', ns) if ISSQNtot is not None else None,
        "Serviço ISS Retido": get_text(ISSQNtot, './/nfe:vISSRet', ns) if ISSQNtot is not None else None,
        "Serviço PIS": get_text(ISSQNtot, './/nfe:vPIS', ns) if ISSQNtot is not None else None,
        "Serviço COFINS": get_text(ISSQNtot, './/nfe:vCOFINS', ns) if ISSQNtot is not None else None,
        "Outras Retenções": get_text(ISSQNtot, './/nfe:vOutro', ns) if ISSQNtot is not None else None,
        "Modalidade Frete": get_modalidade_frete(transp),
        "CNPJ/CPF Transportadora": get_document(transp.find('.//nfe:transporta', namespaces=ns)) if transp is not None else None,
        "Transportadora": get_text(transp, './/nfe:transporta/nfe:xNome', ns),
        "IE Transportadora": get_text(transp, './/nfe:transporta/nfe:IE', ns),
        "Valor Transporte": get_text(transp, './/nfe:retTransp/nfe:vServ', ns),
        "Transporte BC Retido": get_text(transp, './/nfe:retTransp/nfe:vBCRet', ns),
        "Transporte Aliq ICMS Retido": get_text(transp, './/nfe:retTransp/nfe:pICMSRet', ns),
        "Transporte ICMS Retido": get_text(transp, './/nfe:retTransp/nfe:vICMSRet', ns),
        "Transporte CFOP": get_text(transp, './/nfe:retTransp/nfe:CFOP', ns),
        "Transporte Município ICMS Retido": get_text(transp, './/nfe:retTransp/nfe:cMunFG', ns),
        "Chave de acesso": get_text(root, './/nfe:protNFe/nfe:infProt/nfe:chNFe', ns)
    }

    data = {
        "Resumo": summary,
    }
    return data