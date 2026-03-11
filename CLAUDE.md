# CLAUDE.md

## Guardrails — Perímetro de atuação

### Âmbito permitido

- Os agentes **podem usar recursos locais do computador** (CPU, disco, rede) para executar tarefas deste projeto.
- Todas as operações de leitura, escrita, criação e eliminação de ficheiros devem acontecer **exclusivamente dentro deste repositório** e das suas subpastas.
- Downloads de PDFs e dados devem ser guardados em `data/pdfs/` ou `data/raw/` — nunca noutro local do sistema de ficheiros.

### Proibições explícitas

- **Nunca editar, criar ou eliminar ficheiros fora da raiz deste repositório.**
- **Nunca modificar configurações globais do sistema** (variáveis de ambiente do sistema, configurações de shell globais, registos do Windows, etc.).
- **Nunca instalar pacotes globalmente** — usar sempre ambientes virtuais (`venv`, `conda`) dentro do projeto ou instalar com `--user`/`pip install` dentro de um venv ativo.
- **Nunca aceder a ficheiros pessoais do utilizador** (Ambiente de Trabalho, Documentos, Downloads, etc.) fora deste repositório.
- **Nunca enviar dados para serviços externos** além do RCAAP e das fontes documentadas no projeto. Nenhum upload de dados do utilizador para APIs de terceiros sem autorização explícita.
- **Nunca executar comandos destrutivos do sistema** (`rm -rf /`, `format`, `shutdown`, alterações de permissões fora do repo, etc.).
- **Nunca armazenar credenciais em ficheiros do repositório** — usar variáveis de ambiente ou ficheiros `.env` que estejam no `.gitignore`.

### Rede e web scraping

- Respeitar `robots.txt` e termos de uso do RCAAP.
- Implementar rate limiting nos scripts de recolha (mínimo 1-2 segundos entre pedidos).
- Não fazer scraping agressivo que possa sobrecarregar servidores.

### Em caso de dúvida

- Se uma tarefa exigir acesso fora do repositório, **parar e perguntar ao utilizador** antes de prosseguir.
- Se um comando puder ter efeitos irreversíveis, **pedir confirmação** primeiro.

---

## Sobre o projeto
Mapeamento de dissertações e relatórios de Humanidades Digitais em Portugal, com dados recolhidos do [RCAAP](https://www.rcaap.pt/). O objetivo final é um dashboard pesquisável para docentes, investigadores e alunos, e a longo prazo mapear a ligação universidade-mercado de trabalho.

Ver [AGENTS.md](AGENTS.md) para regras detalhadas de inclusão, metadados, categorias e convenções.

## Regra de inclusão obrigatória
Um documento só entra no dataset se "humanidades digitais" aparece no **título**, **resumo** ou **keywords**. Sem exceções silenciosas — em caso de dúvida, enviar para fila de revisão manual.

## Estrutura do repositório
```
data/raw/          # Exportações brutas do RCAAP
data/pdfs/         # PDFs descarregados
data/interim/      # Dados limpos intermédios
data/processed/    # Tabelas finais para dashboard
src/               # Scripts (recolha, parsing, normalização, classificação, exportação)
notebooks/         # Exploração e prototipagem
docs/              # Decisões metodológicas, dicionários, notas
dashboard/         # Aplicação do dashboard
```

## Stack técnica
- **Linguagem principal**: Python
- **Análise alternativa**: R (quando necessário)
- Nomes de colunas em `snake_case`
- Separar sempre dados `raw`, `interim` e `processed`
- Nunca sobrescrever ficheiros brutos; versionar por data quando necessário

## Convenções de código
- Scripts modulares: recolha, parsing, normalização, classificação e exportação em ficheiros separados
- Distinguir claramente metadados originais de campos inferidos/derivados
- Guardar texto bruto extraído separadamente dos campos limpos
- Logs de recolha e falhas de download devem ser persistidos
- Deduplicação determinística e documentada

## Ao criar ou modificar scripts
1. Verificar se já existe funcionalidade semelhante em `src/` antes de criar novo ficheiro
2. Usar `utf-8` como encoding por defeito
3. Tratar erros de rede e parsing graciosamente (log + continuar, não crashar)
4. Não hardcodar caminhos — usar caminhos relativos à raiz do projeto ou variáveis de configuração

## Ao trabalhar com dados
- Prioridade de recolha: metadados RCAAP > link permanente > link PDF > extração de texto do PDF
- Nunca misturar metadados do RCAAP com conteúdo inferido sem sinalização clara
- Normalizar universidades e tipos de documento com tabelas de correspondência explícitas
- Se houver classificação automática, guardar confiança, método e versão do classificador

## Ao fazer commits
- Mensagens de commit em inglês
- Nunca fazer commit de PDFs ou datasets grandes ao git (estão no .gitignore)
- Não fazer commit de ficheiros .env ou credenciais

## Idioma
- Código e commits: inglês
- Documentação e comunicação com o utilizador: português (pt-PT)
- Conteúdo dos dados: preservar o idioma original (pt/en)
