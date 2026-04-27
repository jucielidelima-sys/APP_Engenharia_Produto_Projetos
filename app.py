
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
from datetime import date, datetime, timedelta
from io import BytesIO


# =========================
# LOGIN
# =========================
def autenticar(usuario, senha):
    users = {
        "admin": {"senha": "admin123", "perfil": "admin"},
        "user": {"senha": "user123", "perfil": "visual"}
    }
    if usuario in users and users[usuario]["senha"] == senha:
        return users[usuario]["perfil"]
    return None

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.perfil = None

if not st.session_state.logado:
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        perfil = autenticar(usuario, senha)
        if perfil:
            st.session_state.logado = True
            st.session_state.perfil = perfil
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

st.set_page_config(
    page_title="Painel de Projetos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_DADOS = "projetos.xlsx"

COLUNAS = [
    "Projeto",
    "Necessidade do Projeto",
    "Solicitante do Projeto",
    "Departamento",
    "Responsável",
    "Fornecedor",
    "Riscos",
    "Probabilidade do Risco",
    "Impacto do Risco",
    "Nível do Risco",
    "Etapa",
    "Tarefa",
    "Overall Task Status",
    "Fase In",
    "Fase Out",
    "Data Início",
    "Data Fim",
    "Status",
    "Prioridade",
    "Budget",
    "Payback",
    "Percentual Concluído",
    "Observações"
]

STATUS_OPCOES = ["Pendente", "Em Andamento", "No Prazo", "Atrasada", "Concluída", "Pausada"]
PRIORIDADE_OPCOES = ["Baixa", "Média", "Alta", "Crítica"]
OVERALL_STATUS_OPCOES = ["Dentro do Planejado", "Atenção", "Crítico", "Bloqueado", "Finalizado"]
FASE_OPCOES = ["Não iniciado", "Em execução", "Concluído", "Não aplicável"]
PROBABILIDADE_RISCO_OPCOES = ["Baixa", "Média", "Alta"]
IMPACTO_RISCO_OPCOES = ["Baixo", "Médio", "Alto"]

CORES_STATUS = {
    "Concluída": "#4CAF50",
    "Em Andamento": "#4A90E2",
    "No Prazo": "#4A90E2",
    "Atrasada": "#F44336",
    "Pendente": "#AAB0B8",
    "Pausada": "#FFC107"
}

def dados_exemplo():
    hoje = date.today()
    return pd.DataFrame([
        ["Construção de Escola", "Ampliação da infraestrutura para atender aumento de demanda.", "Diretoria Operacional", "Operações", "Gerente Projetos A", "Fornecedor Alfa", "Risco de prazo/custo", "Média", "Médio", "Médio", "1 Design", "Definir requisitos", "Dentro do Planejado", "Concluído", "Em execução", hoje- timedelta(days=30), hoje+timedelta(days=10), "Concluída", "Alta", 250000, 24, 75, ""],
        ["Construção de Escola", "Ampliação da infraestrutura para atender aumento de demanda.", "Diretoria Operacional", "Operações", "Gerente Projetos A", "Fornecedor Alfa", "1 Design", "Pesquisa de mercado", "Atenção", "Em execução", "Não iniciado", hoje- timedelta(days=25), hoje+timedelta(days=15), "Em Andamento", "Média", 80000, 18, 60, ""],
        ["Criar Planilha para Projetos", "Digitalizar o controle de cronogramas e indicadores dos projetos.", "Gestão Industrial", "TI", "Gerente Projetos C", "Fornecedor Beta", "Risco de prazo/custo", "Média", "Médio", "Médio", "2 Desenvolvimento", "Protótipo", "Finalizado", "Concluído", "Concluído", hoje- timedelta(days=18), hoje+timedelta(days=25), "Concluída", "Alta", 35000, 8, 100, ""],
        ["Criar Planilha para Projetos", "Digitalizar o controle de cronogramas e indicadores dos projetos.", "Gestão Industrial", "TI", "Gerente Projetos C", "Fornecedor Beta", "2 Desenvolvimento", "Validação", "Dentro do Planejado", "Em execução", "Não iniciado", hoje- timedelta(days=10), hoje+timedelta(days=35), "No Prazo", "Média", 15000, 12, 45, ""],
        ["Evento Lançamento Empreendimento", "Organizar ações de divulgação e acompanhamento do lançamento.", "Marketing", "Comunicação", "Gerente Projetos B", "Fornecedor Delta", "Risco de prazo/custo", "Média", "Médio", "Médio", "1 Design", "Briefing", "Finalizado", "Concluído", "Concluído", hoje- timedelta(days=20), hoje+timedelta(days=5), "Concluída", "Alta", 70000, 10, 100, ""],
        ["Evento Lançamento Empreendimento", "Organizar ações de divulgação e acompanhamento do lançamento.", "Marketing", "Comunicação", "Gerente Projetos B", "Fornecedor Delta", "3 Testes", "Checklist final", "Dentro do Planejado", "Em execução", "Não iniciado", hoje+timedelta(days=2), hoje+timedelta(days=20), "No Prazo", "Alta", 25000, 14, 30, ""],
        ["Renovação de Licença Ambiental", "Garantir conformidade legal e continuidade operacional.", "Jurídico / Meio Ambiente", "Meio Ambiente", "Gerente Projetos D", "Fornecedor Verde", "Risco de prazo/custo", "Média", "Médio", "Médio", "2 Desenvolvimento", "Documentação", "Crítico", "Em execução", "Não iniciado", hoje- timedelta(days=40), hoje- timedelta(days=3), "Atrasada", "Crítica", 120000, 36, 33, ""],
        ["Sistema de Análise de Dados", "Melhorar análise de dados e tomada de decisão.", "Controladoria", "TI", "Gerente Projetos C", "Fornecedor Beta", "3 Testes", "Testes internos", "Dentro do Planejado", "Em execução", "Não iniciado", hoje- timedelta(days=7), hoje+timedelta(days=28), "No Prazo", "Média", 90000, 20, 70, ""],
        ["Sistema de Indicadores", "Padronizar indicadores e acompanhamento gerencial.", "Gerência Geral", "TI", "Gerente Projetos C", "Fornecedor Gama", "Risco de prazo/custo", "Média", "Médio", "Médio", "2 Desenvolvimento", "Dashboard", "Atenção", "Não iniciado", "Não iniciado", hoje- timedelta(days=15), hoje+timedelta(days=12), "Pendente", "Média", 45000, 16, 50, ""],
        ["Viaduto de Acesso Rodovia", "Melhorar fluxo logístico e segurança de acesso.", "Logística", "Operações", "Gerente Projetos A", "Fornecedor Alfa", "3 Testes", "Entrega final", "Finalizado", "Concluído", "Concluído", hoje+timedelta(days=15), hoje+timedelta(days=42), "Concluída", "Alta", 480000, 48, 100, ""],
    ], columns=COLUNAS)


def calcular_nivel_risco(probabilidade, impacto):
    mapa = {
        "Baixa": 1,
        "Média": 2,
        "Alta": 3,
        "Baixo": 1,
        "Médio": 2,
        "Alto": 3
    }
    p = mapa.get(str(probabilidade), 0)
    i = mapa.get(str(impacto), 0)
    score = p * i
    if score >= 6:
        return "Crítico"
    if score >= 3:
        return "Médio"
    if score >= 1:
        return "Baixo"
    return "Não informado"

def atualizar_nivel_risco(df):
    df = df.copy()
    if "Probabilidade do Risco" in df.columns and "Impacto do Risco" in df.columns:
        df["Nível do Risco"] = df.apply(
            lambda row: calcular_nivel_risco(row.get("Probabilidade do Risco", ""), row.get("Impacto do Risco", "")),
            axis=1
        )
    return df

def carregar_dados():
    try:
        df = pd.read_excel(ARQUIVO_DADOS)
        for coluna in COLUNAS:
            if coluna not in df.columns:
                df[coluna] = ""
        return tratar_datas(df[COLUNAS])
    except Exception:
        df = dados_exemplo()
        salvar_dados(df)
        return df

def tratar_datas(df):
    df = df.copy()
    df["Data Início"] = pd.to_datetime(df["Data Início"], errors="coerce")
    df["Data Fim"] = pd.to_datetime(df["Data Fim"], errors="coerce")
    df["Percentual Concluído"] = pd.to_numeric(df["Percentual Concluído"], errors="coerce").fillna(0)
    df["Budget"] = pd.to_numeric(df["Budget"], errors="coerce").fillna(0)
    df["Payback"] = pd.to_numeric(df["Payback"], errors="coerce").fillna(0)
    return df

def salvar_dados(df):
    df.to_excel(ARQUIVO_DADOS, index=False)

def atualizar_status_automatico(df):
    df = df.copy()
    hoje = pd.Timestamp(date.today())
    for idx, row in df.iterrows():
        if row["Percentual Concluído"] >= 100:
            df.at[idx, "Status"] = "Concluída"
        elif pd.notna(row["Data Fim"]) and row["Data Fim"] < hoje and row["Status"] != "Concluída":
            df.at[idx, "Status"] = "Atrasada"
    return df

def excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Projetos")
        ws = writer.sheets["Projetos"]
        for col in ws.columns:
            largura = max(len(str(cell.value)) if cell.value else 0 for cell in col) + 3
            ws.column_dimensions[col[0].column_letter].width = largura
    return output.getvalue()

def resumo_projetos(df):
    if df.empty:
        return pd.DataFrame()
    agrupado = df.groupby(["Projeto", "Necessidade do Projeto", "Solicitante do Projeto", "Departamento", "Responsável"], as_index=False).agg(
        Fornecedor=("Fornecedor", lambda x: ", ".join(sorted(set([str(v) for v in x if str(v) != "nan" and str(v) != ""]))[:3])),
        Overall_Status=("Overall Task Status", lambda x: x.mode().iloc[0] if not x.mode().empty else ""),
        Budget=("Budget", "sum"),
        Payback_Medio=("Payback", "mean"),
        Performance=("Percentual Concluído", "mean"),
        No_Prazo=("Status", lambda x: (x == "No Prazo").sum() + (x == "Em Andamento").sum()),
        Atrasadas=("Status", lambda x: (x == "Atrasada").sum()),
        Concluídas=("Status", lambda x: (x == "Concluída").sum()),
        Ações_Total=("Tarefa", "count")
    )
    agrupado["Performance"] = agrupado["Performance"].round(0).astype(int)
    agrupado["Payback_Medio"] = agrupado["Payback_Medio"].round(1)
    return agrupado

def grafico_velocimetro(valor):
    valor = max(0, min(float(valor), 150))

    def ponto(valor_ref, raio=1.0):
        # 0 fica à esquerda, 150 fica à direita
        angulo = math.pi - (valor_ref / 150) * math.pi
        return raio * math.cos(angulo), raio * math.sin(angulo)

    fig = go.Figure()

    faixas = [
        (0, 50, "#F44336", "Baixo"),
        (50, 90, "#FFC107", "Atenção"),
        (90, 150, "#4CAF50", "Bom")
    ]

    # Desenha as faixas do manômetro
    for inicio, fim, cor, nome in faixas:
        valores = [inicio + (fim - inicio) * i / 60 for i in range(61)]
        x_externo, y_externo = zip(*[ponto(v, 1.00) for v in valores])
        x_interno, y_interno = zip(*[ponto(v, 0.68) for v in reversed(valores)])

        fig.add_trace(go.Scatter(
            x=list(x_externo) + list(x_interno),
            y=list(y_externo) + list(y_interno),
            fill="toself",
            mode="lines",
            line=dict(color=cor, width=1),
            fillcolor=cor,
            name=nome,
            hoverinfo="skip",
            showlegend=False
        ))

    # Ponteiro
    x_ponteiro, y_ponteiro = ponto(valor, 0.82)
    fig.add_trace(go.Scatter(
        x=[0, x_ponteiro],
        y=[0, y_ponteiro],
        mode="lines",
        line=dict(color="#263238", width=7),
        hoverinfo="skip",
        showlegend=False
    ))

    # Centro do ponteiro
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode="markers",
        marker=dict(size=22, color="#263238"),
        hoverinfo="skip",
        showlegend=False
    ))

    # Marcações principais
    for tick in [0, 50, 90, 150]:
        x1, y1 = ponto(tick, 1.05)
        x2, y2 = ponto(tick, 1.16)
        xt, yt = ponto(tick, 1.28)

        fig.add_trace(go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="lines",
            line=dict(color="#263238", width=2),
            hoverinfo="skip",
            showlegend=False
        ))

        fig.add_annotation(
            x=xt,
            y=yt,
            text=f"{tick}%",
            showarrow=False,
            font=dict(size=12, color="#263238")
        )

    # Valor central
    fig.add_annotation(
        x=0,
        y=-0.25,
        text=f"<b>{valor:.2f}%</b>",
        showarrow=False,
        font=dict(size=26, color="#1B5E20")
    )

    fig.add_annotation(
        x=0,
        y=1.32,
        text="<b>Performance Média</b>",
        showarrow=False,
        font=dict(size=16, color="#263238")
    )

    fig.update_xaxes(visible=False, range=[-1.35, 1.35])
    fig.update_yaxes(visible=False, range=[-0.35, 1.42], scaleanchor="x", scaleratio=1)

    fig.update_layout(
        height=280,
        margin=dict(l=5, r=5, t=10, b=5),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


def grafico_rosca_status(df):
    contagem = df["Status"].value_counts().reset_index()
    contagem.columns = ["Status", "Qtd"]
    fig = px.pie(
        contagem,
        names="Status",
        values="Qtd",
        hole=0.55,
        color="Status",
        color_discrete_map=CORES_STATUS
    )
    fig.update_layout(title="Ações por Status", height=320, margin=dict(l=10, r=10, t=45, b=10))
    return fig

def grafico_rosca_departamento(df):
    contagem = df["Departamento"].value_counts().reset_index()
    contagem.columns = ["Departamento", "Qtd"]
    fig = px.pie(contagem, names="Departamento", values="Qtd", hole=0.55)
    fig.update_layout(title="Ações por Departamento", height=320, margin=dict(l=10, r=10, t=45, b=10))
    return fig

def grafico_overall_status(df):
    contagem = df["Overall Task Status"].fillna("Não informado").replace("", "Não informado").value_counts().reset_index()
    contagem.columns = ["Overall Task Status", "Qtd"]
    fig = px.pie(contagem, names="Overall Task Status", values="Qtd", hole=0.55)
    fig.update_layout(title="Overall Task Status", height=320, margin=dict(l=10, r=10, t=45, b=10))
    return fig

def grafico_budget_projeto(df):
    budget = df.groupby("Projeto", as_index=False)["Budget"].sum().sort_values("Budget", ascending=True)
    fig = px.bar(budget, x="Budget", y="Projeto", orientation="h", text="Budget")
    fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside", marker_color="#2E7D32")
    fig.update_layout(title="Budget por Projeto", height=320, margin=dict(l=10, r=25, t=45, b=10), xaxis_title="Budget", yaxis_title="")
    return fig

def grafico_payback_projeto(df):
    payback = df.groupby("Projeto", as_index=False)["Payback"].mean().sort_values("Payback", ascending=False)
    fig = px.bar(payback, x="Projeto", y="Payback", text="Payback")
    fig.update_traces(texttemplate="%{text:.1f} meses", textposition="outside", marker_color="#795548")
    fig.update_layout(
        title="Payback Médio por Projeto",
        height=320,
        margin=dict(l=10, r=10, t=45, b=10),
        xaxis_title="Projeto",
        yaxis_title="Meses"
    )
    return fig

def grafico_fase_in_out(df):
    fase = pd.DataFrame({
        "Tipo": ["Fase In Concluído", "Fase In Pendente", "Fase Out Concluído", "Fase Out Pendente"],
        "Qtd": [
            (df["Fase In"] == "Concluído").sum(),
            (df["Fase In"] != "Concluído").sum(),
            (df["Fase Out"] == "Concluído").sum(),
            (df["Fase Out"] != "Concluído").sum()
        ]
    })
    fig = px.bar(fase, x="Tipo", y="Qtd", text="Qtd")
    fig.update_traces(textposition="outside")
    fig.update_layout(title="Fase In / Fase Out Itens", height=320, margin=dict(l=10, r=10, t=45, b=10), xaxis_title="", yaxis_title="Qtd")
    return fig


def grafico_riscos_avancado(df):
    riscos = df["Nível do Risco"].fillna("Não informado").replace("", "Não informado").value_counts().reset_index()
    riscos.columns = ["Nível do Risco", "Qtd"]
    fig = px.bar(
        riscos,
        x="Nível do Risco",
        y="Qtd",
        text="Qtd",
        color="Nível do Risco",
        color_discrete_map={"Crítico": "#d32f2f", "Médio": "#f9a825", "Baixo": "#2e7d32", "Não informado": "#9e9e9e"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(title="Mapa de Riscos por Nível", height=320, xaxis_title="", yaxis_title="Qtd")
    return fig

def grafico_matriz_risco(df):
    base = df.copy()
    if base.empty:
        base = pd.DataFrame({"Probabilidade do Risco": ["Baixa"], "Impacto do Risco": ["Baixo"], "Qtd": [0]})
    matriz = base.groupby(["Probabilidade do Risco", "Impacto do Risco"], as_index=False).size()
    matriz.columns = ["Probabilidade do Risco", "Impacto do Risco", "Qtd"]
    fig = px.density_heatmap(
        matriz,
        x="Impacto do Risco",
        y="Probabilidade do Risco",
        z="Qtd",
        text_auto=True,
        category_orders={"Impacto do Risco": ["Baixo", "Médio", "Alto"], "Probabilidade do Risco": ["Baixa", "Média", "Alta"]},
        color_continuous_scale=["#2e7d32", "#f9a825", "#d32f2f"]
    )
    fig.update_layout(title="Matriz de Risco: Probabilidade x Impacto", height=360, xaxis_title="Impacto", yaxis_title="Probabilidade")
    return fig

def grafico_riscos_por_projeto(df):
    riscos = df.groupby(["Projeto", "Nível do Risco"], as_index=False).size()
    riscos.columns = ["Projeto", "Nível do Risco", "Qtd"]
    fig = px.bar(
        riscos,
        x="Projeto",
        y="Qtd",
        color="Nível do Risco",
        text="Qtd",
        color_discrete_map={"Crítico": "#d32f2f", "Médio": "#f9a825", "Baixo": "#2e7d32", "Não informado": "#9e9e9e"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(title="Riscos por Projeto", height=320, xaxis_title="", yaxis_title="Qtd")
    return fig


def grafico_fornecedor(df):
    fornecedor = df["Fornecedor"].fillna("Não informado").replace("", "Não informado").value_counts().reset_index()
    fornecedor.columns = ["Fornecedor", "Qtd"]
    fig = px.bar(fornecedor, x="Fornecedor", y="Qtd", text="Qtd")
    fig.update_traces(textposition="outside", marker_color="#4A90E2")
    fig.update_layout(title="Ações por Fornecedor", height=320, margin=dict(l=10, r=10, t=45, b=10), xaxis_title="", yaxis_title="Qtd")
    return fig

def grafico_performance(resumo):
    fig = px.bar(
        resumo.sort_values("Performance"),
        x="Performance",
        y="Projeto",
        orientation="h",
        text="Performance",
        range_x=[0, 150]
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_color="#4CAF50")
    fig.update_layout(title="Performance por Projeto", height=320, margin=dict(l=10, r=25, t=45, b=10))
    return fig

def grafico_gantt(df):
    gantt = df.dropna(subset=["Data Início", "Data Fim"]).copy()
    if gantt.empty:
        return None
    gantt["Linha"] = gantt["Etapa"] + " - " + gantt["Tarefa"]
    fig = px.timeline(
        gantt,
        x_start="Data Início",
        x_end="Data Fim",
        y="Linha",
        color="Status",
        hover_data=["Projeto", "Responsável", "Percentual Concluído"],
        color_discrete_map=CORES_STATUS
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        title="Cronograma",
        height=max(430, len(gantt) * 32),
        margin=dict(l=10, r=10, t=45, b=10),
        legend_title_text=""
    )
    return fig


def grafico_gantt_projetos(df):
    base = df.dropna(subset=["Data Início", "Data Fim"]).copy()
    if base.empty:
        return None

    projetos = base.groupby("Projeto", as_index=False).agg(
        Inicio=("Data Início", "min"),
        Fim=("Data Fim", "max"),
        Performance=("Percentual Concluído", "mean"),
        Budget=("Budget", "sum"),
        Payback=("Payback", "mean"),
        Status_Geral=("Status", lambda x: "Atrasada" if (x == "Atrasada").any() else ("Concluída" if (x == "Concluída").all() else "Em Andamento"))
    )

    projetos["Performance"] = projetos["Performance"].round(1)
    projetos["Payback"] = projetos["Payback"].round(1)

    fig = px.timeline(
        projetos,
        x_start="Inicio",
        x_end="Fim",
        y="Projeto",
        color="Status_Geral",
        hover_data=["Performance", "Budget", "Payback"],
        color_discrete_map=CORES_STATUS
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        title="Gantt Geral dos Projetos",
        height=max(450, len(projetos) * 45),
        margin=dict(l=10, r=10, t=55, b=10),
        legend_title_text="Status Geral"
    )
    return fig

def abrir_indicadores_do_projeto(projeto):
    st.session_state.projeto_selecionado = projeto
    st.session_state.pagina_atual = "Dashboard"

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #1f2a33;
}
[data-testid="stSidebar"] * {
    color: white;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}
.big-number {
    font-size: 44px;
    font-weight: 800;
    color: #263238;
}
.small-label {
    color: #667085;
    font-size: 14px;
}

.logo-sidebar {
    text-align: center;
    padding: 8px 0 18px 0;
}
.header-gno {
    display: flex;
    align-items: center;
    gap: 18px;
}
.engineering-icon {
    font-size: 52px;
    line-height: 1;
}
.gno-title-box {
    display: flex;
    flex-direction: column;
}
.gno-subtitle {
    color: #667085;
    margin-top: -8px;
}


/* SIDEBAR GNO */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #142331 0%, #1d2e3c 55%, #142331 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * {
    color: #ffffff;
}
[data-testid="stSidebar"] .stRadio > label {
    display: none;
}
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 7px;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent;
    border-radius: 7px;
    padding: 8px 10px;
    margin-bottom: 4px;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, #ff7043 0%, #f4511e 100%);
    box-shadow: 0 4px 10px rgba(244,81,30,0.35);
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #243746;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 7px;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background-color: #263a49;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 7px;
    color: white;
    font-size: 13px;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #31495b;
    border-color: rgba(255,255,255,0.18);
}
.sidebar-logo-title {
    text-align: left;
    padding: 10px 8px 18px 8px;
}
.sidebar-logo-title .gno {
    font-size: 42px;
    line-height: 40px;
    font-weight: 900;
    color: #ff5a1f;
    letter-spacing: 1px;
}
.sidebar-logo-title .sub {
    font-size: 10px;
    color: #ff8a50;
    letter-spacing: 3px;
    margin-left: 3px;
}
.sidebar-section {
    border-top: 1px solid rgba(255,255,255,0.08);
    margin-top: 16px;
    padding-top: 16px;
}
.sidebar-filter-title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
}
.sidebar-small-label {
    font-size: 12px;
    color: #d0d7de;
    margin-top: 8px;
}


.gear-header-icon {
    font-size: 54px;
    line-height: 1;
    color: #f4511e;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.12);
}
.gear-header-icon-small {
    font-size: 28px;
    color: #263238;
    margin-left: -14px;
    vertical-align: top;
}
</style>
""", unsafe_allow_html=True)

if "df_projetos" not in st.session_state:
    st.session_state.df_projetos = carregar_dados()

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Projetos"

if "projeto_selecionado" not in st.session_state:
    st.session_state.projeto_selecionado = "Todos"

st.session_state.df_projetos = atualizar_nivel_risco(atualizar_status_automatico(st.session_state.df_projetos))

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-title">
        <div class="gno">GNO</div>
        <div class="sub">GRUPO NEW ORDER</div>
    </div>
    """, unsafe_allow_html=True)
    menu_map = {
        "▦  Dashboard": "Dashboard",
        "▦  Projetos": "Projetos",
        "☷  Cronograma (Gantt)": "Projetos",
        "☰  Tarefas": "Editar Planilha",
        "👥  Fornecedores": "Dashboard",
        "▧  Orçamentos": "Dashboard",
        "▥  Relatórios": "Exportar Excel",
        "◻  Documentos": "Importar Excel",
        "▣  Calendário": "Projetos",
        "▥  Indicadores": "Dashboard",
        "⚠  Riscos": "Dashboard",
        "🚨  Projetos Críticos": "Projetos Críticos",
        "⚙  Configurações": "Sobre",
        "＋  Cadastrar Projeto": "Cadastrar Projeto"
    }

    opcoes_menu = list(menu_map.keys())

    pagina_label = st.radio(
        "Menu",
        opcoes_menu,
        index=0 if st.session_state.pagina_atual == "Dashboard" else 1 if st.session_state.pagina_atual == "Projetos" else 0
    )

    pagina = menu_map[pagina_label]
    st.session_state.pagina_atual = pagina
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-filter-title">Filtros rápidos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-small-label">Departamento</div>', unsafe_allow_html=True)
    filtro_sidebar_departamento = st.selectbox("Departamento", ["Todos"], label_visibility="collapsed")
    st.markdown('<div class="sidebar-small-label">Status</div>', unsafe_allow_html=True)
    filtro_sidebar_status = st.selectbox("Status", ["Todos"], label_visibility="collapsed")
    st.markdown('<div class="sidebar-small-label">Responsável</div>', unsafe_allow_html=True)
    filtro_sidebar_responsavel = st.selectbox("Responsável", ["Todos"], label_visibility="collapsed")
    st.button("🗑  Limpar filtros")
    st.markdown('</div>', unsafe_allow_html=True)

df = st.session_state.df_projetos.copy()


def filtrar_projetos_criticos(df):
    base = df.copy()

    condicoes = pd.Series(False, index=base.index)

    if "Prioridade" in base.columns:
        condicoes = condicoes | (base["Prioridade"].astype(str).str.lower() == "crítica")

    if "Nível do Risco" in base.columns:
        condicoes = condicoes | (base["Nível do Risco"].astype(str).str.lower() == "crítico")

    if "Status" in base.columns:
        condicoes = condicoes | (base["Status"].astype(str).str.lower().isin(["atrasado", "atrasada"]))

    return base[condicoes].copy()

def grafico_projetos_criticos(df):
    criticos = filtrar_projetos_criticos(df)
    if criticos.empty:
        return None

    resumo = criticos.groupby("Projeto", as_index=False).agg(
        Qtd_Critica=("Projeto", "count")
    ).sort_values("Qtd_Critica", ascending=True)

    fig = px.bar(
        resumo,
        x="Qtd_Critica",
        y="Projeto",
        orientation="h",
        text="Qtd_Critica",
        title="Quantidade de itens críticos por projeto"
    )
    fig.update_traces(textposition="outside", marker_color="#d32f2f")
    fig.update_layout(height=360, margin=dict(l=10, r=20, t=50, b=10), xaxis_title="Itens críticos", yaxis_title="")
    return fig


if pagina == "Projetos":
    col_icon, col_title = st.columns([0.08, 0.92])
    with col_icon:
        st.markdown('<div><span class="gear-header-icon">⚙️</span><span class="gear-header-icon-small">⚙️</span></div>', unsafe_allow_html=True)
    with col_title:
        st.title("Projetos")
        st.caption("Visão geral em Gantt. Escolha um projeto para abrir os indicadores detalhados.")

    fig_projetos = grafico_gantt_projetos(df)
    if fig_projetos:
        st.plotly_chart(fig_projetos, use_container_width=True)
    else:
        st.warning("Não há dados suficientes para montar o Gantt dos projetos.")

    st.subheader("Abrir indicadores do projeto")

    projetos_lista = ["Todos"] + sorted(df["Projeto"].dropna().astype(str).unique().tolist())
    projeto_escolhido = st.selectbox(
        "Selecione o projeto",
        projetos_lista,
        index=projetos_lista.index(st.session_state.projeto_selecionado) if st.session_state.projeto_selecionado in projetos_lista else 0
    )

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("Abrir indicadores", use_container_width=True):
            abrir_indicadores_do_projeto(projeto_escolhido)
            st.rerun()

    st.subheader("Resumo dos Projetos")
    resumo_inicial = resumo_projetos(df)
    if not resumo_inicial.empty:
        resumo_inicial = resumo_inicial.rename(columns={
            "Overall_Status": "Overall Task Status",
            "Payback_Medio": "Payback Médio",
            "No_Prazo": "No Prazo",
            "Ações_Total": "Ações (Total)"
        })
        st.dataframe(resumo_inicial, use_container_width=True, hide_index=True)


elif pagina == "Projetos Críticos":
    col_icon, col_title = st.columns([0.08, 0.92])
    with col_icon:
        st.markdown('<div><span class="gear-header-icon">🚨</span></div>', unsafe_allow_html=True)
    with col_title:
        st.title("Projetos Críticos / Prioritários")
        st.caption("Projetos que exigem atenção imediata por prioridade crítica, risco crítico ou atraso.")

    df_criticos = filtrar_projetos_criticos(df)

    total_criticos = len(df_criticos)
    projetos_criticos = df_criticos["Projeto"].nunique() if not df_criticos.empty else 0
    riscos_criticos = int((df_criticos["Nível do Risco"].astype(str).str.lower() == "crítico").sum()) if "Nível do Risco" in df_criticos.columns and not df_criticos.empty else 0
    atrasados = int(df_criticos["Status"].astype(str).str.lower().isin(["atrasado", "atrasada"]).sum()) if "Status" in df_criticos.columns and not df_criticos.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projetos Críticos", projetos_criticos)
    c2.metric("Itens Críticos", total_criticos)
    c3.metric("Riscos Críticos", riscos_criticos)
    c4.metric("Itens Atrasados", atrasados)

    if df_criticos.empty:
        st.success("✅ Nenhum projeto crítico encontrado no momento.")
    else:
        st.error("🚨 Existem projetos críticos que precisam de acompanhamento prioritário.")

        fig_criticos = grafico_projetos_criticos(df)
        if fig_criticos:
            st.plotly_chart(fig_criticos, use_container_width=True)

        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            projetos_lista = ["Todos"] + sorted(df_criticos["Projeto"].dropna().astype(str).unique().tolist())
            filtro_projeto_critico = st.selectbox("Filtrar projeto crítico", projetos_lista)
        with col_filtro2:
            responsaveis_lista = ["Todos"] + sorted(df_criticos["Responsável"].dropna().astype(str).unique().tolist()) if "Responsável" in df_criticos.columns else ["Todos"]
            filtro_resp_critico = st.selectbox("Filtrar responsável crítico", responsaveis_lista)

        tabela_criticos = df_criticos.copy()
        if filtro_projeto_critico != "Todos":
            tabela_criticos = tabela_criticos[tabela_criticos["Projeto"] == filtro_projeto_critico]
        if filtro_resp_critico != "Todos" and "Responsável" in tabela_criticos.columns:
            tabela_criticos = tabela_criticos[tabela_criticos["Responsável"] == filtro_resp_critico]

        colunas_exibir = [
            "Projeto",
            "Prioridade",
            "Status",
            "Nível do Risco",
            "Riscos",
            "Responsável",
            "Departamento",
            "Data Fim",
            "Budget",
            "Payback",
            "Percentual Concluído"
        ]
        colunas_exibir = [c for c in colunas_exibir if c in tabela_criticos.columns]

        st.subheader("Lista de Projetos Críticos")
        st.dataframe(tabela_criticos[colunas_exibir], use_container_width=True, hide_index=True)

        if "Data Início" in tabela_criticos.columns and "Data Fim" in tabela_criticos.columns:
            fig_gantt_critico = grafico_gantt(tabela_criticos)
            if fig_gantt_critico:
                st.subheader("Cronograma dos Projetos Críticos")
                st.plotly_chart(fig_gantt_critico, use_container_width=True)


elif pagina == "Dashboard":
    col_icon, col_title = st.columns([0.08, 0.92])
    with col_icon:
        st.markdown('<div><span class="gear-header-icon">⚙️</span><span class="gear-header-icon-small">⚙️</span></div>', unsafe_allow_html=True)
    with col_title:
        st.title("Painel de Projetos")
        st.caption("Acompanhe o desempenho e o cronograma dos projetos.")

    if st.button("← Voltar para Gantt geral dos projetos"):
        st.session_state.pagina_atual = "Projetos"
        st.rerun()

    col_f0, col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([1.1, 1.1, 1, 1, 1, 1])
    projetos = ["Todos"] + sorted(df["Projeto"].dropna().astype(str).unique().tolist())
    departamentos = ["Todos"] + sorted(df["Departamento"].dropna().astype(str).unique().tolist())
    responsaveis = ["Todos"] + sorted(df["Responsável"].dropna().astype(str).unique().tolist())
    fornecedores = ["Todos"] + sorted(df["Fornecedor"].dropna().astype(str).unique().tolist())
    overall_status = ["Todos"] + sorted(df["Overall Task Status"].dropna().astype(str).unique().tolist())
    solicitantes = ["Todos"] + sorted(df["Solicitante do Projeto"].dropna().astype(str).unique().tolist())

    with col_f0:
        filtro_projeto = st.selectbox(
            "Filtrar Projeto",
            projetos,
            index=projetos.index(st.session_state.projeto_selecionado) if st.session_state.projeto_selecionado in projetos else 0
        )
    with col_f1:
        filtro_overall = st.selectbox("Filtrar Overall Task Status", overall_status)
    with col_f2:
        filtro_departamento = st.selectbox("Filtrar por Departamento", departamentos)
    with col_f3:
        filtro_responsavel = st.selectbox("Filtrar por Responsável", responsaveis)
    with col_f4:
        filtro_fornecedor = st.selectbox("Filtrar por Fornecedor", fornecedores)
    with col_f5:
        filtro_solicitante = st.selectbox("Filtrar Solicitante", solicitantes)

    df_filtrado = df.copy()
    if filtro_projeto != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Projeto"] == filtro_projeto]
        st.session_state.projeto_selecionado = filtro_projeto
    else:
        st.session_state.projeto_selecionado = "Todos"

    if filtro_departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == filtro_departamento]
    if filtro_responsavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Responsável"] == filtro_responsavel]
    if filtro_fornecedor != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Fornecedor"] == filtro_fornecedor]
    if filtro_overall != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Overall Task Status"] == filtro_overall]
    if filtro_solicitante != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Solicitante do Projeto"] == filtro_solicitante]

    resumo = resumo_projetos(df_filtrado)
    total_acoes = len(df_filtrado)
    qtd_atrasadas = int((df_filtrado["Status"] == "Atrasada").sum())
    qtd_concluidas = int((df_filtrado["Status"] == "Concluída").sum())
    qtd_prazo = int(((df_filtrado["Status"] == "No Prazo") | (df_filtrado["Status"] == "Em Andamento")).sum())
    performance_media = float(df_filtrado["Percentual Concluído"].mean()) if total_acoes else 0
    budget_total = float(df_filtrado["Budget"].sum()) if total_acoes else 0
    total_fornecedores = df_filtrado["Fornecedor"].replace("", pd.NA).dropna().nunique() if total_acoes else 0
    fase_in_concluida = int((df_filtrado["Fase In"] == "Concluído").sum()) if total_acoes else 0
    fase_out_concluida = int((df_filtrado["Fase Out"] == "Concluído").sum()) if total_acoes else 0
    payback_medio = float(df_filtrado["Payback"].mean()) if total_acoes else 0
    riscos_criticos = int((df_filtrado["Nível do Risco"] == "Crítico").sum()) if total_acoes else 0
    riscos_medios = int((df_filtrado["Nível do Risco"] == "Médio").sum()) if total_acoes else 0
    riscos_baixos = int((df_filtrado["Nível do Risco"] == "Baixo").sum()) if total_acoes else 0
    total_solicitantes = df_filtrado["Solicitante do Projeto"].replace("", pd.NA).dropna().nunique() if total_acoes else 0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric("Budget Total", f"R$ {budget_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with m2:
        st.metric("Fornecedores", total_fornecedores)
    with m3:
        st.metric("Fase In Concluído", fase_in_concluida)
    with m4:
        st.metric("Fase Out Concluído", fase_out_concluida)
    with m5:
        st.metric("Payback Médio", f"{payback_medio:.1f} meses")
    with m6:
        st.metric("Solicitantes", total_solicitantes)

    if riscos_criticos > 0:
        st.error(f"🚨 Atenção: existem {riscos_criticos} risco(s) crítico(s) no filtro atual.")
    elif riscos_medios > 0:
        st.warning(f"⚠️ Existem {riscos_medios} risco(s) médio(s) no filtro atual.")
    else:
        st.success("✅ Não há riscos críticos no filtro atual.")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Riscos Críticos", riscos_criticos)
    with r2:
        st.metric("Riscos Médios", riscos_medios)
    with r3:
        st.metric("Riscos Baixos", riscos_baixos)

    col_tabela, col_gauge = st.columns([3.2, 1])

    with col_tabela:
        st.subheader("Ações do Projeto")
        if resumo.empty:
            st.warning("Nenhum dado encontrado.")
        else:
            tabela = resumo.rename(columns={
                "No_Prazo": "No Prazo",
                "Ações_Total": "Ações (Total)",
                "Overall_Status": "Overall Task Status",
                "Payback_Medio": "Payback Médio"
            })
            st.dataframe(tabela, use_container_width=True, hide_index=True)

    with col_gauge:
        st.plotly_chart(grafico_velocimetro(performance_media), use_container_width=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-number">{total_acoes}</div>
                <div class="small-label">Ações<br>(Total)</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            status_df = pd.DataFrame({
                "Status": ["Atrasada", "Concluída", "No Prazo", "Total"],
                "Qtd": [qtd_atrasadas, qtd_concluidas, qtd_prazo, total_acoes]
            })
            st.dataframe(status_df, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns([1, 1.25, 1.15])
    with col1:
        st.plotly_chart(grafico_rosca_status(df_filtrado), use_container_width=True)
    with col2:
        if not resumo.empty:
            st.plotly_chart(grafico_performance(resumo), use_container_width=True)
    with col3:
        st.plotly_chart(grafico_rosca_departamento(df_filtrado), use_container_width=True)

    col4, col5, col6 = st.columns([1, 1.25, 1.15])
    with col4:
        st.plotly_chart(grafico_overall_status(df_filtrado), use_container_width=True)
    with col5:
        st.plotly_chart(grafico_budget_projeto(df_filtrado), use_container_width=True)
    with col6:
        st.plotly_chart(grafico_fase_in_out(df_filtrado), use_container_width=True)

    col7, col8 = st.columns([1, 1])
    with col7:
        st.plotly_chart(grafico_fornecedor(df_filtrado), use_container_width=True)
    with col8:
        st.plotly_chart(grafico_payback_projeto(df_filtrado), use_container_width=True)

    st.plotly_chart(grafico_riscos_avancado(df_filtrado), use_container_width=True)
    col_risco1, col_risco2 = st.columns(2)
    with col_risco1:
        st.plotly_chart(grafico_matriz_risco(df_filtrado), use_container_width=True)
    with col_risco2:
        st.plotly_chart(grafico_riscos_por_projeto(df_filtrado), use_container_width=True)

    fig_gantt = grafico_gantt(df_filtrado)
    if fig_gantt:
        st.plotly_chart(fig_gantt, use_container_width=True)

elif pagina == "Cadastrar Projeto":
    if st.session_state.perfil == "visual":
        st.warning("🔒 Apenas administradores podem cadastrar.")
    else:
        st.title("Cadastrar Projeto / Tarefa")

    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        with col1:
            projeto = st.text_input("Projeto")
            necessidade_projeto = st.text_area("Necessidade do Projeto")
            solicitante_projeto = st.text_input("Solicitante do Projeto")
            departamento = st.text_input("Departamento")
            responsavel = st.text_input("Responsável")
            fornecedor = st.text_input("Fornecedor")
            riscos = st.text_area("Riscos do Projeto")
            probabilidade_risco = st.selectbox("Probabilidade do Risco", PROBABILIDADE_RISCO_OPCOES)
            impacto_risco = st.selectbox("Impacto do Risco", IMPACTO_RISCO_OPCOES)
            etapa = st.text_input("Etapa")
            tarefa = st.text_input("Tarefa")
        with col2:
            data_inicio = st.date_input("Data Início", value=date.today())
            data_fim = st.date_input("Data Fim", value=date.today() + timedelta(days=7))
            status = st.selectbox("Status", STATUS_OPCOES)
            overall_task_status = st.selectbox("Overall Task Status", OVERALL_STATUS_OPCOES)
            prioridade = st.selectbox("Prioridade", PRIORIDADE_OPCOES)
            budget = st.number_input("Budget", min_value=0.0, step=1000.0, format="%.2f")
            payback = st.number_input("Payback em meses", min_value=0.0, step=1.0, format="%.1f")
            percentual = st.slider("Percentual Concluído", 0, 150, 0)
            fase_in = st.selectbox("Fase In", FASE_OPCOES)
            fase_out = st.selectbox("Fase Out", FASE_OPCOES)
        observacoes = st.text_area("Observações")

        if st.form_submit_button("Salvar"):
            if not projeto or not tarefa:
                st.warning("Preencha pelo menos Projeto e Tarefa.")
            elif data_fim < data_inicio:
                st.warning("A Data Fim não pode ser anterior à Data Início.")
            else:
                novo = pd.DataFrame([{
                    "Projeto": projeto,
                    "Necessidade do Projeto": necessidade_projeto,
                    "Solicitante do Projeto": solicitante_projeto,
                    "Departamento": departamento,
                    "Responsável": responsavel,
                    "Fornecedor": fornecedor,
                    "Riscos": riscos,
                    "Probabilidade do Risco": probabilidade_risco,
                    "Impacto do Risco": impacto_risco,
                    "Nível do Risco": calcular_nivel_risco(probabilidade_risco, impacto_risco),
                    "Etapa": etapa,
                    "Tarefa": tarefa,
                    "Overall Task Status": overall_task_status,
                    "Fase In": fase_in,
                    "Fase Out": fase_out,
                    "Data Início": data_inicio,
                    "Data Fim": data_fim,
                    "Status": status,
                    "Prioridade": prioridade,
                    "Budget": budget,
                    "Payback": payback,
                    "Percentual Concluído": percentual,
                    "Observações": observacoes
                }])
                st.session_state.df_projetos = pd.concat([st.session_state.df_projetos, novo], ignore_index=True)
                salvar_dados(st.session_state.df_projetos)
                st.success("Registro salvo com sucesso!")

elif pagina == "Editar Planilha":
    st.title("Editar Planilha")
    editado = st.data_editor(
        st.session_state.df_projetos,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Necessidade do Projeto": st.column_config.TextColumn("Necessidade do Projeto", width="large"),
            "Solicitante do Projeto": st.column_config.TextColumn("Solicitante do Projeto"),
            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPCOES),
            "Prioridade": st.column_config.SelectboxColumn("Prioridade", options=PRIORIDADE_OPCOES),
            "Overall Task Status": st.column_config.SelectboxColumn("Overall Task Status", options=OVERALL_STATUS_OPCOES),
            "Fase In": st.column_config.SelectboxColumn("Fase In", options=FASE_OPCOES),
            "Fase Out": st.column_config.SelectboxColumn("Fase Out", options=FASE_OPCOES),
            "Budget": st.column_config.NumberColumn("Budget", min_value=0, step=1000, format="R$ %.2f"),
            "Payback": st.column_config.NumberColumn("Payback", min_value=0, step=1, format="%.1f meses"),
            "Percentual Concluído": st.column_config.NumberColumn("Percentual Concluído", min_value=0, max_value=150)
        }
    )
    if st.button("Salvar alterações"):
        st.session_state.df_projetos = tratar_datas(editado)
        salvar_dados(st.session_state.df_projetos)
        st.success("Planilha salva.")

elif pagina == "Importar Excel":
    st.title("Importar Excel")
    arquivo = st.file_uploader("Envie sua planilha .xlsx", type=["xlsx"])
    if arquivo:
        try:
            df_importado = pd.read_excel(arquivo)
            for coluna in COLUNAS:
                if coluna not in df_importado.columns:
                    df_importado[coluna] = ""
            df_importado = tratar_datas(df_importado[COLUNAS])
            st.dataframe(df_importado, use_container_width=True)
            if st.button("Usar esta planilha"):
                st.session_state.df_projetos = df_importado
                salvar_dados(df_importado)
                st.success("Planilha importada com sucesso.")
        except Exception as erro:
            st.error(f"Erro ao importar: {erro}")

elif pagina == "Exportar Excel":
    st.title("Exportar Excel")
    st.download_button(
        "Baixar planilha Excel",
        data=excel_download(st.session_state.df_projetos),
        file_name=f"painel_projetos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.dataframe(st.session_state.df_projetos, use_container_width=True)

else:
    st.title("Sobre")
    st.write("""
    Ferramenta em Python com Streamlit para gestão de projetos, monitoramento de cronograma,
    indicadores de performance, status, responsáveis, departamentos e exportação/importação Excel.
    """)
