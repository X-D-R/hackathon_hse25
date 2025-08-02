import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from dashboard import *


def main():
    """
    Основная функция приложения.
    Загружает и обрабатывает данные, отображает фильтры, а затем строит различные графики:
        - Отдельные графики для метрик качества
        - Сводный график для метрик качества
        - Графики основных метрик (распределение по кампусам, уровням образования и т.д.)
        - Графики, связанные с временем ответа и дополнительными метриками
    """
    st.logo('logo.svg', size='large')

    setup_page(refresh_interval=60)

    data = load_data("data/result.json")
    if not data:
        st.stop()

    df = process_data(data)
    if df.empty:
        st.info("Не удалось обработать данные. Проверь входной файл.")
        st.stop()

    filtered_df = sidebar_layout(df)
    if filtered_df.empty:
        st.info("Нет данных для отображения. Попробуйте изменить фильтры.")
        return

    graphs = Plots(filtered_df)

    # Заголовок приложения
    st.markdown("<h1 style='text-align: center;'>Мониторинг качества чат-бота</h1>",
                unsafe_allow_html=True)

    # Кнопка для скачивания отфильтрованных данных в формате JSON и Excel
    st.markdown("### Экспорт данных")
    col1, col2 = st.columns(2)
    with col1:
        download_json(filtered_df.to_dict(orient="records"))
    with col2:
        download_excel(filtered_df)
    st.divider()

    # KPI-блок
    st.markdown("### Основные показатели")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего записей", len(filtered_df))
    col2.metric("Среднее время ответа",
                f"{filtered_df['response_time'].mean():.1f} сек")
    col3.metric("Доля негативных оценок",
                f"{(filtered_df['user_mark'] < 0).mean() * 100:.1f}%")
    col4.metric("Средний конфликт",
                f"{filtered_df['conflict_metric'].mean() * 100:.1f}%")
    st.divider()

    # --- Метрики качества ---
    st.markdown("## Отдельные метрики качества")
    graphs.plot_quality_metrics_separate()

    st.markdown("## Сводный график метрик качества")
    graphs.plot_quality_metrics_combined()

    # --- Основные метрики ---
    st.markdown("## Основные метрики")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Распределение по кампусам")
        graphs.plot_pie_chart("campus", "unused_title")
    with col2:
        st.subheader("Распределение по уровням образования")
        graphs.plot_pie_chart("education_level", "unused_title")
    with col3:
        st.subheader("Частота уточняющих вопросов")
        graphs.plot_follow_up_pie_chart()

    # --- Время ответа ---
    st.markdown("## Сравнение времени ответа")
    graphs.plot_response_time_by_category()

    col4, col5 = st.columns(2)
    with col4:
        st.subheader("По кампусам")
        graphs.plot_response_time_chart_with_campus()
    with col5:
        st.subheader("Усреднённое время (по группам)")
        graphs.plot_averaged_response_time_chart(bin_size=10)

    st.subheader("BoxPlot времени ответа")
    graphs.plot_response_time_boxplot()

    # --- Оценки и текстовые метрики ---
    st.markdown("## Распределение пользовательских оценок")
    graphs.plot_user_mark_distribution()

    st.markdown("## Текстовые метрики")
    graphs.plot_naive_text_metrics()

    st.markdown("## Верность ответов")
    graphs.plot_faithfulness_scores()

    st.markdown("## Сходство с контекстом")
    graphs.plot_answer_correctness()


main()
