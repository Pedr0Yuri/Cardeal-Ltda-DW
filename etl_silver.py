import pandas as pd
import sqlite3
import ast

print("=" * 60)
print("Iniciando processamento para a Camada Silver...")
print("=" * 60)

conn = sqlite3.connect('ecommerce_dw.db')

df_vendas = pd.read_sql("SELECT * FROM bronze_vendas", conn)
df_clientes = pd.read_sql("SELECT * FROM bronze_clientes", conn)
df_ibge = pd.read_sql("SELECT * FROM bronze_ibge_estados", conn)

total_original = len(df_vendas)
registros_descartados = {}

print(f"\n[INFO] Total de registros brutos recebidos da Bronze: {total_original}")

# --- 1. Tratamento de duplicatas ---
print("\n--- Etapa 1: Remoção de Duplicatas ---")
antes = len(df_vendas)
df_vendas = df_vendas.drop_duplicates()
duplicatas_removidas = antes - len(df_vendas)
registros_descartados['Duplicatas'] = duplicatas_removidas
print(f"  > {duplicatas_removidas} duplicatas removidas.")

# --- 2. Tratamento de nulos ---
print("\n--- Etapa 2: Tratamento de Nulos ---")
nulos_quantidade = df_vendas['quantidade'].isna().sum()
df_vendas['quantidade'] = df_vendas['quantidade'].fillna(1)  # Preenche nulos com 1
print(f"  > {nulos_quantidade} registros com quantidade nula preenchidos com 1.")

nulos_restantes = df_vendas.isna().any(axis=1).sum()
df_vendas = df_vendas.dropna()  # Remove se ainda houver nulos em campos críticos
registros_descartados['Nulos (campos críticos)'] = nulos_restantes
print(f"  > {nulos_restantes} registros descartados por nulos em campos críticos (data, valor, etc).")

# --- 3. Validação de Ranges ---
print("\n--- Etapa 3: Validação de Ranges ---")
antes = len(df_vendas)

# Remover registros com valor <= 0 (erro do ERP)
invalidos_valor = (df_vendas['valor'] <= 0).sum()
df_vendas = df_vendas[df_vendas['valor'] > 0]
registros_descartados['Valor <= 0'] = invalidos_valor
print(f"  > {invalidos_valor} registros removidos por valor <= 0 (preço unitário inválido).")

# Remover registros com quantidade <= 0 (erro do ERP)
invalidos_qtd = (df_vendas['quantidade'] <= 0).sum()
df_vendas = df_vendas[df_vendas['quantidade'] > 0]
registros_descartados['Quantidade <= 0'] = invalidos_qtd
print(f"  > {invalidos_qtd} registros removidos por quantidade <= 0 (lote inválido).")

# --- 4. Padronização de datas ---
print("\n--- Etapa 4: Padronização de Datas ---")
df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'], format='mixed', dayfirst=False)

# --- 5. Criação de colunas derivadas ---
print("\n--- Etapa 5: Criação de Colunas Derivadas ---")
df_vendas['valor_total'] = df_vendas['valor'] * df_vendas['quantidade']
df_vendas['custo_total'] = df_vendas['custo'] * df_vendas['quantidade']
df_vendas['lucro'] = df_vendas['valor_total'] - df_vendas['custo_total']
print("  > Colunas criadas: valor_total, custo_total, lucro.")

# --- 6. Padronização de Clientes ---
print("\n--- Etapa 6: Padronização de Clientes ---")
df_clientes['nome'] = df_clientes['nome'].str.upper()
df_clientes['uf'] = df_clientes['uf'].str.upper()
print("  > Nomes e UFs padronizados para maiúsculas.")

# --- 7. Tratamento dos dados da API do IBGE ---
print("\n--- Etapa 7: Tratamento de Dados IBGE ---")
# Conversão da coluna regiao (vem como dict da API, precisa extrair o nome)
df_ibge['regiao'] = df_ibge['regiao'].astype(str)

def extrair_regiao(regiao_str):
    try:
        dicionario = ast.literal_eval(regiao_str)
        return dicionario['nome']
    except:
        return 'Desconhecida'

df_ibge['nome_regiao'] = df_ibge['regiao'].apply(extrair_regiao)
df_ibge_clean = df_ibge[['sigla', 'nome', 'nome_regiao']].rename(columns={'sigla': 'uf', 'nome': 'nome_estado'})
print(f"  > {len(df_ibge_clean)} estados processados com nome_estado e nome_regiao.")

# --- 8. Integração de fontes (Clientes + IBGE) ---
print("\n--- Etapa 8: Integração de Fontes (Clientes + IBGE) ---")
df_clientes_integrado = pd.merge(df_clientes, df_ibge_clean, on='uf', how='left')
df_clientes_integrado = df_clientes_integrado.fillna('NÃO INFORMADO')
print(f"  > {len(df_clientes_integrado)} subsidiárias enriquecidas com dados geográficos do IBGE.")

# --- Carga na Silver ---
df_vendas.to_sql("silver_vendas", conn, if_exists="replace", index=False)
df_clientes_integrado.to_sql("silver_clientes", conn, if_exists="replace", index=False)

# --- Relatório Final de Qualidade ---
total_descartados = sum(registros_descartados.values())
total_final = len(df_vendas)

print("\n" + "=" * 60)
print("RELATÓRIO DE QUALIDADE DOS DADOS - CAMADA SILVER")
print("=" * 60)
print(f"  Registros recebidos (Bronze):   {total_original}")
for motivo, qtd in registros_descartados.items():
    if qtd > 0:
        print(f"  (-) {motivo}:  {qtd}")
print(f"  -------------------------------------------")
print(f"  Registros válidos (Silver):     {total_final}")
print(f"  Taxa de aproveitamento:         {total_final/total_original*100:.1f}%")
print("=" * 60)

conn.close()
print("\nCamada Silver finalizada!")