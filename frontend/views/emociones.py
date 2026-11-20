import streamlit as st

from frontend.api_client import create_diario, delete_diario, get_diario, get_emociones
from frontend.state import is_authenticated

EMOCION_ICONOS = {
    "alegría": "😊",
    "tristeza": "😢",
    "miedo": "😨",
    "enojo": "😠",
    "frustración": "😤",
    "preocupación": "😟",
}


def _extract_list(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "emociones", "registros", "entradas", "diario"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def _pick(item: dict, candidates: tuple[str, ...], default: str = "") -> str:
    lowered = {k.lower(): v for k, v in item.items()}
    for key in candidates:
        val = lowered.get(key.lower())
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return default


def render_emociones() -> None:
    st.header("Emociones y Diario Emocional")
    st.caption("Explora estrategias de afrontamiento y lleva un registro privado de cómo te sientes.")

    with st.spinner("Cargando catálogo de emociones..."):
        ok_emo, data_emo, msg_emo = get_emociones()

    emociones = _extract_list(data_emo) if ok_emo else []
    emociones_por_id = {
        e["Id_emocion"]: e["Nombre"]
        for e in emociones
        if isinstance(e, dict) and "Id_emocion" in e
    }

    tab_catalogo, tab_diario = st.tabs(["Catálogo de emociones", "Mi diario privado"])

    with tab_catalogo:
        if not ok_emo:
            st.error(f"No se pudo cargar el catálogo de emociones: {msg_emo}")
        elif not emociones:
            st.warning("No hay emociones registradas.")
        else:
            cols = st.columns(2)
            for idx, emo in enumerate(emociones):
                nombre = emo.get("Nombre", "Emoción")
                icono = EMOCION_ICONOS.get(nombre.lower(), "💭")
                with cols[idx % 2]:
                    with st.container(border=True):
                        st.subheader(f"{icono} {nombre}")
                        st.write(emo.get("Descripcion", ""))
                        with st.expander("Ver estrategias de afrontamiento"):
                            st.info(emo.get("Estrategias_afrontamiento", "Sin estrategias registradas."))

    with tab_diario:
        if not is_authenticated():
            st.info("Inicia sesión en **Inicio y Acceso** para consultar y registrar entradas en tu diario privado.")
            return

        st.subheader("Registrar nueva entrada")
        if not emociones_por_id:
            st.warning("Se necesita cargar el catálogo de emociones para registrar una entrada.")
        else:
            with st.form("form_diario", clear_on_submit=True):
                id_emocion = st.selectbox(
                    "¿Cómo te sientes hoy?",
                    options=list(emociones_por_id.keys()),
                    format_func=lambda eid: f"{EMOCION_ICONOS.get(emociones_por_id[eid].lower(), '💭')} {emociones_por_id[eid]}",
                )
                nota_priv = st.text_area(
                    "Nota privada",
                    placeholder="Escribe qué ocurrió o cómo te sentiste hoy...",
                )
                submitted = st.form_submit_button("Guardar en mi diario", type="primary", use_container_width=True)

            if submitted:
                payload = {
                    "Id_emocion": int(id_emocion),
                    "Nota_priv": nota_priv.strip(),
                }
                ok_post, _, msg_post = create_diario(payload)
                if ok_post:
                    st.success("Entrada guardada en tu diario.")
                    st.rerun()
                else:
                    st.error(f"No se pudo guardar la entrada: {msg_post}")

        st.divider()
        st.subheader("Historial reciente")
        ok_d, data_d, msg_d = get_diario()
        if not ok_d:
            st.error(f"No se pudo consultar el diario: {msg_d}")
            return

        entradas = _extract_list(data_d)
        if not entradas:
            st.caption("Aún no tienes registros en tu diario emocional.")
            return

        for idx, entrada in enumerate(entradas):
            if not isinstance(entrada, dict):
                continue

            entry_id = entrada.get("Id_diario") or entrada.get("Id_registro") or entrada.get("id")
            id_emo_entry = entrada.get("Id_emocion")
            nombre_emo = emociones_por_id.get(
                id_emo_entry,
                _pick(entrada, ("Emocion", "Nombre_emocion"), f"Emoción #{id_emo_entry}"),
            )
            fecha = _pick(entrada, ("Fecha_registro", "Fecha_creacion", "Fecha", "Created_at"), "Sin fecha")
            nota_txt = _pick(entrada, ("Nota_priv", "Nota_personal", "Nota"), "Sin nota escrita.")

            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"{EMOCION_ICONOS.get(nombre_emo.lower(), '💭')} **{nombre_emo}**")
                    st.caption(f"🗓️ {fecha}")
                    st.write(nota_txt)
                with c2:
                    if entry_id is not None and st.button(
                        "🗑️ Eliminar",
                        key=f"del_diario_{entry_id}_{idx}",
                        use_container_width=True,
                    ):
                        ok_del, _, msg_del = delete_diario(int(entry_id))
                        if ok_del:
                            st.success("Registro eliminado.")
                            st.rerun()
                        else:
                            st.error(msg_del)