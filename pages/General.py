import plotly.express as px
import streamlit as st

from dashboard import Plots, load_data, process_data, sidebar_layout
from dashboard.alerts import get_system_alert_status, render_system_alert


def main():
    st.logo('logo.svg', size='large',
            link='https://youtu.be/dQw4w9WgXcQ?si=o_DarwH6AyHbJm_k')

    st.set_page_config(layout="wide")
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

    # --- Фильтрация по категориям, кампусам и т.п. ---
    df_filtered = sidebar_layout(df)

    # --- Статус системы ---
    status = get_system_alert_status(df)
    status_color = status['level']
    render_system_alert(status)
    st.page_link('pages/Errors.py',
                 label='Показать ошибки', use_container_width=True, icon="ℹ️")

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
        df_to_plot = df
    else:
        df_to_plot = df[df["conflict_metric"] == 1]

    graphs = Plots(df_to_plot, color_sequence=color_sequence)

    Plots(df, color_sequence=color_sequence).plot_conflict_metric(
        color_map_for_bar.get(status_color, "red"))

    # --- Метрики ---
    col1, col2, col3 = st.columns(3)

    # Подсчёт базовых метрик
    total_negative = (df_filtered["user_mark"] < 0).sum()
    avg_time = df_filtered["response_time"].mean()
    conflict_percent = df_filtered["conflict_metric"].mean() * 100

    # Для примитивной "динамики" — сравнение с последними 10 запросами
    if len(df_filtered) >= 20:
        prev = df_filtered.iloc[:-10]
        curr = df_filtered.iloc[-10:]
        delta_neg = (curr["user_mark"] < 0).mean()*100 - \
            (prev["user_mark"] < 0).mean()*100
        delta_time = curr["response_time"].mean() - \
            prev["response_time"].mean()
        delta_conf = curr["conflict_metric"].mean()*100 - \
            prev["conflict_metric"].mean()*100
    else:
        delta_neg = delta_time = delta_conf = 0.0

    with col1:
        st.metric(
            "👎 Отрицательных оценок",
            f"{total_negative}",
            f"{delta_neg:.1f}%",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            "⏱ Среднее время ответа",
            f"{avg_time:.2f} сек",
            f"{delta_time:.2f} сек",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "⚠️ Конфликтность",
            f"{conflict_percent:.1f}%",
            f"{delta_conf:.1f}%",
            delta_color="inverse"
        )


main()
