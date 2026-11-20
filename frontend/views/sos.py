import streamlit as st

from frontend.api_client import get_emergencias


def _pick(item: dict, candidates: tuple[str, ...], default: str = "") -> str:
    lowered = {k.lower(): v for k, v in item.items()}
    for key in candidates:
        val = lowered.get(key.lower())
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return default


def render_sos() -> None:
    st.error("🆘 Si estás en una situación de riesgo inmediato, comunícate de inmediato con una de estas líneas de atención.")
    st.header("Red de Apoyo y Líneas de Emergencia")
    st.caption("Acceso público inmediato — no requiere iniciar sesión.")

    if st.button("🔄 Actualizar líneas de apoyo"):
        st.rerun()

    with st.spinner("Cargando líneas de emergencia..."):
        ok, data, msg = get_emergencias()

    if not ok:
        st.error(f"No fue posible consultar la red de apoyo: {msg}")
        return

    # Soporta tanto lista directa en data como objeto con lista interna
    lineas = data if isinstance(data, list) else (data.get("items") or data.get("lineas") or [] if isinstance(data, dict) else [])

    if not lineas:
        st.warning("No hay líneas de emergencia registradas en la base de datos.")
        return

    cols = st.columns(2)
    for idx, linea in enumerate(lineas):
        if not isinstance(linea, dict):
            continue

        nombre = _pick(linea, ("Nombre", "Nombre_entidad", "Entidad", "Titulo", "Institucion"), "Línea de apoyo")
        contacto = _pick(linea, ("Telefono", "Numero", "Linea", "Contacto", "Canal"), "Sin número registrado")
        descripcion = _pick(linea, ("Descripcion", "Detalle", "Servicios", "Tipo_apoyo"))
        horario = _pick(linea, ("Horario", "Disponibilidad", "Horario_atencion"))
        enlace = _pick(linea, ("Url", "Enlace", "Web", "Sitio_web"))

        with cols[idx % 2]:
            with st.container(border=True):
                st.subheader(f"📞 {nombre}")
                st.markdown(f"### `{contacto}`")
                if horario:
                    st.caption(f"🕒 Disponibilidad: {horario}")
                if descripcion:
                    st.write(descripcion)
                if enlace:
                    st.link_button("Abrir sitio de ayuda", enlace, use_container_width=True)