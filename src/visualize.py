from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from pyvis.network import Network
import owlrl

# ============================================================
# CONFIGURACAO
# ============================================================

LIB = Namespace("http://mylibrary.org/ontology#")

CORES_POR_TIPO = {
    "Novel":      "#42A5F5",
    "TextBook":   "#1E88E5",
    "ShortStory": "#1565C0",
    "Author":     "#EF5350",
    "Editor":     "#E57373",
    "Genre":      "#66BB6A",
    "Publisher":  "#FFA726",
}

TAMANHO_POR_TIPO = {
    "Novel": 25,
    "TextBook": 22,
    "ShortStory": 22,
    "Author": 30,
    "Editor": 20,
    "Genre": 18,
    "Publisher": 22,
}

# Classes de instancia (entidades que devem ser nos no grafo)
CLASSES_INSTANCIA = {
    LIB.Book, LIB.Novel, LIB.TextBook, LIB.ShortStoryCollection,
    LIB.Author, LIB.Editor, LIB.Genre, LIB.Publisher,
}

# Predicados de propriedade (arestas entre instancias)
PREDICADOS_INSTANCIA = {
    LIB.writtenBy, LIB.editedBy, LIB.belongsToGenre, LIB.publishedBy,
    LIB.authorOf, LIB.relatedTo,
}

# Propriedades de dados que geram arestas (titulo, nome, etc.)
PROPRIEDADES_DADOS = {
    LIB.title, LIB.name, LIB.publishedYear, LIB.isbn,
    LIB.numberOfPages, LIB.nationality, LIB.publisherCountry,
}

# Predicados do RDF/OWL que devem ser ignorados
PREDICADOS_IGNORADOS = {
    RDF.type, RDFS.label, RDFS.comment, RDFS.subClassOf,
    RDFS.domain, RDFS.range, OWL.inverseOf, OWL.disjointWith,
    OWL.sameAs, OWL.inverseOf,
}

def uri_para_nome(uri):
    """Extrai o nome amigavel de uma URI."""
    if not uri or '#' not in str(uri):
        return str(uri).split('/')[-1]
    return str(uri).split('#')[-1]

def eh_literal(valor):
    """Verifica se um valor RDF e um literal."""
    return hasattr(valor, 'value')

def eh_classe_owl(uri):
    """Verifica se uma URI e uma classe ou propriedade OWL/RDFS."""
    uri_str = str(uri)
    return any(uri_str.startswith(prefixo) for prefixo in [
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "http://www.w3.org/2000/01/rdf-schema#",
        "http://www.w3.org/2002/07/owl#",
        "http://www.w3.org/2001/XMLSchema#",
    ])

def eh_instancia(grafo, uri):
    """Verifica se uma URI e uma instancia de uma classe da biblioteca."""
    if eh_literal(uri) or eh_classe_owl(uri):
        return False
    for tipo in grafo.objects(uri, RDF.type):
        if tipo in CLASSES_INSTANCIA:
            return True
    return False

def obter_tipo_no(grafo, uri):
    """Determina o tipo principal de um no para colorizacao."""
    for tipo in grafo.objects(uri, RDF.type):
        if tipo == LIB.Novel:
            return "Novel"
        elif tipo == LIB.TextBook:
            return "TextBook"
        elif tipo == LIB.ShortStoryCollection:
            return "ShortStory"
        elif tipo == LIB.Author:
            return "Author"
        elif tipo == LIB.Editor:
            return "Editor"
        elif tipo == LIB.Genre:
            return "Genre"
        elif tipo == LIB.Publisher:
            return "Publisher"
    return "default"

def obter_rotulo(grafo, uri):
    """Obtem o rdfs:label ou o nome da URI como rotulo."""
    labels = list(grafo.objects(uri, RDFS.label))
    if labels:
        return str(labels[0])
    return uri_para_nome(uri)

def construir_tooltip(grafo, uri):
    """Constroi o tooltip detalhado de um no."""
    tipo = obter_tipo_no(grafo, uri)
    rotulo = obter_rotulo(grafo, uri)
    partes = [f"{rotulo}", f"Tipo: {tipo}"]

    for propriedade, nome in [
        (LIB.name, "Nome"), (LIB.nationality, "Nacionalidade"),
        (LIB.title, "Titulo"), (LIB.isbn, "ISBN"),
        (LIB.publishedYear, "Ano"), (LIB.numberOfPages, "Paginas"),
        (LIB.publisherCountry, "Pais"),
    ]:
        valores = list(grafo.objects(uri, propriedade))
        if valores:
            partes.append(f"{nome}: {valores[0]}")

    return "\n".join(partes)

# ============================================================
# CARREGAMENTO DO GRAFO
# ============================================================

print("Carregando ontologia e dados...")
g = Graph()
g.parse("data/ontology.ttl", format="turtle")
g.parse("data/data.ttl", format="turtle")

print(f"Grafo (antes do raciocinio): {len(g)} triplas")
owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics).expand(g)
print(f"Grafo (depois do raciocinio): {len(g)} triplas")

# ============================================================
# CONSTRUCAO DO GRAFO DE VISUALIZACAO
# ============================================================

print("Construindo grafo de visualizacao...")

net = Network(
    height="900px",
    width="100%",
    bgcolor="#1a1a2e",
    font_color="white",
    directed=True,
    notebook=False,
    cdn_resources="in_line",
)

net.set_options("""
{
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -3000,
      "centralGravity": 0.3,
      "springLength": 150,
      "springConstant": 0.02,
      "damping": 0.09
    },
    "stabilization": {
      "iterations": 200
    }
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 100
  }
}
""")

# 1. Coletar todas as instancias (nos que devem aparecer no grafo)
instancias = set()
for s, p, o in g:
    if eh_instancia(g, s):
        instancias.add(s)
    if eh_instancia(g, o):
        instancias.add(o)

print(f"Instancias encontradas: {len(instancias)}")

# 2. Adicionar nos para cada instancia
for inst in instancias:
    tipo = obter_tipo_no(g, inst)
    if tipo == "default":
        continue
    rotulo = obter_rotulo(g, inst)
    cor = CORES_POR_TIPO.get(tipo, "#BDBDBD")
    tamanho = TAMANHO_POR_TIPO.get(tipo, 15)
    tooltip = construir_tooltip(g, inst)

    net.add_node(
        str(inst),
        label=rotulo,
        color=cor,
        size=tamanho,
        title=tooltip,
        borderWidth=2,
        borderWidthSelected=4,
    )

# 3. Adicionar arestas entre instancias
ARESTAS_ADICIONADAS = set()

for s, p, o in g:
    # Pular predicos ignorados
    if p in PREDICADOS_IGNORADOS:
        continue
    # Pular literais
    if eh_literal(o):
        continue
    # Pular URIs do RDF/OWL/XML Schema
    if eh_classe_owl(o):
        continue
    # Pular se sujeito ou objeto nao e instancia
    if s not in instancias or o not in instancias:
        continue
    # Pular se nao e um predicado de instancia
    if p not in PREDICADOS_INSTANCIA:
        continue

    aresta = (str(s), str(p), str(o))
    if aresta not in ARESTAS_ADICIONADAS:
        rotulo_aresta = uri_para_nome(p)
        cor_aresta = "#888888"

        if p in (LIB.writtenBy, LIB.authorOf):
            cor_aresta = "#EF5350"
        elif p == LIB.belongsToGenre:
            cor_aresta = "#66BB6A"
        elif p == LIB.publishedBy:
            cor_aresta = "#FFA726"
        elif p == LIB.editedBy:
            cor_aresta = "#E57373"
        elif p == LIB.relatedTo:
            cor_aresta = "#CE93D8"

        net.add_edge(
            str(s),
            str(o),
            label=rotulo_aresta,
            color=cor_aresta,
            title=rotulo_aresta,
            arrows="to",
            width=1.5,
            font={"size": 10, "color": "#aaaaaa", "strokeWidth": 0},
        )
        ARESTAS_ADICIONADAS.add(aresta)

# ============================================================
# LEGENDA (via HTML customizado)
# ============================================================

ARQUIVO_SAIDA = "output/grafo_biblioteca.html"
net.save_graph(ARQUIVO_SAIDA)

# Injetar legenda via HTML no final do arquivo
legend_html = """
<div style="position:fixed; top:10px; left:10px; background:rgba(26,26,46,0.9);
     padding:15px; border-radius:8px; border:1px solid #444; z-index:9999;
     font-family:Arial,sans-serif; font-size:13px; color:white;">
  <b style="font-size:14px;">Legenda</b><br><br>
"""

for tipo, cor in CORES_POR_TIPO.items():
    legend_html += f'<span style="display:inline-block;width:14px;height:14px;background:{cor};border-radius:50%;margin-right:8px;vertical-align:middle;"></span>{tipo}<br>'

legend_html += "</div>"

with open(ARQUIVO_SAIDA, "r", encoding="utf-8") as f:
    conteudo = f.read()

conteudo = conteudo.replace("<body>", f"<body>\n{legend_html}")

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write(conteudo)

print(f"\nGrafo salvo em: {ARQUIVO_SAIDA}")
print(f"Total de nos: {len(net.nodes)}")
print(f"Total de arestas: {len(net.edges)}")
print("Abra o arquivo HTML no navegador para interagir com o grafo.")
