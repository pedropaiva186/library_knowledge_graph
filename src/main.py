from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, URIRef
import owlrl

# ============================================================
# CONFIGURACAO
# ============================================================

LIB = Namespace("http://mylibrary.org/ontology#")
PREFIXO = "http://mylibrary.org/ontology#"

def uri_para_nome(uri):
    """Extrai o nome amigavel de uma URI (parte depois do #)."""
    if not uri or '#' not in str(uri):
        return str(uri)
    return str(uri).split('#')[-1]

# ============================================================
# CONSULTAS SPARQL
# ============================================================

# Consulta 1 (SPARQL): SELECT com ORDER BY — todos os livros com titulo e nome do autor
SPARQL_CONSULTA_1 = """
PREFIX lib: <http://mylibrary.org/ontology#>

SELECT ?title ?authorName WHERE {
  ?book a lib:Book ;
        lib:title ?title ;
        lib:writtenBy ?author .
  ?author lib:name ?authorName .
}
ORDER BY ?title
"""

# Consulta 2 (SPARQL): SELECT com FILTER — livros publicados depois de 1990
SPARQL_CONSULTA_2 = """
PREFIX lib: <http://mylibrary.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?title ?year WHERE {
  ?book a lib:Book ;
        lib:title ?title ;
        lib:publishedYear ?year .
  FILTER(?year > 1990)
}
ORDER BY ?year
"""

# Consulta 3 (SPARQL): SELECT com agregacao — contagem de livros por autor
SPARQL_CONSULTA_3 = """
PREFIX lib: <http://mylibrary.org/ontology#>

SELECT ?authorName (COUNT(?book) AS ?total) WHERE {
  ?book a lib:Book ;
        lib:writtenBy ?author .
  ?author lib:name ?authorName .
}
GROUP BY ?authorName
HAVING (COUNT(?book) > 1)
ORDER BY DESC(?total)
"""

# Consulta 4 (SPARQL): SELECT com FILTER NOT EXISTS — livros sem editora
SPARQL_CONSULTA_4 = """
PREFIX lib: <http://mylibrary.org/ontology#>

SELECT ?title WHERE {
  ?book a lib:Book ;
        lib:title ?title .
  FILTER NOT EXISTS { ?book lib:publishedBy ?publisher . }
}
"""

# Consulta 5 (SPARQL): ASK — verificar se um autor especifico existe
SPARQL_CONSULTA_5 = """
PREFIX lib: <http://mylibrary.org/ontology#>

ASK {
  ?author a lib:Author ;
          lib:name "George Orwell" .
}
"""

# Consulta 6 (SPARQL): CONSTRUCT — construir subgrafo de autores e seus livros
SPARQL_CONSULTA_6 = """
PREFIX lib: <http://mylibrary.org/ontology#>

CONSTRUCT {
  ?author lib:authorOf ?book .
  ?book lib:title ?title .
}
WHERE {
  ?book a lib:Book ;
        lib:writtenBy ?author ;
        lib:title ?title .
}
"""

# Consulta 7 (SPARQL): UPDATE INSERT — adicionar um novo livro ao grafo
SPARQL_CONSULTA_7 = """
PREFIX lib: <http://mylibrary.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
  lib:Book_NewBook a lib:Novel ;
    lib:title "The New Book" ;
    lib:publishedYear "2024"^^xsd:integer ;
    lib:isbn "978-0-000-00000-0" ;
    lib:numberOfPages 200 ;
    lib:writtenBy lib:Author_Martin ;
    lib:belongsToGenre lib:Genre_Fiction ;
    lib:publishedBy lib:Publisher_Penguin .
}
"""

# Consulta 8 (SPARQL): UPDATE DELETE — remover um triple especifico
SPARQL_CONSULTA_8 = """
PREFIX lib: <http://mylibrary.org/ontology#>

DELETE DATA {
  lib:Book_NewBook lib:publishedYear "2024"^^<http://www.w3.org/2001/XMLSchema#integer> .
}
"""

# Consulta 9 (SPARQL): UPDATE DELETE/INSERT — atualizar o ano de publicacao de um livro
SPARQL_CONSULTA_9 = """
PREFIX lib: <http://mylibrary.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

DELETE {
  lib:Book_1984 lib:publishedYear ?oldYear .
}
INSERT {
  lib:Book_1984 lib:publishedYear "1949"^^xsd:integer .
}
WHERE {
  lib:Book_1984 lib:publishedYear ?oldYear .
}
"""

# ============================================================
# CARREGAMENTO DO GRAFO
# ============================================================

g = Graph()
g.parse("data/ontology.ttl", format="turtle")
g.parse("data/data.ttl", format="turtle")

print(f"Grafo carregado (antes do raciocinio): {len(g)} triplas")

owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics).expand(g)

print(f"Grafo carregado (depois do raciocinio): {len(g)} triplas\n")
print("=" * 60)

# ============================================================
# PARTE 1 — CONSULTAS g.triples()
# ============================================================

print("\n>>> PARTE 1 — Consultas g.triples()\n")

# Consulta 1: Sujeito fixo — todos os triples sobre o livro '1984'
print("Consulta 1: Todos os triples sobre o livro '1984'")
print("-" * 60)
book_1984 = URIRef(f"{PREFIXO}Book_1984")
for s, p, o in g.triples((book_1984, None, None)):
    print(f"  {uri_para_nome(s)} -- {uri_para_nome(p)} -- {uri_para_nome(o)}")
print()

# Consulta 2: Predicado fixo — todos os livros e seus autores (writtenBy)
print("Consulta 2: Todos os livros e seus autores (writtenBy)")
print("-" * 60)
for s, p, o in g.triples((None, LIB.writtenBy, None)):
    print(f"  {uri_para_nome(s)} escrito por {uri_para_nome(o)}")
print()

# Consulta 3: Objeto fixo — todos os livros no genero Ficcao
print("Consulta 3: Todos os livros no genero Ficcao")
print("-" * 60)
genero_ficcao = URIRef(f"{PREFIXO}Genre_Fiction")
for s, p, o in g.triples((None, LIB.belongsToGenre, genero_ficcao)):
    print(f"  {uri_para_nome(s)}")
print()

# Consulta 4: Predicado + Objeto fixos — todos os individuos do tipo Author
print("Consulta 4: Todos os individuos do tipo Author")
print("-" * 60)
for s, p, o in g.triples((None, RDF.type, LIB.Author)):
    print(f"  {uri_para_nome(s)}")
print()

# Consulta 5: Sujeito + Predicado fixos — titulo de um livro especifico
print("Consulta 5: Titulo do livro 'Don Quixote'")
print("-" * 60)
book_quixote = URIRef(f"{PREFIXO}Book_DonQuixote")
for s, p, o in g.triples((book_quixote, LIB.title, None)):
    print(f"  Titulo: {uri_para_nome(o)}")
print()

print("=" * 60)

# ============================================================
# PARTE 2 — CONSULTAS SPARQL
# ============================================================

print("\n>>> PARTE 2 — Consultas SPARQL\n")

# Consulta 1: SELECT com ORDER BY — todos os livros com titulo e nome do autor
print("Consulta 1 (SPARQL): Todos os livros com titulo e nome do autor, ordenados por titulo")
print("-" * 60)
for row in g.query(SPARQL_CONSULTA_1):
    print(f"  {row.title} — {row.authorName}")
print()

# Consulta 2: SELECT com FILTER — livros publicados depois de 1990
print("Consulta 2 (SPARQL): Livros publicados depois de 1990")
print("-" * 60)
for row in g.query(SPARQL_CONSULTA_2):
    print(f"  {row.title} ({row.year})")
print()

# Consulta 3: SELECT com agregacao — contagem de livros por autor
print("Consulta 3 (SPARQL): Contagem de livros por autor (apenas autores com mais de 1 livro)")
print("-" * 60)
for row in g.query(SPARQL_CONSULTA_3):
    print(f"  {row.authorName}: {row.total} livros")
print()

# Consulta 4: SELECT com FILTER NOT EXISTS — livros sem editora
print("Consulta 4 (SPARQL): Livros sem editora")
print("-" * 60)
resultados_q4 = list(g.query(SPARQL_CONSULTA_4))
if resultados_q4:
    for row in resultados_q4:
        print(f"  {row.title}")
else:
    print("  Todos os livros possuem editora.")
print()

# Consulta 5: ASK — verificar se George Orwell existe como Author
print("Consulta 5 (SPARQL): George Orwell existe como Author?")
print("-" * 60)
resultado_q5 = bool(g.query(SPARQL_CONSULTA_5))
print(f"  {resultado_q5}")
print()

# Consulta 6: CONSTRUCT — subgrafo de autores e seus livros
print("Consulta 6 (SPARQL): Subgrafo CONSTRUCT de autores e seus livros")
print("-" * 60)
construido = g.query(SPARQL_CONSULTA_6)
for s, p, o in construido:
    print(f"  {uri_para_nome(s)} -- {uri_para_nome(p)} -- {uri_para_nome(o)}")
print()

# Consulta 7: UPDATE INSERT — adicionar um novo livro ao grafo
print("Consulta 7 (SPARQL): Inserir um novo livro no grafo")
print("-" * 60)
g.update(SPARQL_CONSULTA_7)
print(f"  Grafo agora possui {len(g)} triplas.")
print("  Triplas sobre Book_NewBook:")
for s, p, o in g.triples((LIB.Book_NewBook, None, None)):
    print(f"    {uri_para_nome(s)} -- {uri_para_nome(p)} -- {uri_para_nome(o)}")
print()

# Consulta 8: UPDATE DELETE — remover o triple publishedYear de Book_NewBook
print("Consulta 8 (SPARQL): Deletar o triple publishedYear de Book_NewBook")
print("-" * 60)
g.update(SPARQL_CONSULTA_8)
print(f"  Grafo agora possui {len(g)} triplas.")
print("  Triplas sobre Book_NewBook apos remocao:")
for s, p, o in g.triples((LIB.Book_NewBook, None, None)):
    print(f"    {uri_para_nome(s)} -- {uri_para_nome(p)} -- {uri_para_nome(o)}")
print()

# Consulta 9: UPDATE DELETE/INSERT — atualizar o ano de publicacao de Book_1984
print("Consulta 9 (SPARQL): Atualizar o publishedYear de Book_1984 para 1949")
print("-" * 60)
g.update(SPARQL_CONSULTA_9)
print(f"  Grafo agora possui {len(g)} triplas.")
print("  Ano de publicacao de Book_1984:")
for s, p, o in g.triples((LIB.Book_1984, LIB.publishedYear, None)):
    print(f"    {uri_para_nome(o)}")

print("\n" + "=" * 60)
print("Todas as consultas foram executadas com sucesso.")
print(f"Tamanho final do grafo: {len(g)} triplas")
