import plotly.express as px
import streamlit as st

from dashboard import Plots, load_data, process_data
from dashboard.alerts import show_system_alert

st.set_page_config(page_title="Общий обзор", page_icon="📊", layout="wide")

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
status_color = show_system_alert(df)

# custom_green_palette = [
#     "#0b6623",  # тёмно-зелёный (глубокий)
#     "#228B22",  # forest green
#     "#2ecc71",  # flat UI green
#     "#27ae60",
#     "#58d68d",
#     "#82e0aa",
#     "#abebc6",
#     "#d5f5e3"
# ]


# палитры
palette_map = {
    # custom_green_palette, #px.colors.sequential.Greens
    "green": px.colors.sequential.YlGn_r,
    "yellow": px.colors.sequential.Inferno_r,
    "red": px.colors.sequential.YlOrRd_r,
    "blue": px.colors.sequential.Blues,
}
color_sequence = palette_map.get(status_color, px.colors.sequential.Blues)

# --- Графики ---

graphs = Plots(df, color_sequence=color_sequence)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Количество вопросов по категориям")
    graphs.plot_pie_chart("question_category", "")

with col2:
    st.subheader("Среднее время ответа по категориям")
    graphs.plot_response_time_by_category()

st.markdown("### Метрика конфликтных ответов")
color_map_for_bar = {
    "green": "#28a745",
    "yellow": "#ffc107",
    "red": "#dc3545",
    "blue": "#17becf"
}
graphs.plot_conflict_metric(bar_color=color_map_for_bar.get(status_color))
