# AGENTS.md

## Propósito do repositório
Este repositório serve para mapear dissertações e relatórios relacionados com Humanidades Digitais em Portugal, usando como fonte principal o RCAAP (`https://www.rcaap.pt/`).

O objetivo operacional é construir uma base pesquisável de documentos académicos e respetivos metadados para suportar um dashboard consultável por docentes, investigadores e estudantes.

O objetivo analítico de médio prazo é identificar padrões de produção científica, áreas temáticas, instituições envolvidas e, mais tarde, apoiar o mapeamento da ligação entre universidade e mercado de trabalho.

## Regra principal de inclusão
Um documento só entra no universo principal do projeto se a expressão `humanidades digitais` aparecer em pelo menos um dos seguintes campos:

1. título
2. resumo / abstract
3. palavras-chave / keywords

Se houver dúvida, o documento pode ser guardado numa camada de revisão manual, mas não deve entrar no dataset final validado sem cumprir esta regra.

## Fontes e prioridade de recolha
Fonte primária:
- RCAAP

Sempre que possível, privilegiar metadados estruturados antes de recorrer a extração a partir do PDF.

Ordem preferida de recolha:
1. metadados estruturados do RCAAP
2. link permanente do registo
3. link para ficheiro PDF
4. texto extraído do PDF, apenas quando necessário para completar informação ou análise de conteúdo

## Entregáveis esperados
Qualquer agente que trabalhe neste repositório deve orientar o trabalho para quatro saídas principais:

1. Dataset de documentos elegíveis
2. Repositório local de PDFs
3. Base enriquecida com metadados e variáveis analíticas
4. Dashboard com pesquisa, filtros e visualização

## Metadados mínimos por documento
Sempre que disponíveis, recolher e normalizar os seguintes campos:

- identificador único interno
- título
- autor / aluno
- orientador, se existir
- instituição / universidade
- unidade orgânica / escola / departamento, se existir
- tipo de documento
- grau académico, se existir
- data de publicação / defesa
- resumo
- abstract
- keywords
- idioma
- URL do registo RCAAP
- URL do PDF
- nome do ficheiro PDF local
- disponibilidade do texto integral

## Variáveis analíticas a construir
Além dos metadados originais, o projeto deve criar variáveis derivadas úteis para análise e dashboard:

- indicador de inclusão por critério (`titulo`, `resumo`, `keywords`)
- categoria temática de Humanidades Digitais
- subcategoria temática, quando aplicável
- universidade normalizada
- ano normalizado
- tipo de documento normalizado
- existência de PDF descarregado
- qualidade da extração de texto
- estado de revisão manual

## Análise de conteúdo
A análise de conteúdo deve ser reproduzível e auditável.

Regras:
- guardar sempre o texto bruto extraído separadamente dos campos limpos
- distinguir claramente metadados originais de campos inferidos
- manter um dicionário de categorias temáticas com definições curtas e consistentes
- se houver classificação automática, guardar também confiança, método e versão do classificador
- qualquer heurística de categorização deve ser documentada

Categorias temáticas podem incluir, por exemplo:
- arquivos e bibliotecas digitais
- edição digital
- património digital
- humanidades espaciais / GIS
- análise textual e NLP
- preservação digital
- visualização de informação
- métodos computacionais aplicados às humanidades

Estas categorias são iniciais e podem ser refinadas, mas mudanças devem ser documentadas para evitar quebras de comparabilidade.

## Dashboard: requisito funcional
Todo o pipeline deve facilitar a construção de um dashboard com:

- pesquisa por texto
- filtros por universidade
- filtros por ano
- filtros por tipo de documento
- filtros por categoria e subcategoria de Humanidades Digitais
- consulta de resumo, keywords e ligação ao PDF
- indicadores agregados por instituição, período e tema

O modelo de dados deve ser pensado desde o início para consumo por dashboard, evitando campos ambíguos, duplicados e valores livres não normalizados.

## Estrutura recomendada do repositório
Criar esta estrutura à medida que o projeto avançar:

- `data/raw/` para dumps brutos e exportações originais
- `data/pdfs/` para os PDFs descarregados
- `data/interim/` para dados limpos intermédios
- `data/processed/` para tabelas finais do dashboard
- `src/` para scripts de recolha, limpeza, enriquecimento e classificação
- `notebooks/` para exploração, validação e prototipagem
- `docs/` para decisões metodológicas, dicionários e notas de validação
- `dashboard/` para a aplicação final, se for construída dentro deste repositório

## Convenções de trabalho
- Nunca sobrescrever ficheiros brutos sem necessidade; preferir ficheiros versionados por data.
- Separar claramente dados `raw`, `interim` e `processed`.
- Guardar logs de recolha, falhas de download e documentos não processados.
- Usar nomes de colunas estáveis e em `snake_case`.
- Normalizar nomes de universidades e tipos de documento com tabelas de correspondência explícitas.
- Deduplicação deve ser determinística e documentada.

## Qualidade e validação
Antes de considerar uma tarefa concluída, validar pelo menos:

1. se o documento cumpre a regra de inclusão
2. se o PDF corresponde ao registo certo
3. se os campos essenciais não ficaram trocados entre português e inglês
4. se universidade, ano e tipo de documento foram normalizados
5. se o texto extraído do PDF tem qualidade mínima para análise

## Guardrails — Perímetro de atuação

### Âmbito permitido

- Os agentes **podem usar recursos locais do computador** (CPU, disco, rede) para executar tarefas deste projeto.
- Todas as operações de ficheiros devem acontecer **exclusivamente dentro deste repositório** e das suas subpastas.
- Downloads de PDFs e dados devem ser guardados em `data/pdfs/` ou `data/raw/` — nunca noutro local do sistema.

### Proibições explícitas

- **Nunca editar, criar ou eliminar ficheiros fora da raiz deste repositório.**
- **Nunca modificar configurações globais do sistema** (variáveis de ambiente do sistema, configurações de shell, registos do Windows, etc.).
- **Nunca instalar pacotes globalmente** — usar sempre ambientes virtuais (`venv`, `conda`) dentro do projeto.
- **Nunca aceder a ficheiros pessoais do utilizador** fora deste repositório.
- **Nunca enviar dados para serviços externos** além do RCAAP e das fontes documentadas. Nenhum upload sem autorização explícita.
- **Nunca executar comandos destrutivos do sistema** (`rm -rf /`, `format`, `shutdown`, alterações de permissões fora do repo, etc.).
- **Nunca armazenar credenciais em ficheiros do repositório** — usar `.env` (que está no `.gitignore`).

### Rede e web scraping

- Respeitar `robots.txt` e termos de uso do RCAAP.
- Implementar rate limiting nos scripts de recolha (mínimo 1-2 segundos entre pedidos).
- Não fazer scraping agressivo que possa sobrecarregar servidores.

### Em caso de dúvida

- Se uma tarefa exigir acesso fora do repositório, **parar e perguntar ao utilizador**.
- Se um comando puder ter efeitos irreversíveis, **pedir confirmação** primeiro.

## Regras para agentes — Dados e metodologia

- Não assumir que todos os registos do RCAAP têm metadados completos.
- Não inferir categorias temáticas sem deixar rasto do critério usado.
- Não misturar metadados extraídos do RCAAP com conteúdo inferido sem sinalização clara.
- Não apagar ficheiros descarregados ou tabelas intermédias sem motivo explícito.
- Sempre que forem criados scripts, privilegiar modularidade: recolha, parsing, normalização, classificação e exportação devem ficar separados.
- Sempre que houver ambiguidade sobre inclusão, criar uma fila de revisão manual em vez de forçar uma decisão silenciosa.

## Pergunta de investigação de longo prazo
O repositório deve ser preparado para, numa fase posterior, cruzar a produção académica em Humanidades Digitais com trajetórias profissionais e relação com o mercado de trabalho.

Isso significa que o desenho dos dados deve preservar:
- identidade institucional
- temporalidade
- temática
- autoria

sem comprometer a rastreabilidade da origem de cada observação.
