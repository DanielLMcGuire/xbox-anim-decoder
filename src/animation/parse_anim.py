import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from array_parse import parse_nested_array, parse_flat_array

text = open('./anim_data.h').read()

rot_anim_seq = parse_nested_array(text, 'theRotAnimSeq', end_pattern=r'\n\};')
pos_anim_seq = parse_nested_array(text, 'thePosAnimSeq', end_pattern=r'\n\};')
the_pos = parse_flat_array(text, 'thePos')

print("theRotAnimSeq rows:", len(rot_anim_seq), "first row len:", len(rot_anim_seq[0]))
print("thePosAnimSeq rows:", len(pos_anim_seq), "first row len:", len(pos_anim_seq[0]))
print("thePos count:", len(the_pos), "-> num vecs:", len(the_pos)//3)

json.dump({
    'theRotAnimSeq': rot_anim_seq,
    'thePosAnimSeq': pos_anim_seq,
    'thePos': the_pos,
}, open('./anim_parsed.json','w'))
