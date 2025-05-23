from datetime import datetime

def get_text(element, path, ns):
    elem = element.find(path, namespaces=ns)
    return elem.text if elem is not None else None

def parse_date(date_iso):
    try:
        return datetime.strptime(date_iso, "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m/%Y")
    except:
        return date_iso 