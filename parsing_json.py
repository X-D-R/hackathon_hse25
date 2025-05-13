import json
import re
from typing import Dict, Any
import pandas as pd

from prepocess_calculate.metrics import *
from profiling import Profiler


class LogsAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def _clean_text(text: str) -> str:
        """Очистка текста"""
        if not text:
            return ''
        return re.sub(r'\\[nrt]|[\n\r\t]+|\s+', ' ', text).strip()

    def parse_all_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Парсинг всех данных"""
        return self._parse_data(file_path, include_time=True)

    def parse_item(self, item: Dict, metric_obj: MetricsCalculator, include_time: bool):
        context = self._clean_text(" ".join(item['chat_history']['cleaned_contexts']))
        answer = self._clean_text(item['chat_history']['old_answers'][0])
        parsed = {
            'selected_role': item['Выбранная роль'],
            'campus': item['Кампус'],
            'education_level': item['Уровень образования'],
            'question_category': item['Категория вопроса'],
            'user_question': self._clean_text(item['chat_history']['old_questions'][0]),
            'user_filters': item['user_filters'],
            'question_filters': item['question_filters'],
            'answer': answer,
            'user_mark': 1 if item['Оценка пользователя'] == "+" else -1 if item['Оценка пользователя'] == "-" else 0,
            'contexts': context,
            'answer_correctness_literal': metric_obj.answer_correctness_literal(context, answer),  # time narrow space
            'answer_correctness_neural': metric_obj.answer_correctness_neural(context, answer)  # time narrow space
        }

        if include_time:
            parsed.update({
                'response_time': item['Время ответа модели']
            })

        return parsed

    def _parse_data(self, file_path: str, include_time: bool) -> List[Dict[str, Any]]:
        """Базовая функция парсинга"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise

        metric_obj = MetricsCalculator()
        result = []
        for item in data:
            result.append(self.parse_item(item, metric_obj, include_time))

        return result

    def export_data(self, data: List[Dict[str, Any]], output_name: str = "result", extension: str = "json") -> None:
        """Экспорт данных в различные форматы"""
        df = pd.DataFrame(data)

        if extension == "csv":
            df.to_csv(f"{output_name}.csv", index=False)
        elif extension == "xlsx":
            df.to_excel(f"{output_name}.xlsx", index=False)
        elif extension == "json":
            df.to_json(f"{output_name}.json", index=False)
        else:
            print("Unsupported format")


def main():
    log_obj = LogsAnalyzer()
    data = log_obj.parse_all_data("logs/new_logs.json")
    log_obj.export_data(data, output_name="result", extension="xlsx")


if __name__ == "__main__":
    profiler = Profiler(output_dir="profiling_results")
    profiler.run_with_profiling(main)
