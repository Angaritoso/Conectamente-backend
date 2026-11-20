import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from frontend.state import clear_session, get_role, get_user, init_session, is_authenticated
from frontend.views.auth import render_auth
from frontend.views.dashboard import render_dashboard
from frontend.views.emociones import render_emociones
from frontend.views.encuestas import render_encuestas
from frontend.views.recursos import render_recursos
from frontend.views.sos import render_sos

st.set_page_config(
    page_title="ConectaMente",
    page_icon="🧠",
    layout="wide",
)

init_session()
if "mostrar_sos" not in st.session_state:
    st.session_state.mostrar_sos = False


def _salir_sos() -> None:
    st.session_state.mostrar_sos = False


# --- Barra lateral global ---
with st.sidebar:
    st.title("🧠 ConectaMente")
    st.caption("Plataforma de bienestar emocional")

    if st.button("🆘 BOTÓN SOS - Ayuda Inmediata", type="primary", use_container_width=True):
        st.session_state.mostrar_sos = True

    st.divider()

    opciones = [
        "Inicio y Acceso",
        "Emociones y Diario",
        "Recursos y Actividades",
        "Encuestas y Feedback",
    ]
    if is_authenticated() and (get_role() or "").lower() in ("admin", "orientador"):
        opciones.append("Dashboard de Métricas")

    seleccion = st.radio(
        "Módulos",
        opciones,
        key="modulo_seleccionado",
        on_change=_salir_sos,
    )

    st.divider()

    if is_authenticated():
        user = get_user() or {}
        st.success(f"Conectado: {user.get('Name', 'Usuario')}")
        st.caption(f"Rol: `{user.get('Rol', '-')}`")
        if st.button("Cerrar sesión", key="sidebar_logout", use_container_width=True):
            clear_session()
            st.rerun()
    else:
        st.info("Navegando como invitado")

# --- Enrutador de vistas ---
if st.session_state.mostrar_sos:
    if st.button("← Volver a los módulos"):
        st.session_state.mostrar_sos = False
        st.rerun()
    render_sos()
elif seleccion == "Inicio y Acceso":
    render_auth()
elif seleccion == "Emociones y Diario":
    render_emociones()
elif seleccion == "Recursos y Actividades":
    render_recursos()
elif seleccion == "Encuestas y Feedback":
    render_encuestas()
elif seleccion == "Dashboard de Métricas":
    render_dashboard()