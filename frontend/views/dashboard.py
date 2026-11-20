import pandas as pd
import streamlit as st

from frontend.api_client import get_dashboard_metrics
from frontend.state import get_role, is_authenticated


def _format_label(key: str) -> str:
    return key.replace("_", " ").strip().capitalize()


def _is_scalar(val) -> bool:
    return isinstance(val, (int, float, str, bool))


def _render_scalar_grid(items: list[tuple[str, object]]) -> None:
    if not items:
        return
    cols = st.columns(min(4, len(items)))
    for idx, (k, v) in enumerate(items):
        valor = f"{v:.2f}" if isinstance(v, float) else str(v)
        cols[idx % len(cols)].metric(label=_format_label(k), value=valor)


def _render_chart_from_dict(title: str, mapping: dict) -> None:
    st.markdown(f"**{_format_label(title)}**")
    if not mapping:
        st.caption("Sin datos registrados aún.")
        return

    if all(isinstance(v, (int, float)) for v in mapping.values()):
        df = pd.DataFrame(
            {"Categoría": list(mapping.keys()), "Total": list(mapping.values())}
        ).set_index("Categoría")
        st.bar_chart(df)
    else:
        rows = [{"Indicador": _format_label(str(k)), "Valor": str(v)} for k, v in mapping.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_list_block(title: str, items: list) -> None:
    st.markdown(f"**{_format_label(title)}**")
    if not items:
        st.caption("Sin registros disponibles.")
        return

    if all(isinstance(i, dict) for i in items):
        df = pd.DataFrame(items)
        # Si tiene exactamente 1 columna de texto y 1 numérica, graficarla además de mostrar tabla
        str_cols = [c for c in df.columns if df[c].dtype == "object"]
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if len(str_cols) == 1 and len(num_cols) == 1:
            st.bar_chart(df.set_index(str_cols[0])[num_cols[0]])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        for item in items:
            st.markdown(f"- {item}")


def _render_section(section_name: str, content) -> None:
    st.subheader(_format_label(section_name))

    if isinstance(content, dict):
        scalars = [(k, v) for k, v in content.items() if _is_scalar(v)]
        nested = [(k, v) for k, v in content.items() if not _is_scalar(v) and v is not None]

        if scalars:
            _render_scalar_grid(scalars)

        if nested:
            cols = st.columns(min(2, len(nested)))
            for idx, (k, v) in enumerate(nested):
                with cols[idx % len(cols)]:
                    if isinstance(v, dict):
                        _render_chart_from_dict(k, v)
                    elif isinstance(v, list):
                        _render_list_block(k, v)
    elif isinstance(content, list):
        _render_list_block(section_name, content)
    else:
        st.write(content)


def render_dashboard() -> None:
    st.header("📊 Dashboard de Evaluación y Métricas")
    st.caption("Indicadores consolidados de ConectaMente en tiempo real desde MySQL.")

    if not is_authenticated() or (get_role() or "").lower() not in ("admin", "orientador"):
        st.warning("Acceso restringido. Inicia sesión con una cuenta de **administrador** u **orientador**.")
        return

    if st.button("🔄 Actualizar métricas"):
        st.rerun()

    with st.spinner("Consultando métricas del sistema..."):
        ok, data, msg = get_dashboard_metrics()

    if not ok:
        st.error(f"No se pudieron cargar las métricas: {msg}")
        return

    if not isinstance(data, dict) or not data:
        st.info("El endpoint de métricas no devolvió datos todavía.")
        return

    top_scalars = [(k, v) for k, v in data.items() if _is_scalar(v)]
    top_complex = [(k, v) for k, v in data.items() if not _is_scalar(v) and v is not None]

    if top_scalars:
        st.subheader("Resumen general")
        _render_scalar_grid(top_scalars)

    for key, val in top_complex:
        st.divider()
        _render_section(key, val)

    st.divider()
    with st.expander("🔍 Ver respuesta completa de /api/v1/metrics/dashboard (JSON)"):
        st.json(data)