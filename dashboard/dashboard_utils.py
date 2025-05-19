import json

import pandas as pd


def load_data(file_name: str):
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


def process_data(data):
    df = pd.DataFrame(data)

    if "chat_history" in df.columns:
        df["has_chat_history"] = df["chat_history"].apply(
            lambda x: len(x.get("old_questions", [])) > 0)
        df["conflict_metric"] = df.apply(
            lambda row: 1 if (len(row.get("chat_history", {}).get("old_questions", [])) > 1 and row["response_time"] > 3)
            else 0,
            axis=1
        )
    elif "contexts" in df.columns:
        df["has_contexts"] = df["contexts"].apply(
            lambda x: len(x) > 0 if isinstance(x, list) else False)
        df["conflict_metric"] = df.apply(
            lambda row: 1 if (row["has_contexts"] and len(row.get("contexts", [])) > 1 and row["response_time"] > 3)
            else 0,
            axis=1
        )
    else:
        df["conflict_metric"] = 0

    df["response_time"] = pd.to_numeric(df["response_time"], errors="coerce")
    return df
