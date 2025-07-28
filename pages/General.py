import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard import (Plots, load_data, plot_mini_trend, process_data,
                       sidebar_layout)
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


def calculate_metrics(df):
    total_negative = (df["user_mark"] < 0).sum()
    avg_time = df["response_time"].mean()
    conflict_percent = df["conflict_metric"].mean() * 100

    prev = pd.DataFrame()
    curr = pd.DataFrame()

    if len(df) >= 20:
        prev = df.iloc[:-10]
        curr = df.iloc[-10:]
        delta_neg = (curr["user_mark"] < 0).mean()*100 - \
            (prev["user_mark"] < 0).mean()*100
        delta_time = curr["response_time"].mean() - \
            prev["response_time"].mean()
        delta_conf = curr["conflict_metric"].mean(
        )*100 - (prev["conflict_metric"].mean()*100)
        prev_neg = (prev["user_mark"] < 0).mean()*100
        curr_neg = (curr["user_mark"] < 0).mean()*100
        prev_time = prev["response_time"].mean()
        curr_time = curr["response_time"].mean()
        prev_conf = prev["conflict_metric"].mean()*100
        curr_conf = curr["conflict_metric"].mean()*100
    else:
        delta_neg = delta_time = delta_conf = 0.0
        prev_neg = curr_neg = total_negative
        prev_time = curr_time = avg_time
        prev_conf = curr_conf = conflict_percent

    return {
        "total_negative": total_negative,
        "avg_time": avg_time,
        "conflict_percent": conflict_percent,
        "delta_neg": delta_neg,
        "delta_time": delta_time,
        "delta_conf": delta_conf,
        "prev_neg": prev_neg,
        "curr_neg": curr_neg,
        "prev_time": prev_time,
        "curr_time": curr_time,
        "prev_conf": prev_conf,
        "curr_conf": curr_conf
    }


def show_metrics(metrics):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "👎 Отрицательных оценок",
            f"{metrics['total_negative']}",
            f"{metrics['delta_neg']:.1f}%",
            delta_color="inverse"
        )
        plot_mini_trend(metrics["prev_neg"],
                        metrics["curr_neg"])

    with col2:
        st.metric(
            "⏱ Среднее время ответа",
            f"{metrics['avg_time']:.2f} сек",
            f"{metrics['delta_time']:.2f} сек",
            delta_color="inverse"
        )
        plot_mini_trend(metrics["prev_time"],
                        metrics["curr_time"])

    with col3:
        st.metric(
            "⚠️ Конфликтность",
            f"{metrics['conflict_percent']:.1f}%",
            f"{metrics['delta_conf']:.1f}%",
            delta_color="inverse"
        )
        plot_mini_trend(metrics["prev_conf"],
                        metrics["curr_conf"])


def main():
    st.set_page_config(layout="wide")
    st.logo('logo.svg', size='large',
            link='https://youtu.be/dQw4w9WgXcQ?si=o_DarwH6AyHbJm_k')
    st.title("📊 Обзор общей картины")

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
    st.page_link('pages/Errors.py',
                 label='Показать ошибки', use_container_width=True, icon="ℹ️")

    color_sequence = get_color_palette(status['level'])
    bar_color = get_bar_color(status['level'])

    df_to_plot = df if status['level'] == "green" else df[df["conflict_metric"] == 1]
    graphs = Plots(df, color_sequence=color_sequence)

    graphs.plot_conflict_metric(bar_color)

    metrics = calculate_metrics(df_filtered)
    show_metrics(metrics)


main()
