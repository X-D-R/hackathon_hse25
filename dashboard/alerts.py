import pandas as pd
import streamlit as st


def get_system_alert_status(df: pd.DataFrame) -> dict:
    total = len(df)
    conflicts = df["conflict_metric"].sum()
    percent = round(conflicts / total * 100, 1) if total else 0

    if percent <= 10:
        return {
            "emoji": "✅",
            "color": "#d4edda",
            "border": "#28a745",
            "message": "Система работает стабильно",
            "level": "green",
            "conflicts": conflicts,
            "total": total,
            "percent": percent
        }
    elif percent <= 25:
        return {
            "emoji": "⚠️",
            "color": "#fff3cd",
            "border": "#ffc107",
            "message": "Повышен уровень подозрительных ответов",
            "level": "yellow",
            "conflicts": conflicts,
            "total": total,
            "percent": percent
        }
    else:
        return {
            "emoji": "🛑",
            "color": "#f8d7da",
            "border": "#dc3545",
            "message": "Высокий процент ошибок. Необходима проверка",
            "level": "red",
            "conflicts": conflicts,
            "total": total,
            "percent": percent
        }


def render_system_alert(status: dict):
    st.markdown(f"""
    <div style="
        background-color: {status['color']};
        border-left: 6px solid {status['border']};
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        color: #212529;
        font-family: sans-serif;">
        <h4 style="margin:0; font-weight: bold;">
            {status['emoji']} {status['message']}
        </h4>
        <p style="margin:0.5rem 0 0;">
            Подозрительных ответов: <b>{status['conflicts']} из {status['total']}</b> ({status['percent']}%)
        </p>
    </div>
    """, unsafe_allow_html=True)
