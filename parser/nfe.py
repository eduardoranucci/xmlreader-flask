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

    nfe_number = get_text(ide, './/nfe:nNF', ns)
    emit_document = get_document(emit)
    summary = {
        "Número": nfe_number,
        "Série": get_text(ide, './/nfe:serie', ns),
        "Emissão": parse_date(get_text(ide, './/nfe:dhEmi', ns)),
        "Tipo": 'Saída' if get_text(ide, './/nfe:tpNF', ns) == '1' else 'Entrada',
        "Finalidade": get_purpose(ide),
        "Natureza": get_text(ide, './/nfe:natOp', ns),
        "CNPJ/CPF Emitente": emit_document,
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
        "Produtos": parse_nfe_products(det_list, nfe_number, emit_document, ns)
    }
    return data

def parse_nfe_products(det_list, nfe, document, ns):
    icms_tags = ['00', '02', '10', '15', '20', '30', '40', '41', '50', '51', '53', '60', '61', '70', '90']
    cson_tags = ['101', '102', '103', '201', '202', '203', '300', '400', '500', '900']
    trib_tags = ['NT', 'Trib', 'Aliq', 'Qtde', 'Outr']

    products = []
    for det in det_list:
        prod = det.find('.//nfe:prod', namespaces=ns)
        imposto = det.find('.//nfe:imposto', namespaces=ns)
        imp_icms = imposto.find('.//nfe:ICMS', namespaces=ns) if imposto is not None else None

        product = {
            "Número NFe": nfe,
            "CNPJ/CPF Emitente": document,
            "Código": get_text(prod, './/nfe:cProd', ns),
            "Descrição": get_text(prod, './/nfe:xProd', ns),
            "NCM": get_text(prod, './/nfe:NCM', ns),
            "CEST": get_text(prod, './/nfe:CEST', ns),
            "CFOP": get_text(prod, './/nfe:CFOP', ns),
            "Unidade": get_text(prod, './/nfe:uCom', ns),
            "Quantidade": get_text(prod, './/nfe:qCom', ns),
            "Valor Unitário": get_text(prod, './/nfe:vUnCom', ns),
            "Valor Total": get_text(prod, './/nfe:vProd', ns),
            "Quantidade Tributável": get_text(prod, './/nfe:qTrib', ns),
            "Valor Unitário Tributável": get_text(prod, './/nfe:vUnTrib', ns),
        }

        # ICMS/CSOSN
        icms_tag = None
        if imp_icms is not None:
            for tag in icms_tags:
                icms_tag = imp_icms.find(f'.//nfe:ICMS{tag}', namespaces=ns)
                if icms_tag is not None:
                    break
            if icms_tag is None:
                for tag in cson_tags:
                    icms_tag = imp_icms.find(f'.//nfe:ICMSSN{tag}', namespaces=ns)
                    if icms_tag is not None:
                        break

        icms_fields = [
            ("Origem ICMS", './/nfe:orig'),
            ("CST ICMS", './/nfe:CST'),
            ("CSOSN", './/nfe:CSOSN'),
            ("BC ICMS", './/nfe:vBC'),
            ("Alíquota ICMS", './/nfe:pICMS'),
            ("ICMS", './/nfe:vICMS'),
            ("Alíquota adrem ICMS", './/nfe:adRemICMS'),
            ("ICMS próprio", './/nfe:vICMSMono'),
            ("Redução BC ICMS", './/nfe:pRedBC'),
            ("ICMS Op", './/nfe:vICMSOp'),
            ("Redução BC ICMS ST", './/nfe:pRedBCST'),
            ("BC ICMS ST", './/nfe:vBCST'),
            ("Alíquota ICMS ST", './/nfe:pICMSST'),
            ("Valor ICMS ST", './/nfe:vICMSST'),
            ("BC ICMS ST retido", './/nfe:vBCSTRet'),
            ("Valor ICMS ST retido", './/nfe:vICMSSTRet'),
            ("Alíquota ST", './/nfe:pST'),
            ("ICMS Substituto", './/nfe:vICMSSubstituto'),
            ("Alíquota adrem retido", './/nfe:adRemICMSReten'),
            ("ICMS próprio retido", './/nfe:vICMSMonoReten'),
            ("Alíquota adrem retido anteriormente", './/nfe:adRemICMSRet'),
            ("ICMS retido anteriormente", './/nfe:vICMSMonoRet'),
            ("ICMS próprio Op", './/nfe:vICMSMonoOp'),
            ("Percentual do diferimento ICMS", './/nfe:pDif'),
            ("ICMS próprio diferido", './/nfe:vICMSMonoDif'),
            ("ICMS diferido", './/nfe:vICMSDif'),
            ("Alíquota ICMS Efetivo", './/nfe:pICMSEfet'),
            ("ICMS Efetivo", './/nfe:vICMSEfet'),
            ("Alíquota crédito ICMS SN", './/nfe:pCredSN'),
            ("Crédito ICMS SN", './/nfe:vCredICMSSN'),
            ("Percentual MVAST", './/nfe:pMVAST'),
        ]
        for label, path in icms_fields:
            product[label] = get_text(icms_tag, path, ns) if icms_tag is not None else None

        # IPI
        ipi_tag = None
        if imposto is not None:
            for tag in trib_tags:
                ipi_tag = imposto.find(f'.//nfe:IPI/nfe:IPI{tag}', namespaces=ns)
                if ipi_tag is not None:
                    break
        product["Enquadramento IPI"] = get_text(imposto, './/nfe:IPI/nfe:cEnq', ns)
        product["CST IPI"] = get_text(ipi_tag, './/nfe:CST', ns) if ipi_tag is not None else None
        product["BC IPI"] = get_text(ipi_tag, './/nfe:vBC', ns) if ipi_tag is not None else None
        product["Alíquota IPI"] = get_text(ipi_tag, './/nfe:pIPI', ns) if ipi_tag is not None else None
        product["IPI"] = get_text(ipi_tag, './/nfe:vIPI', ns) if ipi_tag is not None else None

        # PIS
        pis_tag = None
        if imposto is not None:
            for tag in trib_tags:
                pis_tag = imposto.find(f'.//nfe:PIS/nfe:PIS{tag}', namespaces=ns)
                if pis_tag is not None:
                    break
        product["CST PIS"] = get_text(pis_tag, './/nfe:CST', ns) if pis_tag is not None else None
        product["BC PIS"] = get_text(pis_tag, './/nfe:vBC', ns) if pis_tag is not None else None
        product["Alíquota PIS"] = get_text(pis_tag, './/nfe:pPIS', ns) if pis_tag is not None else None
        product["BC PIS Prod"] = get_text(pis_tag, './/nfe:qBCProd', ns) if pis_tag is not None else None
        product["Alíquota PIS Prod"] = get_text(pis_tag, './/nfe:vAliqProd', ns) if pis_tag is not None else None
        product["PIS"] = get_text(pis_tag, './/nfe:vPIS', ns) if pis_tag is not None else None

        # COFINS
        cofins_tag = None
        if imposto is not None:
            for tag in trib_tags:
                cofins_tag = imposto.find(f'.//nfe:COFINS/nfe:COFINS{tag}', namespaces=ns)
                if cofins_tag is not None:
                    break
        product["CST COFINS"] = get_text(cofins_tag, './/nfe:CST', ns) if cofins_tag is not None else None
        product["BC COFINS"] = get_text(cofins_tag, './/nfe:vBC', ns) if cofins_tag is not None else None
        product["Alíquota COFINS"] = get_text(cofins_tag, './/nfe:pCOFINS', ns) if cofins_tag is not None else None
        product["BC COFINS Prod"] = get_text(cofins_tag, './/nfe:qBCProd', ns) if cofins_tag is not None else None
        product["Alíquota COFINS Prod"] = get_text(cofins_tag, './/nfe:vAliqProd', ns) if cofins_tag is not None else None
        product["COFINS"] = get_text(cofins_tag, './/nfe:vCOFINS', ns) if cofins_tag is not None else None

        # ISSQN
        issqn = imposto.find('.//nfe:ISSQN', namespaces=ns) if imposto is not None else None
        issqn_fields = [
            ("BC ISSQN", './/nfe:vBC'),
            ("Alíquota ISSQN", './/nfe:vAliq'),
            ("ISSQN", './/nfe:vISSQN'),
            ("Deduções ISSQN", './/nfe:vDeducao'),
            ("Outras retenções ISSQN", './/nfe:vOutro'),
            ("Desconto Incondicionado ISSQN", './/nfe:vDescIncond'),
            ("Desconto Condicionado ISSQN", './/nfe:vDescCond'),
            ("ISSQN Retido", './/nfe:vISSRet'),
            ("Código Serviço", './/nfe:cServico'),
            ("Código Município", './/nfe:cMun'),
            ("Número Processo", './/nfe:nProcesso'),
        ]
        for label, path in issqn_fields:
            product[label] = get_text(issqn, path, ns) if issqn is not None else None

        products.append(product)
    return products