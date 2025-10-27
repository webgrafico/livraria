import os
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote
from PIL import Image
from zipfile import ZipFile

# Configurações principais
BASE_URL = "https://webgrafico.github.io/livraria"
EBOOKS_DIR = "Ebooks"
OUTPUT_MAIN = "catalog.xml"

# Função para gerar miniatura da capa dentro da pasta do livro
def gerar_capa(livro_path):
    try:
        with ZipFile(livro_path, "r") as zf:
            cover_name = None
            for name in zf.namelist():
                if "cover" in name.lower() and name.lower().endswith((".jpg", ".jpeg", ".png")):
                    cover_name = name
                    break
            if not cover_name:
                return None

            with zf.open(cover_name) as cover_file:
                img = Image.open(cover_file)
                img.thumbnail((300, 300))
                pasta_livro = os.path.dirname(livro_path)
                output_cover = os.path.join(pasta_livro, "cover_300.jpg")
                img.save(output_cover, "JPEG")
                return output_cover
    except Exception as e:
        print(f"Erro ao gerar capa para {livro_path}: {e}")
        return None


# Função para criar XML OPDS
def criar_catalogo():
    feed = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom", attrib={"xmlns:opds": "http://opds-spec.org/2010/catalog"})
    ET.SubElement(feed, "id").text = BASE_URL
    ET.SubElement(feed, "title").text = "Catálogo de Livros - Livraria"
    ET.SubElement(feed, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for autor in os.listdir(EBOOKS_DIR):
        autor_path = os.path.join(EBOOKS_DIR, autor)
        if not os.path.isdir(autor_path):
            continue
        if autor in [".caltrash", ".calnotes"]:
            continue

        # Catálogo individual do autor
        autor_feed = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom", attrib={"xmlns:opds": "http://opds-spec.org/2010/catalog"})
        ET.SubElement(autor_feed, "id").text = f"{BASE_URL}/{quote(autor_path)}"
        ET.SubElement(autor_feed, "title").text = f"Livros de {autor}"
        ET.SubElement(autor_feed, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        for root, _, files in os.walk(autor_path):
            for file in files:
                if not file.endswith(".epub"):
                    continue
                if file in ["metadata.db", "metadata_db_prefs_backup.json"]:
                    continue

                title = os.path.splitext(file)[0]
                full_path = os.path.join(root, file)
                relative_path = full_path.replace("\\", "/")
                encoded_path = quote(relative_path)
                file_url = f"{BASE_URL}/{encoded_path}"

                # Gera capa (cover_300.jpg)
                cover_path = os.path.join(root, "cover_300.jpg")
                if not os.path.exists(cover_path):
                    gerar_capa(full_path)

                cover_url = None
                if os.path.exists(cover_path):
                    relative_cover = cover_path.replace("\\", "/")
                    encoded_cover = quote(relative_cover)
                    cover_url = f"{BASE_URL}/{encoded_cover}"

                # Entry principal
                entry = ET.SubElement(autor_feed, "entry")
                ET.SubElement(entry, "title").text = title
                ET.SubElement(entry, "author").text = autor
                ET.SubElement(entry, "id").text = file_url
                ET.SubElement(entry, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

                if cover_url:
                    ET.SubElement(entry, "link", rel="http://opds-spec.org/image", href=cover_url, type="image/jpeg")

                ET.SubElement(entry, "link", rel="http://opds-spec.org/acquisition", href=file_url, type="application/epub+zip")

                # Também adiciona esse autor ao catálogo principal
                main_entry = ET.SubElement(feed, "entry")
                ET.SubElement(main_entry, "title").text = f"{title} - {autor}"
                ET.SubElement(main_entry, "id").text = file_url
                ET.SubElement(main_entry, "updated").text = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                ET.SubElement(main_entry, "link", rel="subsection", href=f"{BASE_URL}/{quote(autor_path)}/catalog.xml")

        # Salva catálogo individual do autor dentro da própria pasta
        autor_catalog_path = os.path.join(autor_path, "catalog.xml")
        ET.ElementTree(autor_feed).write(autor_catalog_path, encoding="utf-8", xml_declaration=True)

    # Salva catálogo principal
    ET.ElementTree(feed).write(OUTPUT_MAIN, encoding="utf-8", xml_declaration=True)
    print(f"\n✅ Catálogo principal gerado: {OUTPUT_MAIN}")


if __name__ == "__main__":
    criar_catalogo()
