from utils import get_text, parse_date
from lxml import etree

def parser_nfse(xml_data):
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

        data = {}

        # Dados gerais
        data["Número"] = get_text(nfse, './/Numero', ns)
        data["Data Emissão"] = parse_date(get_text(nfse, './/DataEmissao', ns))

        # Tomador de Serviço
        taker = get_text(tomador, './/IdentificacaoTomador/CpfCnpj/Cnpj', ns)
        if taker is None:
            taker = get_text(tomador, './/IdentificacaoTomador/CpfCnpj/Cpf', ns)
        data["CNPJ/CPF Tomador"] = taker
        data["Razão Social Tomador"] = get_text(tomador, './/RazaoSocial', ns)
        data["Código Município Tomador"] = get_text(tomador, './/Endereco/CodigoMunicipio', ns)
        data["UF Tomador"] = get_text(tomador, './/Endereco/Uf', ns)
        
        # Prestador de Serviço
        data["CNPJ Prestador"] = get_text(prestador, './/IdentificacaoPrestador/Cnpj', ns)
        data["Inscrição Municipal Prestador"] = get_text(prestador, './/IdentificacaoPrestador/InscricaoMunicipal', ns)
        data["Nome Fantasia Prestador"] = get_text(prestador, './/NomeFantasia', ns)
        data["Código Município Prestador"] = get_text(prestador, './/Endereco/CodigoMunicipio', ns)
        data["UF Prestador"] = get_text(prestador, './/Endereco/Uf', ns)

        data["Natureza"] = get_text(nfse, './/NaturezaOperacao', ns)
        data["Regime Especial"] = get_text(nfse, './/RegimeEspecialTributacao', ns)
        data["Optante Simples Nacional"] = get_text(nfse, './/OptanteSimplesNacional', ns)
        data["Incentivador Cultural"] = get_text(nfse, './/IncentivadorCultural', ns)

        # RPS
        data["Número RPS"] = get_text(rps, './/Numero', ns)
        data["Série RPS"] = get_text(rps, './/Serie', ns)
        data["Tipo RPS"] = get_text(rps, './/Tipo', ns)
        data["Data Emissão RPS"] = parse_date(get_text(nfse, './/DataEmissaoRps', ns))

        # Serviço
        data["Valor Serviços"] = get_text(servico, './/Valores/ValorServicos', ns)
        data["Valor Crédito"] = get_text(nfse, './/ValorCredito', ns)
        data["Valor Deduções"] = get_text(servico, './/Valores/ValorDeducoes', ns)
        data["Valor Líquido NFSe"] = get_text(servico, './/Valores/ValorLiquidoNfse', ns)
        data["Pis"] = get_text(servico, './/Valores/ValorPis', ns)
        data["Cofins"] = get_text(servico, './/Valores/ValorCofins', ns)
        data["Inss"] = get_text(servico, './/Valores/ValorInss', ns)
        data["Ir"] = get_text(servico, './/Valores/ValorIr', ns)
        data["Csll"] = get_text(servico, './/Valores/ValorCsll', ns)
        data["ISS Retido"] = get_text(servico, './/Valores/IssRetido', ns)
        data["ISS"] = get_text(servico, './/Valores/ValorIss', ns)
        data["ISS Retido"] = get_text(servico, './/Valores/ValorIssRetido', ns)
        data["Outras Retenções"] = get_text(servico, './/Valores/OutrasRetencoes', ns)
        data["Base Cálculo"] = get_text(servico, './/Valores/BaseCalculo', ns)
        data["Alíquota"] = get_text(servico, './/Valores/Aliquota', ns)
        data["Desconto Incondicionado"] = get_text(servico, './/Valores/DescontoIncondicionado', ns)
        data["Desconto Condicionado"] = get_text(servico, './/Valores/DescontoCondicionado', ns)
        
        data["Item Lista Serviço"] = get_text(nfse, './/ItemListaServico', ns)
        data["Código CNAE"] = get_text(nfse, './/CodigoCnae', ns)
        data["Código Município"] = get_text(nfse, './/CodigoMunicipio', ns)

        nfses.append(data)

    return nfses

