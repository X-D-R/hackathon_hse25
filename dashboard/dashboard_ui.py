import streamlit as st
from streamlit_autorefresh import st_autorefresh


def setup_page(refresh_interval: int = 10):
    # ---------------------------
    # НАСТРОЙКА СТРАНИЦЫ STREAMLIT
    # ---------------------------
    st.set_page_config(page_title="Аналитика Чат-Бота",
                       page_icon="🤖", layout="wide")

    # CSS-хак для кнопок скачивания
    st.markdown("""
    <style>
    button[data-testid="stDownloadButton"] {
        width: 120px !important;
        height: 35px !important;
        font-size: 12px;
        padding: 0 4px;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Автоматическая перезагрузка
    st_autorefresh(interval=refresh_interval * 1000, key="data_refresh")


def sidebar_layout(df):
    # ---------------------------
    # ФУНКЦИЯ САЙДБАРА ДЛЯ ФИЛЬТРАЦИИ ДАННЫХ
    # ---------------------------
    st.sidebar.image(
        "https://github.com/X-D-R/hackathon_hse25/raw/main/logo.png",
        use_container_width=True
    )
    st.sidebar.title("Фильтры")

    campuses = df["campus"].dropna().unique(
    ).tolist() if "campus" in df.columns else []
    categories = df["question_category"].dropna().unique(
    ).tolist() if "question_category" in df.columns else []
    education_levels = df["education_level"].dropna().unique(
    ).tolist() if "education_level" in df.columns else []

    selected_campus = st.sidebar.multiselect(
        "Выберите кампус", campuses, default=campuses)
    selected_category = st.sidebar.multiselect(
        "Выберите категорию вопроса", categories, default=categories)
    selected_edu_level = st.sidebar.multiselect(
        "Выберите уровень образования", education_levels, default=education_levels)

    filtered_df = df.copy()
    if "campus" in df.columns:
        filtered_df = filtered_df[filtered_df["campus"].isin(selected_campus)]
    if "question_category" in df.columns:
        filtered_df = filtered_df[filtered_df["question_category"].isin(
            selected_category)]
    if "education_level" in df.columns:
        filtered_df = filtered_df[filtered_df["education_level"].isin(
            selected_edu_level)]

    return filtered_df
