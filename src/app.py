import streamlit as st
from agente import construir_agente

st.set_page_config(page_title="Agente BimBam Buy", page_icon="🤖")

st.title("🤖 Agente Inteligente - BimBam Buy")
st.write(
    "Pregúntame sobre políticas de reembolsos, envíos, métodos de pago, "
    "programa de afiliados o garantía de productos."
)

# Cargar el agente una sola vez y guardarlo en memoria de sesión
if "agente" not in st.session_state:
    with st.spinner("Cargando documentos y preparando el agente..."):
        st.session_state.agente = construir_agente()

# Inicializar historial de conversación
if "historial" not in st.session_state:
    st.session_state.historial = []

# Mostrar historial previo
for pregunta, respuesta, fuentes in st.session_state.historial:
    with st.chat_message("user"):
        st.write(pregunta)
    with st.chat_message("assistant"):
        st.write(respuesta)
        st.caption(f"📄 Fuentes: {', '.join(fuentes)}")

# Entrada de nueva pregunta
pregunta = st.chat_input("Escribe tu pregunta aquí...")

if pregunta:
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando la respuesta..."):
            resultado = st.session_state.agente.invoke({"input": pregunta})
            respuesta = resultado["answer"]
            fuentes = list({doc.metadata["fuente"] for doc in resultado["context"]})

        st.write(respuesta)
        st.caption(f"📄 Fuentes: {', '.join(fuentes)}")

    st.session_state.historial.append((pregunta, respuesta, fuentes))