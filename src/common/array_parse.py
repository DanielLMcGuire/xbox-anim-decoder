import re

def _extract_body(text, array_name, end_pattern):
    pattern = re.escape(array_name) + r'\[\]\s*=\s*\{(.*?)' + end_pattern
    m = re.search(pattern, text, re.S)
    if not m:
        raise ValueError(f"array '{array_name}' not found")
    return m.group(1)


def _clean_token(tok):
    return tok.strip().rstrip('f')


def parse_flat_array(text, array_name, cast=int, end_pattern=r'\};'):
    body = _extract_body(text, array_name, end_pattern)
    return [cast(_clean_token(tok)) for tok in body.split(',') if tok.strip() != '']


def parse_nested_array(text, array_name, cast=int, end_pattern=r'\};'):
    body = _extract_body(text, array_name, end_pattern)
    rows = []
    depth = 0
    cur = ''
    for ch in body:
        if ch == '{':
            depth += 1
            if depth == 1:
                cur = ''
                continue
        elif ch == '}':
            depth -= 1
            if depth == 0:
                rows.append(cur)
                continue
        if depth >= 1:
            cur += ch

    result = []
    for row in rows:
        vals = [cast(_clean_token(tok)) for tok in row.split(',') if tok.strip() != '']
        result.append(vals)
    return result


def _auto_cast(tok):
    if '.' in tok or 'e' in tok.lower():
        return float(tok)
    return int(tok)


def parse_records_array(text, array_name, end_pattern=r'\};'):
    rows = parse_nested_array(text, array_name, cast=_auto_cast, end_pattern=end_pattern)
    return [tuple(r) for r in rows]


def parse_const(text, name, cast=int):
    m = re.search(re.escape(name) + r'\s*=\s*(-?[\d.]+)\s*;', text)
    if not m:
        raise ValueError(f"const '{name}' not found")
    return cast(m.group(1))


def split_top_level(s, open_c='{', close_c='}'):
    groups = []
    depth = 0
    cur = ''
    for ch in s:
        if ch == open_c:
            depth += 1
            cur += ch
        elif ch == close_c:
            depth -= 1
            cur += ch
            if depth == 0 and cur.strip():
                groups.append(cur.strip())
                cur = ''
        elif depth > 0:
            cur += ch
    return groups
