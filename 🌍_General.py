import plotly.express as px
import streamlit as st

from dashboard import Plots, load_data, process_data
from dashboard.alerts import show_system_alert


# ---------------------------
# ГЛАВНАЯ ФУНКЦИЯ
# ---------------------------
def main():
    st.logo('logo.svg', size='large',
            link='https://youtu.be/dQw4w9WgXcQ?si=o_DarwH6AyHbJm_k')
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

    # палитры
    palette_map = {
        # px.colors.sequential.Greens
        "green": px.colors.sequential.YlGn_r,
        "yellow": px.colors.sequential.Inferno_r,
        "red": px.colors.sequential.YlOrRd_r,
        "blue": px.colors.sequential.Blues,
    }
    color_sequence = palette_map.get(status_color, px.colors.sequential.Blues)

    color_map_for_bar = {
        "green": "#28a745",
        "yellow": "#ffc107",
        "red": "#dc3545",
        "blue": "#17becf"
    }

    # --- Графики ---
    if status_color == "green":
        df_to_plot = df  # всё
    else:
        df_to_plot = df[df["conflict_metric"] == 1]

    graphs = Plots(df_to_plot, color_sequence=color_sequence)

    Plots(df, color_sequence=color_sequence).plot_conflict_metric(
        color_map_for_bar.get(status_color, "red"))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Количество вопросов по категориям")
        graphs.plot_pie_chart("question_category", "")

    with col2:
        st.subheader("Среднее время ответа по категориям")
        graphs.plot_response_time_by_category()

    with col3:
        st.subheader("Среднее оценка по категориям")
        graphs.plot_avg_user_mark_by_category()


if __name__ == "__main__":
    main()
