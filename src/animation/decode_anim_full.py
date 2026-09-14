import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from delta_codec import decompress_delta_stream

anim = json.load(open('./anim_parsed.json'))

OO_POS_ANIM_SCALE_X = 0.002755
OO_POS_ANIM_SCALE_Y = 0.002755
OO_POS_ANIM_SCALE_Z = 0.002440
POS_ANIM_DELTA_X = -0.159046
POS_ANIM_DELTA_Y = -0.741611
POS_ANIM_DELTA_Z = 2.155624

MAX_ROT_SAMPLES = 30
MAX_POS_SAMPLES = 30


def decompress_indices_anim(raw_ints, ncount=30):
    return decompress_delta_stream(raw_ints, ncount, escape_byte=127,
                                    first_can_escape=True, on_missing='hold')


def decompress_vecs(flat_shorts, nvecs):
    vecs = []
    for i in range(nvecs):
        x,y,z = flat_shorts[i*3:i*3+3]
        X = x*OO_POS_ANIM_SCALE_X + POS_ANIM_DELTA_X
        Y = y*OO_POS_ANIM_SCALE_Y + POS_ANIM_DELTA_Y
        Z = z*OO_POS_ANIM_SCALE_Z + POS_ANIM_DELTA_Z
        vecs.append((X,Y,Z))
    return vecs

pPos = decompress_vecs(anim['thePos'], len(anim['thePos'])//3)

pQuatIdSeq = [decompress_indices_anim(row, MAX_ROT_SAMPLES) for row in anim['theRotAnimSeq']]
pPosIdSeq = [decompress_indices_anim(row, MAX_POS_SAMPLES) for row in anim['thePosAnimSeq']]

if __name__ == '__main__':
    import itertools
    allq = list(itertools.chain.from_iterable(pQuatIdSeq))
    allp = list(itertools.chain.from_iterable(pPosIdSeq))
    print("pQuatIdSeq full range:", min(allq), max(allq), "(must be within [0,412])")
    print("pPosIdSeq full range:", min(allp), max(allp), "(must be within [0,319])")


def lerp3(a, b, t):
    return (a[0]*(1-t)+b[0]*t, a[1]*(1-t)+b[1]*t, a[2]*(1-t)+b[2]*t)

def slerp_quat(a, b, t):
    ax,ay,az,aw = a
    bx,by,bz,bw = b
    dot = ax*bx+ay*by+az*bz+aw*bw
    if dot < 0:
        bx,by,bz,bw = -bx,-by,-bz,-bw
        dot = -dot
    if dot > 0.9995:
        rx = ax+(bx-ax)*t; ry=ay+(by-ay)*t; rz=az+(bz-az)*t; rw=aw+(bw-aw)*t
        n = math.sqrt(rx*rx+ry*ry+rz*rz+rw*rw)
        return (rx/n, ry/n, rz/n, rw/n)
    theta0 = math.acos(max(-1.0,min(1.0,dot)))
    theta = theta0*t
    s0 = math.cos(theta) - dot*math.sin(theta)/math.sin(theta0)
    s1 = math.sin(theta)/math.sin(theta0)
    return (ax*s0+bx*s1, ay*s0+by*s1, az*s0+bz*s1, aw*s0+bw*s1)

def compute_anim_state(fpos, quats):
    n_pos_seq = len(pPosIdSeq)
    n_rot_seq = len(pQuatIdSeq)

    pos_anims = []
    ffrac_pos = fpos * (MAX_POS_SAMPLES-2)
    pos_id = int(ffrac_pos)
    ffrac = ffrac_pos - pos_id
    for i in range(n_pos_seq):
        if fpos <= 0.0:
            pos_anims.append(pPos[pPosIdSeq[i][0]])
        elif fpos >= 1.0:
            pos_anims.append(pPos[pPosIdSeq[i][MAX_POS_SAMPLES-1]])
        else:
            a = pPos[pPosIdSeq[i][pos_id]]
            b = pPos[pPosIdSeq[i][pos_id+1]]
            pos_anims.append(lerp3(a,b,ffrac))

    rot_anims = []
    ffrac_pos_r = fpos * (MAX_ROT_SAMPLES-2)
    rot_id = int(ffrac_pos_r)
    ffrac_r = ffrac_pos_r - rot_id
    for i in range(n_rot_seq):
        if fpos <= 0.0:
            rot_anims.append(quats[pQuatIdSeq[i][0]])
        elif fpos >= 1.0:
            rot_anims.append(quats[pQuatIdSeq[i][MAX_ROT_SAMPLES-1]])
        else:
            a = quats[pQuatIdSeq[i][rot_id]]
            b = quats[pQuatIdSeq[i][rot_id+1]]
            rot_anims.append(slerp_quat(a,b,ffrac_r))

    return pos_anims, rot_anims

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'primitives'))
    from geom_core import load_quats
    quats = load_quats()
    pos_anims, rot_anims = compute_anim_state(0.5, quats)
    print("sample pos_anims[0..3]:", pos_anims[:4])
    print("sample rot_anims[0..3]:", rot_anims[:4])
    json.dump({'pos_anims': pos_anims, 'rot_anims': rot_anims},
               open('./mid_anim_state.json','w'))
