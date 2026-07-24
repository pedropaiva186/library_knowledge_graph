# Grafos de Conhecimento de Biblioteca Pessoal

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![RDF](https://img.shields.io/badge/RDF-Turtle-orange)](https://www.w3.org/TR/turtle/)
[![SPARQL](https://img.shields.io/badge/SPARQL-1.1-yellow)](https://www.w3.org/TR/sparql11-overview/)

Um grafo de conhecimento semântico para uma biblioteca pessoal de livros utilizando **RDF**, **RDFS** e **OWL** com Python.

---

## Sumario

- [Visao Geral](#visao-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Dominio Modelado](#dominio-modelado)
- [Ontologia](#ontologia)
  - [Classes](#classes)
  - [Taxonomia](#taxonomia)
  - [Propriedades](#propriedades)
  - [Construcoes OWL](#construcoes-owl)
- [Dados Instanciados](#dados-instanciados)
- [Consultas](#consultas)
  - [Parte 1 — g.triples()](#parte-1--gtriples)
  - [Parte 2 — SPARQL](#parte-2--sparql)
- [Pre-requisitos](#pre-requisitos)
- [Instalacao e Execucao](#instalacao-e-execucao)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Autor](#autor)
- [Licenca](#licenca)

---

## Visao Geral

Este projeto modela uma colecao de biblioteca pessoal como um grafo de conhecimento semântico. Ele define uma ontologia para livros, autores, generos e editoras, popula com dados reais de livros e permite consultas semanticas via **SPARQL** e o metodo `g.triples()` da biblioteca **rdflib**.

O grafo suporta raciocinio semântico (propriedades inversas, transitividade, simetria, funcionalidade) e consultas enriquecidas sobre os dados da biblioteca.

---

## Estrutura do Projeto

```
sbc_books_project/
├── README.md              # Esta documentacao
├── LICENSE                # Licenca MIT
├── .gitignore             # Arquivos ignorados pelo Git
├── requirements.txt       # Dependencias do projeto
├── data/
│   ├── ontology.ttl       # Ontologia OWL: classes, propriedades, construcoes
│   └── data.ttl           # Dados instanciados: 33 individuos, 284+ triples
└── src/
    └── main.py            # Script Python: carregamento + consultas
```

---

## Dominio Modelado

O grafo de conhecimento representa uma colecao de biblioteca pessoal contendo livros reais, seus autores, editoras, generos e relacoes entre eles. O dominio inclui:

- **14 livros** (10 romances, 2 livros-texto, 2 colecoes de contos)
- **8 autores** com nomes e nacionalidades reais
- **2 editores** responsaveis pela edicao de livros
- **4 generos** literarios e tematicos
- **5 editoras** com informacoes de pais de origem

---

## Ontologia

### Classes

| Classe                       | Descricao                                                 |
|------------------------------|-----------------------------------------------------------|
| `lib:Resource`               | Classe raiz para todas as entidades da biblioteca         |
| `lib:Book`                   | Um livro na biblioteca                                    |
| `lib:Novel`                  | Um livro de ficcao (subclasse de Book)                    |
| `lib:TextBook`               | Um livro academico (subclasse de Book)                    |
| `lib:ShortStoryCollection`   | Uma colecao de contos (subclasse de Book)                 |
| `lib:Person`                 | Uma pessoa envolvida com um livro                         |
| `lib:Author`                 | Uma pessoa que escreveu um livro (subclasse de Person)    |
| `lib:Editor`                 | uma pessoa que editou um livro (subclasse de Person)      |
| `lib:Genre`                  | Um genero literario                                       |
| `lib:Publisher`              | Uma empresa que publicou um livro                         |

### Taxonomia

```
lib:Resource  (raiz)
├── lib:Book
│   ├── lib:Novel
│   ├── lib:TextBook
│   └── lib:ShortStoryCollection
├── lib:Person
│   ├── lib:Author
│   └── lib:Editor
├── lib:Genre
└── lib:Publisher
```

### Propriedades

#### Propriedades de Objeto

| Propriedade           | Dominio     | Range           | Descricao                                  |
|-----------------------|-------------|------------------|--------------------------------------------|
| `lib:writtenBy`       | `lib:Book`  | `lib:Author`    | Liga um livro ao seu autor                 |
| `lib:editedBy`        | `lib:Book`  | `lib:Editor`    | Liga um livro ao seu editor                |
| `lib:belongsToGenre`  | `lib:Book`  | `lib:Genre`     | Liga um livro ao seu genero                |
| `lib:publishedBy`     | `lib:Book`  | `lib:Publisher` | Liga um livro a sua editora                |
| `lib:authorOf`        | `lib:Author`| `lib:Book`      | Inversa de writtenBy                       |
| `lib:relatedTo`       | `lib:Book`  | `lib:Book`      | Relacao transitiva e simetrica entre livros|

#### Propriedades de Dados

| Propriedade            | Dominio       | Range           | Descricao                           |
|------------------------|---------------|-----------------|-------------------------------------|
| `lib:title`            | `lib:Book`   | `xsd:string`    | Titulo do livro                     |
| `lib:name`             | `lib:Person` | `xsd:string`    | Nome completo da pessoa             |
| `lib:publishedYear`    | `lib:Book`   | `xsd:integer`   | Ano de publicacao do livro          |
| `lib:isbn`             | `lib:Book`   | `xsd:string`    | Numero ISBN do livro                |
| `lib:numberOfPages`    | `lib:Book`   | `xsd:integer`   | Numero de paginas do livro          |
| `lib:nationality`      | `lib:Person` | `xsd:string`    | Nacionalidade da pessoa             |
| `lib:publisherCountry` | `lib:Publisher`| `xsd:string`  | Pais da sede da editora             |

### Construcoes OWL

| Construcao                  | Propriedade / Classe         | Justificativa                                                           |
|-----------------------------|------------------------------|-------------------------------------------------------------------------|
| `owl:inverseOf`             | `lib:authorOf`               | Se um livro e escrito por um autor, o autor e autor do livro            |
| `owl:TransitiveProperty`    | `lib:relatedTo`              | Se A esta relacionado com B e B com C, entao A esta relacionado com C  |
| `owl:SymmetricProperty`     | `lib:relatedTo`              | Se A esta relacionado com B, entao B esta relacionado com A            |
| `owl:FunctionalProperty`    | `lib:isbn`                   | Cada livro possui exatamente um ISBN                                    |
| `owl:disjointWith`          | `lib:Author` / `lib:Publisher`| Um autor nao pode ser uma editora ao mesmo tempo                       |

---

## Dados Instanciados

### Livros

| Livro                       | Tipo                  | Autor                | Genero      | Ano   |
|-----------------------------|-----------------------|----------------------|-------------|-------|
| 1984                        | Novel                 | George Orwell        | Ficcao      | 1949  |
| Don Quixote                 | Novel                 | Miguel de Cervantes  | Ficcao      | 1605  |
| Ficciones                   | Novel                 | Jorge Luis Borges    | Ficcao      | 1944  |
| The Lord of the Rings       | Novel                 | J.R.R. Tolkien       | Ficcao      | 1954  |
| Animal Farm                 | Novel                 | George Orwell        | Ficcao      | 1945  |
| The Neverending Story       | Novel                 | George Orwell        | Ficcao      | 1979  |
| Brave New World             | Novel                 | Stephen Hawking      | Ficcao      | 1932  |
| Fahrenheit 451              | Novel                 | J.R.R. Tolkien       | Ficcao      | 1953  |
| Memorias Postumas de Bras Cubas | Novel            | Machado de Assis     | Ficcao      | 1881  |
| Le Petit Prince             | Novel                 | Antoine de Saint-Exupéry | Ficcao  | 1943  |
| Clean Code                  | TextBook              | Robert C. Martin     | Tecnologia  | 2008  |
| The Pragmatic Programmer    | TextBook              | Robert C. Martin     | Tecnologia  | 1999  |
| Labyrinths                  | ShortStoryCollection  | Jorge Luis Borges    | Filosofia   | 1962  |
| A Brief History of Time     | ShortStoryCollection  | Stephen Hawking      | Ciencia     | 1988  |

### Autores

| Autor                      | Nacionalidade |
|----------------------------|---------------|
| George Orwell              | Britanico     |
| Miguel de Cervantes        | Espanhol      |
| Stephen Hawking            | Britanico     |
| Robert C. Martin           | Americano     |
| Jorge Luis Borges          | Argentino     |
| J.R.R. Tolkien             | Britanico     |
| Machado de Assis           | Brasileiro    |
| Antoine de Saint-Exupéry   | Frances       |

### Editoras

| Editora              | Pais           |
|----------------------|----------------|
| Penguin Books        | Reino Unido    |
| O'Reilly Media       | Estados Unidos |
| Planeta              | Espanha        |
| Companhia das Letras | Brasil         |
| Gallimard            | Franca         |

---

## Consultas

### Parte 1 — g.triples()

| # | Padrao                          | Objetivo                                        |
|---|---------------------------------|--------------------------------------------------|
| 1 | Sujeito fixo                    | Todos os triples sobre um livro especifico       |
| 2 | Predicado fixo                  | Todos os livros e seus autores (writtenBy)       |
| 3 | Objeto fixo                     | Todos os livros no genero Ficcao                 |
| 4 | Predicado + Objeto fixos        | Todos os individuos do tipo Author (RDF.type)    |
| 5 | Sujeito + Predicado fixos       | Titulo de um livro especifico                    |

### Parte 2 — SPARQL

| # | Tipo                           | Objetivo                                        |
|---|--------------------------------|--------------------------------------------------|
| 1 | SELECT + ORDER BY              | Todos os livros com titulo e nome do autor       |
| 2 | SELECT + FILTER                | Livros publicados depois de 1990                 |
| 3 | SELECT + agregacao             | Contagem de livros por autor                     |
| 4 | SELECT + FILTER NOT EXISTS     | Livros sem editora                               |
| 5 | ASK                            | Verificar se um autor especifico existe          |
| 6 | CONSTRUCT                      | Construir subgrafo de autores e seus livros      |
| 7 | UPDATE INSERT                  | Adicionar um novo livro                          |
| 8 | UPDATE DELETE                  | Remover um triple especifico                     |
| 9 | UPDATE DELETE/INSERT           | Atualizar o ano de publicacao de um livro        |

---

## Visualizacao

O projeto inclui um script de visualizacao interativa usando a biblioteca **pyvis**. O grafo e renderizado como um arquivo HTML interativo que pode ser aberto em qualquer navegador.

### Cores por Tipo de Entidade

| Cor       | Tipo        |
|-----------|-------------|
| Azul      | Livro       |
| Vermelho  | Autor       |
| Laranja   | Editora     |
| Verde     | Genero      |
| Rosa      | Editor      |

### Como executar

```bash
python src/visualize.py
```

O arquivo gerado sera salvo em `output/grafo_biblioteca.html`.

### Funcionalidades interativas

- **Arrastar nos**: mova qualquer entidade para reposicionar
- **Zoom**: use a roda do mouse para ampliar/reduzir
- **Hover**: passe o mouse sobre um no para ver detalhes (titulo, autor, ISBN, etc.)
- **Click**: clique e arraste o fundo para mover toda a visualizacao

---

## Pre-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes)

## Instalacao e Execucao

1. **Clone o repositorio:**

```bash
git clone https://github.com/pedropaiva186/library_knowledge_graph.git
cd library_knowledge_graph
```

2. **Crie um ambiente virtual (recomendado):**

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

3. **Instale as dependencias:**

```bash
pip install -r requirements.txt
```

4. **Execute o script principal:**

```bash
python src/main.py
```

5. **Gere a visualizacao interativa do grafo:**

```bash
python src/visualize.py
```

O arquivo HTML sera salvo em `output/grafo_biblioteca.html`. Abra no navegador para interagir com o grafo (arrastar, zoom, hover para detalhes).

---

## Tecnologias Utilizadas

| Tecnologia      | Versao  | Descricao                                    |
|-----------------|---------|----------------------------------------------|
| Python          | 3.x     | Linguagem de programacao principal           |
| rdflib          | >=7.0.0 | Manipulacao de grafos RDF e consultas SPARQL |
| owlrl           | >=7.0.0 | Raciocinio OWL/RDFS                          |
| pyvis           | >=0.3.0 | Visualizacao interativa de grafos em HTML    |
| Turtle          | -       | Formato de serializacao RDF                  |
| SPARQL          | 1.1     | Linguagem de consultas RDF                   |

---

## Autor

**Pedro Henrique Paiva Souza**

- GitHub: [pedropaiva186](https://github.com/pedropaiva186)
- Repositorio: [library_knowledge_graph](https://github.com/pedropaiva186/library_knowledge_graph)

---

## Licenca

Este projeto esta licenciado sob a licenca MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
