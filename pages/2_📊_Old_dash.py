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
    st.logo('logo.svg', size='large',
            link='https://youtu.be/dQw4w9WgXcQ?si=o_DarwH6AyHbJm_k')
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

    # Кнопка для скачивания отфильтрованных данных в формате JSON
    st.markdown("### Экспорт данных")

    col1, col2 = st.columns(2)
    with col1:
        download_json(filtered_df.to_dict(orient="records"))
    with col2:
        normal_q, bad_q, unsure_q = split_by_answer_quality(
            filtered_df.to_dict(orient="records"))
        excel_file = create_excel_file(normal_q, bad_q, unsure_q)

        st.download_button(
            label="📥 Скачать Excel",
            data=excel_file,
            file_name="chatbot_logs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # --- 1) Отдельные графики для метрик качества ---
    st.markdown("## Отдельные метрики качества")
    graphs.plot_quality_metrics_separate()

    # --- 2) Сводный график метрик качества ---
    st.markdown("## Сводный график метрик качества")
    graphs.plot_quality_metrics_combined()

    # --- 3) Основные метрики ---
    st.markdown("## Основные метрики")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Распределение запросов по кампусам")
        graphs.plot_pie_chart("campus", "unused_title")
    with col2:
        st.subheader("Распределение по уровням образования")
        graphs.plot_pie_chart("education_level", "unused_title")
    with col3:
        st.subheader("Частота уточняющих вопросов")
        graphs.plot_follow_up_pie_chart()

    # --- 4) Сравнение времени ответа по категориям ---
    st.markdown("## Сравнение времени ответа по категориям")
    graphs.plot_response_time_by_category()

    # --- 5) Среднее время ответа (по кампусам и группам) ---
    st.markdown("## Сравнения по времени ответа")
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Среднее время ответа по кампусам")
        graphs.plot_response_time_chart_with_campus()
    with col5:
        st.subheader("Усреднённое время ответа (по группам)")
        graphs.plot_averaged_response_time_chart(bin_size=10)

    # --- 6) Дополнительные графики ---
    st.markdown("## Дополнительные графики")
    st.subheader("Распределение времени ответа (BoxPlot)")
    graphs.plot_response_time_boxplot()
    st.subheader("Метрика конфликтного ответа")
    graphs.plot_conflict_metric()

    # --- 7) Метрики по ответу и тексту ---
    st.markdown("## Оценка пользователя")
    graphs.plot_user_mark_distribution()

    st.markdown("## Наивные текстовые метрики")
    graphs.plot_naive_text_metrics()

    st.markdown("## Верность ответа контексту")
    graphs.plot_faithfulness_scores()

    st.markdown("## Сходство ответа с контекстом")
    graphs.plot_answer_correctness()


if __name__ == '__main__':
    main()
