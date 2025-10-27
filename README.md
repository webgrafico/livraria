# Livraria

https://webgrafico.github.io/livraria/catalog.xml

Gera um catálogo OPDS (catalog.xml) automaticamente a partir dos arquivos .epub
armazenados dentro da pasta "Ebooks". Compatível com KOReader e GitHub Pages.

Estrutura esperada:

```
livraria/
├── gerar_catalogo.py
├── Ebooks/
│   ├── Allan Pease/
│   │   ├── livro1.epub
│   │   ├── livro2.epub
│   │   └── autor.xml   ← gerado automaticamente
│   ├── Dan Brown/
│   │   ├── Inferno.epub
│   │   └── Dan Brown.xml
│   └── ...
└── catalog.xml  ← catálogo principal
```