from utils import get_text, parse_date
from lxml import etree

def parse_nfe(xml_data):
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

    summary = {}
    summary["Número"] = get_text(ide, './/nfe:nNF', ns)
    summary["Série"] = get_text(ide, './/nfe:serie', ns)
    summary["Emissão"] = parse_date(get_text(ide, './/nfe:dhEmi', ns))
    summary["Tipo"] = 'Saída' if get_text(ide, './/nfe:tpNF', ns) == '1' else 'Entrada'
    summary["Finalidade"] = purpose
    summary["Natureza"] = get_text(ide, './/nfe:natOp', ns)

    summary["CNPJ/CPF Emitente"] = emit_document.text if emit_document is not None else None
    summary["Emitente"] = get_text(emit, './/nfe:xNome', ns)
    summary["Município Emitente"] = get_text(emit, './/nfe:enderEmit/nfe:xMun', ns)
    summary["UF Emitente"] = get_text(emit, './/nfe:enderEmit/nfe:UF', ns)
    summary["IE Emitente"] = get_text(emit, './/nfe:IE', ns)
    summary["CRT Emitente"] = get_text(emit, './/nfe:CRT', ns)

    summary["CNPJ/CPF Destinatário"] = dest_document.text if dest_document is not None else None
    summary["Destinatário"] = get_text(dest, './/nfe:xNome', ns)
    summary["Município Destinatário"] = get_text(dest, './/nfe:enderDest/nfe:xMun', ns)
    summary["UF Destinatário"] = get_text(dest, './/nfe:enderDest/nfe:UF', ns)
    summary["IE Destinatário"] = get_text(dest, './/nfe:IE', ns)

    summary["Valor Total"] = get_text(ICMSTot, './/nfe:vNF', ns)
    summary["Valor Total Produtos"] = get_text(ICMSTot, './/nfe:vProd', ns)
    summary["Frete"] = get_text(transp, './/nfe:vFrete', ns)
    summary["Desconto"] = get_text(ICMSTot, './/nfe:vDesc', ns)
    summary["Outras Despesas"] = get_text(ICMSTot, './/nfe:vOutro', ns)
    summary["Seguro"] = get_text(ICMSTot, './/nfe:vSeg', ns)
    summary["BC"] = get_text(ICMSTot, './/nfe:vBC', ns)
    summary["ICMS"] = get_text(ICMSTot, './/nfe:vICMS', ns)
    summary["ICMS Desonerado"] = get_text(ICMSTot, './/nfe:vICMSDeson', ns)
    summary["BCST"] = get_text(ICMSTot, './/nfe:vBCST', ns)
    summary["ST"] = get_text(ICMSTot, './/nfe:vST', ns)
    summary["IPI"] = get_text(ICMSTot, './/nfe:vIPI', ns)
    summary["IPI Devolvido"] = get_text(ICMSTot, './/nfe:vIPIDevol', ns)
    summary["PIS"] = get_text(ICMSTot, './/nfe:vPIS', ns)
    summary["COFINS"] = get_text(ICMSTot, './/nfe:vCOFINS', ns)
    summary["Imposto Importação"] = get_text(ICMSTot, './/nfe:vII', ns)

    if ISSQNtot is not None:
        summary["Valor Total Serviços"] = get_text(ISSQNtot, './/nfe:vServ', ns)
        summary["Desconto Incondicionado"] = get_text(ISSQNtot, './/nfe:vDescIncond', ns)
        summary["Desconto Condicionado"] = get_text(ISSQNtot, './/nfe:vDescCond', ns)
        summary["Serviço BC"] = get_text(ISSQNtot, './/nfe:vBC', ns)
        summary["Serviço ISS"] = get_text(ISSQNtot, './/nfe:vISS', ns)
        summary["Serviço ISS Retido"] = get_text(ISSQNtot, './/nfe:vISSRet', ns)
        summary["Serviço PIS"] = get_text(ISSQNtot, './/nfe:vPIS', ns)
        summary["Serviço COFINS"] = get_text(ISSQNtot, './/nfe:vCOFINS', ns)
        summary["Outras Retenções"] = get_text(ISSQNtot, './/nfe:vOutro', ns)
    else:
        summary["Valor Total Serviços"] = None
        summary["Desconto Incondicionado"] = None
        summary["Desconto Condicionado"] = None
        summary["Serviço BC"] = None
        summary["Serviço ISS"] = None
        summary["Serviço ISS Retido"] = None
        summary["Serviço PIS"] = None
        summary["Serviço COFINS"] = None
        summary["Outras Retenções"] = None

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
    
    summary["Modalidade Frete"] = modality
    summary["CNPJ/CPF Transportadora"] = carrier_document.text if carrier_document is not None else None
    summary["Transportadora"] = get_text(transp, './/nfe:transporta/nfe:xNome', ns)
    summary["IE Transportadora"] = get_text(transp, './/nfe:transporta/nfe:IE', ns)
    summary["Valor Transporte"] = get_text(transp, './/nfe:retTransp/nfe:vServ', ns)
    summary["Transporte BC Retido"] = get_text(transp, './/nfe:retTransp/nfe:vBCRet', ns)
    summary["Transporte Aliq ICMS Retido"] = get_text(transp, './/nfe:retTransp/nfe:pICMSRet', ns)
    summary["Transporte ICMS Retido"] = get_text(transp, './/nfe:retTransp/nfe:vICMSRet', ns)
    summary["Transporte CFOP"] = get_text(transp, './/nfe:retTransp/nfe:CFOP', ns)
    summary["Transporte Município ICMS Retido"] = get_text(transp, './/nfe:retTransp/nfe:cMunFG', ns)

    summary["Chave de acesso"] = root.find('.//nfe:protNFe/nfe:infProt/nfe:chNFe', namespaces=ns).text
    products = {}
    products["codigo"] = "0111"
    products["nome"] = "prego"
    products["valor"] = "10"

    data = {
        "Resumo": summary,
        "Produtos": products,
    }

    return data
