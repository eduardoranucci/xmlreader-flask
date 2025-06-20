from utils import get_text, parse_date
from lxml import etree

def parse_nfse(xml_data):
    root = etree.fromstring(xml_data)
    ns = {"ns": ""}

    nfse_list = root.findall('.//tcCompNfse', namespaces=ns)
    
    nfses = []
    for inf_nfse in nfse_list:

        nfse = inf_nfse.find('.//Nfse/InfNfse', namespaces=ns)
        rps = nfse.find('.//IdentificacaoRps', namespaces=ns)
        servico = nfse.find('.//Servico', namespaces=ns)
        prestador = nfse.find('.//PrestadorServico', namespaces=ns)
        tomador = nfse.find('.//TomadorServico', namespaces=ns)

        summary = {}

        # Dados gerais
        summary["Número"] = get_text(nfse, './/Numero', ns)
        summary["Data Emissão"] = parse_date(get_text(nfse, './/DataEmissao', ns))

        # Tomador de Serviço
        taker = get_text(tomador, './/IdentificacaoTomador/CpfCnpj/Cnpj', ns)
        if taker is None:
            taker = get_text(tomador, './/IdentificacaoTomador/CpfCnpj/Cpf', ns)
        summary["CNPJ/CPF Tomador"] = taker
        summary["Razão Social Tomador"] = get_text(tomador, './/RazaoSocial', ns)
        summary["Código Município Tomador"] = get_text(tomador, './/Endereco/CodigoMunicipio', ns)
        summary["UF Tomador"] = get_text(tomador, './/Endereco/Uf', ns)
        
        # Prestador de Serviço
        summary["CNPJ Prestador"] = get_text(prestador, './/IdentificacaoPrestador/Cnpj', ns)
        summary["Inscrição Municipal Prestador"] = get_text(prestador, './/IdentificacaoPrestador/InscricaoMunicipal', ns)
        summary["Nome Fantasia Prestador"] = get_text(prestador, './/NomeFantasia', ns)
        summary["Código Município Prestador"] = get_text(prestador, './/Endereco/CodigoMunicipio', ns)
        summary["UF Prestador"] = get_text(prestador, './/Endereco/Uf', ns)

        summary["Natureza"] = get_text(nfse, './/NaturezaOperacao', ns)
        summary["Regime Especial"] = get_text(nfse, './/RegimeEspecialTributacao', ns)
        summary["Optante Simples Nacional"] = get_text(nfse, './/OptanteSimplesNacional', ns)
        summary["Incentivador Cultural"] = get_text(nfse, './/IncentivadorCultural', ns)

        # RPS
        summary["Número RPS"] = get_text(rps, './/Numero', ns)
        summary["Série RPS"] = get_text(rps, './/Serie', ns)
        summary["Tipo RPS"] = get_text(rps, './/Tipo', ns)
        summary["Data Emissão RPS"] = parse_date(get_text(nfse, './/DataEmissaoRps', ns))

        # Serviço
        summary["Valor Serviços"] = get_text(servico, './/Valores/ValorServicos', ns)
        summary["Valor Crédito"] = get_text(nfse, './/ValorCredito', ns)
        summary["Valor Deduções"] = get_text(servico, './/Valores/ValorDeducoes', ns)
        summary["Valor Líquido NFSe"] = get_text(servico, './/Valores/ValorLiquidoNfse', ns)
        summary["Pis"] = get_text(servico, './/Valores/ValorPis', ns)
        summary["Cofins"] = get_text(servico, './/Valores/ValorCofins', ns)
        summary["Inss"] = get_text(servico, './/Valores/ValorInss', ns)
        summary["Ir"] = get_text(servico, './/Valores/ValorIr', ns)
        summary["Csll"] = get_text(servico, './/Valores/ValorCsll', ns)
        summary["ISS Retido"] = get_text(servico, './/Valores/IssRetido', ns)
        summary["ISS"] = get_text(servico, './/Valores/ValorIss', ns)
        summary["ISS Retido"] = get_text(servico, './/Valores/ValorIssRetido', ns)
        summary["Outras Retenções"] = get_text(servico, './/Valores/OutrasRetencoes', ns)
        summary["Base Cálculo"] = get_text(servico, './/Valores/BaseCalculo', ns)
        summary["Alíquota"] = get_text(servico, './/Valores/Aliquota', ns)
        summary["Desconto Incondicionado"] = get_text(servico, './/Valores/DescontoIncondicionado', ns)
        summary["Desconto Condicionado"] = get_text(servico, './/Valores/DescontoCondicionado', ns)
        
        summary["Item Lista Serviço"] = get_text(nfse, './/ItemListaServico', ns)
        summary["Código CNAE"] = get_text(nfse, './/CodigoCnae', ns)
        summary["Código Município"] = get_text(nfse, './/CodigoMunicipio', ns)

        nfses.append(summary)

    data = {
        "Resumo": nfses
    }

    return data

