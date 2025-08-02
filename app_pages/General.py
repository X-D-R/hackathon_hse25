import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import linregress
from streamlit_autorefresh import st_autorefresh

from dashboard import (Plots, load_data, plot_metric_trend_over_time,
                       process_data, sidebar_layout)
from dashboard.alerts import get_system_alert_status, render_system_alert


def get_color_palette(level):
    palette_map = {
        "green": px.colors.sequential.YlGn_r,
        "yellow": px.colors.sequential.Inferno_r,
        "red": px.colors.sequential.YlOrRd_r,
        "blue": px.colors.sequential.Blues,
    }
    return palette_map.get(level, px.colors.sequential.Blues)


def get_bar_color(level):
    return {
        "green": "#28a745",
        "yellow": "#ffc107",
        "red": "#dc3545",
        "blue": "#17becf"
    }.get(level, "#dc3545")


def slope_to_color(slope, inverse=True, epsilon=0.01):
    if abs(slope) < epsilon:
        return "#888888"
    elif (slope < 0 and inverse) or (slope > 0 and not inverse):
        return "#28a745"
    else:
        return "#dc3545"


def calculate_metrics(df, window=5, epsilon=0.01):
    df = df.copy()
    df["time_question"] = pd.to_datetime(df["time_question"])
    df["date"] = df["time_question"].dt.date

    total_negative = (df["user_mark"] < 0).sum()
    avg_time = df["response_time"].mean()
    conflict_percent = df["conflict_metric"].mean() * 100

    daily = df.groupby("date").agg({
        "user_mark": lambda x: (x < 0).sum(),
        "response_time": "mean",
        "conflict_metric": lambda x: x.mean() * 100
    }).reset_index()

    daily = daily.sort_values("date").reset_index(drop=True)

    # rolling применим только к response_time и conflict_metric
    daily["rolling_user_mark"] = daily["user_mark"]
    daily["rolling_response_time"] = daily["response_time"].rolling(
        window, min_periods=1).mean()
    daily["rolling_conflict_metric"] = daily["conflict_metric"].rolling(
        window, min_periods=1).mean()

    # Вычислим наклоны
    def slope_of(series):
        if len(series) < 2:
            return 0.0
        return linregress(range(len(series)), series)[0]

    delta_neg = slope_of(daily["rolling_user_mark"])
    delta_time = slope_of(daily["rolling_response_time"])
    delta_conf = slope_of(daily["rolling_conflict_metric"])

    return {
        "total_negative": total_negative,
        "avg_time": avg_time,
        "conflict_percent": conflict_percent,
        "delta_neg": delta_neg,
        "delta_time": delta_time,
        "delta_conf": delta_conf,
        "rolling_user_mark": daily["rolling_user_mark"].tolist(),
        "rolling_response_time": daily["rolling_response_time"].tolist(),
        "rolling_conflict_metric": daily["rolling_conflict_metric"].tolist(),
        "color_user_mark": slope_to_color(delta_neg, inverse=True),
        "color_response_time": slope_to_color(delta_time, inverse=True),
        "color_conflict_metric": slope_to_color(delta_conf, inverse=True),
    }


def show_metrics(df_filtered, metrics):
    col1, col2, col3 = st.columns(3)

    with col1:
        delta = metrics["delta_neg"]
        if delta == 0:
            st.metric("👎 Отрицательных оценок",
                      metrics["total_negative"], "~ без изменений", delta_color="off")
        else:
            st.metric("👎 Отрицательных оценок",
                      metrics["total_negative"], f"{delta:.1f}%", delta_color="inverse")
        plot_metric_trend_over_time(
            df_filtered, "user_mark", inverse=True, color=metrics["color_user_mark"])

    with col2:
        delta = metrics["delta_time"]
        if delta == 0:
            st.metric("⏱ Среднее время ответа",
                      f"{metrics['avg_time']:.2f} сек", "~ без изменений", delta_color="off")
        else:
            st.metric("⏱ Среднее время ответа",
                      f"{metrics['avg_time']:.2f} сек", f"{delta:.2f} сек", delta_color="inverse")
        plot_metric_trend_over_time(
            df_filtered, "response_time", inverse=True, color=metrics["color_response_time"])

    with col3:
        delta = metrics["delta_conf"]
        if delta == 0:
            st.metric("⚠️ Конфликтность",
                      f"{metrics['conflict_percent']:.1f}%", "~ без изменений", delta_color="off")
        else:
            st.metric("⚠️ Конфликтность",
                      f"{metrics['conflict_percent']:.1f}%", f"{delta:.1f}%", delta_color="inverse")
        plot_metric_trend_over_time(
            df_filtered, "conflict_metric", inverse=True, color=metrics["color_conflict_metric"])


def draw_graphs(graphs):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Количество вопросов по категориям")
        graphs.plot_pie_chart("question_category", "")

    with col2:
        st.subheader("Среднее время ответа по категориям")
        graphs.plot_response_time_by_category()

    with col3:
        st.subheader("Количество оценок по категориям")
        graphs.plot_avg_user_mark_by_category()


def main():
    time_refresh = 60
    st.set_page_config(layout="wide")
    st_autorefresh(interval=time_refresh * 1000, key="datarefresh")
    st.logo('logo.svg', size='large', link='')
    st.title("Обзор общей картины")

    data = load_data("data/result.json")
    if not data:
        st.warning("Нет данных.")
        st.stop()

    df = process_data(data)
    if df.empty:
        st.warning("Данные не обработаны.")
        st.stop()

    df_filtered = sidebar_layout(df)

    status = get_system_alert_status(df)
    render_system_alert(status)
    st.page_link('app_pages/Errors.py',
                 label='Показать ошибки', use_container_width=True, icon="ℹ️")

    color_sequence = get_color_palette(status['level'])
    bar_color = get_bar_color(status['level'])

    df_to_plot = df_filtered if status['level'] == "green" else df_filtered[df_filtered["conflict_metric"] == 1]
    graphs = Plots(df_to_plot, color_sequence=color_sequence)

    Plots(df, color_sequence=color_sequence).plot_conflict_metric(bar_color)

    metrics = calculate_metrics(df_filtered)
    show_metrics(df_filtered, metrics)

    st.divider()
    draw_graphs(graphs)


main()
