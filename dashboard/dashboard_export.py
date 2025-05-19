import io
import json

import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Font


def create_excel_file(normal, bad, unsure):
    wb = Workbook()
    headers = [
        "Вопрос", "Ответ AI", "Категория вопроса",
        "user_filters", "question_filters", "Очищенный контекст", "Все контексты"
    ]

    def make_headers_bold(ws):
        for cell in ws[1]:
            cell.font = Font(bold=True)

    def set_manual_column_widths(ws):
        column_widths = {
            "A": 40, "B": 50, "C": 20, "D": 30, "E": 30, "F": 50, "G": 70
        }
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

    def fill_sheet(ws, data, title):
        ws.title = title
        ws.append(headers)
        make_headers_bold(ws)
        for case in data:
            ws.append([
                case.get("question", ""),
                case.get("answer", ""),
                case.get("question_category", ""),
                ", ".join(case.get("user_filters", [])),
                ", ".join(case.get("question_filters", [])),
                case.get("ground_truth", ""),
                "\n---\n".join(case.get("contexts", []))
            ])
        set_manual_column_widths(ws)

    ws1 = wb.active
    fill_sheet(ws1, normal, "Вопросы с ответом")
    fill_sheet(wb.create_sheet(), bad, "Вопросы без ответа")
    fill_sheet(wb.create_sheet(), unsure, "Частичный ответ")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def download_json(data):
    json_data = json.dumps(data, indent=4, ensure_ascii=False, default=str)
    st.download_button(
        label="📥 Скачать JSON",
        data=json_data,
        file_name="chatbot_logs.json",
        mime="application/json"
    )


def split_by_answer_quality(data):
    normal, bad, unsure = [], [], []
    for case in data:
        answer = case.get("answer", "")
        if not answer.strip():
            bad.append(case)
        elif any(x in answer.lower() for x in ["возможно", "не уверен", "не могу сказать"]):
            unsure.append(case)
        else:
            normal.append(case)
    return normal, bad, unsure
