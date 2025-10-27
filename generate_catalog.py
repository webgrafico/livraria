#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um catálogo OPDS (catalog.xml) automaticamente a partir dos arquivos .epub
armazenados dentro da pasta "Ebooks", ignorando diretórios .caltrash.
"""

import os
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote

BASE_URL = "https://webgrafico.github.io/livraria"
EBOOKS_DIR = "Ebooks"
OUTPUT_FILE = "catalog.xml"

# Lista de padrões a ignorar
IGNORED = [".caltrash", ".calnotes", "metadata_db_prefs_backup.json", "metadata.db"]

feed = ET.Element(
    "feed",
    xmlns="http://www.w3.org/2005/Atom",
    attrib={"xmlns:opds": "http://opds-spec.org/2010/catalog"},
)

ET.SubElement(feed, "id").text = BASE_URL
ET.SubElement(feed, "title").text = "Catálogo de Livros - Livraria"
ET.SubElement(feed, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# Lista para armazenar todos os arquivos .epub encontrados
epub_files = []

for root, dirs, files in os.walk(EBOOKS_DIR):
    if any(ignored in root.lower() for ignored in IGNORED):
        continue

    for file in files:
        if any(file.lower() == ignored for ignored in IGNORED):
            continue
        if file.endswith(".epub"):
            full_path = os.path.join(root, file).replace("\\", "/")
            author = os.path.basename(os.path.dirname(root))
            title = os.path.splitext(file)[0]

            epub_files.append({
                "title": title,
                "author": author,
                "path": full_path
            })

# Ordena a lista pelo título do arquivo (alfabética)
epub_files.sort(key=lambda x: x["title"].lower())

# Cria as entradas no XML
for epub in epub_files:
    encoded_path = quote(epub["path"])
    file_url = f"{BASE_URL}/{encoded_path}"

    entry = ET.SubElement(feed, "entry")
    ET.SubElement(entry, "title").text = epub["title"]
    ET.SubElement(entry, "author").text = epub["author"]
    ET.SubElement(entry, "id").text = file_url
    ET.SubElement(entry, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    ET.SubElement(
        entry,
        "link",
        rel="http://opds-spec.org/acquisition",
        href=file_url,
        type="application/epub+zip",
    )

tree = ET.ElementTree(feed)
tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

print(f"✅ Catálogo OPDS gerado com sucesso: {OUTPUT_FILE}")
print(f"📚 Base URL: {BASE_URL}")
