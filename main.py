import os

import streamlit as st

from parsing import pipeline

REQUIRED_FILES = [
    "data/result.json",
    "data/parsed_data_cache.json",
    "data/log3.json"
]


def show_loader():
    st.set_page_config(page_title="Загрузка", layout="wide")
    with st.spinner("Загружаю данные..."):
        pipeline()
    st.success("Готово! Перезапусти страницу ⟳")
    st.stop()


def start():
    if not all(os.path.exists(f) for f in REQUIRED_FILES):
        show_loader()

    page_dict = {
        "Навигация": [
            st.Page("app_pages/General.py", title="Общий обзор", icon="🌍"),
            st.Page("app_pages/Errors.py", title="Ошибки", icon="🚨")
        ],
        "Для разработчиков": [
            st.Page("app_pages/Old_dash.py", title="Вся статистика", icon="📊")
        ]
    }
    pg = st.navigation(page_dict)
    pg.run()


if __name__ == "__main__":
    start()
