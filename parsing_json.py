import json
import re
from typing import Dict, Any
import pandas as pd

from prepocess_calculate.metrics import *
from profiling import Profiler


class LogsAnalyzer:
    def __init__(self):
        self.clean_text = re.compile(r'\\[nrt]|[\n\r\t]|\s+')

    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not text:
            return ''
        return self.clean_text.sub(' ', text).strip()

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
            df.to_json(f"{output_name}.json", orient='records', indent=2, force_ascii=False)
        else:
            print("Unsupported format")


def main():
    log_obj = LogsAnalyzer()
    data = log_obj.parse_all_data("logs/new_logs.json")
    log_obj.export_data(data, output_name="result", extension="json")


def check_export(data: List[Dict[str, Any]]):
    log_obj = LogsAnalyzer()
    log_obj.export_data(data, output_name="result", extension="json")


def check_clean_text():
    log_obj = LogsAnalyzer()
    data = log_obj._clean_text("студентов равно двум — это значит, что у студента две задолженности, и он допускается "
                               "к пересдачам, но если получит третью неудовлетворительную оценку, то будет отчислен. "
                               "Критическое значение КУД (качество учебной деятельности) для студентов, относящихся к "
                               "отдельным категориям равно пяти , если превышение обычного КУД (качество учебной "
                               "деятельности) в отношении студента зафиксировано в первый раз . Студенты, "
                               "КУД (качество учебной деятельности) которых превышает критическое значение (с учетом "
                               "отнесения студента к отдельной категории и наличия или отсутствия повтора критической "
                               "ситуации), подлежат отчислению как не выполняющие обязанности по добросовестному "
                               "освоению образовательной программы и выполнению учебного плана. Подробнее об "
                               "отдельных категориях студентов . Пример расчета обычного КУД (качество учебной "
                               "деятельности) : КУД=0 — у студента нет задолженностей, все хорошо КУД=2 — у студента "
                               "две задолженности, он допускается к пересдачам КУД=4 — у студента четыре "
                               "задолженности, он подлежит отчислению Документы Положение об организации "
                               "промежуточной аттестации и текущего контроля успеваемости студентов НИУ (Национальный "
                               "исследовательский университет) ВШЭ (Высшая школа экономики) (ПО")


if __name__ == "__main__":
    profiler = Profiler(output_dir="profiling_results")
    profiler.run_with_profiling(main)
    # timer = timeit.Timer(lambda: main())
    # times = timer.repeat(repeat=1000, number=1)
    # print(f"Overall time: {sum(times)}")
    # print(f"Mean time: {sum(times) / len(times)}")
