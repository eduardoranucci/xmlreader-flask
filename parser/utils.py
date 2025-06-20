from dateutil.parser import parse

def get_text(element, path, ns):
    elem = element.find(path, namespaces=ns)
    return elem.text if elem is not None else None

def parse_date(date):
    try:
        parsed_date = parse(date)
        return parsed_date.strftime("%d/%m/%Y")
    except Exception:
        return date
