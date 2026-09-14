import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from delta_codec import decompress_delta_stream

data = json.load(open('./logo_parsed.json'))

xbl_OO_POS_SCALE = 0.009876
xbl_POS_DELTA = 161.715363
xbl_OO_TEX_SCALE = 0.000058
xbl_TEX_DELTA = 0.947661


def decompress_index_data(raw_ints, ncount):
    return decompress_delta_stream(raw_ints, ncount, escape_byte=126,
                                    first_can_escape=False, on_missing='truncate')

def decompress_pos_tex_data(raw_shorts, ncount):
    verts = []
    for i in range(ncount):
        x,y,z,u,v = raw_shorts[i*5:i*5+5]
        X = x*xbl_OO_POS_SCALE + xbl_POS_DELTA
        Y = y*xbl_OO_POS_SCALE + xbl_POS_DELTA
        Z = z*xbl_OO_POS_SCALE + xbl_POS_DELTA
        U = u*xbl_OO_TEX_SCALE + xbl_TEX_DELTA
        V = v*xbl_OO_TEX_SCALE + xbl_TEX_DELTA
        verts.append((X,Y,Z,U,V))
    return verts

meshes = {}
for name, d in data.items():
    verts = decompress_pos_tex_data(d['verts_raw'], d['vertex_count'])
    idx = decompress_index_data(d['indices_raw_bytes'], d['index_count'])
    meshes[name] = {'verts': verts, 'indices': idx}
    rng = (min(idx), max(idx)) if idx else (None,None)
    print(f"{name}: {len(verts)} verts decoded, {len(idx)}/{d['index_count']} indices decoded, "
          f"index range {rng}")

json.dump(meshes, open('./meshes_decoded.json','w'))
