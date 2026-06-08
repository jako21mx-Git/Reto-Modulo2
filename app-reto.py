import streamlit as st
import pandas as pd
from firestore_service import get_dataframe
from firestore_service import get_dataframe, client 
from sqlalchemy import create_engine, text 

conn = st.connection(
    "postgresql",
    type="sql",
    url=st.secrets["POSTGRES_URL"]
)


# Se ejecuta al iniciar la aplicación
movies_df = get_dataframe()

st.title("🎬 Netflix App Jair")

## Verificación
#st.write("Datos cargados desde Firestore")
#st.subheader("Todas los filmes")
#st.dataframe(movies_df)

# Sidebar
st.sidebar.header("📽️ Opciones")
muestra_todo = st.sidebar.checkbox("Ver todos los filmes")

if muestra_todo:
    st.subheader("Todos los filmes")
    st.dataframe(movies_df)

st.sidebar.header("🔍 Busqueda rápida")
search_text = st.sidebar.text_input("Título del filme:")
search_button = st.sidebar.button("Buscar filmes")

if search_button:

    if search_text:

        #filtro con coincidencia "que contenga"
        filtered_df = movies_df[
            movies_df["name"].str.contains(search_text, case=False, na=False)
        ]

        st.caption(f"Total filmes mostrados: {len(filtered_df)}")
        st.dataframe(filtered_df)

    else:
        st.warning("Escribe un título para buscar")


director_selected = st.sidebar.selectbox(
    "Selecciona un director",
    sorted(movies_df["director"].unique())
)

filter_button = st.sidebar.button("Filtrar director")

if filter_button:

    filtered_director_df = movies_df[
            movies_df["director"].str.contains(director_selected, case=False, na=False)
            ]

    st.caption(f"Total filmes mostrados: {len(filtered_director_df)}")
    st.dataframe(filtered_director_df)


# --- Formulario para agregar nuevo filme ---
st.sidebar.header("Agregar nuevo filme")

name = st.sidebar.text_input("Nombre del filme")
genre = st.sidebar.text_input("Género")
director = st.sidebar.text_input("Director")
company = st.sidebar.text_input("Compañía")

submit = st.sidebar.button("Crear nuevo filme")

if submit:
    if name and genre and director and company:
        # Crear documento con ID automático
        client.collection("Movies").add({
            "name": name,
            "genre": genre,
            "director": director,
            "company": company
        })
        
        # Limpiar caché
        get_dataframe.clear()
        

        # recarga la app para actualizar tabla
        #movies_df = get_dataframe()  

        st.sidebar.success("Filme agregado correctamente")
        
        import time
        time.sleep(0.5)
        st.rerun()
        
    else:
        st.sidebar.warning("Completa todos los campos")

st.sidebar.markdown("""---""")

st.sidebar.header("💬 Libro de visitas")

# Inputs con keys para poder limpiar luego
# Inputs con keys
if "guest_email" not in st.session_state:
    st.session_state.guest_email = ""
if "guest_comment" not in st.session_state:
    st.session_state.guest_comment = ""

email = st.sidebar.text_input("Email", key="guest_email", value=st.session_state.guest_email)
comment = st.sidebar.text_area("Comentario", key="guest_comment", value=st.session_state.guest_comment)


submit_comment = st.sidebar.button("Registrar Visita")
if submit_comment:
    if email and comment:

        # Inserción usando parámetros
        with conn.session as session:
            session.execute(
            text(
                "INSERT INTO people (email, comment) VALUES (:email, :comment)"
                ),
             {
                "email": email,
                "comment": comment
                }
            )
            session.commit()

        st.sidebar.success("Comentario guardado correctamente")
        
        import time
        time.sleep(0.5)

        # Limpiar inputs
        #st.session_state.guest_email = ""
        #st.session_state.guest_comment = ""
        st.rerun()
    else:
        st.sidebar.warning("Completa ambos campos")

st.sidebar.markdown("""---""")

show_comments = st.sidebar.button("Ver visitas")

if show_comments:

    try:

        df_comments = conn.query(
            """
            SELECT email, comment
            FROM people
            ORDER BY email
            LIMIT 50
            """,
            ttl="10m"
        )

        st.sidebar.caption(
            f"Total comentarios mostrados: {len(df_comments)}"
        )

        for i, row in enumerate(df_comments.itertuples(), start=1):

            st.sidebar.markdown(
                f"""
                **{i}. {row.comment}**

                <span style="font-size:12px;color:gray;">
                {row.email}
                </span>
                """,
                unsafe_allow_html=True
            )

            st.sidebar.markdown("---")

    except Exception as e:
        st.sidebar.error(f"No fue posible cargar comentarios: {e}")