import json
import os
import sys

import requests
from loguru import logger

from .parsed_data_cache import ParsedCacheManager
from .parsing_json import LogsAnalyzer

logger.remove()

logger.add(
    sys.stdout,
    format="{time:HH:mm:ss} | {level: <7}| {message}",
    level="INFO"
)

logger.add(
    "../logs/pipeline.log",
    rotation="00:00",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {message}",
    retention="1 month",
)

FILE_PATH = 'data/'
LOG_PATH = f"{FILE_PATH}log3.json"
LAST_TIME_FILE = f"{FILE_PATH}last_log_time.txt"
RESULT_PATH = f"{FILE_PATH}result.json"
RESULT_XLSX = f"{FILE_PATH}result.xlsx"

# --- 1. Подгружаем логи с сервера ---


def fetch_logs():
    url = "http://46.229.141.86:44455/get_logs"
    search_request = {
        "log_name": "actual_july_logs.json",
    }

    try:
        response = requests.post(url, json=search_request)
        if response.status_code == 200:
            data = response.json()
            with open(LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Логи обновлены. Последнее время: {data.get('time')}")
        else:
            logger.warning(f"Ошибка при запросе логов: {response.status_code}")
    except Exception as e:
        logger.exception(f"Ошибка при загрузке логов: {e}")


# --- 2. Основной пайплайн ---
def load_logs():
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        full_data = json.load(f)
    logs = full_data["logs"]
    time = full_data["time"]
    return logs, time


def load_last_time() -> str:
    if os.path.exists(LAST_TIME_FILE):
        with open(LAST_TIME_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_last_time(time: str):
    with open(LAST_TIME_FILE, "w", encoding="utf-8") as f:
        f.write(time)


def pipeline():
    fetch_logs()

    logs, current_time = load_logs()
    last_time = load_last_time()

    if current_time == last_time:
        logger.info("⏸ Логи не изменились — парсинг пропущен.")
        return

    logger.info("🔄 Обнаружены изменения — выполняется парсинг...")
    analyzer = LogsAnalyzer()
    cache = ParsedCacheManager()

    parsed_count = 0
    for item in logs:
        ts = item.get("Дата вопроса")
        if not ts or cache.is_already_parsed(ts):
            continue

        parsed = analyzer.parse_item(item, analyzer.metric_obj)
        cache.add_parsed_entry(ts, parsed)
        parsed_count += 1

    if parsed_count == 0:
        logger.success("✅ Все записи уже были обработаны.")
    else:
        cache.save()
        all_data = cache.get_all()
        analyzer.export_data(all_data, RESULT_PATH.replace(
            ".json", ""), extension="json")
        logger.success(f"✅ Добавлено новых записей: {parsed_count}")

    save_last_time(current_time)
