import json
from typing import List

import pandas as pd
import streamlit as st


def load_data(file_name: str) -> List[dict]:
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("JSON-файл должен содержать список объектов.")
            return data
    except FileNotFoundError:
        st.error(f"Файл '{file_name}' не найден.")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Ошибка разбора JSON-файла: {e}")
        return []
    except ValueError as e:
        st.error(f"Неверный формат данных: {e}")
        return []


def process_data(data: List[dict]) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()

    try:
        df = pd.DataFrame(data)

        if "chat_history" in df.columns:
            df["has_chat_history"] = df["chat_history"].apply(
                lambda x: len(x.get("old_questions", [])
                              ) > 0 if isinstance(x, dict) else False
            )
            df["conflict_metric"] = df.apply(
                lambda row: 1 if (len(row.get("chat_history", {}).get("old_questions", [])) > 1
                                  and row.get("response_time", 0) > 3) else 0,
                axis=1
            )
        elif "contexts" in df.columns:
            df["has_contexts"] = df["contexts"].apply(
                lambda x: len(x) > 0 if isinstance(x, list) else False
            )
            df["conflict_metric"] = df.apply(
                lambda row: 1 if (row["has_contexts"] and len(row.get("contexts", [])) > 1
                                  and row.get("response_time", 0) > 3) else 0,
                axis=1
            )
        else:
            df["conflict_metric"] = 0

        df["response_time"] = pd.to_numeric(
            df.get("response_time", 0), errors="coerce")
        
        df["conflict_metric"] = 0

        if "user_mark" in df.columns:
            df.loc[df["user_mark"] < 0, "conflict_metric"] = 1

        if "response_time" in df.columns:
            df.loc[df["response_time"] > 10, "conflict_metric"] = 1

        if "is_conflict" in df.columns:
            df.loc[df["is_conflict"] == True, "conflict_metric"] = 1
        return df

    except Exception as e:
        st.error(f"Ошибка обработки данных: {e}")
        return pd.DataFrame()
