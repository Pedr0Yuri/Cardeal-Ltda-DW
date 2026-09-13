import json
with open('clientes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for d in data:
    if " - " not in d['nome']:
        d['nome'] = f"{d['nome']} - {d['uf']}"
with open('clientes.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
