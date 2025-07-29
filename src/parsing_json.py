import json
from typing import Dict, Any
import pandas as pd

from metrics import *


class LogsAnalyzer:
    def __init__(self):
        self.clean_text = re.compile(r'\\[nrt]|[\n\r\t]|\s+')

    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not text:
            return ''
        return self.clean_text.sub(' ', text).strip()

    def _extract_topic_tags(self, text: str):
        topic_tag_pattern = r"'([^']+)'(?=\s*,|\s*\])"
        tags = re.findall(topic_tag_pattern, text)
        return tags

    def _extract_urls(self, text: str):
        url_pattern = r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s\'",]*)?'
        urls = re.findall(url_pattern, text)
        return urls

    def _extract_contents(self, text: str):
        pattern = r"page_content\s*=\s*'(.*?)'"
        page_contents = re.findall(pattern, text, re.DOTALL)
        return page_contents

    def parse_all_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Парсинг всех данных"""
        return self._parse_data(file_path)

    def parse_item(self, item: Dict, metric_obj: MetricsCalculator):
        context = self._clean_text(" ".join(item['chat_history']['cleaned_contexts']))[:1000]
        if len(context) == 0:
            context = "Cleaned context is empty, getting info from page contents in contexts: " + self._clean_text(
                " ".join(self._extract_contents(item['chat_history']['old_contexts'][0])))[:1000]
        answer = self._clean_text(item['chat_history']['old_answers'][0])[:1000]
        naive_text_fluency = metric_obj.naive_text_fluency(answer)
        faithfulness_score = metric_obj.faithfulness_score(context, answer)
        question = self._clean_text(item['chat_history']['old_questions'][0])
        user_filters = item['user_filters']
        question_filters = item['question_filters']
        context_filters = self._extract_topic_tags(" ".join(item['chat_history']['old_contexts']))
        context_urls = self._extract_urls(item['chat_history']['old_contexts'][0])
        question_length = len(question.split())
        context_count = item['chat_history']['old_contexts'][0].count("Document")
        if "Размышления модели" in item:
            reasoning = item["Размышления модели"]
            relevance = item["Релевантность контекста"]
        else:
            reasoning = None
            relevance = None

        parsed = {
            # Основные данные
            'selected_role': item['Выбранная роль'],
            'campus': item['Кампус'],
            'education_level': item['Уровень образования'],
            'question_category': item['Категория вопроса'],
            'user_question': question,
            'user_filters': user_filters,
            'question_filters': question_filters,
            'context_filters': context_filters,
            'answer': answer,
            'user_mark': 1 if item['Оценка пользователя'] == "+" else -1 if item['Оценка пользователя'] == "-" else 0,
            'contexts': context,
            'time': item['Дата вопроса'],

            # Дополнительные данные
            'context_urls': context_urls,
            'question_length': question_length,
            'context_count': context_count,
            'answer_length': len(answer.split()),
            'contains_links': bool('http' in answer),
            'reasoning': reasoning,
            'response_time': item['Время ответа модели'],

            # Текстовые оценки
            'sentence_count': naive_text_fluency['sentence_count'],
            'word_count': naive_text_fluency['word_count'],
            'avg_sentence_len': naive_text_fluency['avg_sentence_len'],
            'unique_word_ratio': naive_text_fluency['unique_word_ratio'],

            # Основные метрики
            'faithfulness_score_entailment': faithfulness_score['entailment'],
            'faithfulness_score_neutral': faithfulness_score['neutral'],
            'faithfulness_score_contradiction': faithfulness_score['contradiction'],
            'answer_correctness_literal': metric_obj.answer_correctness_literal(context, answer),
            'answer_correctness_neural': metric_obj.answer_correctness_neural(context, answer),
            'answer_relevance': metric_obj.answer_relevance(question, answer),
            'jaccard_similarity': metric_obj.jaccard_similarity(set(question_filters), set(context_filters)),
            'cosine_tag_answer': metric_obj.cosine_tag_answer("".join(question_filters), answer),
            'relevance': relevance,
        }

        return parsed

    def _parse_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Базовая функция парсинга"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise

        metric_obj = MetricsCalculator()
        result = []
        for item in data:
            result.append(self.parse_item(item, metric_obj))

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
    folder = '../data/'
    data = log_obj.parse_all_data(f"{folder}log.json")
    log_obj.export_data(data, output_name=f"{folder}result", extension="xlsx")
    log_obj.export_data(data, output_name=f"{folder}result", extension="json")


if __name__ == "__main__":
    main()
