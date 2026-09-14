import json, struct, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'primitives'))
from geom_core import load_quats, mat_scale, make_offset_mat, get_world_mat
from geom_gen import (create_sphere_version, create_box_version, create_cylinder_version, create_cone_version, create_torus_version, create_surf_of_rev_version)
from decode_anim_full import compute_anim_state

NUM_FRAMES = 30
data = json.load(open('../primitives/parsed_data.json'))
quats = load_quats()
surfofrev_vers = json.load(open('./surfofrev_vers.json'))


def decompose_matrix(M):
    t = (M[3,0], M[3,1], M[3,2])

    sx = math.sqrt(M[0][0]**2 + M[0][1]**2 + M[0][2]**2)
    sy = math.sqrt(M[1][0]**2 + M[1][1]**2 + M[1][2]**2)
    sz = math.sqrt(M[2][0]**2 + M[2][1]**2 + M[2][2]**2)

    R = [
        [M[i][j] / (sx if i==0 else (sy if i==1 else sz)) for j in range(3)] for i in range(3)
    ]

    tr = R[0][0] + R[1][1] + R[2][2]
    if tr > 0:
        S = math.sqrt(tr + 1.0) * 2
        qw = 0.25 * S
        qx = (R[1][2] - R[2][1]) / S
        qy = (R[2][0] - R[0][2]) / S
        qz = (R[0][1] - R[1][0]) / S
    elif (R[0][0] > R[1][1]) and (R[0][0] > R[2][2]):
        S = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        qw = (R[1][2] - R[2][1]) / S
        qx = 0.25 * S
        qy = (R[0][1] + R[1][0]) / S
        qz = (R[0][2] + R[2][0]) / S
    elif R[1][1] > R[2][2]:
        S = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        qw = (R[2][0] - R[0][2]) / S
        qx = (R[0][1] + R[1][0]) / S
        qy = 0.25 * S
        qz = (R[1][2] + R[2][1]) / S
    else:
        S = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
        qw = (R[0][1] - R[1][0]) / S
        qx = (R[0][2] + R[2][0]) / S
        qy = (R[1][2] + R[2][1]) / S
        qz = 0.25 * S

    return t, (qx, qy, qz, qw), (sx, sy, sz)

bin_data = bytearray()
def add_to_bin(values, fmt):
    global bin_data
    offset = len(bin_data)
    for val in values:
        if isinstance(val, (list, tuple)):
            bin_data.extend(struct.pack(fmt * len(val), *val))
        else:
            bin_data.extend(struct.pack(fmt, val))
    return offset

meshes_geo = {}

for i, v in enumerate(data['theSphereVers']):
    v_pos, v_tri = create_sphere_version(int(v[0]), 0)
    v_off = add_to_bin(v_pos, 'f')
    i_off = add_to_bin([idx for tri in v_tri for idx in tri], 'I')
    meshes_geo[f"sph_{i}"] = {"v_off": v_off, "i_off": i_off, "v_cnt": len(v_pos), "i_cnt": len(v_tri)*3}

v_pos, v_tri = create_box_version()
v_off = add_to_bin(v_pos, 'f')
i_off = add_to_bin([idx for tri in v_tri for idx in tri], 'I')
meshes_geo["box"] = {"v_off": v_off, "i_off": i_off, "v_cnt": len(v_pos), "i_cnt": len(v_tri)*3}

for i, v in enumerate(data['theCylinderVers']):
    v_pos, v_tri = create_cylinder_version(int(v[1]), int(v[0]), 0)
    v_off = add_to_bin(v_pos, 'f')
    i_off = add_to_bin([idx for tri in v_tri for idx in tri], 'I')
    meshes_geo[f"cyl_{i}"] = {"v_off": v_off, "i_off": i_off, "v_cnt": len(v_pos), "i_cnt": len(v_tri)*3}

for i, v in enumerate(data['theTorusVers']):
    v_pos, v_tri = create_torus_version(v[0], int(v[1]), int(v[2]), 0)
    v_off = add_to_bin(v_pos, 'f')
    i_off = add_to_bin([idx for tri in v_tri for idx in tri], 'I')
    meshes_geo[f"tor_{i}"] = {"v_off": v_off, "i_off": i_off, "v_cnt": len(v_pos), "i_cnt": len(v_tri)*3}

for i, v in enumerate(data['theConeVers']):
    v_pos, v_tri = create_cone_version(v[0], v[1], v[2], int(v[3]), int(v[4]), 0)
    v_off = add_to_bin(v_pos, 'f')
    i_off = add_to_bin([idx for tri in v_tri for idx in tri], 'I')
    meshes_geo[f"con_{i}"] = {"v_off": v_off, "i_off": i_off, "v_cnt": len(v_pos), "i_cnt": len(v_tri)*3}

for i, v in enumerate(surfofrev_vers):
    v_pos, v_tri = create_surf_of_rev_version(v['pts'], (v['ax'],v['ay'],v['az']), (v['px'],v['py'],v['pz']), v['nSegs'], 0)
    v_off = add_to_bin(v_pos, 'f')
    i_off = add_to_bin([idx for tri in v_tri for idx in tri], 'I')
    meshes_geo[f"sov_{i}"] = {"v_off": v_off, "i_off": i_off, "v_cnt": len(v_pos), "i_cnt": len(v_tri)*3}

nodes = []
animations = []
times = [f / (NUM_FRAMES - 1) for f in range(NUM_FRAMES)]
time_off = add_to_bin(times, 'f')

frame_anim_states = [compute_anim_state(fpos, quats) for fpos in times]


def process_insts(inst_list, mesh_key_func, scale_func, pos_anim_idx, rot_anim_idx, quat_idx, trans_vals):
    for inst in inst_list:
        m_key = mesh_key_func(inst)
        s_mat = scale_func(inst)
        o_mat = make_offset_mat(quats, quat_idx(inst), *trans_vals(inst))

        t_vals, r_vals, s_vals = [], [], []
        for f in range(NUM_FRAMES):
            pos_anims, rot_anims = frame_anim_states[f]
            world_mat = get_world_mat(s_mat, o_mat, pos_anim_idx(inst), rot_anim_idx(inst), pos_anims, rot_anims)
            t, r, s = decompose_matrix(world_mat)
            t_vals.append((t[0], t[1], t[2]))
            r_vals.append((r[0], r[1], r[2], r[3]))
            s_vals.append((s[0], s[1], s[2]))

        t_off = add_to_bin(t_vals, 'f')
        r_off = add_to_bin(r_vals, 'f')
        s_off = add_to_bin(s_vals, 'f')

        node_idx = len(nodes)
        nodes.append({"mesh": m_key})
        animations.append({
            "node": node_idx,
            "t_off": t_off, "r_off": r_off, "s_off": s_off
        })

process_insts(data['theSphereInsts'], lambda x: f"sph_{int(x[3])}", lambda x: mat_scale(x[6],x[6],x[6]), lambda x: x[4], lambda x: x[5], lambda x: None, lambda x: x[0:3])
process_insts(data['theBoxInsts'], lambda x: "box", lambda x: mat_scale(x[9],x[7],x[8]), lambda x: x[5], lambda x: x[6], lambda x: x[0], lambda x: x[1:4])
process_insts(data['theCylinderInsts'], lambda x: f"cyl_{int(x[4])}", lambda x: mat_scale(x[7],x[7],x[8]*2.0), lambda x: x[5], lambda x: x[6], lambda x: x[0], lambda x: x[1:4])
process_insts(data['theTorusInsts'], lambda x: f"tor_{int(x[4])}", lambda x: mat_scale(x[7],x[7],x[7]), lambda x: x[5], lambda x: x[6], lambda x: x[0], lambda x: x[1:4])
process_insts(data['theConeInsts'], lambda x: f"con_{int(x[4])}", lambda x: mat_scale(1,1,1), lambda x: x[5], lambda x: x[6], lambda x: x[0], lambda x: x[1:4])
process_insts(data['theSurfOfRevInsts'], lambda x: f"sov_{int(x[4])}", lambda x: mat_scale(1,1,1), lambda x: x[5], lambda x: x[6], lambda x: x[0], lambda x: x[1:4])

bvs = []
accs = []
def add_acc(off, cnt, typ, comp_cnt):
    bv_idx = len(bvs)
    byte_len = cnt * comp_cnt * (4 if typ in ["f", "I"] else 0)

    bvs.append({
        "buffer": 0,
        "byteOffset": off,
        "byteLength": byte_len
    })

    acc_idx = len(accs)
    accs.append({
        "bufferView": bv_idx,
        "componentType": 5126 if typ == "f" else 5125,
        "count": cnt,
        "type": "VEC3" if comp_cnt == 3 else ("VEC4" if comp_cnt == 4 else "SCALAR")
    })
    return acc_idx

mesh_name_to_idx = {}
gltf_meshes = []
for i, (name, geo) in enumerate(meshes_geo.items()):
    mesh_name_to_idx[name] = i
    v_acc = add_acc(geo["v_off"], geo["v_cnt"], "f", 3)
    i_acc = add_acc(geo["i_off"], geo["i_cnt"], "I", 1)
    gltf_meshes.append({
        "primitives": [{
            "attributes": {"POSITION": v_acc},
            "indices": i_acc
        }]
    })

gltf_nodes = [{"mesh": mesh_name_to_idx[n["mesh"]]} for n in nodes]

gltf = {
    "asset": {"version": "2.0", "generator": "Xbox Anim Export"},
    "scenes": [{"nodes": list(range(len(nodes)))}],
    "nodes": gltf_nodes,
    "meshes": gltf_meshes,
    "animations": [],
    "buffers": [{"byteLength": len(bin_data), "uri": "xbox_anim.bin"}]
}

anim_channels = []
anim_samplers = []
for a in animations:
    s_idx = len(anim_samplers)
    anim_samplers.append({"input": add_acc(time_off, NUM_FRAMES, "f", 1), "interpolation": "LINEAR", "output": add_acc(a["t_off"], NUM_FRAMES, "f", 3)})
    anim_channels.append({"sampler": s_idx, "target": {"node": a["node"], "path": "translation"}})

    s_idx = len(anim_samplers)
    anim_samplers.append({"input": add_acc(time_off, NUM_FRAMES, "f", 1), "interpolation": "LINEAR", "output": add_acc(a["r_off"], NUM_FRAMES, "f", 4)})
    anim_channels.append({"sampler": s_idx, "target": {"node": a["node"], "path": "rotation"}})

    s_idx = len(anim_samplers)
    anim_samplers.append({"input": add_acc(time_off, NUM_FRAMES, "f", 1), "interpolation": "LINEAR", "output": add_acc(a["s_off"], NUM_FRAMES, "f", 3)})
    anim_channels.append({"sampler": s_idx, "target": {"node": a["node"], "path": "scale"}})

gltf["animations"].append({"channels": anim_channels, "samplers": anim_samplers})
gltf["bufferViews"] = bvs
gltf["accessors"] = accs

with open('xbox_anim.gltf', 'w') as f:
    json.dump(gltf, f, indent=2)
with open('xbox_anim.bin', 'wb') as f:
    f.write(bin_data)

print("Exported xbox_anim.gltf and xbox_anim.bin. Import these into Blender via File -> Import -> glTF 2.0")
