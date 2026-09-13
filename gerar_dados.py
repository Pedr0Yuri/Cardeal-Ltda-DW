import pandas as pd
import random
import json
from datetime import datetime, timedelta

random.seed(42)

start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 9, 30)
days_between = (end_date - start_date).days

faixas_preco = {
    100: (2500.0, 5000.0), # Notebook
    101: (1500.0, 4000.0), # Celular
    102: (500.0, 1500.0),  # Monitor
    103: (2000.0, 4500.0), # Geladeira
    104: (800.0, 2000.0),  # Fogão
    105: (400.0, 800.0),   # Micro-ondas
    106: (3500.0, 4500.0)  # PS5
}

# probabilidade de venda por produto
produtos_pesos = {
    100: 0.08, # Notebook
    101: 0.35, # Celular
    102: 0.20, # Monitor
    103: 0.05, # Geladeira
    104: 0.15, # Fogão
    105: 0.15, # Micro-ondas
    106: 0.02  # PS5
}

# menor que 1 = lucro, maior que 1 = prejuízo

dna_produto = {
    100: 0.80, # 20% margem base
    101: 0.85, # 15% margem base
    102: 0.80, 
    103: 0.90, 
    104: 0.90, 
    105: 1.15, 
    106: 0.90  
}

# Rentabilidade das Subsidiárias
dna_cliente = {
    1: 0.85,  # MG - Lucro
    2: 0.75,  # PE - Muito Lucro
    3: 1.15,  # RJ - Prejuízo Forte
    4: 0.80,  # MT - Lucro
    5: 1.10,  # RJ - Prejuízo
    6: 1.05,  # DF - Leve Prejuízo
    7: 0.80,  # PE - Lucro
    8: 0.85,  # PE - Lucro
    9: 1.05,  # RJ - Leve Prejuízo
    10: 0.90, # GO - Lucro Menor
    11: 0.80, # PE - Lucro
    12: 0.85, # PE - Lucro
    13: 0.70, # SP - Muito Lucro
    14: 0.90, # BA - Lucro Menor
    15: 1.10  # BA - Prejuízo
}

with open('clientes.json', 'r', encoding='utf-8') as f:
    clientes = json.load(f)
cliente_ids = [c['id_cliente'] for c in clientes]

n_vendas = 1200
vendas_data = []

produtos_lista = list(produtos_pesos.keys())
pesos_lista = list(produtos_pesos.values())

for i in range(n_vendas):
    data_venda = start_date + timedelta(days=random.randint(0, days_between))
    cli = random.choice(cliente_ids)
    
    # distribui por peso
    prod = random.choices(produtos_lista, weights=pesos_lista, k=1)[0]
    
    # qtde por lote 
    if prod in [101, 102, 104, 105]: # Celular, Monitor, Fogão, Micro-ondas
        qtd = random.randint(10, 50) # Lotes maiores
    else: # Notebook, Geladeira, PS5
        qtd = random.randint(2, 15)  # Lotes menores (itens caros)

    val = round(random.uniform(faixas_preco[prod][0], faixas_preco[prod][1]), 2)

    # Cálculo rentabilidade baseada no perfil do produto e do cliente
    mu_base = (dna_produto[prod] * 0.4) + (dna_cliente[cli] * 0.6)
    sigma = 0.04
    
    fator_custo = random.gauss(mu_base, sigma)
    fator_custo = max(0.50, min(fator_custo, 1.50))  

    custo = round(val * fator_custo, 2)
    
    
    if random.random() < 0.02:  # 2% de chance de vir sem quantidade
        qtd = None
    
    # Sujeira intencional: valores zerados ou negativos (simulando erro do ERP)
    if random.random() < 0.01:  # 1% de chance de valor zerado
        val = 0.0
    if random.random() < 0.005:  # 0.5% de chance de quantidade negativa
        qtd = -random.randint(1, 10)

    data_str = data_venda.strftime("%Y-%m-%d")
    if random.random() < 0.01:  # 1% de chance de vir sem data (nulo)
        data_str = "" # String vazia para o pandas tratar como NaT

    vendas_data.append({
        "id_venda": i + 1,
        "id_cliente": cli,
        "id_produto": prod,
        "data_venda": data_str,
        "valor": val,
        "custo": custo,
        "quantidade": qtd
    })

df_vendas = pd.DataFrame(vendas_data)

# Introduz duplicatas intencionais
duplicatas = df_vendas.sample(15, random_state=42)
df_vendas = pd.concat([df_vendas, duplicatas], ignore_index=True)

df_vendas.to_csv("vendas.csv", index=False)

print(f"Arquivo 'vendas.csv' gerado com {len(df_vendas)} transacoes")