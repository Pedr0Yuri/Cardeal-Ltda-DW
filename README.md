Data Warehouse - Cardeal Ltda

Projeto prático desenvolvido para a disciplina de Sistemas de Apoio à Decisão.

Integrantes
- Geovani Machado Cardeal
- Nadson Pereira de Almeida Santos
- Pedro Yuri de Oliveira Góes
- Daniel de Souza Pereira
- Ana Beatriz Silva Aragão

## Como Executar

1. Instalar as dependências:
```bash
pip install -r requirements.txt
```

2. Executar o pipeline ETL completo e iniciar o Dashboard:
```bash
python gerar_dados.py ; python etl_bronze.py ; python etl_silver.py ; python etl_gold.py ; python -m streamlit run app_dashboard.py
``` 
3. (Opcional) Exportar camada Gold para CSV:
```bash
python exportar_gold.py
``` 
