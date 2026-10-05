# 🛒 Vendas em E-commerce no Brasil — Projeto G1

**Aluno:** Felipe Barbosa da Silva
**Disciplina:** Linguagens de Programação
**Professor:** Alexandre Neves Louzada

Projeto acadêmico de análise de dados e desenvolvimento de dashboard interativo sobre vendas de e-commerce no Brasil.

## Objetivo

Analisar o comportamento das vendas entre 2015 e 2024, identificando:

* evolução do faturamento e lucro;
* categorias e produtos de destaque;
* estados e regiões com maior faturamento;
* sazonalidade;
* canais de venda;
* logística;
* relação entre avaliação dos clientes e vendas;
* oportunidades comerciais.

## Tecnologias

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Streamlit
* SQLAlchemy
* SQLite
* Jupyter Notebook
* GitHub
* GitHub Pages
* Streamlit Community Cloud

## Estrutura

```text
projeto-ecommerce/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── index.html
├── dados/
│   └── simulacao_ecommerce_brasil.csv
├── database/
│   └── ecommerce.db   (gerado automaticamente em execução)
├── notebooks/
│   ├── analise_ecommerce.ipynb
│   └── analise_ecommerce_g1.ipynb
└── imagens/
```

## Banco de dados

O arquivo `database.py` cria e atualiza um banco SQLite em `database/ecommerce.db`.

A dimensão de produto considera a combinação `produto + categoria`, evitando conflitos quando o mesmo nome de produto aparece em categorias diferentes.

## Execução local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicação

1. Envie todo o conteúdo para um repositório público no GitHub.
2. Ative GitHub Pages usando a branch `main` e a pasta `/ (root)`.
3. No Streamlit Community Cloud, selecione o repositório, branch `main` e arquivo `app.py`.

## Observação sobre ticket médio

Como a base fornecida não possui um identificador de pedido (`id_pedido`), o projeto documenta o indicador como valor médio de venda por unidade (`faturamento / quantidade`). Isso evita apresentar como ticket médio de pedido uma métrica que a base não permite calcular diretamente.

---

### 📚 Informações Acadêmicas

**Aluno:** Felipe Barbosa da Silva
**Disciplina:** Linguagens de Programação
**Professor:** Alexandre Neves Louzada
