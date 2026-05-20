from __future__ import annotations

from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from pyswip import Prolog
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
PROLOG_FILE = ROOT / "prolog" / "rede_social.pl"
DATA_FILE = ROOT / "data" / "dados_financeiros.csv"
OUTPUT_DIR = ROOT / "outputs"


def atom(nome: str) -> str:
    """Converte o identificador do cliente em átomo Prolog seguro para este dataset."""
    return nome.strip().lower().replace(" ", "_")


class ExtratorRelacional:
    def __init__(self, arquivo_prolog: Path):
        self.prolog = Prolog()
        self.prolog.consult(str(arquivo_prolog))

    def menor_grau_para_inadimplente(self, cliente: str) -> int:
        """
        Retorna o menor grau de conexão entre o cliente e qualquer inadimplente conhecido.
        999 representa ausência de conexão encontrada.
        """
        consulta = f"risco_com_inadimplente({atom(cliente)}, PessoaRisco, Grau)"
        resultados = list(self.prolog.query(consulta))
        if not resultados:
            return 999
        return min(int(r["Grau"]) for r in resultados)

    def quantidade_inadimplentes_proximos(self, cliente: str, limite_grau: int = 3) -> int:
        """Conta inadimplentes conectados até determinado grau de distância."""
        consulta = f"risco_com_inadimplente({atom(cliente)}, PessoaRisco, Grau)"
        resultados = list(self.prolog.query(consulta))
        pessoas = {
            str(r["PessoaRisco"])
            for r in resultados
            if int(r["Grau"]) <= limite_grau
        }
        return len(pessoas)


def carregar_e_enriquecer_dados() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    extrator = ExtratorRelacional(PROLOG_FILE)

    df["grau_risco_rede"] = df["cliente_id"].apply(extrator.menor_grau_para_inadimplente)
    df["inadimplentes_ate_grau_3"] = df["cliente_id"].apply(
        lambda nome: extrator.quantidade_inadimplentes_proximos(nome, limite_grau=3)
    )
    return df


def treinar_modelo(df: pd.DataFrame) -> Pipeline:
    features = [
        "renda_mensal",
        "score_classico",
        "grau_risco_rede",
        "inadimplentes_ate_grau_3",
    ]
    X = df[features]
    y = df["inadimplente_historico"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    modelo = Pipeline(
        steps=[
            ("escala", StandardScaler()),
            ("regressao", LogisticRegression(random_state=42)),
        ]
    )
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    print("\n=== Avaliação do modelo ===")
    print(f"Acurácia: {accuracy_score(y_test, y_pred):.2f}")
    print(classification_report(y_test, y_pred, zero_division=0))

    coeficientes = modelo.named_steps["regressao"].coef_[0]
    print("\n=== Coeficientes aprendidos ===")
    for nome_feature, peso in zip(features, coeficientes):
        print(f"{nome_feature}: {peso:.4f}")

    return modelo


def gerar_regra_probabilistica(
    modelo: Pipeline,
    cliente_id: str,
    renda_mensal: float,
    score_classico: float,
    grau_risco_rede: int,
    inadimplentes_ate_grau_3: int,
) -> str:
    entrada = pd.DataFrame(
        [
            {
                "renda_mensal": renda_mensal,
                "score_classico": score_classico,
                "grau_risco_rede": grau_risco_rede,
                "inadimplentes_ate_grau_3": inadimplentes_ate_grau_3,
            }
        ]
    )
    probabilidade = modelo.predict_proba(entrada)[0][1]
    return (
        f"{probabilidade:.2f} :: risco({atom(cliente_id)}) :- "
        f"grau_risco_rede({atom(cliente_id)}, {grau_risco_rede}), "
        f"inadimplentes_ate_grau_3({atom(cliente_id)}, {inadimplentes_ate_grau_3})."
    )


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=== Análise de Risco de Crédito com SRL + Prolog + Python ===")
    df = carregar_e_enriquecer_dados()
    print("\n=== Dataset enriquecido com features relacionais ===")
    print(df.to_string(index=False))

    modelo = treinar_modelo(df)

    caminho_dataset = OUTPUT_DIR / "dados_enriquecidos.csv"
    caminho_modelo = OUTPUT_DIR / "modelo_risco.joblib"
    df.to_csv(caminho_dataset, index=False)
    joblib.dump(modelo, caminho_modelo)

    print("\n=== Regra probabilística estilo ProbLog ===")
    regra = gerar_regra_probabilistica(
        modelo=modelo,
        cliente_id="joao",
        renda_mensal=5200,
        score_classico=750,
        grau_risco_rede=int(df.loc[df["cliente_id"] == "joao", "grau_risco_rede"].iloc[0]),
        inadimplentes_ate_grau_3=int(
            df.loc[df["cliente_id"] == "joao", "inadimplentes_ate_grau_3"].iloc[0]
        ),
    )
    print(regra)

    print(f"\nDataset salvo em: {caminho_dataset}")
    print(f"Modelo salvo em: {caminho_modelo}")


if __name__ == "__main__":
    main()
