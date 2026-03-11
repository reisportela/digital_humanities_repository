# Relatório de verificação de PDFs

Data da verificação: 2026-03-11

## Escopo

- Dataset analisado: `data/processed/dashboard_documents.csv`
- Pasta local de PDFs: `data/pdfs/`
- Verificação online feita aos `persistent_id`, páginas de registo e URLs candidatas de PDF

## Resumo executivo

- Documentos elegíveis no dataset final: 41
- PDFs presentes localmente em `data/pdfs/`: 31
- Registos elegíveis sem PDF local: 10
- Destes 10 casos:
- 7 têm PDF publicamente acessível online e não foram descarregados por falha do pipeline
- 3 não têm download público direto no momento da verificação e ficaram corretamente sem PDF local

## Conclusão

Não, o repositório local ainda não tem todos os PDFs publicamente disponíveis.

Faltam 7 PDFs que estão acessíveis online e que deveriam ter sido descarregados:

- 6 casos da Universidade Nova de Lisboa (`run.unl.pt`)
- 1 caso da Universidade de Aveiro (`ria.ua.pt`)

Os outros 3 casos parecem estar com acesso condicionado:

- 1 caso da Universidade de Coimbra redireciona para login LDAP
- 1 caso da Universidade da Beira Interior só mostra página `request-a-copy`
- 1 caso da Universidade de Évora redireciona para página `request-item`

## Evidência por registo

### PDFs acessíveis online mas em falta localmente

1. `oai:run.unl.pt:10362/190217`
- Título: Museus em Transformação: Análise dos Contributos da Curadoria e das Humanidades Digitais nos Modelos de Avaliação de Impacto
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://run.unl.pt/entities/publication/72d2263c-7ea4-4eee-8382-5ba857d7de9d>
- PDF: <https://run.unl.pt/bitstreams/07a687b5-7496-44fc-afa6-b8759470bd8a/download>
- Diagnóstico: o pipeline não encontrou candidatos porque a resolução automática do `handle` falhou com erro de certificado SSL

2. `oai:run.unl.pt:10362/181868`
- Título: Por Entre Espelhos, Covas e Ecrãs: a Criança Transgressiva de Lewis Carroll e suas Reinterpretações no Videojogo
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://run.unl.pt/entities/publication/669d64f7-9296-45f1-8eb5-82c82863a75d>
- PDF: <https://run.unl.pt/bitstreams/0586352c-9e71-4475-aa4b-b9b88923d71f/download>
- Diagnóstico: mesmo problema de SSL na resolução do `handle`

3. `oai:run.unl.pt:10362/128082`
- Título: Finger-Counting in Two Illuminated Grammatical Manuscripts (12th – 13th centuries)
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://run.unl.pt/entities/publication/39380aad-cdf1-42d1-aa65-f7aea0ee1063>
- PDF: <https://run.unl.pt/bitstreams/de87aa8f-d28e-45af-b97a-0f63929c4467/download>
- Diagnóstico: mesmo problema de SSL na resolução do `handle`

4. `oai:run.unl.pt:10362/154579`
- Título: Implementing the International Image Interoperability Framework (IIIF) for accessibility and reuse of cultural heritage resources on the web – Challenges and Advantages
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://run.unl.pt/entities/publication/a956229a-1346-4e51-8340-5da65d0a86cc>
- PDF: <https://run.unl.pt/bitstreams/33b78a3f-3ed4-4233-80b5-922800f02260/download>
- Diagnóstico: mesmo problema de SSL na resolução do `handle`

5. `oai:run.unl.pt:10362/134773`
- Título: Da narrativa histórica à história digital: Estudo da edição digital da revista "A Águia"
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://run.unl.pt/entities/publication/701027fb-ee0b-4def-bc32-49aefe2bee35>
- PDF: <https://run.unl.pt/bitstreams/b1afcb11-9096-430f-99aa-50dfd687bd90/download>
- Diagnóstico: mesmo problema de SSL na resolução do `handle`

6. `oai:run.unl.pt:10362/137023`
- Título: Terminological Methods in Lexicography: Conceptualising, Organising, and Encoding Terms in General Language Dictionaries
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://run.unl.pt/entities/publication/0c412093-e28b-491c-b8b9-a46a6bb8d81f>
- PDF: <https://run.unl.pt/bitstreams/cb422d26-cadb-4b2c-bcee-473db182344b/download>
- Diagnóstico: mesmo problema de SSL na resolução do `handle`

7. `oai:ria.ua.pt:10773/42068`
- Título: Sistema integrado de suporte à edição eletrónica de forais medievais portugueses e de desenvolvimento de um glossário
- Estado online: PDF acessível com resposta `200` e `content-type: application/pdf`
- Página: <https://ria.ua.pt/handle/10773/42068>
- PDF: <https://ria.ua.pt/bitstream/10773/42068/1/Documento_Jose_Vasco_Sousa.pdf>
- Diagnóstico: o CSV regista erro `403` para `https://ria.ua.pt/feedback`, mas no momento da verificação o link direto do PDF respondeu corretamente; trata-se de falha do pipeline ou de erro transitório de navegação/redirecionamento

### Casos sem download público direto no momento da verificação

8. `oai:estudogeral.uc.pt:10316/122000`
- Título: Um sopro de vida em desedição: pedaços, avessos e outros personagens nos manuscritos de Clarice Lispector
- Página: <https://estudogeral.uc.pt/handle/10316/122000>
- Link candidato registado: <https://estudogeral.uc.pt/retrieve/284182/uc_tese_p%c3%b3s%20def.pdf>
- Estado online: o link do ficheiro redireciona para `https://estudogeral.uc.pt/ldap-login...` com `content-type: text/html`
- Diagnóstico: acesso condicionado por autenticação; não há PDF público direto disponível

9. `oai:ubibliorum.ubi.pt:10400.6/15147`
- Título: Memória Curta: A Lã e a Neve como Espelho da Revolução Silenciada
- Página: <https://ubibliorum.ubi.pt/entities/publication/2eb4bf38-6af4-4bd8-8df1-7ab6cf879e3f>
- Link encontrado na página: <https://ubibliorum.ubi.pt/items/2eb4bf38-6af4-4bd8-8df1-7ab6cf879e3f/request-a-copy?bitstream=a358d8b3-f647-4c8a-9bba-2246f1291503>
- Estado online: apenas página `request-a-copy`, sem resposta PDF
- Diagnóstico: o item não está em acesso aberto direto

10. `oai:dspace.uevora.pt:10174/35754`
- Título: Património ferroviário e urbanismo em cidades portuárias da Península Ibérica
- Página: <http://dspace.uevora.pt/rdpc/handle/10174/35754>
- Link candidato registado: <http://dspace.uevora.pt/rdpc/bitstream/10174/35754/1/Doutoramento-Historia-Fernanda_de_Lima_Lourencetti.pdf>
- Estado online: o link do ficheiro redireciona para `request-item` com `content-type: text/html`
- Diagnóstico: acesso condicionado; não há PDF público direto disponível

## Padrões de falha identificados

1. `run.unl.pt`
- O pipeline engole a exceção na resolução da landing page e fica com `pdf_candidate_count=0`
- A causa observada foi falha de verificação de certificado SSL ao seguir o `handle`
- Resultado: 6 PDFs públicos ficaram por descarregar

2. `ria.ua.pt`
- O link do PDF está operacional
- O erro guardado no CSV (`403` para `/feedback`) não reproduziu na verificação atual
- Resultado: pelo menos 1 PDF público ficou por descarregar

3. Repositórios com acesso condicionado
- `estudogeral.uc.pt`: login LDAP
- `ubibliorum.ubi.pt`: `request-a-copy`
- `dspace.uevora.pt`: `request-item`
- Resultado: estes 3 casos devem ser marcados como acesso restrito e não como simples falha de download

## Recomendação operacional

1. Corrigir o tratamento de SSL e de exceções em `run.unl.pt` para não perder a descoberta de PDFs.
2. Revalidar a lógica de download para `ria.ua.pt`, porque o PDF está online.
3. Introduzir um estado distinto para acesso restrito, separado de falha técnica de download.
4. Reexecutar apenas a etapa de descoberta/download para os 7 casos recuperáveis.
