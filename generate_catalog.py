import os
import xml.etree.ElementTree as ET
from urllib.parse import quote

# === CONFIGURAÇÕES ===
BASE_URL = "https://webgrafico.github.io/livraria/Ebooks"  # domínio do GitHub Pages
ROOT_FOLDER = "Ebooks"  # onde ficam os livros
OUTPUT_FILE = "catalog.xml"
IGNORED_FOLDERS = {".calnotes", ".caltrash"}
IGNORED_FILES = {"metadata.db", "metadata_db_prefs_backup.json"}

# === CRIAÇÃO DO CATÁLOGO OPDS ===
feed = ET.Element(
    "feed",
    {
        "xmlns": "http://www.w3.org/2005/Atom",
        "xmlns:opds": "http://opds-spec.org/2010/catalog",
    },
)
ET.SubElement(feed, "id").text = BASE_URL
ET.SubElement(feed, "title").text = "Catálogo de Livros - Livraria"
ET.SubElement(feed, "updated").text = "2025-10-26T00:00:00Z"

# === Função para criar entrada de autor ===
def criar_entrada_autor(nome_autor):
    entry = ET.Element("entry")
    ET.SubElement(entry, "title").text = nome_autor
    ET.SubElement(entry, "id").text = f"{BASE_URL}/{quote(nome_autor)}"
    ET.SubElement(entry, "updated").text = "2025-10-26T00:00:00Z"

    ET.SubElement(
        entry,
        "link",
        {
            "rel": "subsection",
            "href": f"{BASE_URL}/{quote(nome_autor)}/index.xml",
            "type": "application/atom+xml;profile=opds-catalog",
        },
    )
    return entry

# === Função para criar o catálogo de cada autor ===
def criar_catalogo_autor(nome_autor, livros):
    feed_autor = ET.Element(
        "feed",
        {
            "xmlns": "http://www.w3.org/2005/Atom",
            "xmlns:opds": "http://opds-spec.org/2010/catalog",
        },
    )
    ET.SubElement(feed_autor, "id").text = f"{BASE_URL}/{quote(nome_autor)}"
    ET.SubElement(feed_autor, "title").text = nome_autor
    ET.SubElement(feed_autor, "updated").text = "2025-10-26T00:00:00Z"

    for livro in livros:
        entry = ET.SubElement(feed_autor, "entry")
        ET.SubElement(entry, "title").text = os.path.splitext(livro)[0]
        ET.SubElement(entry, "id").text = f"{BASE_URL}/{quote(nome_autor)}/{quote(livro)}"
        ET.SubElement(entry, "updated").text = "2025-10-26T00:00:00Z"
        ET.SubElement(
            entry,
            "link",
            {
                "rel": "http://opds-spec.org/acquisition/open-access",
                "href": f"{BASE_URL}/{quote(nome_autor)}/{quote(livro)}",
                "type": "application/epub+zip",
            },
        )

    output_path = os.path.join(ROOT_FOLDER, nome_autor, "index.xml")
    ET.ElementTree(feed_autor).write(output_path, encoding="utf-8", xml_declaration=True)

# === Geração automática do catálogo principal ===
for autor in sorted(os.listdir(ROOT_FOLDER)):
    autor_path = os.path.join(ROOT_FOLDER, autor)

    if not os.path.isdir(autor_path) or autor in IGNORED_FOLDERS:
        continue

    livros = [
        f for f in os.listdir(autor_path)
        if f.lower().endswith(".epub") and f not in IGNORED_FILES
    ]

    if not livros:
        continue

    feed.append(criar_entrada_autor(autor))
    criar_catalogo_autor(autor, livros)
    print(f"Autor encontrado: {autor} ({len(livros)} livros)")

# === Salva o catálogo principal ===
ET.ElementTree(feed).write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

print(f"\n✅ Catálogo OPDS gerado com sucesso: {OUTPUT_FILE}")
print("Agora faça commit e push para o GitHub Pages:")
print("git add . && git commit -m 'update catalog.xml' && git push")
print(f"Feed disponível em: {BASE_URL.replace('/Ebooks','')}/{OUTPUT_FILE}")
