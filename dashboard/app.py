from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from digital_humanities_repository.config import PROCESSED_DIR  # noqa: E402


st.set_page_config(
    page_title="Humanidades Digitais em Portugal",
    page_icon="HD",
    layout="wide",
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, dict]:
    data_path = PROCESSED_DIR / "dashboard_documents.csv"
    summary_path = PROCESSED_DIR / "dashboard_summary.json"
    if not data_path.exists():
        return pd.DataFrame(), {}

    dataframe = pd.read_csv(data_path)
    summary = {}
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return dataframe, summary


def filter_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    institutions = sorted(item for item in dataframe["institution_normalized"].dropna().unique() if item)
    categories = sorted(item for item in dataframe["primary_category_label"].dropna().unique() if item)
    years = sorted(item for item in dataframe["year"].dropna().astype(str).unique() if item)
    doc_types = sorted(item for item in dataframe["document_type"].dropna().unique() if item)

    selected_institutions = st.sidebar.multiselect("Universidade / instituição", institutions)
    selected_categories = st.sidebar.multiselect("Categoria HD", categories)
    selected_years = st.sidebar.multiselect("Ano", years)
    selected_doc_types = st.sidebar.multiselect("Tipo de documento", doc_types)
    only_with_pdf = st.sidebar.checkbox("Apenas com PDF", value=False)
    query = st.sidebar.text_input("Pesquisa livre", placeholder="título, resumo, keywords, autor")

    filtered = dataframe.copy()
    if selected_institutions:
        filtered = filtered[filtered["institution_normalized"].isin(selected_institutions)]
    if selected_categories:
        filtered = filtered[filtered["primary_category_label"].isin(selected_categories)]
    if selected_years:
        filtered = filtered[filtered["year"].astype(str).isin(selected_years)]
    if selected_doc_types:
        filtered = filtered[filtered["document_type"].isin(selected_doc_types)]
    if only_with_pdf:
        filtered = filtered[filtered["pdf_downloaded"] == True]  # noqa: E712
    if query:
        searchable = (
            filtered["title"].fillna("")
            + " "
            + filtered["abstract"].fillna("")
            + " "
            + filtered["keywords"].fillna("")
            + " "
            + filtered["authors"].fillna("")
        )
        filtered = filtered[searchable.str.contains(query, case=False, na=False)]
    return filtered


def render_metrics(filtered: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Documentos", len(filtered))
    col2.metric("Instituições", filtered["institution_normalized"].nunique())
    col3.metric("Com PDF", int(filtered["pdf_downloaded"].sum()))
    col4.metric("Categorias", filtered["primary_category_label"].nunique())


def render_charts(filtered: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        st.subheader("Distribuição por instituição")
        institution_counts = (
            filtered["institution_normalized"]
            .fillna("Sem instituição")
            .value_counts()
            .head(15)
            .sort_values(ascending=True)
        )
        st.bar_chart(institution_counts)

    with right:
        st.subheader("Distribuição por categoria")
        category_counts = (
            filtered["primary_category_label"]
            .fillna("Sem categoria")
            .value_counts()
            .sort_values(ascending=True)
        )
        st.bar_chart(category_counts)


def render_table(filtered: pd.DataFrame) -> None:
    st.subheader("Base consultável")
    display_columns = [
        "title",
        "authors",
        "institution_normalized",
        "year",
        "document_type",
        "primary_category_label",
        "pdf_downloaded",
        "manual_review_status",
    ]
    st.dataframe(
        filtered[display_columns].rename(
            columns={
                "title": "Título",
                "authors": "Autor(es)",
                "institution_normalized": "Instituição",
                "year": "Ano",
                "document_type": "Tipo",
                "primary_category_label": "Categoria",
                "pdf_downloaded": "PDF",
                "manual_review_status": "Estado",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_record_detail(filtered: pd.DataFrame) -> None:
    st.subheader("Detalhe do documento")
    options = {
        f"{row['title']} ({row['year']})": row
        for _, row in filtered.sort_values(["year", "title"], ascending=[False, True]).iterrows()
    }
    if not options:
        st.info("Nenhum documento corresponde aos filtros escolhidos.")
        return

    selected_label = st.selectbox("Selecionar documento", list(options.keys()))
    record = options[selected_label]

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### {record['title']}")
        st.write(record["authors"])
        st.write(f"Instituição: {record['institution_normalized']}")
        st.write(f"Tipo: {record['document_type']}")
        st.write(f"Categoria: {record['primary_category_label']}")
        st.write(f"Critério de inclusão: {record['search_criteria_hits']}")
        st.write(f"Keywords: {record['keywords'] or 'Sem keywords'}")
        st.write(record["abstract"] or "Sem resumo disponível.")

    with col2:
        if record["record_url"]:
            st.markdown(f"[Registo RCAAP]({record['record_url']})")
        if record["persistent_id"]:
            st.markdown(f"[Identificador persistente]({record['persistent_id']})")
        if record["pdf_url"]:
            st.markdown(f"[PDF remoto]({record['pdf_url']})")
        if record["pdf_local_path"]:
            st.code(record["pdf_local_path"])
        st.write(f"Qualidade do texto: {record['pdf_text_quality']}")
        st.write(f"Estado: {record['manual_review_status']}")


def main() -> None:
    dataframe, summary = load_data()
    st.title("Mapeamento de Humanidades Digitais")
    st.caption(
        "Protótipo sobre dissertações e relatórios com a expressão 'humanidades digitais' no título, resumo ou keywords."
    )

    if summary:
        st.caption(
            f"Última atualização: {summary.get('generated_at_utc', 'n/d')} | "
            f"Registos elegíveis: {summary.get('eligible_records', 0)}"
        )

    if dataframe.empty:
        st.warning("Ainda não existe dataset processado. Corre primeiro o pipeline.")
        return

    filtered = filter_dataframe(dataframe)
    render_metrics(filtered)
    render_charts(filtered)
    st.download_button(
        label="Descarregar CSV filtrado",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="humanidades_digitais_filtrado.csv",
        mime="text/csv",
    )
    render_table(filtered)
    render_record_detail(filtered)


if __name__ == "__main__":
    main()
