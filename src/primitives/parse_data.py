import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from array_parse import parse_records_array

if __name__ == '__main__':
    text = open('./raw_data.h').read()
    out = {}
    for name in ['theSphereInsts','theSphereVers','theCylinderInsts','theCylinderVers',
                 'theBoxInsts','theTorusInsts','theTorusVers','theConeInsts','theConeVers',
                 'theSurfOfRevInsts']:
        data = parse_records_array(text, name)
        out[name] = data
        print(name, len(data), data[0] if data else None)

    with open('./parsed_data.json','w') as f:
        json.dump(out, f)
