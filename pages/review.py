import streamlit as st

from dashboard import Plots, load_data, process_data
from dashboard.alerts import show_system_alert

st.set_page_config(page_title="Обзор", layout="wide")

st.title("📊 Обзор общей картины")

# --- Загрузка и обработка данных ---
data = load_data("data/result.json")
if not data:
    st.warning("Нет данных.")
    st.stop()

df = process_data(data)
if df.empty:
    st.warning("Данные не обработаны.")
    st.stop()

# --- Плашка статуса и детализация ---
show_system_alert(df)

# --- Графики ---
graphs = Plots(df)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Количество вопросов по категориям")
    graphs.plot_pie_chart("question_category", "")

with col2:
    st.subheader("Среднее время ответа по категориям")
    graphs.plot_response_time_by_category()

st.markdown("### Метрика конфликтных ответов")
graphs.plot_conflict_metric()
