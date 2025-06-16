#!/usr/bin/env python3
import re

# Ler o arquivo menu_data.py
with open('menu_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir valores booleanos
content = re.sub(r'"visible":\s*true', '"visible": True', content)
content = re.sub(r'"visible":\s*false', '"visible": False', content)

# Escrever o arquivo corrigido
with open('menu_data.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo menu_data.py corrigido com sucesso!")

# Verificar sintaxe
try:
    import menu_data
    print("✓ Sintaxe Python validada")
except Exception as e:
    print(f"✗ Erro de sintaxe: {e}")