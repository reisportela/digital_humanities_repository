from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PDF_DIR = DATA_DIR / "pdfs"
INTERIM_DIR = DATA_DIR / "interim"
TEXT_DIR = INTERIM_DIR / "texts"
PROCESSED_DIR = DATA_DIR / "processed"

SEARCH_PHRASE = "humanidades digitais"
RCAAP_BASE_URL = "https://www.rcaap.pt"
SEARCH_FIELDS = {
    "title": "title.main",
    "abstract": "abstract",
    "keywords": "subject.all",
}

INCLUDED_DOCUMENT_TYPES = {
    "bachelor thesis",
    "doctoral thesis",
    "internal report",
    "master thesis",
    "other type of report",
    "report",
    "research report",
    "technical report",
    "thesis",
}

INCLUDED_DOCUMENT_TYPE_URIS = (
    "http://purl.org/coar/resource_type/c_7a1f",
    "http://purl.org/coar/resource_type/c_bdcc",
    "http://purl.org/coar/resource_type/c_db06",
    "http://purl.org/coar/resource_type/c_46ec",
    "http://purl.org/coar/resource_type/c_93fc",
    "http://purl.org/coar/resource_type/c_18ws",
    "http://purl.org/coar/resource_type/c_18gh",
    "http://purl.org/coar/resource_type/c_18ww",
    "http://purl.org/coar/resource_type/c_18wq",
)

PORTUGUESE_DOMAIN_SUFFIXES = (".pt",)

CATEGORY_RULES = [
    {
        "category": "arquivos_bibliotecas_digitais",
        "label": "Arquivos e bibliotecas digitais",
        "keywords": [
            "arquivo digital",
            "arquivos digitais",
            "biblioteca digital",
            "bibliotecas digitais",
            "repositório digital",
            "repositorio digital",
            "base de dados bibliográfica",
            "base de dados bibliografica",
            "catálogo",
            "catalogo",
            "metadata",
            "metadados",
        ],
    },
    {
        "category": "edicao_digital",
        "label": "Edição digital",
        "keywords": [
            "edição digital",
            "edicao digital",
            "edições digitais",
            "edicoes digitais",
            "tei",
            "text encoding initiative",
            "transcrição",
            "transcricao",
            "transcrição digital",
            "transcricao digital",
        ],
    },
    {
        "category": "patrimonio_digital",
        "label": "Património digital",
        "keywords": [
            "património",
            "patrimonio",
            "museu",
            "museus",
            "heritage",
            "coleção digital",
            "colecao digital",
            "acervo digital",
            "património cultural",
            "patrimonio cultural",
        ],
    },
    {
        "category": "humanidades_espaciais_gis",
        "label": "Humanidades espaciais / GIS",
        "keywords": [
            "gis",
            "sig",
            "sistemas de informação geográfica",
            "sistemas de informacao geografica",
            "humanidades espaciais",
            "spatial humanities",
            "cartografia",
            "georreferencia",
            "georreferenciação",
            "mapa digital",
        ],
    },
    {
        "category": "analise_textual_nlp",
        "label": "Análise textual e NLP",
        "keywords": [
            "análise textual",
            "analise textual",
            "processamento de linguagem natural",
            "natural language processing",
            "nlp",
            "text mining",
            "mineração de texto",
            "mineracao de texto",
            "linguística computacional",
            "linguistica computacional",
            "corpus",
        ],
    },
    {
        "category": "preservacao_digital",
        "label": "Preservação digital",
        "keywords": [
            "preservação digital",
            "preservacao digital",
            "curadoria digital",
            "digital preservation",
            "arquivo eletrónico",
            "arquivo eletronico",
            "long term preservation",
        ],
    },
    {
        "category": "visualizacao_informacao",
        "label": "Visualização de informação",
        "keywords": [
            "visualização",
            "visualizacao",
            "visualização de dados",
            "visualizacao de dados",
            "dashboard",
            "network analysis",
            "análise de redes",
            "analise de redes",
            "infografia",
            "visual analytics",
        ],
    },
    {
        "category": "metodos_computacionais",
        "label": "Métodos computacionais aplicados às humanidades",
        "keywords": [
            "humanidades digitais",
            "métodos digitais",
            "metodos digitais",
            "métodos computacionais",
            "metodos computacionais",
            "aprendizagem automática",
            "aprendizagem automatica",
            "machine learning",
            "inteligência artificial",
            "inteligencia artificial",
            "base de dados",
            "hipertexto",
        ],
    },
    {
        "category": "ensino_formacao",
        "label": "Ensino e formação",
        "keywords": [
            "material pedagógico",
            "material pedagogico",
            "ensino",
            "aprendizagem",
            "módulo",
            "modulo",
            "disciplina",
            "curso",
        ],
    },
]

REQUEST_TIMEOUT = 45
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)
