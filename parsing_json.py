import json
import re
import ast
from typing import List, Dict, Any
import pandas as pd
from prepocess_calculate.metrics import *


def _clean_text(text: str) -> str:
    """Очистка текста"""
    if not text: return ''
    return re.sub(r'\\[nrt]|[\n\r\t]+|\s+', ' ', text).strip()


def parse_all_data(file_path: str) -> List[Dict[str, Any]]:
    """Парсинг всех данных"""
    return _parse_data(file_path, include_time=True)


def _parse_data(file_path: str, include_time: bool) -> List[Dict[str, Any]]:
    """Базовая функция парсинга"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = []
    for item in data:
        context = _clean_text(" ".join(item['chat_history']['cleaned_contexts']))
        answer = _clean_text(item['chat_history']['old_answers'][0])
        parsed = {
            'selected_role': item['Выбранная роль'],
            'campus': item['Кампус'],
            'education_level': item['Уровень образования'],
            'question_category': item['Категория вопроса'],
            'user_question': _clean_text(item['chat_history']['old_questions'][0]),
            'user_filters': item['user_filters'],
            'question_filters': item['question_filters'],
            'answer': answer,
            'user_mark': 1 if item['Оценка пользователя'] == "+" else 0,
            'contexts': context,
            'answer_correctness_literal': answer_correctness_literal(context, answer),
            'answer_correctness_neural': answer_correctness_neural(context, answer)
        }

        if include_time:
            parsed.update({
                'response_time': item['Время ответа модели']
            })

        result.append(parsed)

    return result


if __name__ == "__main__":
    df = pd.DataFrame(parse_all_data("logs/new_logs.json"))
    df.to_csv('result.csv')
    df.to_excel('result.xlsx')
