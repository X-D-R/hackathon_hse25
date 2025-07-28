import streamlit as st

page_dict = {}
page_dict["Навигация"] = [
    st.Page("pages/General.py", title="Общий обзор", icon="🌍"),
    st.Page("pages/Errors.py", title="Ошибки", icon="🚨")
]
page_dict['Для разработчиков'] = [st.Page("pages/Old_dash.py", title="Вся статистика", icon="📊")]

pg = st.navigation(page_dict)
pg.run()
