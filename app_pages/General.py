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


def calculate_metrics(df):
    total_negative = (df["user_mark"] < 0).sum()
    avg_time = df["response_time"].mean()
    conflict_percent = df["conflict_metric"].mean() * 100

    n = len(df)
    if n >= 3:
        third = n // 3
        early = df.iloc[:third]
        middle = df.iloc[third:2*third]
        late = df.iloc[2*third:]

        # Оцениваем рост от early → middle и от middle → late
        neg_early = (early["user_mark"] < 0).mean() * 100
        neg_middle = (middle["user_mark"] < 0).mean() * 100
        neg_late = (late["user_mark"] < 0).mean() * 100

        time_early = early["response_time"].mean()
        time_middle = middle["response_time"].mean()
        time_late = late["response_time"].mean()

        conf_early = early["conflict_metric"].mean() * 100
        conf_middle = middle["conflict_metric"].mean() * 100
        conf_late = late["conflict_metric"].mean() * 100

        # Финальный прирост — от первой к последней трети
        delta_neg = neg_late - neg_early
        delta_time = time_late - time_early
        delta_conf = conf_late - conf_early

        # Для мини-графиков — просто сравнение начальной и конечной трети
        prev_neg, curr_neg = neg_early, neg_late
        prev_time, curr_time = time_early, time_late
        prev_conf, curr_conf = conf_early, conf_late
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
        plot_metric_trend_over_time(df_filtered.assign(neg=(df_filtered["user_mark"] < 0).astype(int)),
                                    column="neg",
                                    inverse=True)

    with col2:
        delta = metrics["delta_time"]
        if delta == 0:
            st.metric("⏱ Среднее время ответа",
                      f"{metrics['avg_time']:.2f} сек", "~ без изменений", delta_color="off")
        else:
            st.metric("⏱ Среднее время ответа",
                      f"{metrics['avg_time']:.2f} сек", f"{delta:.2f} сек", delta_color="inverse")
        plot_metric_trend_over_time(df_filtered,
                                    column="response_time",
                                    inverse=True)

    with col3:
        delta = metrics["delta_conf"]
        if delta == 0:
            st.metric("⚠️ Конфликтность",
                      f"{metrics['conflict_percent']:.1f}%", "~ без изменений", delta_color="off")
        else:
            st.metric("⚠️ Конфликтность",
                      f"{metrics['conflict_percent']:.1f}%", f"{delta:.1f}%", delta_color="inverse")
        plot_metric_trend_over_time(df_filtered,
                                    column="conflict_metric",
                                    inverse=True)


def draw_graphs(graphs):
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
