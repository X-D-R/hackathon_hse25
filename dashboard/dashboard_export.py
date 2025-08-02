import io
import json

import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Font


def download_excel(df, filename="chatbot_logs.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Данные"

    column_mapping = {
        "selected_role": "Роль пользователя",
        "campus": "Кампус",
        "education_level": "Уровень образования",
        "question_category": "Категория вопроса",
        "user_question": "Вопрос пользователя",
        "user_filters": "Фильтры пользователя",
        "question_filters": "Фильтры вопроса",
        "context_filters": "Фильтры контекста",
        "answer": "Ответ AI",
        "user_mark": "Оценка пользователя",
        "contexts": "Контексты",
        "time_question": "Время вопроса",
        "context_urls": "Ссылки на источники",
        "question_length": "Длина вопроса",
        "context_count": "Кол-во контекстов",
        "answer_length": "Длина ответа",
        "contains_links": "Содержит ссылки",
        "reasoning": "Наличие рассуждений",
        "response_time": "Время ответа (сек)",
        "sentence_count": "Кол-во предложений",
        "word_count": "Кол-во слов",
        "avg_sentence_len": "Ср. длина предложения",
        "unique_word_ratio": "Уникальность слов (%)",
        "faithfulness_score_entailment": "Правдоподобие: подтверждение",
        "faithfulness_score_neutral": "Правдоподобие: нейтральное",
        "faithfulness_score_contradiction": "Правдоподобие: противоречие",
        "answer_correctness_literal": "Точность ответа (буквальная)",
        "answer_correctness_neural": "Точность ответа (нейронная)",
        "answer_relevance": "Актуальность ответа",
        "jaccard_similarity": "Сходство (Жаккар)",
        "cosine_tag_answer": "Косинусная близость (теги-ответ)",
        "relevance": "Релевантность",
        "has_contexts": "Есть контексты",
        "conflict_metric": "Метрика конфликта"
    }

    translated_headers = [column_mapping.get(col, col) for col in df.columns]
    ws.append(translated_headers)

    # Данные
    for row in df.itertuples(index=False):
        safe_row = []
        for cell in row:
            if isinstance(cell, list):
                safe_row.append(", ".join(map(str, cell)))
            else:
                safe_row.append(str(cell) if cell is not None else "")
        ws.append(safe_row)

    for col in ws.columns:
        max_len = max(len(str(cell.value))
                      if cell.value else 0 for cell in col)
        col_letter = col[0].column_letter
        ws.column_dimensions[col_letter].width = max_len + 2

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    st.download_button(
        label="📥 Скачать Excel",
        data=output,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def download_json(data):
    json_data = json.dumps(data, indent=4, ensure_ascii=False, default=str)
    st.download_button(
        label="📥 Скачать JSON",
        data=json_data,
        file_name="chatbot_logs.json",
        mime="application/json"
    )
