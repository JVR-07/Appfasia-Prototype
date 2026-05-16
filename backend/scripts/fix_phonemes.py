import re

# Lista de fonemas ordenados por longitud para buscar primero los compuestos
valid_phonemes = ['rr', 'pl', 'br', 'tr', 'gr', 'cl', 'fl', 'ch', 'm', 'p', 'b', 't', 'd', 'l', 'n', 'f', 's', 'r']

import sys
sys.path.append("/home/javier/Documents/code/Appfasia-Prototype/backend/scripts")
from seed_postgres import RECURSOS_SEED

fixed_count = 0

for item in RECURSOS_SEED:
    texto_lower = item['texto'].lower()
    current_fonema = item.get('fonema', '')
    
    if current_fonema not in texto_lower:
        found = False
        for ph in valid_phonemes:
            if ph in texto_lower:
                item['fonema'] = ph
                found = True
                fixed_count += 1
                break
        
        if not found:
            item['fonema'] = texto_lower[0]
            fixed_count += 1

out = "RECURSOS_SEED: List[Dict[str, Any]] = [\n"
for r in RECURSOS_SEED:
    out += f"    {repr(r)},\n"
out += "]"

path_seed = "/home/javier/Documents/code/Appfasia-Prototype/backend/scripts/seed_postgres.py"
with open(path_seed, "r", encoding="utf-8") as f:
    orig_code = f.read()

import re
new_code = re.sub(r"RECURSOS_SEED:\s*List\[Dict\[str,\s*Any\]\]\s*=\s*\[.*?\n\]", out, orig_code, flags=re.DOTALL)

with open(path_seed, "w", encoding="utf-8") as f:
    f.write(new_code)

print(f"Se corrigieron {fixed_count} recursos que tenían fonemas inconsistentes.")
