import os
import threading
import time

import streamlit as st

from parsing import log, pipeline

REQUIRED_FILES = [
    "data/result.json",
    "data/parsed_data_cache.json",
    "data/log3.json"
]

APP_PAGES = 'app_pages'


def show_loader():
    st.set_page_config(page_title="Загрузка", layout="wide",
                       initial_sidebar_state="collapsed")
    st.logo('logo.svg', size='large', link="")

    with st.status("⏳ Подготовка данных...", expanded=True) as status:
        start_time = time.time()
        st.write("🔍 Загружаю и проверяю логи...")
        pipeline()
        duration = time.time() - start_time
        st.write("📦 Парсю новые записи...")
        time.sleep(1)
        st.write(f"✅ Завершено за {duration:.2f} секунд.")
        status.update(label="🎉 Загрузка завершена",
                      state="complete", expanded=True)
        time.sleep(2)

    st.rerun()


def run_pipeline_async():
    while True:
        try:
            log("Старт фонового парсинга...")
            start = time.time()
            pipeline()
            log(f"✅ Парсинг завершён за {time.time() - start:.2f} сек.")
        except Exception as e:
            log(f"⚠️ Ошибка при выполнении pipeline: {e}")
        time.sleep(60)


def start():
    if not all(os.path.exists(f) for f in REQUIRED_FILES):
        show_loader()

    if not any(t.name == "BackgroundParser" for t in threading.enumerate()):
        threading.Thread(target=run_pipeline_async, daemon=True,
                         name="BackgroundParser").start()
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
