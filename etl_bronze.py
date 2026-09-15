import pandas as pd
import requests
import sqlite3
import json

conn = sqlite3.connect('ecommerce_dw.db')

print("Iniciando extração para a Camada Bronze...")

df_vendas_bronze = pd.read_csv("vendas.csv")
df_vendas_bronze.to_sql("bronze_vendas", conn, if_exists="replace", index=False)
print("CSV carregado na Bronze.")

with open("clientes.json", "r") as f:
    dados_clientes = json.load(f)
df_clientes_bronze = pd.DataFrame(dados_clientes)
df_clientes_bronze.to_sql("bronze_clientes", conn, if_exists="replace", index=False)
print("- Clientes (JSON) carregados na Bronze.")

url_ibge = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
try:
    response = requests.get(url_ibge, timeout=10)
    response.raise_for_status()
    dados_ibge = response.json()
    df_ibge_bronze = pd.DataFrame(dados_ibge)
    # Serializa coluna 'regiao' (dict) para string para compatibilidade com SQLite
    df_ibge_bronze['regiao'] = df_ibge_bronze['regiao'].astype(str)
    df_ibge_bronze.to_sql("bronze_ibge_estados", conn, if_exists="replace", index=False)
    print("Dados de Estados (API IBGE) carregados na Bronze.")
except Exception as e:
    print(f"Aviso: Erro ao acessar a API do IBGE ({e}).")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bronze_ibge_estados'")
    if cursor.fetchone():
        print("Usando dados de estados previamente cacheados no banco de dados.")
    else:
        print("Sem cache disponível. Criando fallback vazio para não quebrar a camada Silver.")
        df_ibge_fallback = pd.DataFrame(columns=['id', 'sigla', 'nome', 'regiao'])
        df_ibge_fallback.to_sql("bronze_ibge_estados", conn, if_exists="replace", index=False)

# Simulação de ingestão da base de produtos
produtos_brutos = [
    {"id_produto": 100, "nome_produto": "Notebook", "categoria": "Eletrônicos"},
    {"id_produto": 101, "nome_produto": "Celular", "categoria": "Eletrônicos"},
    {"id_produto": 102, "nome_produto": "Monitor", "categoria": "Eletrônicos"},
    {"id_produto": 103, "nome_produto": "Geladeira", "categoria": "Eletrodomésticos"},
    {"id_produto": 104, "nome_produto": "Fogão", "categoria": "Eletrodomésticos"},
    {"id_produto": 105, "nome_produto": "Micro-ondas", "categoria": "Eletrodomésticos"},
    {"id_produto": 106, "nome_produto": "PlayStation 5", "categoria": "Eletrônicos"}
]
df_produtos_bronze = pd.DataFrame(produtos_brutos)
df_produtos_bronze.to_sql("bronze_produtos", conn, if_exists="replace", index=False)
print("Dados de Produtos carregados na Bronze.")

conn.close()
print("Camada Bronze finalizada")