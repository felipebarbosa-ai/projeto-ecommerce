from pathlib import Path
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "dados" / "simulacao_ecommerce_brasil.csv"
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "ecommerce.db"

ENGINE = create_engine(f"sqlite:///{DB_PATH}")


def ler_csv():
    """Lê e prepara a base CSV."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Base não encontrada em: {CSV_PATH}. "
            "Verifique se o arquivo está em dados/simulacao_ecommerce_brasil.csv."
        )

    df = pd.read_csv(CSV_PATH)

    # Padronização básica de nomes
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Conversões numéricas
    numeric_cols = [
        "ano", "mes", "quantidade", "preco_unitario", "faturamento",
        "custo", "lucro", "prazo_entrega", "avaliacao_cliente"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # Remove linhas totalmente vazias
    df = df.dropna(how="all").copy()

    # Remove linhas sem informações essenciais
    required = [c for c in ["ano", "mes", "regiao", "uf", "categoria",
                            "produto", "quantidade", "faturamento"] if c in df.columns]
    if required:
        df = df.dropna(subset=required)

    # Recalcula métricas derivadas se necessário
    if "faturamento" not in df.columns and {"quantidade", "preco_unitario"}.issubset(df.columns):
        df["faturamento"] = df["quantidade"] * df["preco_unitario"]

    if "lucro" not in df.columns and {"faturamento", "custo"}.issubset(df.columns):
        df["lucro"] = df["faturamento"] - df["custo"]

    return df.reset_index(drop=True)


def inicializar_banco():
    """
    Cria/recria o banco SQLite a partir do CSV.

    A dimensão de produto usa produto + categoria como chave lógica,
    porque o mesmo nome de produto pode aparecer em categorias diferentes.
    O banco é recriado quando necessário para evitar conflitos de versões
    antigas do schema.
    """
    df = ler_csv()

    # Recria o banco de forma idempotente, evitando dados duplicados entre
    # reinicializações do Streamlit.
    with ENGINE.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fato_vendas"))
        conn.execute(text("DROP TABLE IF EXISTS dim_produto"))
        conn.execute(text("DROP TABLE IF EXISTS dim_local"))
        conn.execute(text("DROP TABLE IF EXISTS dim_tempo"))

    # Dimensão tempo
    tempo_cols = [c for c in ["ano", "mes", "data"] if c in df.columns]
    tempo = df[tempo_cols].drop_duplicates().copy()

    # Dimensão local
    local_cols = [c for c in ["regiao", "uf", "cidade"] if c in df.columns]
    local = df[local_cols].drop_duplicates().copy()

    # Dimensão produto: produto + categoria são a combinação lógica
    produto_cols = [c for c in ["produto", "categoria"] if c in df.columns]
    produtos = df[produto_cols].drop_duplicates().copy()

    # Fato: mantém as colunas originais
    fato = df.copy()

    # Persistência
    tempo.to_sql("dim_tempo", ENGINE, if_exists="replace", index=False)
    local.to_sql("dim_local", ENGINE, if_exists="replace", index=False)
    produtos.to_sql("dim_produto", ENGINE, if_exists="replace", index=False)
    fato.to_sql("fato_vendas", ENGINE, if_exists="replace", index=False)


def carregar_fato():
    """Inicializa o banco e retorna a tabela fato completa."""
    inicializar_banco()
    return pd.read_sql("SELECT * FROM fato_vendas", ENGINE)


def testar_banco():
    """Retorna contagens básicas para diagnóstico."""
    inicializar_banco()
    with ENGINE.connect() as conn:
        resultado = conn.execute(
            text("SELECT COUNT(*) FROM fato_vendas")
        ).scalar_one()
    return resultado


if __name__ == "__main__":
    n = testar_banco()
    print(f"Banco inicializado com {n} registros.")
