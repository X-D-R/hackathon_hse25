import pandas as pd
import streamlit as st

from dashboard import load_data, process_data
from dashboard.alerts import get_system_alert_status, render_system_alert


def main():
    time = 20
    st.logo('logo.svg', size='large',
            link='https://youtu.be/dQw4w9WgXcQ?si=o_DarwH6AyHbJm_k')
    st.title("🛑 Системные сбои и отклонения")

    data = load_data("data/result.json")
    if not data:
        st.warning("Нет данных.")
        st.stop()

    df = process_data(data)
    if df.empty:
        st.warning("Невозможно обработать данные.")
        st.stop()

    status = get_system_alert_status(df)
    render_system_alert(status)

    all_view(df, status)
    st.divider()
    st.subheader("🛠 Подозрительные случаи")

    # Долгие ответы
    long_answers = df[df["response_time"] > time]

    # Пустой ответ модели
    empty_responses = df[df["answer"].str.strip() == "Сервер не отвечает, пожалуйста, попробуйте позже."]

    # Очень короткие ответы (< 3 слов)
    short_responses = df[df["answer"].str.split().str.len() < 3]

    # Низкая оценка
    low_mark = df[df["user_mark"] < 0]

    # --- Списки кейсов ---
    cases = []

    if len(long_answers):
        cases.append({
            "title": "⏱ Долгое время генерации (>20 сек)",
            "df": long_answers[["user_question", "answer", "response_time", 'question_category']],
            "count": len(long_answers)
        })

    if len(empty_responses):
        cases.append({
            "title": "📭 Пустой ответ модели",
            "df": empty_responses[["user_question", "answer", 'question_category']],
            "count": len(empty_responses)
        })

    if len(short_responses):
        cases.append({
            "title": "✂️ Слишком короткий ответ (< 3 слов)",
            "df": short_responses[["user_question", "answer", 'question_category']],
            "count": len(short_responses)
        })

    if len(low_mark):
        cases.append({
            "title": "⚠️ Низкая оценка",
            "df": low_mark[["user_question", "answer", "user_mark", 'question_category']],
            "count": len(low_mark)
        })

    # --- Рендер с приоритетом по вертикали (1–2 случая) ---
    if len(cases) <= 2:
        for i, case in enumerate(cases):
            with st.expander(f"{case['title']} (Найдено: {case['count']})", expanded=True):
                df_to_show = case["df"]

                # Фильтр по категории
                if 'question_category' in df_to_show.columns:
                    cats = df_to_show['question_category'].dropna(
                    ).unique().tolist()
                    selected = st.multiselect(
                        label=" ", options=cats, default=cats, key=f"cat_{i}"
                    )
                    df_to_show = df_to_show[df_to_show["question_category"].isin(
                        selected)]

                st.dataframe(df_to_show, use_container_width=True)

    # --- Рендер в 2 колонки, если кейсов больше ---
    else:
        for i in range(0, len(cases), 2):
            cols = st.columns(min(2, len(cases) - i))
            for j, col in enumerate(cols):
                case = cases[i + j]
                with col.expander(f"{case['title']} (Найдено: {case['count']})", expanded=True):
                    df_to_show = case["df"]

                    if 'question_category' in df_to_show.columns:
                        cats = df_to_show['question_category'].dropna(
                        ).unique().tolist()
                        selected = st.multiselect(
                            label=" ", options=cats, default=cats, key=f"cat_{i}_{j}"
                        )
                        df_to_show = df_to_show[df_to_show["question_category"].isin(
                            selected)]

                    st.dataframe(
                        df_to_show, use_container_width=True)


def all_view(df, status):
    conflicts = status['conflicts']

    st.subheader('🔍 Подробнее: подозрительные ответы')
    if conflicts == 0:
        st.success("*Нет подозрительных ответов.*")
    else:
        suspicious_df = df[df["conflict_metric"] == 1][
            ["user_question", "answer", "question_category",
                "response_time", "user_mark"]
        ].reset_index(drop=True)

        # --- Фильтр по категории ---
        available_cats = suspicious_df["question_category"].dropna(
        ).unique().tolist()
        selected_cats = st.multiselect(
            label=' ', options=available_cats, default=available_cats, key="filter_cats_allview")
        suspicious_df = suspicious_df[suspicious_df["question_category"].isin(
            selected_cats)]

        # # --- Поиск по тексту ---
        # search_text = st.text_input("🔍 Поиск по вопросу", key="search_allview")
        # if search_text:
        #     suspicious_df = suspicious_df[suspicious_df["user_question"].str.contains(
        #         search_text, case=False, na=False)]

        st.dataframe(suspicious_df, use_container_width=True, height=350)

    # --- Категории с высоким % ошибок ---
    st.markdown("### 📌 Подозрительные категории")

    if conflicts == 0:
        st.success("Нет категорий с превышением порога.")
    else:
        suspicious = (
            df[df["conflict_metric"] == 1]
            .groupby("question_category")
            .size()
            .sort_values(ascending=False)
            .reset_index(name="count")
        )
        total_per_cat = (
            df.groupby("question_category").size().reset_index(name="total")
        )
        merged = suspicious.merge(total_per_cat, on="question_category")
        merged["percent"] = round(merged["count"] / merged["total"] * 100, 1)

        # --- Настраиваемый порог ---
        threshold = st.slider(
            "⚠️ Порог процента подозрительных ответов", min_value=0, max_value=100, value=20)
        merged = merged[merged["percent"] > threshold]

        if merged.empty:
            st.success("Нет категорий с высоким уровнем конфликтов.")
        else:
            st.warning(
                "Обнаружены категории с повышенным уровнем подозрительных ответов:")
            st.dataframe(merged, use_container_width=True, height=300)


main()
