[README.md](https://github.com/user-attachments/files/28038556/README.md)
# Análise de Risco de Crédito com SRL, Prolog e Python

Este repositório implementa o exemplo avaliativo de **Análise de Risco de Crédito Híbrido em Redes Sociais**, integrando:

- uma base relacional em **Prolog**;
- extração de atributos lógicos com **pyswip**;
- enriquecimento de dados com **Pandas**;
- treinamento de classificador com **Regressão Logística** no **Scikit-Learn**;
- geração de uma regra probabilística em estilo **ProbLog**.

A ideia central é transformar relações sociais/financeiras em atributos numéricos, permitindo que o modelo estatístico aprenda pesos para variáveis individuais e relacionais.

---

## Estrutura do projeto

```text
analise-risco-srl/
├── data/
│   └── dados_financeiros.csv
├── outputs/
├── prolog/
│   └── rede_social.pl
├── src/
│   └── main.py
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Pré-requisitos

### Opção 1: executar localmente

Instale:

- Python 3.10 ou superior;
- SWI-Prolog;
- pip.

No Ubuntu/Debian:

```bash
sudo apt update
sudo apt install swi-prolog python3 python3-pip python3-venv
```

No Windows, instale o SWI-Prolog pelo site oficial e marque a opção para adicionar o programa ao `PATH`.

---

## Como clonar e executar

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd analise-risco-srl
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python src/main.py
```

---

## Execução com Docker

Caso prefira rodar sem instalar o SWI-Prolog manualmente:

```bash
docker build -t analise-risco-srl .
docker run --rm analise-risco-srl
```

---

## O que o programa faz

1. Carrega a base de fatos `rede_social.pl`.
2. Consulta o Prolog para calcular o grau de proximidade entre clientes e pessoas inadimplentes.
3. Cria as features relacionais:
   - `grau_risco_rede`;
   - `inadimplentes_ate_grau_3`.
4. Junta essas features com os dados financeiros tradicionais:
   - `renda_mensal`;
   - `score_classico`.
5. Treina uma Regressão Logística.
6. Exibe coeficientes aprendidos e uma regra probabilística explicável.
7. Salva os arquivos gerados em `outputs/`.

---

## Exemplo de saída esperada

```text
=== Dataset enriquecido com features relacionais ===
cliente_id  renda_mensal  score_classico  inadimplente_historico  grau_risco_rede  inadimplentes_ate_grau_3
     joao          5200             750                       0                2                        2
      ana          3100             610                       0                1                        2
   carlos          1800             420                       1                1                        1
```

Exemplo de regra probabilística:

```text
0.34 :: risco(joao) :- grau_risco_rede(joao, 2), inadimplentes_ate_grau_3(joao, 2).
```

O valor pode variar conforme a base de dados e o treinamento.

---

## Relação com SRL

O projeto segue o paradigma de **Statistical Relational Learning**, pois combina representação lógica de relações com aprendizado estatístico. O Prolog modela a estrutura relacional do problema, enquanto a Regressão Logística calibra numericamente a influência das variáveis extraídas dessa estrutura.

---
