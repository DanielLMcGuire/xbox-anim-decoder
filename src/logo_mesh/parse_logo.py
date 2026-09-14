import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from array_parse import parse_flat_array, parse_const

text = open('./logo_data.h').read()

meshes = ['xboxlogointerior', 'xboxlogolip', 'xboxlogosurfacetop', 'xboxlogosurface', 'tm_slash', 'tm_wordmark']

data = {}
for name in meshes:
    verts = parse_flat_array(text, f'verts_{name}_0C')
    indices_raw = parse_flat_array(text, f'indices_{name}_0C')
    vcount = parse_const(text, f'vertex_count_{name}_0')
    icount = parse_const(text, f'index_count_{name}_0')
    data[name] = {
        'verts_raw': verts,
        'indices_raw_bytes': indices_raw,
        'vertex_count': vcount,
        'index_count': icount,
    }
    print(name, 'verts_raw len', len(verts), '(expect', vcount*5,')',
          'indices_raw len', len(indices_raw), 'index_count(decoded)', icount)

json.dump(data, open('./logo_parsed.json','w'))
