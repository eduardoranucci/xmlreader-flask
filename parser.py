from utils import get_text, parse_date
from lxml import etree

def nfe_parser(xml_data):
    root = etree.fromstring(xml_data)
    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
    
    nfe = root.find(".//nfe:NFe/nfe:infNFe", namespaces=ns)
    ide = nfe.find('.//nfe:ide', namespaces=ns)
    emit = nfe.find('.//nfe:emit', namespaces=ns)
    dest = nfe.find('.//nfe:dest', namespaces=ns)
    det = nfe.findall('.//nfe:det', namespaces=ns)
    total = nfe.find('.//nfe:total', namespaces=ns)
    ICMSTot = total.find('.//nfe:ICMSTot', namespaces=ns)
    ISSQNtot = total.find('.//nfe:ISSQNtot', namespaces=ns)
    transp = nfe.find('.//nfe:transp', namespaces=ns)

    icms_tags = ['00', '02', '10', '15', '20', '30', '40', '41', '50', '51', '53', '60', '61', '70', '90']
    cson_tags = ['101', '102', '103', '201', '202', '203', '300', '400', '500', '900']

    purpose = int(get_text(ide, './/nfe:finNFe', ns))
    match purpose:
        case 1:
            purpose = 'Normal'
        case 2:
            purpose = 'Complementar'
        case 3:
            purpose = 'Ajuste'
        case 4:
            purpose = 'Devolução'

    emit_document = emit.find('.//nfe:CNPJ', namespaces=ns)
    if emit_document is None:
        emit_document = emit.find('.//nfe:CPF', namespaces=ns)

    dest_document = dest.find('.//nfe:CNPJ', namespaces=ns)
    if dest_document is None:
        dest_document = dest.find('.//nfe:CPF', namespaces=ns)

    data = {}
    data = {
        "Número": get_text(ide, './/nfe:nNF', ns),
        "Série": get_text(ide, './/nfe:serie', ns),
        "Emissão": parse_date(get_text(ide, './/nfe:dhEmi', ns)),
        "Tipo": 'Saída' if get_text(ide, './/nfe:tpNF', ns) == '1' else 'Entrada',
        'Finalidade': purpose,
        "Natureza": get_text(ide, './/nfe:natOp', ns),

        "CNPJ/CPF Emitente": emit_document.text if emit_document is not None else None,
        "Emitente": get_text(emit, './/nfe:xNome', ns),
        "Município Emitente": get_text(emit, './/nfe:enderEmit/nfe:xMun', ns),
        "UF Emitente": get_text(emit, './/nfe:enderEmit/nfe:UF', ns),
        "IE Emitente": get_text(emit, './/nfe:IE', ns),
        "CRT Emitente": get_text(emit, './/nfe:CRT', ns),

        "CNPJ/CPF Destinatário": dest_document.text if dest_document is not None else None,
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
    }

    if ISSQNtot is not None:
        data["Valor Total Serviços"] = get_text(ISSQNtot, './/nfe:vServ', ns)
        data["Desconto Incondicionado"] = get_text(ISSQNtot, './/nfe:vDescIncond', ns)
        data["Desconto Condicionado"] = get_text(ISSQNtot, './/nfe:vDescCond', ns)
        data["Serviço BC"] = get_text(ISSQNtot, './/nfe:vBC', ns)
        data["Serviço ISS"] = get_text(ISSQNtot, './/nfe:vISS', ns)
        data["Serviço ISS Retido"] = get_text(ISSQNtot, './/nfe:vISSRet', ns)
        data["Serviço PIS"] = get_text(ISSQNtot, './/nfe:vPIS', ns)
        data["Serviço COFINS"] = get_text(ISSQNtot, './/nfe:vCOFINS', ns)
        data["Outras Retenções"] = get_text(ISSQNtot, './/nfe:vOutro', ns)
    else:
        data["Valor Total Serviços"] = None
        data["Desconto Incondicionado"] = None
        data["Desconto Condicionado"] = None
        data["Serviço BC"] = None
        data["Serviço ISS"] = None
        data["Serviço ISS Retido"] = None
        data["Serviço PIS"] = None
        data["Serviço COFINS"] = None
        data["Outras Retenções"] = None

    carrier_document = transp.find('.//nfe:transporta/nfe:CNPJ', namespaces=ns)
    if carrier_document is None:
        carrier_document = transp.find('.//nfe:transporta/nfe:CPF', namespaces=ns)

    modality = int(get_text(transp, './/nfe:modFrete', ns))
    match modality:
        case 0:
            modality = 'Por conta do Emitente/Remetente'
        case 1:
            modality = 'Por conta do Destinatário'
        case 2:
            modality = 'por conta de terceiros'
        case 9:
            modality = 'Sem frete'
    
    data["Modalidade Frete"] = modality
    data["CNPJ/CPF Transportadora"] = carrier_document.text if carrier_document is not None else None
    data["Transportadora"] = get_text(transp, './/nfe:transporta/nfe:xNome', ns)
    data["IE Transportadora"] = get_text(transp, './/nfe:transporta/nfe:IE', ns)
    data["Valor Transporte"] = get_text(transp, './/nfe:retTransp/nfe:vServ', ns)
    data["Transporte BC Retido"] = get_text(transp, './/nfe:retTransp/nfe:vBCRet', ns)
    data["Transporte Aliq ICMS Retido"] = get_text(transp, './/nfe:retTransp/nfe:pICMSRet', ns)
    data["Transporte ICMS Retido"] = get_text(transp, './/nfe:retTransp/nfe:vICMSRet', ns)
    data["Transporte CFOP"] = get_text(transp, './/nfe:retTransp/nfe:CFOP', ns)
    data["Transporte Município ICMS Retido"] = get_text(transp, './/nfe:retTransp/nfe:cMunFG', ns)

    data["Chave de acesso"] = root.find('.//nfe:protNFe/nfe:infProt/nfe:chNFe', namespaces=ns).text

    return data
