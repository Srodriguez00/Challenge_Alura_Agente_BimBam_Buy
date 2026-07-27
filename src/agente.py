import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from leer_documento import cargar_documentos

# 1. Cargar la API key desde el archivo .env
load_dotenv()
api_key = os.getenv("COHERE_API_KEY")

if not api_key:
    raise ValueError("No se encontró COHERE_API_KEY. Revisa tu archivo .env")


def construir_agente():
    # 2. Leer los 5 PDFs de la carpeta docs/
    documentos = cargar_documentos("docs")

    # 3. Dividir cada documento en fragmentos pequeños (chunks)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    textos = []
    metadatos = []

    for nombre_archivo, contenido in documentos.items():
        fragmentos = splitter.split_text(contenido)
        for fragmento in fragmentos:
            textos.append(fragmento)
            metadatos.append({"fuente": nombre_archivo})

    print(f"Documentos divididos en {len(textos)} fragmentos.")

    # 4. Crear los embeddings y guardarlos en la base vectorial (FAISS)
    embeddings = CohereEmbeddings(
        cohere_api_key=api_key,
        model="embed-multilingual-v3.0",
    )

    base_vectorial = FAISS.from_texts(textos, embeddings, metadatas=metadatos)

    # 5. Crear el modelo de lenguaje que generará las respuestas
    llm = ChatCohere(
        cohere_api_key=api_key,
        model="command-a-03-2025",
        temperature=0,
    )

    # 6. Definir el prompt que le dice al modelo cómo usar el contexto encontrado
    system_prompt = (
        "Eres un asistente que responde preguntas sobre la documentación "
        "interna de BimBam Buy. Usa únicamente el siguiente contexto para "
        "responder de forma clara y directa. Si no encuentras la respuesta "
        "en el contexto, di que no tienes esa información.\n\n"
        "Contexto:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 7. Armar la cadena: primero busca los fragmentos relevantes,
    #    luego se los pasa al modelo junto con la pregunta
    combinar_documentos = create_stuff_documents_chain(llm, prompt)
    agente = create_retrieval_chain(
        base_vectorial.as_retriever(search_kwargs={"k": 4}),
        combinar_documentos,
    )

    return agente


if __name__ == "__main__":
    agente = construir_agente()

    print("\n🤖 Agente listo. Escribe tu pregunta (o 'salir' para terminar)\n")

    while True:
        pregunta = input("Tu pregunta: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            break

        resultado = agente.invoke({"input": pregunta})

        print(f"\nRespuesta: {resultado['answer']}\n")

        fuentes_unicas = {doc.metadata['fuente'] for doc in resultado["context"]}
        print("Fuentes consultadas:")
        for fuente in fuentes_unicas:
            print(f"  - {fuente}")
        print()