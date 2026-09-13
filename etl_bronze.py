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
response = requests.get(url_ibge)

if response.status_code == 200:
    dados_ibge = response.json()
    df_ibge_bronze = pd.DataFrame(dados_ibge)
    # Serializa coluna 'regiao' (dict) para string para compatibilidade com SQLite
    df_ibge_bronze['regiao'] = df_ibge_bronze['regiao'].astype(str)
    df_ibge_bronze.to_sql("bronze_ibge_estados", conn, if_exists="replace", index=False)
    print("Dados de Estados (API IBGE) carregados na Bronze.")
else:
    print("Erro ao acessar a API do IBGE.")

conn.close()
print("Camada Bronze finalizada")