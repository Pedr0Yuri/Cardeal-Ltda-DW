import pandas as pd
import sqlite3

conn = sqlite3.connect('ecommerce_dw.db')

fato_vendas = pd.read_sql("SELECT * FROM fato_vendas", conn)
dim_cliente = pd.read_sql("SELECT * FROM dim_cliente", conn)
dim_tempo = pd.read_sql("SELECT * FROM dim_tempo", conn)
dim_produto = pd.read_sql("SELECT * FROM dim_produto", conn)

fato_vendas.to_csv("gold_fato_vendas.csv", index=False)
dim_cliente.to_csv("gold_dim_cliente.csv", index=False)
dim_tempo.to_csv("gold_dim_tempo.csv", index=False)
dim_produto.to_csv("gold_dim_produto.csv", index=False)

conn.close()
print("Tabelas Gold exportadas!")