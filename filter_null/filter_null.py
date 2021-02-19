import json

with open('data.json') as f:
    d = json.loads(f.read())

d = {x['navnelbnr']: x for x in d if not x['seneste_kontrol'] and x['cvrnr']}

with open('out.json', 'w') as f:
    f.write(json.dumps(d, indent=4))