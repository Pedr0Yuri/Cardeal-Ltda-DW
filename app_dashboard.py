import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Cardeal Centro de Distribuicao Ltda.", layout="wide")

st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #1E1E2E;
    border: 1px solid #333344;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
div[data-testid="metric-container"] > label {
    font-size: 1rem !important;
    font-weight: 600;
    color: #A0A0B0;
    margin-bottom: 5px;
}
div[data-testid="metric-container"] > div > div {
    font-size: 1.8rem !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def filtros_cascata(df_base, sufixo):
    regioes = sorted(df_base['nome_regiao'].unique().tolist())

    reg_key = f'regiao_{sufixo}'
    est_key = f'estado_{sufixo}'
    cli_key = f'cliente_{sufixo}'
    prev_reg = f'_prev_reg_{sufixo}'
    prev_est = f'_prev_est_{sufixo}'

    col1, col2, col3 = st.columns(3)

    with col1:
        regioes_sel = st.multiselect("Região", options=regioes, default=regioes, key=reg_key)

    
    if regioes_sel:
        df_por_regiao = df_base[df_base['nome_regiao'].isin(regioes_sel)]
    else:
        df_por_regiao = df_base

    estados_disp = sorted(df_por_regiao['nome_estado'].unique().tolist())

    if prev_reg in st.session_state and st.session_state[prev_reg] != regioes_sel:
        
        if not regioes_sel:
            st.session_state[est_key] = []
            st.session_state[cli_key] = []
        else:
          
            st.session_state[est_key] = estados_disp
            st.session_state[cli_key] = sorted(df_por_regiao['nome'].unique().tolist())
        
        st.session_state[prev_reg] = regioes_sel
        st.session_state[prev_est] = st.session_state[est_key]
        st.rerun()
    st.session_state[prev_reg] = regioes_sel

    with col2:
        estados_sel = st.multiselect("Estado", options=estados_disp, default=estados_disp, key=est_key)

  
    if estados_sel:
        df_por_estado = df_por_regiao[df_por_regiao['nome_estado'].isin(estados_sel)]
        clientes_disp = sorted(df_por_estado['nome'].unique().tolist())
    else:
        df_por_estado = df_base.head(0)
        clientes_disp = []

    if prev_est in st.session_state and st.session_state[prev_est] != estados_sel:
        if not estados_sel:
            st.session_state[cli_key] = []
        else:
            st.session_state[cli_key] = clientes_disp
        st.session_state[prev_est] = estados_sel
        st.rerun()
    st.session_state[prev_est] = estados_sel

    with col3:
        clientes_sel = st.multiselect("Cliente", options=clientes_disp, default=clientes_disp, key=cli_key)

    if clientes_sel:
        df_final = df_por_estado[df_por_estado['nome'].isin(clientes_sel)]
    else:
        df_final = df_base.head(0)

    return df_final


def load_data():
    import sqlite3
    conn = sqlite3.connect('ecommerce_dw.db')
    
 
    query = """
    SELECT 
        f.*, 
        c.nome, c.uf, c.nome_estado, c.nome_regiao,
        t.data_venda, t.ano, t.mes, t.dia, t.trimestre,
        p.nome_produto, p.categoria
    FROM fato_vendas f
    JOIN dim_cliente c ON f.id_cliente = c.id_cliente
    JOIN dim_tempo t ON f.id_tempo = t.id_tempo
    JOIN dim_produto p ON f.id_produto = p.id_produto
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df['mes_ano'] = df['data_venda'].dt.to_period('M').astype(str)
    return df

df = load_data()

st.title("Cardeal Centro de Distribuição Ltda.")
st.caption("Dashboard Analítico de Vendas das filiais da Cardeal Centro de Distribuição Ltda.")
st.caption("Integrantes: Geovani Machado Cardeal · Nadson Pereira de Almeida Santos · Pedro Yuri de Oliveira Góes · Daniel de Souza Pereira · Ana Beatriz Silva Aragão")

st.sidebar.header("Filtro Global")
anos_disponiveis = sorted(df['ano'].unique().tolist())
ano_selecionado = st.sidebar.multiselect("Ano Fiscal", options=anos_disponiveis, default=anos_disponiveis)

if ano_selecionado:
    df_filtrado = df[df['ano'].isin(ano_selecionado)]
else:
    df_filtrado = df

tab1, tab2, tab3 = st.tabs(["Visao Geral de Vendas", "Analise de Subsidiarias", "Analise de Produtos"])

COLOR_LUCRO = '#2ca02c'
COLOR_PREJUIZO = '#d62728'
color_map_status = {'Lucro': COLOR_LUCRO, 'Prejuízo': COLOR_PREJUIZO}
ALTURA_GRAFICO = 550

with tab1:
    st.header("Visão Geral de Vendas")
    st.caption("Panorama financeiro consolidado com evolução temporal e comparativo regional.")

    df_tab1 = filtros_cascata(df_filtrado, 't1')

    faturamento = df_tab1['valor_total'].sum()
    custo = df_tab1['custo_total'].sum()
    lucro = df_tab1['lucro'].sum()
    pedidos = df_tab1['id_venda'].nunique()
    margem = (lucro / faturamento * 100) if faturamento > 0 else 0
    ticket = faturamento / pedidos if pedidos > 0 else 0

    tamanho_lote = df_tab1['quantidade'].sum() / pedidos if pedidos > 0 else 0

    st.markdown("### Indicadores Principais")
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturamento Bruto", formatar_brl(faturamento))
    k2.metric("Custo Operacional", formatar_brl(custo))
    k3.metric("Lucro Líquido", formatar_brl(lucro))

    st.write("") 
    
    k4, k5, k6, k7 = st.columns(4)
    k4.metric("Margem", f"{margem:.1f}%")
    k5.metric("Lotes Despachados", f"{pedidos:,}".replace(",", "."))
    k6.metric("Tamanho Médio do Lote", f"{tamanho_lote:.0f} un.")
    k7.metric("Ticket Médio do Lote", formatar_brl(ticket))

    st.markdown("---")

    fat_regiao_mensal = df_tab1.groupby(['mes_ano', 'nome_regiao']).agg(
        faturamento=('valor_total', 'sum'),
        custo=('custo_total', 'sum'),
        lucro=('lucro', 'sum')
    ).reset_index()

    cores_regiao = {'Centro-Oeste': '#FF6B35', 'Nordeste': '#1f77b4', 'Sudeste': '#9467bd'}
    regioes_presentes = sorted(fat_regiao_mensal['nome_regiao'].unique().tolist())

    # Gráfico Faturamento e Custo Mensal por Região
    fig_fat_mensal = go.Figure()
    for regiao in regioes_presentes:
        cor = cores_regiao.get(regiao, '#888888')
        dados_r = fat_regiao_mensal[fat_regiao_mensal['nome_regiao'] == regiao].sort_values('mes_ano')
        
        # Linha de Faturamento 
        fig_fat_mensal.add_trace(go.Scatter(
            x=dados_r['mes_ano'], y=dados_r['faturamento'],
            mode='lines+markers', name=f'{regiao} (Fat.)',
            line=dict(color=cor, width=3)
        ))
        
        # Linha de Custo 
        fig_fat_mensal.add_trace(go.Scatter(
            x=dados_r['mes_ano'], y=dados_r['custo'],
            mode='lines+markers', name=f'{regiao} (Custo)',
            line=dict(color=cor, width=2, dash='dash')
        ))

    fig_fat_mensal.update_layout(
        title='Faturamento e Custo Operacional Mensal por Região',
        height=ALTURA_GRAFICO, xaxis_title='Período', yaxis_title='Valor (R$)',
        yaxis_tickprefix='R$ ', yaxis_tickformat=',.0f',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=12)),
        margin=dict(t=80, b=60)
    )
    st.plotly_chart(fig_fat_mensal, use_container_width=True)

    st.markdown("---")

    # Gráfico Lucro Acumulado por Região
    fig_lucro_acum = go.Figure()
    for regiao in regioes_presentes:
        cor = cores_regiao.get(regiao, '#888888')
        dados_r = fat_regiao_mensal[fat_regiao_mensal['nome_regiao'] == regiao].sort_values('mes_ano')
        dados_r = dados_r.copy()
        dados_r['lucro_acumulado'] = dados_r['lucro'].cumsum()
        fig_lucro_acum.add_trace(go.Scatter(
            x=dados_r['mes_ano'], y=dados_r['lucro_acumulado'],
            mode='lines+markers', name=regiao,
            line=dict(color=cor, width=2),
            fill='tozeroy'
        ))
    fig_lucro_acum.update_layout(
        title='Lucro Acumulado por Região',
        height=ALTURA_GRAFICO, xaxis_title='Período', yaxis_title='Lucro Acumulado (R$)',
        yaxis_tickprefix='R$ ', yaxis_tickformat=',.0f',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=12)),
        margin=dict(t=80, b=60)
    )
    
    fig_lucro_acum.add_hline(y=0, line_dash='dash', line_color='white', opacity=0.5)
    st.plotly_chart(fig_lucro_acum, use_container_width=True)
    st.caption("O lucro acumulado mostra a evolução do resultado financeiro ao longo do tempo. Valores abaixo de zero indicam prejuízo acumulado.")

    st.markdown("---")

    dados_regiao = df_tab1.groupby('nome_regiao').agg(
        faturamento=('valor_total', 'sum'),
        custo=('custo_total', 'sum'),
        resultado=('lucro', 'sum')
    ).reset_index().sort_values('faturamento', ascending=False)

    fig_regiao = go.Figure()
    
    # Barra 1: Faturamento
    fig_regiao.add_trace(go.Bar(
        x=dados_regiao['nome_regiao'], 
        y=dados_regiao['faturamento'], 
        name='Faturamento', 
        marker_color='#9467bd', 
        text=dados_regiao['faturamento'].apply(lambda x: f'R$ {x:,.0f}'), 
        textposition='outside'
    ))

    # Barra 2: Custo Operacional 
    fig_regiao.add_trace(go.Bar(
        x=dados_regiao['nome_regiao'], 
        y=dados_regiao['custo'], 
        name='Custo Operacional', 
        marker_color='#ff7f0e',
        text=dados_regiao['custo'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Barra 3: Resultado 
    cores_resultado = [COLOR_LUCRO if val >= 0 else COLOR_PREJUIZO for val in dados_regiao['resultado']]
    fig_regiao.add_trace(go.Bar(
        x=dados_regiao['nome_regiao'], 
        y=dados_regiao['resultado'], 
        name='Resultado', 
        marker_color=cores_resultado, 
        text=dados_regiao['resultado'].apply(lambda x: f'R$ {x:,.0f}'), 
        textposition='outside'
    ))

    fig_regiao.update_layout(title='Faturamento, Custo e Resultado por Região', height=ALTURA_GRAFICO, barmode='group', xaxis_title='Região', yaxis_title='Valor (R$)', yaxis_tickprefix='R$ ', yaxis_tickformat=',.0f', legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=12)), margin=dict(t=80, b=60))
    st.plotly_chart(fig_regiao, use_container_width=True)

with tab2:
    st.header("Análise de Subsidiárias e Lojistas")
    st.caption("Rentabilidade por subsidiária regional, identificando unidades que geram lucro ou prejuízo para a operação.")

    df_tab2 = filtros_cascata(df_filtrado, 't2')

    clientes_unicos = df_tab2['id_cliente'].nunique()
    fat_t2 = df_tab2['valor_total'].sum()
    custo_t2 = df_tab2['custo_total'].sum()
    lucro_t2 = df_tab2['lucro'].sum()
    margem_t2 = (lucro_t2 / fat_t2 * 100) if fat_t2 > 0 else 0

    st.markdown("### Indicadores da Rede")
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturamento Global", formatar_brl(fat_t2))
    k2.metric("Custo Total", formatar_brl(custo_t2))
    k3.metric("Lucro Consolidado", formatar_brl(lucro_t2))

    st.write("")
    
    k4, k5 = st.columns(2)
    k4.metric("Subsidiárias Ativas", clientes_unicos)
    k5.metric("Margem Consolidada", f"{margem_t2:.1f}%")

    st.markdown("---")

    lucro_cliente = df_tab2.groupby(['nome', 'nome_estado'])['lucro'].sum().reset_index().sort_values('lucro')
    lucro_cliente['Status'] = lucro_cliente['lucro'].apply(lambda x: 'Lucro' if x >= 0 else 'Prejuízo')

    fig_cli = px.bar(lucro_cliente, x='lucro', y='nome', orientation='h',
                     title='Resultado por Subsidiária (Lucro/Prejuízo)', color='Status', color_discrete_map=color_map_status,
                     hover_data={'nome_estado': True})
    fig_cli.update_traces(texttemplate='R$ %{x:,.0f}', textposition='auto')
    fig_cli.update_layout(height=ALTURA_GRAFICO, yaxis={'categoryorder': 'total ascending'}, xaxis_title='Resultado (R$)', yaxis_title='', xaxis_tickprefix='R$ ', xaxis_tickformat=',.0f', margin=dict(t=60, b=40, l=150))
    st.plotly_chart(fig_cli, use_container_width=True)

    st.markdown("---")

    lucro_estado = df_tab2.groupby('nome_estado')['lucro'].sum().reset_index().sort_values('lucro')
    lucro_estado['Status'] = lucro_estado['lucro'].apply(lambda x: 'Lucro' if x >= 0 else 'Prejuízo')

    fig_est = px.bar(lucro_estado, x='lucro', y='nome_estado', orientation='h',
                     title='Resultado por Estado (Lucro/Prejuízo)', color='Status', color_discrete_map=color_map_status)
    fig_est.update_traces(texttemplate='R$ %{x:,.0f}', textposition='auto')
    fig_est.update_layout(height=ALTURA_GRAFICO, yaxis={'categoryorder': 'total ascending'}, xaxis_title='Resultado (R$)', yaxis_title='', xaxis_tickprefix='R$ ', xaxis_tickformat=',.0f', margin=dict(t=60, b=40, l=150))
    st.plotly_chart(fig_est, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribuição Geográfica")

    col_pie1, col_pie2 = st.columns(2)

    with col_pie1:
        cli_regiao = df_tab2.groupby('nome_regiao')['id_cliente'].nunique().reset_index()
        cli_regiao = cli_regiao.rename(columns={'id_cliente': 'Qtd. Lojas/Clientes'})
        fig_p1 = px.pie(cli_regiao, values='Qtd. Lojas/Clientes', names='nome_regiao',
                        title='Subsidiárias por Região', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_p1.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Qtd. Lojas/Clientes: %{value}<extra></extra>')
        fig_p1.update_layout(height=450, margin=dict(t=60, b=40))
        st.plotly_chart(fig_p1, use_container_width=True)

    with col_pie2:
        fat_regiao = df_tab2.groupby('nome_regiao').agg({'valor_total': 'sum', 'lucro': 'sum'}).reset_index()
        fat_regiao = fat_regiao.rename(columns={'lucro': 'Resultado'})
        fig_p2 = px.pie(fat_regiao, values='valor_total', names='nome_regiao',
                        title='Faturamento por Região', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_p2.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<br>Resultado: R$ %{customdata[0]:,.2f}<extra></extra>',
            customdata=fat_regiao[['Resultado']]
        )
        fig_p2.update_layout(height=450, margin=dict(t=60, b=40))
        st.plotly_chart(fig_p2, use_container_width=True)

    st.markdown("---")
    st.subheader("Dados Detalhados")
    with st.expander("Exibir tabela detalhada de vendas por subsidiária", expanded=False):
        tabela_detalhe = df_tab2.groupby(['nome', 'uf', 'nome_estado', 'nome_regiao']).agg(
            lotes=('id_venda', 'nunique'),
            unidades=('quantidade', 'sum'),
            faturamento=('valor_total', 'sum'),
            custo=('custo_total', 'sum'),
            resultado=('lucro', 'sum')
        ).reset_index()
        tabela_detalhe['margem'] = (tabela_detalhe['resultado'] / tabela_detalhe['faturamento'] * 100).round(1)
        tabela_detalhe = tabela_detalhe.sort_values('resultado', ascending=False)
        tabela_detalhe.columns = ['Subsidiária', 'UF', 'Estado', 'Região', 'Lotes', 'Unidades', 'Faturamento (R$)', 'Custo (R$)', 'Resultado (R$)', 'Margem (%)']
        st.dataframe(tabela_detalhe, use_container_width=True, hide_index=True)

with tab3:
    st.header("Análise de Produtos")
    st.caption("Desempenho do mix de produtos em volume de vendas e rentabilidade, segmentado por categoria.")

    df_tab3_base = filtros_cascata(df_filtrado, 't3')

    categorias = sorted(df_tab3_base['categoria'].unique().tolist()) if not df_tab3_base.empty else []
    cat_sel = st.multiselect("Categoria", options=categorias, default=categorias, key='cat_t3')

    df_tab3 = df_tab3_base[df_tab3_base['categoria'].isin(cat_sel)] if cat_sel else df_tab3_base.head(0)

    total_itens = df_tab3['quantidade'].sum()
    fat_t3 = df_tab3['valor_total'].sum()
    lucro_t3 = df_tab3['lucro'].sum()
    margem_t3 = (lucro_t3 / fat_t3 * 100) if fat_t3 > 0 else 0

    if not df_tab3.empty:
        vendas_agrup = df_tab3.groupby('nome_produto')['id_venda'].nunique()
        qtd_top = vendas_agrup.max()
        tops = vendas_agrup[vendas_agrup == qtd_top].index.tolist()
        produto_top = " e ".join(tops)
    else:
        produto_top = "N/A"
        qtd_top = 0

    st.markdown("### Indicadores de Escoamento")
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturamento por Categoria", formatar_brl(fat_t3))
    k2.metric("Lucro por Categoria", formatar_brl(lucro_t3))
    k3.metric("Margem Consolidada", f"{margem_t3:.1f}%")

    st.write("")

    k4, k5 = st.columns(2)
    k4.metric("Unidades Despachadas (Volume)", f"{total_itens:,}".replace(",", "."))
    k5.metric("Produto Líder de Lotes", f"{produto_top}")

    st.markdown("---")

    vendas_prod = df_tab3.groupby('nome_produto').agg(
        unidades=('quantidade', 'sum'),
        lotes=('id_venda', 'nunique')
    ).reset_index()
    vendas_prod['unidades_por_lote'] = vendas_prod['unidades'] / vendas_prod['lotes']
    vendas_prod = vendas_prod.sort_values('unidades', ascending=False)

    fig_qtd = go.Figure()
    
    # Barra 1: Unidades
    fig_qtd.add_trace(go.Bar(
        x=vendas_prod['nome_produto'], 
        y=vendas_prod['unidades'], 
        name='Unidades', 
        marker_color='#1f77b4', 
        text=vendas_prod['unidades'].apply(lambda x: f'{x:,.0f} un.'), 
        textposition='outside'
    ))

    # Barra 2: Lotes
    fig_qtd.add_trace(go.Bar(
        x=vendas_prod['nome_produto'], 
        y=vendas_prod['lotes'], 
        name='Lotes', 
        marker_color='#ff7f0e',
        text=vendas_prod['lotes'].apply(lambda x: f'{x:,.0f} lotes'),
        textposition='outside'
    ))

    fig_qtd.update_layout(
        title='Volume de Escoamento: Lotes vs Unidades', 
        height=ALTURA_GRAFICO, 
        barmode='group', 
        xaxis_title='Produto', 
        yaxis_title='Quantidade', 
        legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=12)), 
        margin=dict(t=80, b=60)
    )
    st.plotly_chart(fig_qtd, use_container_width=True)

    dados_prod = df_tab3.groupby('nome_produto').agg(
        faturamento=('valor_total', 'sum'),
        custo=('custo_total', 'sum'),
        resultado=('lucro', 'sum')
    ).reset_index().sort_values('faturamento', ascending=False)

    fig_prod = go.Figure()
    
    # Barra 1: Faturamento
    fig_prod.add_trace(go.Bar(
        x=dados_prod['nome_produto'], 
        y=dados_prod['faturamento'], 
        name='Faturamento', 
        marker_color='#9467bd', 
        text=dados_prod['faturamento'].apply(lambda x: f'R$ {x:,.0f}'), 
        textposition='outside'
    ))

    # Barra 2: Custo Operacional 
    fig_prod.add_trace(go.Bar(
        x=dados_prod['nome_produto'], 
        y=dados_prod['custo'], 
        name='Custo Operacional', 
        marker_color='#ff7f0e',
        text=dados_prod['custo'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Barra 3: Resultado 
    cores_resultado_prod = [COLOR_LUCRO if val >= 0 else COLOR_PREJUIZO for val in dados_prod['resultado']]
    fig_prod.add_trace(go.Bar(
        x=dados_prod['nome_produto'], 
        y=dados_prod['resultado'], 
        name='Resultado', 
        marker_color=cores_resultado_prod, 
        text=dados_prod['resultado'].apply(lambda x: f'R$ {x:,.0f}'), 
        textposition='outside'
    ))

    fig_prod.update_layout(title='Faturamento, Custo e Resultado por Produto', height=ALTURA_GRAFICO, barmode='group', xaxis_title='Produto', yaxis_title='Valor (R$)', yaxis_tickprefix='R$ ', yaxis_tickformat=',.0f', legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=12)), margin=dict(t=80, b=60))
    st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("---")

    fat_cat = df_tab3.groupby('categoria')['valor_total'].sum().reset_index()
    fig_cat = px.pie(fat_cat, values='valor_total', names='categoria',
                     title='Participação por Categoria', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
    fig_cat.update_traces(textposition='inside', textinfo='percent+label')
    fig_cat.update_layout(height=ALTURA_GRAFICO, margin=dict(t=60, b=40))
    st.plotly_chart(fig_cat, use_container_width=True)
