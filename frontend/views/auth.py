import streamlit as st

from frontend.api_client import get_me, login, register
from frontend.state import clear_session, get_user, is_authenticated, set_session


def _render_authenticated_profile() -> None:
    st.subheader("Sesión activa")
    user = get_user() or {}

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Nombre:** {user.get('Name', 'Sin nombre')}")
        st.markdown(f"**Correo:** {user.get('Email', '-')}")
        st.markdown(f"**Rol:** `{user.get('Rol', '-')}`")
        st.markdown(f"**ID de usuario:** `{user.get('Id_usuario', '-')}`")

    with col2:
        if st.button("Verificar token (/auth/me)", use_container_width=True):
            ok, data, msg = get_me()
            if ok and isinstance(data, dict):
                # Actualiza el perfil en sesión si /auth/me devuelve el objeto usuario
                perfil = data.get("user", data)
                st.session_state.user = perfil
                st.success(f"Token válido ({msg}).")
            else:
                st.error(f"Sesión inválida o expirada: {msg}")

        if st.button("Cerrar sesión", type="secondary", use_container_width=True):
            clear_session()
            st.rerun()

    st.info("Usa el menú lateral para acceder a tus módulos habilitados según tu rol.")


def render_auth() -> None:
    st.header("Bienvenido a ConectaMente")
    st.caption("Inicia sesión con tu cuenta o regístrate para acceder al diario emocional y seguimiento.")

    if is_authenticated():
        _render_authenticated_profile()
        return

    tab_login, tab_register = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with tab_login:
        with st.form("form_login"):
            email = st.text_input("Correo electrónico", placeholder="admin@conectamente.edu.co")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

        if submitted:
            if not email.strip() or not password:
                st.warning("Completa el correo y la contraseña.")
            else:
                with st.spinner("Validando credenciales..."):
                    ok, data, msg = login(email.strip(), password)

                if ok and isinstance(data, dict) and data.get("access_token"):
                    token = data["access_token"]
                    user = data.get("user") or {}

                    # Si el login no devolviera el objeto user, lo consulta en /auth/me
                    set_session(token, user)
                    if not user:
                        ok_me, me_data, _ = get_me()
                        if ok_me and isinstance(me_data, dict):
                            set_session(token, me_data)

                    st.success(msg or "Inicio de sesión exitoso.")
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        with st.form("form_register", clear_on_submit=True):
            name = st.text_input("Nombre completo", placeholder="Ej. Laura Gómez")
            reg_email = st.text_input("Correo institucional o personal", placeholder="estudiante@conectamente.edu.co")
            reg_password = st.text_input("Contraseña", type="password")
            reg_confirm = st.text_input("Confirmar contraseña", type="password")
            reg_submitted = st.form_submit_button("Registrarme", type="primary", use_container_width=True)

        if reg_submitted:
            if not name.strip() or not reg_email.strip() or not reg_password:
                st.warning("Todos los campos son obligatorios.")
            elif reg_password != reg_confirm:
                st.error("Las contraseñas no coinciden.")
            else:
                with st.spinner("Creando cuenta..."):
                    ok, _, msg = register(name.strip(), reg_email.strip(), reg_password)

                if ok:
                    st.success("Cuenta creada correctamente. Ahora puedes iniciar sesión en la pestaña 'Iniciar sesión'.")
                else:
                    st.error(f"No se pudo completar el registro: {msg}")