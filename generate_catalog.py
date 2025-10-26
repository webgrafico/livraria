import os
import datetime
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EBOOKS_DIR = os.path.join(BASE_DIR, "Ebooks")

IGNORAR = {".calnotes", ".caltrash", "metadata.db", "metadata_db_prefs_backup.json"}

# ======================
# 1️⃣ GERAR catalog.xml
# ======================

feed = ET.Element("feed", {
    "xmlns": "http://www.w3.org/2005/Atom",
    "xmlns:opds": "http://opds-spec.org/2010/catalog"
})

ET.SubElement(feed, "id").text = "https://webgrafico.github.io/livraria"
ET.SubElement(feed, "title").text = "Catálogo de Livros - Livraria"
ET.SubElement(feed, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

catalog_data = []

for author_dir in sorted(os.listdir(EBOOKS_DIR)):
    if author_dir in IGNORAR:
        continue
    author_path = os.path.join(EBOOKS_DIR, author_dir)
    if not os.path.isdir(author_path):
        continue

    books = []
    for root, _, files in os.walk(author_path):
        epub_files = [f for f in files if f.lower().endswith(".epub")]
        for epub in epub_files:
            rel_path = os.path.relpath(os.path.join(root, epub), BASE_DIR).replace("\\", "/")
            file_url = f"https://webgrafico.github.io/livraria/{rel_path}"
            cover_path = os.path.join(root, "cover.jpg")
            cover_url = None
            if os.path.exists(cover_path):
                rel_cover = os.path.relpath(cover_path, BASE_DIR).replace("\\", "/")
                cover_url = f"https://webgrafico.github.io/livraria/{rel_cover}"

            book_title = os.path.splitext(epub)[0]
            books.append({
                "title": book_title,
                "url": file_url,
                "cover": cover_url
            })

            entry = ET.SubElement(feed, "entry")
            ET.SubElement(entry, "title").text = book_title
            ET.SubElement(entry, "author").text = author_dir
            ET.SubElement(entry, "id").text = file_url
            ET.SubElement(entry, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            ET.SubElement(entry, "link", {
                "rel": "http://opds-spec.org/acquisition",
                "href": file_url,
                "type": "application/epub+zip"
            })

    if books:
        catalog_data.append({"author": author_dir, "books": books})

xml_output = os.path.join(BASE_DIR, "catalog.xml")
ET.ElementTree(feed).write(xml_output, encoding="utf-8", xml_declaration=True)
print(f"✅ Catálogo OPDS gerado: {xml_output}")

# ======================
# 2️⃣ GERAR index.html
# ======================

html_path = os.path.join(BASE_DIR, "index.html")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>📚 Catálogo de Livros - Livraria</title>
<style>
  body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; color: #333; }
  h1 { text-align: center; }
  .author { margin-top: 40px; }
  .books { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; }
  .book { background: white; border-radius: 8px; padding: 10px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
  .book img { width: 100%; border-radius: 6px; max-height: 220px; object-fit: cover; }
  .book-title { font-size: 14px; margin-top: 6px; }
  .book a { text-decoration: none; color: #0070f3; }
  footer { margin-top: 50px; text-align: center; font-size: 14px; color: #666; }
</style>
</head>
<body>
<h1>📚 Catálogo de Livros - Livraria</h1>
<p style="text-align:center;">Navegue pelos autores abaixo e clique para baixar os livros.</p>
"""

for author in catalog_data:
    html_content += f"<div class='author'><h2>{author['author']}</h2><div class='books'>"
    for book in author["books"]:
        html_content += "<div class='book'>"
        if book["cover"]:
            html_content += f"<a href='{book['url']}'><img src='{book['cover']}' alt='Capa'></a>"
        else:
            html_content += f"<a href='{book['url']}'><div style='height:220px;display:flex;align-items:center;justify-content:center;background:#eee;border-radius:6px;'>Sem capa</div></a>"
        html_content += f"<div class='book-title'><a href='{book['url']}'>{book['title']}</a></div></div>"
    html_content += "</div></div>"

html_content += f"""
<footer>
  <p>Gerado automaticamente em {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
  <p><a href="catalog.xml">📄 Versão OPDS (XML)</a></p>
</footer>
</body></html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Página HTML gerada: {html_path}")
print("🚀 Tudo pronto! Faça commit e push para o GitHub Pages.")
