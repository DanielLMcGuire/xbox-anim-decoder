import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from array_parse import parse_flat_array

text = open('./quats_data.h').read()

quats = parse_flat_array(text, 'theQuats')
signs = parse_flat_array(text, 'theQuatSigns', cast=lambda tok: int(tok, 16))

print('theQuats count', len(quats), '-> nquats', len(quats)//3)
print('theQuatSigns count', len(signs))

json.dump({'theQuats': quats, 'theQuatSigns': signs}, open('./quats_parsed.json', 'w'))
