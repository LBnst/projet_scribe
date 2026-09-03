import streamlit as st

#app streamlit
pages = [
    st.Page("accueil.py", title="Transcription", default=True),
    st.Page("historique.py", title="Historique"),
]

st.navigation(pages).run()
