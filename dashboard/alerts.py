import pandas as pd
import streamlit as st


def show_system_alert(df: pd.DataFrame):
    total = len(df)
    conflicts = df["conflict_metric"].sum()
    percent = round(conflicts / total * 100, 1) if total else 0
    color_code = "blue"

    # --- Цветовая индикация ---
    if percent < 10:
        color = "#d4edda"
        border = "#28a745"
        emoji = "✅"
        msg = "Система работает стабильно"
        color_code = "green"
    elif percent < 25:
        color = "#fff3cd"
        border = "#ffc107"
        emoji = "⚠️"
        msg = "Повышен уровень подозрительных ответов"
        color_code = "yellow"
    else:
        color = "#f8d7da"
        border = "#dc3545"
        emoji = "🛑"
        msg = "Высокий процент ошибок. Необходима проверка"
        color_code = "red"

    # --- Баннер ---
    st.markdown(f"""
    <div style="
        background-color: {color};
        border-left: 6px solid {border};
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        color: #212529;
        font-family: sans-serif;">
        <h4 style="margin:0; font-weight: bold; color: #212529; text-shadow: 0 0 1px rgba(0,0,0,0.1);">
            {emoji} {msg}
        </h4>
        <p style="margin:0.5rem 0 0; font-size: 0.95rem; color: #333;">
            Подозрительных ответов: <b>{conflicts} из {total}</b> ({percent}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Раскрывающийся блок с деталями ---
    with st.expander("🔍 Подробнее: подозрительные ответы"):
        if conflicts == 0:
            st.markdown("*Нет подозрительных ответов.*")
        else:
            st.dataframe(
                df[df["conflict_metric"] == 1][
                    ["user_question", "answer", "question_category", "response_time"]
                ].reset_index(drop=True),
                use_container_width=True
            )

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
        merged = merged[merged["percent"] > 20]  # Порог

        if merged.empty:
            st.info("Нет категорий с высоким уровнем конфликтов.")
        else:
            st.warning(
                "Обнаружены категории с повышенным уровнем подозрительных ответов:")
            st.dataframe(merged, use_container_width=True)
    return color_code 

