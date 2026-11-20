import streamlit as st

from frontend.api_client import (
    create_actividad,
    create_recurso,
    delete_actividad,
    delete_recurso,
    get_actividades,
    get_emociones,
    get_recursos,
)
from frontend.state import get_role, is_authenticated


def _extract_list(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "recursos", "actividades", "emociones"):
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


def _es_gestor() -> bool:
    return is_authenticated() and (get_role() or "").lower() in ("admin", "orientador")


def render_recursos() -> None:
    st.header("Recursos Educativos y Actividades")
    st.caption("Materiales de apoyo psicoeducativo y ejercicios interactivos de bienestar.")

    ok_emo, data_emo, _ = get_emociones()
    emociones = _extract_list(data_emo) if ok_emo else []
    emociones_por_id = {
        e["Id_emocion"]: e["Nombre"]
        for e in emociones
        if isinstance(e, dict) and "Id_emocion" in e
    }

    tab_rec, tab_act = st.tabs(["📚 Recursos educativos", "🎯 Actividades interactivas"])

    with tab_rec:
        if _es_gestor():
            with st.expander("➕ Publicar nuevo recurso educativo"):
                with st.form("form_recurso", clear_on_submit=True):
                    titulo = st.text_input("Título")
                    categoria = st.selectbox(
                        "Categoría",
                        ["Salud Mental", "Manejo del Estrés", "Autocuidado", "Emociones", "Hábitos de Estudio"],
                    )
                    tiempo_lectura = st.number_input("Tiempo de lectura (minutos)", min_value=1, max_value=120, value=5)
                    contenido_md = st.text_area(
                        "Contenido (soporta Markdown)",
                        placeholder="Escribe el artículo o guía educativa...",
                    )
                    enviado = st.form_submit_button("Publicar recurso", type="primary")

                if enviado:
                    if not titulo.strip() or not contenido_md.strip():
                        st.warning("El título y el contenido son obligatorios.")
                    else:
                        payload = {
                            "Titulo": titulo.strip(),
                            "Categoria": categoria,
                            "Contenido_markdown": contenido_md.strip(),
                            "Tiempo_lectura": int(tiempo_lectura),
                        }
                        ok_c, _, msg_c = create_recurso(payload)
                        if ok_c:
                            st.success("Recurso publicado correctamente.")
                            st.rerun()
                        else:
                            st.error(f"No se pudo publicar el recurso: {msg_c}")

        ok_r, data_r, msg_r = get_recursos()
        if not ok_r:
            st.error(f"No se pudieron cargar los recursos: {msg_r}")
        else:
            recursos = _extract_list(data_r)
            if not recursos:
                st.info("Aún no hay recursos educativos publicados.")
            else:
                cols = st.columns(2)
                for idx, rec in enumerate(recursos):
                    if not isinstance(rec, dict):
                        continue
                    rec_id = rec.get("Id_recurso") or rec.get("id")
                    titulo = _pick(rec, ("Titulo", "Nombre"), "Recurso educativo")
                    categoria = _pick(rec, ("Categoria", "Tipo"))
                    contenido = _pick(rec, ("Contenido_markdown", "Contenido", "Descripcion"))
                    tiempo = _pick(rec, ("Tiempo_lectura", "Duracion"))

                    with cols[idx % 2]:
                        with st.container(border=True):
                            st.subheader(titulo)
                            meta = []
                            if categoria:
                                meta.append(f"🏷️ {categoria}")
                            if tiempo:
                                meta.append(f"⏱️ {tiempo} min de lectura")
                            if meta:
                                st.caption(" · ".join(meta))
                            if contenido:
                                st.markdown(contenido)
                            if _es_gestor() and rec_id is not None:
                                if st.button(
                                    "🗑️ Eliminar recurso",
                                    key=f"del_rec_{rec_id}_{idx}",
                                    use_container_width=True,
                                ):
                                    ok_d, _, msg_d = delete_recurso(int(rec_id))
                                    if ok_d:
                                        st.success("Recurso eliminado.")
                                        st.rerun()
                                    else:
                                        st.error(msg_d)

    with tab_act:
        if _es_gestor():
            with st.expander("➕ Crear nueva actividad interactiva"):
                with st.form("form_actividad", clear_on_submit=True):
                    act_titulo = st.text_input("Título de la actividad")
                    act_tipo = st.selectbox(
                        "Tipo de actividad",
                        ["Respiración", "Reflexión", "Mindfulness", "Relajación", "Autoevaluación"],
                    )
                    act_duracion = st.number_input("Duración estimada (minutos)", min_value=1, max_value=120, value=5)
                    if emociones_por_id:
                        act_id_emocion = st.selectbox(
                            "Emoción asociada",
                            options=list(emociones_por_id.keys()),
                            format_func=lambda eid: emociones_por_id[eid],
                        )
                    else:
                        act_id_emocion = st.number_input("ID de emoción asociada", min_value=1, value=1)
                    act_instrucciones = st.text_area("Instrucciones paso a paso")
                    act_env = st.form_submit_button("Guardar actividad", type="primary")

                if act_env:
                    if not act_titulo.strip() or not act_instrucciones.strip():
                        st.warning("El título y las instrucciones son obligatorios.")
                    else:
                        payload = {
                            "Titulo": act_titulo.strip(),
                            "Tipo_actividad": act_tipo,
                            "Instrucciones": act_instrucciones.strip(),
                            "Duracion_estimada": int(act_duracion),
                            "Id_emocion": int(act_id_emocion),
                        }
                        ok_ca, _, msg_ca = create_actividad(payload)
                        if ok_ca:
                            st.success("Actividad creada correctamente.")
                            st.rerun()
                        else:
                            st.error(f"No se pudo crear la actividad: {msg_ca}")

        ok_a, data_a, msg_a = get_actividades()
        if not ok_a:
            st.error(f"No se pudieron cargar las actividades: {msg_a}")
        else:
            actividades = _extract_list(data_a)
            if not actividades:
                st.info("Aún no hay actividades interactivas registradas.")
            else:
                cols = st.columns(2)
                for idx, act in enumerate(actividades):
                    if not isinstance(act, dict):
                        continue
                    act_id = act.get("Id_actividad") or act.get("id")
                    titulo = _pick(act, ("Titulo", "Nombre"), "Actividad interactiva")
                    tipo = _pick(act, ("Tipo_actividad", "Tipo"))
                    instrucciones = _pick(act, ("Instrucciones", "Descripcion"))
                    duracion = _pick(act, ("Duracion_estimada", "Duracion"))
                    emo_id = act.get("Id_emocion")
                    emo_nombre = emociones_por_id.get(emo_id)

                    with cols[idx % 2]:
                        with st.container(border=True):
                            st.subheader(f"🎯 {titulo}")
                            meta = []
                            if tipo:
                                meta.append(f"🏷️ {tipo}")
                            if duracion:
                                meta.append(f"⏱️ {duracion} min")
                            if emo_nombre:
                                meta.append(f"💭 {emo_nombre}")
                            if meta:
                                st.caption(" · ".join(meta))
                            if instrucciones:
                                st.write(instrucciones)
                            if _es_gestor() and act_id is not None:
                                if st.button(
                                    "🗑️ Eliminar actividad",
                                    key=f"del_act_{act_id}_{idx}",
                                    use_container_width=True,
                                ):
                                    ok_da, _, msg_da = delete_actividad(int(act_id))
                                    if ok_da:
                                        st.success("Actividad eliminada.")
                                        st.rerun()
                                    else:
                                        st.error(msg_da)