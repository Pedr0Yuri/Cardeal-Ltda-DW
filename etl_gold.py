import pandas as pd
import sqlite3

print("Iniciando modelagem para a Camada Gold (Data Warehouse)...")

conn = sqlite3.connect('ecommerce_dw.db')
cursor = conn.cursor()

# chaves estrangeiras no SQLite
cursor.execute("PRAGMA foreign_keys = ON;")

# extração dos dados limpos da camada Silver
df_vendas = pd.read_sql("SELECT * FROM silver_vendas", conn)
df_clientes = pd.read_sql("SELECT * FROM silver_clientes", conn)
df_produtos = pd.read_sql("SELECT * FROM silver_produtos", conn)

# preparando os DataFrames da Camada Gold
print("Preparando Tabelas Dimensão e Fato...")
dim_cliente = df_clientes[['id_cliente', 'nome', 'uf', 'nome_estado', 'nome_regiao']].copy()

df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])
dim_tempo = pd.DataFrame({'data_venda': df_vendas['data_venda'].unique()})
dim_tempo['id_tempo'] = dim_tempo['data_venda'].dt.strftime('%Y%m%d').astype(int)
dim_tempo['ano'] = dim_tempo['data_venda'].dt.year
dim_tempo['mes'] = dim_tempo['data_venda'].dt.month
dim_tempo['dia'] = dim_tempo['data_venda'].dt.day
dim_tempo['trimestre'] = dim_tempo['data_venda'].dt.quarter
# datetime para string
dim_tempo['data_venda'] = dim_tempo['data_venda'].dt.strftime('%Y-%m-%d')

dim_produto = df_produtos[['id_produto', 'nome_produto', 'categoria']].copy()

fato_vendas = df_vendas.copy()
fato_vendas['id_tempo'] = fato_vendas['data_venda'].dt.strftime('%Y%m%d').astype(int)

# Cálculo das métricas analíticas (Fato)
fato_vendas['valor_total'] = fato_vendas['valor'] * fato_vendas['quantidade']
fato_vendas['custo_total'] = fato_vendas['custo'] * fato_vendas['quantidade']
fato_vendas['lucro'] = fato_vendas['valor_total'] - fato_vendas['custo_total']

fato_vendas = fato_vendas[['id_venda', 'id_cliente', 'id_produto', 'id_tempo', 'quantidade', 'valor', 'custo', 'valor_total', 'custo_total', 'lucro']]

# tabelas com PK e FK
print("Criando esquemas com PKs e FKs explícitas no banco de dados...")
cursor.execute("DROP TABLE IF EXISTS fato_vendas;")
cursor.execute("DROP TABLE IF EXISTS dim_cliente;")
cursor.execute("DROP TABLE IF EXISTS dim_produto;")
cursor.execute("DROP TABLE IF EXISTS dim_tempo;")

cursor.execute('''
CREATE TABLE dim_cliente (
    id_cliente INTEGER PRIMARY KEY,
    nome TEXT,
    uf TEXT,
    nome_estado TEXT,
    nome_regiao TEXT
)
''')

cursor.execute('''
CREATE TABLE dim_tempo (
    id_tempo INTEGER PRIMARY KEY,
    data_venda TEXT,
    ano INTEGER,
    mes INTEGER,
    dia INTEGER,
    trimestre INTEGER
)
''')

cursor.execute('''
CREATE TABLE dim_produto (
    id_produto INTEGER PRIMARY KEY,
    nome_produto TEXT,
    categoria TEXT
)
''')

cursor.execute('''
CREATE TABLE fato_vendas (
    id_venda INTEGER PRIMARY KEY,
    id_cliente INTEGER,
    id_produto INTEGER,
    id_tempo INTEGER,
    quantidade INTEGER,
    valor REAL,
    custo REAL,
    valor_total REAL,
    custo_total REAL,
    lucro REAL,
    FOREIGN KEY(id_cliente) REFERENCES dim_cliente(id_cliente),
    FOREIGN KEY(id_produto) REFERENCES dim_produto(id_produto),
    FOREIGN KEY(id_tempo) REFERENCES dim_tempo(id_tempo)
)
''')

# carga na camada Gold
print("Carregando os dados nas tabelas Gold...")
dim_cliente.to_sql("dim_cliente", conn, if_exists="append", index=False)
dim_tempo.to_sql("dim_tempo", conn, if_exists="append", index=False)
dim_produto.to_sql("dim_produto", conn, if_exists="append", index=False)
fato_vendas.to_sql("fato_vendas", conn, if_exists="append", index=False)

conn.commit()
conn.close()
print("Camada Gold finalizada")