import streamlit as st

page_dict = {}
page_dict["Навигация"] = [
    st.Page("screens/General.py", title="Общий обзор", icon="🌍"),
    st.Page("screens/Errors.py", title="Ошибки", icon="🚨"),
    st.Page("screens/Old_dash.py", title="Старый дашборд", icon="📊")
]

pg = st.navigation(page_dict)
pg.run()
