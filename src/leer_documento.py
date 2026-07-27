from pathlib import Path
from pypdf import PdfReader


def leer_pdf(ruta_archivo: Path) -> str:
    """
    Lee un archivo PDF y devuelve todo su contenido como texto.
    """
    lector = PdfReader(ruta_archivo)
    texto_completo = ""

    for pagina in lector.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto_completo += texto_pagina + "\n"

    return texto_completo


def cargar_documentos(carpeta: str = "docs") -> dict[str, str]:
    """
    Lee todos los PDFs de una carpeta y devuelve un diccionario
    {nombre_archivo: contenido_texto}.
    """
    carpeta_docs = Path(carpeta)
    documentos = {}

    for archivo_pdf in carpeta_docs.glob("*.pdf"):
        print(f"Leyendo {archivo_pdf.name}...")
        documentos[archivo_pdf.name] = leer_pdf(archivo_pdf)

    return documentos


if __name__ == "__main__":
    documentos = cargar_documentos()

    print(f"\nSe cargaron {len(documentos)} documentos:\n")
    for nombre, contenido in documentos.items():
        print(f"- {nombre}: {len(contenido)} caracteres")