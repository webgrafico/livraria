#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um catálogo OPDS (catalog.xml) automaticamente a partir dos arquivos .epub
armazenados dentro da pasta "Ebooks". Compatível com KOReader e GitHub Pages.

Estrutura esperada:
Ebooks/
 ├── Autor 1/
 │    └── Título do Livro/
 │         ├── cover.jpg
 │         ├── metadata.opf
 │         └── Livro - Autor.epub
 ├── Autor 2/
 │    └── Outro Livro/
 │         └── Outro Livro - Autor.epub
 └── ...

Autor: Hugo (adaptado por GPT-5)
Data: 2025-10-27
"""

import os
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote

# URL base do seu repositório GitHub Pages
BASE_URL = "https://webgrafico.github.io/livraria"
# Caminho local onde estão os ebooks
EBOOKS_DIR = "Ebooks"
# Nome do arquivo de saída (gerado na raiz do projeto)
OUTPUT_FILE = "catalog.xml"

# Criação do feed OPDS principal
feed = ET.Element(
    "feed",
    xmlns="http://www.w3.org/2005/Atom",
    attrib={"xmlns:opds": "http://opds-spec.org/2010/catalog"},
)

ET.SubElement(feed, "id").text = BASE_URL
ET.SubElement(feed, "title").text = "Catálogo de Livros - Livraria"
ET.SubElement(feed, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# Percorre todos os diretórios e subdiretórios em busca de arquivos .epub
for root, dirs, files in os.walk(EBOOKS_DIR):
    for file in files:
        if file.endswith(".epub"):
            # Extrai nome do autor (diretório pai)
            author = os.path.basename(os.path.dirname(root))
            # Extrai o título (nome do arquivo sem extensão)
            title = os.path.splitext(file)[0]

            # Caminho relativo e codificação para URL segura
            relative_path = os.path.join(root, file).replace("\\", "/")
            encoded_path = quote(relative_path)
            file_url = f"{BASE_URL}/{encoded_path}"

            # Cria a entrada no catálogo
            entry = ET.SubElement(feed, "entry")
            ET.SubElement(entry, "title").text = title
            ET.SubElement(entry, "author").text = author
            ET.SubElement(entry, "id").text = file_url
            ET.SubElement(entry, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            # Link para download do arquivo
            ET.SubElement(
                entry,
                "link",
                rel="http://opds-spec.org/acquisition",
                href=file_url,
                type="application/epub+zip",
            )

# Gera o arquivo XML final
tree = ET.ElementTree(feed)
tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

print(f"✅ Catálogo OPDS gerado com sucesso: {OUTPUT_FILE}")
print(f"📚 Base URL: {BASE_URL}")
