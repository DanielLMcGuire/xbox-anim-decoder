import os
import numpy as np
import math, json

OO_PRIM_TRANS_SCALE_X = 0.004131
OO_PRIM_TRANS_SCALE_Y = 0.008252
OO_PRIM_TRANS_SCALE_Z = 0.004421
PRIM_TRANS_DELTA_X = -27.844984
PRIM_TRANS_DELTA_Y = -0.228729
PRIM_TRANS_DELTA_Z = 0.497086

def mat_identity():
    return np.identity(4)

def mat_scale(sx, sy, sz):
    M = np.identity(4)
    M[0,0] = sx; M[1,1] = sy; M[2,2] = sz
    return M

def mat_mul(A, B):
    return A @ B

def mat_inverse(A):
    return np.linalg.inv(A)

def mat_transpose(A):
    return A.T

def transform_vector(v, M):
    v = np.array([v[0], v[1], v[2], 0.0])
    out = v @ M
    return out[:3]

def transform_point(v, M):
    v = np.array([v[0], v[1], v[2], 1.0])
    out = v @ M
    return out[:3]

def rot_from_lh_quat(q):
    x,y,z,w = q
    M = np.identity(4)
    M[0,0] = w*w + x*x - y*y - z*z
    M[1,0] = 2*x*y + 2*w*z
    M[2,0] = 2*x*z - 2*w*y
    M[3,0] = 0.0

    M[0,1] = 2*x*y - 2*w*z
    M[1,1] = w*w - x*x + y*y - z*z
    M[2,1] = 2*y*z + 2*w*x
    M[3,1] = 0.0

    M[0,2] = 2*x*z + 2*w*y
    M[1,2] = 2*y*z - 2*w*x
    M[2,2] = w*w - x*x - y*y + z*z
    M[3,2] = 0.0

    M[0,3] = M[1,3] = M[2,3] = 0.0
    M[3,3] = 1.0
    return M

def rot_from_rh_quat(q):
    x,y,z,w = q
    M = np.identity(4)
    M[0,0] = w*w + x*x - y*y - z*z
    M[0,1] = 2*x*y + 2*w*z
    M[0,2] = 2*x*z - 2*w*y
    M[1,0] = 2*x*y - 2*w*z
    M[1,1] = w*w - x*x + y*y - z*z
    M[1,2] = 2*y*z + 2*w*x
    M[2,0] = 2*x*z + 2*w*y
    M[2,1] = 2*y*z - 2*w*x
    M[2,2] = w*w - x*x - y*y + z*z
    M[3,0]=M[3,1]=M[3,2]=0.0
    M[3,3]=1.0
    return M

def quat_from_axis_angle(axis, theta):
    ax = normalize(axis)
    s = math.sin(theta/2.0)
    c = math.cos(theta/2.0)
    return (ax[0]*s, ax[1]*s, ax[2]*s, c)

def cross(a, b):
    return np.cross(a, b)

def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        return np.array(v, dtype=float)
    return np.array(v, dtype=float) / n

def sincos(theta):
    return math.sin(theta), math.cos(theta)

def decompress_quats(flat_shorts, sign_dwords, nquats):
    quats = []
    oo_scale = 1.0/32750.0
    for i in range(nquats):
        x = flat_shorts[i*3+0] * oo_scale
        y = flat_shorts[i*3+1] * oo_scale
        z = flat_shorts[i*3+2] * oo_scale
        w2 = 1.0 - x*x - y*y - z*z
        w = math.sqrt(w2) if w2 > 0 else 0.0
        idw = i >> 5
        bpos = i & 31
        b_pos_w = (sign_dwords[idw] & (1 << bpos)) != 0
        if not b_pos_w:
            w = -w
        quats.append((x,y,z,w))
    return quats

def load_quats():
    _here = os.path.dirname(os.path.abspath(__file__))
    d = json.load(open(os.path.join(_here, 'quats_parsed.json')))
    nums = d['theQuats']
    signs = d['theQuatSigns']
    nquats = len(nums)//3
    return decompress_quats(nums, signs, nquats)

def offset_translation(tx, ty, tz):
    return (tx*OO_PRIM_TRANS_SCALE_X + PRIM_TRANS_DELTA_X,
            ty*OO_PRIM_TRANS_SCALE_Y + PRIM_TRANS_DELTA_Y,
            tz*OO_PRIM_TRANS_SCALE_Z + PRIM_TRANS_DELTA_Z)


def make_offset_mat(quats, idQuat, tx, ty, tz):
    if idQuat is None:
        M = mat_identity()
    else:
        M = rot_from_lh_quat(quats[int(idQuat)])
    ox, oy, oz = offset_translation(tx, ty, tz)
    M[3, 0] = ox; M[3, 1] = oy; M[3, 2] = oz
    return M


def get_world_mat(matScale, matOffset, idxPosAnim, idxRotAnim, pos_anims=None, rot_anims=None):
    idxPosAnim = int(idxPosAnim) if idxPosAnim is not None else -1
    idxRotAnim = int(idxRotAnim) if idxRotAnim is not None else -1
    use_rot = idxRotAnim >= 0 and rot_anims is not None
    use_pos = idxPosAnim >= 0 and pos_anims is not None

    if not (use_rot or use_pos):
        return mat_mul(matScale, matOffset)

    if use_rot:
        rot_anim_mat = rot_from_lh_quat(rot_anims[idxRotAnim])
        tmp = mat_mul(matOffset, rot_anim_mat)
    else:
        tmp = matOffset.copy()
    if use_pos:
        px, py, pz = pos_anims[idxPosAnim]
        tmp[3, 0] += px; tmp[3, 1] += py; tmp[3, 2] += pz
    return mat_mul(matScale, tmp)
