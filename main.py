import os
import time

import streamlit as st

from parsing import pipeline

REQUIRED_FILES = [
    "data/result.json",
    "data/parsed_data_cache.json",
    "data/log3.json"
]

APP_PAGES = 'app_pages'


def show_loader():
    st.set_page_config(page_title="Загрузка", layout="wide",
                       initial_sidebar_state="collapsed")

    with st.status("⏳ Подготовка данных...", expanded=True) as status:
        start_time = time.time()

        st.write("🔍 Загружаю и проверяю логи...")
        st.write("📦 Парсю новые записи...")
        pipeline()

        duration = time.time() - start_time
        st.write(f"✅ Завершено за {duration:.2f} секунд.")
        status.update(label="🎉 Загрузка завершена",
                      state="complete", expanded=False)

    st.rerun()


def start():
    if not all(os.path.exists(f) for f in REQUIRED_FILES):
        show_loader()
    pipeline()

    page_dict = {
        "Навигация": [
            st.Page(f"{APP_PAGES}/General.py", title="Общий обзор", icon="🌍"),
            st.Page(f"{APP_PAGES}/Errors.py", title="Ошибки", icon="🚨")
        ],
        "Для разработчиков": [
            st.Page(f"{APP_PAGES}/Old_dash.py",
                    title="Вся статистика", icon="📊")
        ]
    }
    pg = st.navigation(page_dict)
    pg.run()


if __name__ == "__main__":
    start()
