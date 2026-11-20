import streamlit as st

from frontend.api_client import (
    enviar_diagnostico,
    enviar_usabilidad,
    evaluar_bienestar,
    get_cuestionario_bienestar,
)


def _render_diagnostico() -> None:
    st.subheader("Encuesta Anónima de Diagnóstico")
    st.caption("Tus respuestas son 100% anónimas y ayudan a identificar necesidades prioritarias.")

    with st.form("form_diagnostico_anonimo", clear_on_submit=True):
        rango_edad = st.selectbox(
            "Rango de edad",
            ["12-15 años", "16-18 años", "19-25 años", "25+"],
        )
        necesidad = st.selectbox(
            "¿Cuál es tu necesidad principal actualmente?",
            [
                "Salud Mental y Bienestar",
                "Manejo del Estrés Académico",
                "Orientación Vocacional",
                "Habilidades Socioemocionales",
                "Apoyo Familiar o Social",
                "Otra",
            ],
        )
        detalles = st.text_area(
            "Detalles adicionales",
            placeholder="Cuéntanos brevemente cómo podría ayudarte la plataforma...",
        )
        submitted = st.form_submit_button("Enviar diagnóstico anónimo", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "Rango_edad": rango_edad,
            "Necesidad_principal": necesidad,
            "Detalles": detalles.strip() or None,
        }
        with st.spinner("Registrando respuesta anónima..."):
            ok, _, msg = enviar_diagnostico(payload)

        if ok:
            st.success("¡Gracias! Tu encuesta de diagnóstico fue registrada de forma anónima.")
        else:
            st.error(f"No se pudo enviar el diagnóstico: {msg}")


def _render_usabilidad() -> None:
    st.subheader("Evaluación de Usabilidad del Prototipo")
    st.caption("Califica tu experiencia usando ConectaMente para ayudarnos a mejorar la plataforma.")

    with st.form("form_feedback_usabilidad", clear_on_submit=True):
        facilidad = st.slider(
            "¿Qué tan fácil de usar te pareció la plataforma? (1 = Muy difícil, 5 = Muy fácil)",
            min_value=1,
            max_value=5,
            value=4,
        )
        utilidad = st.slider(
            "¿Qué tan útil consideras el contenido y herramientas? (1 = Nada útil, 5 = Muy útil)",
            min_value=1,
            max_value=5,
            value=4,
        )
        comentario = st.text_area(
            "Comentarios o sugerencias de mejora",
            placeholder="¿Qué mejorarías o agregarías en la siguiente versión?",
        )
        submitted = st.form_submit_button("Enviar feedback", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "Calificacion_facilidad": int(facilidad),
            "Utilidad_percibida": int(utilidad),
            "Comentario_mejora": comentario.strip() or None,
        }
        with st.spinner("Guardando retroalimentación..."):
            ok, _, msg = enviar_usabilidad(payload)

        if ok:
            st.success("¡Gracias por evaluar ConectaMente! Tu opinión ya quedó registrada.")
        else:
            st.error(f"No se pudo enviar el feedback: {msg}")


def _etiqueta_opcion(valor: int, min_val: int, max_val: int, etq_min: str, etq_max: str) -> str:
    if valor == min_val:
        return f"{valor} - {etq_min}"
    if valor == max_val:
        return f"{valor} - {etq_max}"
    return str(valor)


def _render_bienestar() -> None:
    st.subheader("Autoevaluación de Bienestar Emocional")
    st.caption("Responde en escala de 1 a 5 (donde mayor puntaje representa mayor carga o alerta en la dimensión evaluada).")

    with st.spinner("Cargando cuestionario..."):
        ok_q, data_q, msg_q = get_cuestionario_bienestar()

    if not ok_q:
        st.error(f"No se pudo cargar el cuestionario: {msg_q}")
        return

    preguntas = data_q if isinstance(data_q, list) else (data_q.get("preguntas", []) if isinstance(data_q, dict) else [])
    if not preguntas:
        st.warning("El backend no devolvió preguntas para el cuestionario.")
        with st.expander("Ver respuesta recibida"):
            st.json(data_q)
        return

    with st.form("form_cuestionario_bienestar"):
        respuestas = []
        for idx, item in enumerate(preguntas, start=1):
            p_id = int(item.get("pregunta_id", idx))
            dimension = item.get("dimension", "")
            enunciado = item.get("enunciado", f"Pregunta {p_id}")
            min_val = int(item.get("escala_min", 1))
            max_val = int(item.get("escala_max", 5))
            etq_min = item.get("etiqueta_min", "Nunca / Muy bajo")
            etq_max = item.get("etiqueta_max", "Siempre / Muy alto")

            if dimension:
                st.caption(f"📌 Dimensión: **{dimension}**")

            opciones = list(range(min_val, max_val + 1))
            seleccion = st.radio(
                f"{p_id}. {enunciado}",
                options=opciones,
                format_func=lambda v, mn=min_val, mx=max_val, emin=etq_min, emax=etq_max: _etiqueta_opcion(
                    v, mn, mx, emin, emax
                ),
                horizontal=True,
                key=f"bienestar_p_{p_id}",
            )
            respuestas.append({"pregunta_id": p_id, "valor": int(seleccion)})
            st.divider()

        evaluar = st.form_submit_button("Evaluar mi bienestar", type="primary", use_container_width=True)

    if evaluar:
        with st.spinner("Calculando resultado..."):
            ok_ev, res, msg_ev = evaluar_bienestar({"respuestas": respuestas})

        if not ok_ev:
            st.error(f"No se pudo procesar la evaluación: {msg_ev}")
            return

        st.success("Evaluación completada.")
        if isinstance(res, dict):
            c1, c2 = st.columns(2)
            puntaje = res.get("puntaje_total", res.get("puntaje", res.get("score")))
            nivel = res.get("nivel", res.get("nivel_riesgo", res.get("nivel_estres", res.get("categoria"))))

            if puntaje is not None:
                c1.metric("Puntaje obtenido", str(puntaje))
            if nivel is not None:
                c2.metric("Nivel identificado", str(nivel))

            recomendacion = res.get("recomendacion") or res.get("mensaje") or res.get("descripcion")
            if recomendacion:
                st.info(str(recomendacion))

            sugerencias = res.get("recomendaciones") or res.get("acciones_sugeridas")
            if isinstance(sugerencias, list) and sugerencias:
                st.markdown("**Recomendaciones sugeridas:**")
                for s in sugerencias:
                    st.markdown(f"- {s}")

            if res.get("alerta_sos") or res.get("requiere_atencion"):
                st.error("Detectamos un nivel alto de malestar. Recuerda que tienes el **Botón SOS** disponible en la barra lateral.")

            with st.expander("Ver detalle completo del resultado"):
                st.json(res)
        else:
            st.write(res)


def render_encuestas() -> None:
    st.header("Diagnóstico, Bienestar y Feedback")
    st.caption("Participa en el diagnóstico anónimo, evalúa tu bienestar o califica el prototipo.")

    tab_diag, tab_bien, tab_usab = st.tabs([
        "📋 Diagnóstico anónimo",
        "🧠 Cuestionario de bienestar",
        "⭐ Feedback de usabilidad",
    ])

    with tab_diag:
        _render_diagnostico()
    with tab_bien:
        _render_bienestar()
    with tab_usab:
        _render_usabilidad()