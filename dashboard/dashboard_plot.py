import locale

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU')
    except:
        pass


def show_plot_with_download_below(fig, filename: str):
    st.plotly_chart(fig, use_container_width=True)
    try:
        img_bytes = fig.to_image(format="png")
        st.download_button(
            label="Скачать график",
            data=img_bytes,
            file_name=f"{filename}.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"Ошибка экспорта: {e}")


class Plots:
    def __init__(self, data, color_sequence=None):
        self.data = data
        self.color_sequence = color_sequence or px.colors.qualitative.Plotly

    def plot_pie_chart(self, column: str, _unused_title: str):
        if self.data.empty or column not in self.data.columns or self.data[column].dropna().empty:
            return st.info("Нет данных для построения графика")
        counts = self.data[column].value_counts()
        fig = px.pie(
            names=counts.index,
            values=counts.values,
            hole=0.4,
            color_discrete_sequence=self.color_sequence
        )
        show_plot_with_download_below(fig, f"pie_{column}")

    def plot_bar_chart(self, column: str, _unused_title: str, x_label: str, y_label: str):
        if self.data.empty or column not in self.data.columns or self.data[column].dropna().empty:
            return st.info("Нет данных для построения графика")
        counts = self.data[column].value_counts()
        if counts.empty:
            return st.info("Нет данных для построения графика")
        fig = px.bar(
            x=counts.index,
            y=counts.values,
            labels={'x': x_label, 'y': y_label},
            text_auto=True,
            color_discrete_sequence=self.color_sequence
        )
        show_plot_with_download_below(fig, f"bar_{column}")

    def plot_response_time_chart_with_campus(self):
        if self.data.empty or "campus" not in self.data.columns or "response_time" not in self.data.columns:
            return st.info("Нет данных для построения графика")
        group_data = self.data.groupby(
            "campus")["response_time"].mean().reset_index()
        if group_data.empty:
            return st.info("Нет данных для построения графика")
        fig = px.bar(
            group_data,
            x="campus",
            y="response_time",
            color="campus",
            text_auto=True,
            color_discrete_sequence=self.color_sequence
        )
        show_plot_with_download_below(fig, "resp_time_by_campus")

    def plot_averaged_response_time_chart(self, bin_size: int = 10):
        if self.data.empty or "response_time" not in self.data.columns:
            return st.info("Нет данных для построения графика")
        df_copy = self.data.copy()
        df_copy["group"] = df_copy.index // bin_size
        grouped = df_copy.groupby(
            "group")["response_time"].mean().reset_index()
        fig = px.bar(
            grouped,
            x="group",
            y="response_time",
            labels={"group": f"Номер группы (по {bin_size} запросов)",
                    "response_time": "Среднее время ответа (сек)"}
        )
        show_plot_with_download_below(fig, "resp_time_averaged")

    def plot_follow_up_pie_chart(self):
        if self.data.empty:
            return st.info("Нет данных для построения графика")
        flag = "has_chat_history" if "has_chat_history" in self.data.columns else "has_contexts"
        if flag not in self.data.columns or self.data[flag].dropna().empty:
            return st.info("Нет данных для построения графика")
        avg_flag = self.data[flag].mean()
        fig = px.pie(
            names=["Без уточнений", "С уточнениями"],
            values=[1 - avg_flag, avg_flag],
            hole=0.3,
            color_discrete_sequence=self.color_sequence
        )
        show_plot_with_download_below(fig, "follow_up_pie")

    def plot_conflict_metric(self, bar_color=None, background_color=None):
        bar_color = bar_color or "#FF6666"  # цвет стрелки
        background_color = background_color or "#222222"

        if self.data.empty or "conflict_metric" not in self.data.columns:
            return st.info("Нет данных для построения графика")

        conflict_rate = self.data["conflict_metric"].mean() * 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conflict_rate,
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': bar_color},
                'bgcolor': background_color,
                'steps': [
                    {'range': [0, 100], 'color': background_color}
                ],
            },
            number={'font': {'color': bar_color}}
        ))

        st.plotly_chart(fig, use_container_width=True)

    def plot_response_time_by_category(self):
        if self.data.empty or "question_category" not in self.data.columns or "response_time" not in self.data.columns:
            return st.info("Нет данных для построения графика")
        grouped = self.data.groupby("question_category")[
            "response_time"].mean().reset_index()
        if grouped.empty:
            return st.info("Нет данных для построения графика")
        fig = px.bar(
            grouped,
            x="question_category",
            y="response_time",
            text_auto=True,
            labels={'question_category': '', 'response_time': 'Среднее время'},
            color_discrete_sequence=self.color_sequence
        )
        show_plot_with_download_below(fig, "resp_time_by_category")

    def plot_response_time_boxplot(self):
        if self.data.empty or "response_time" not in self.data.columns:
            return st.info("Нет данных для построения графика")
        fig = px.box(
            self.data,
            y="response_time",
            color_discrete_sequence=self.color_sequence
        )
        show_plot_with_download_below(fig, "resp_time_boxplot")

    def plot_quality_metrics_separate(self):
        needed_cols = [
            "question_category",
            "user_mark",
            "faithfulness_score_entailment",
            "faithfulness_score_neutral",
            "faithfulness_score_contradiction",
            "answer_correctness_literal",
            "answer_correctness_neural"
        ]
        for c in needed_cols:
            if c not in self.data.columns:
                return st.info(f"Нет столбца '{c}' для построения метрик.")

        metrics = needed_cols[1:]
        cols = st.columns(3)
        for i, metric in enumerate(metrics):
            grouped = self.data.groupby("question_category")[
                metric].mean().reset_index()
            fig = px.bar(
                grouped,
                x="question_category",
                y=metric,
                title=f"Метрика: {metric}",
                labels={"question_category": "Категория", metric: "Среднее"}
            )
            with cols[i % 3]:
                show_plot_with_download_below(fig, f"separate_{metric}")

    def plot_quality_metrics_combined(self):
        needed_cols = [
            "question_category",
            "user_mark",
            "faithfulness_score_entailment",
            "faithfulness_score_neutral",
            "faithfulness_score_contradiction",
            "answer_correctness_literal",
            "answer_correctness_neural"
        ]
        for c in needed_cols:
            if c not in self.data.columns:
                return st.info(f"Нет столбца '{c}' для построения метрик.")

        metrics = needed_cols[1:]
        grouped = self.data.groupby("question_category")[
            metrics].mean().reset_index()

        # нормализуем в пределах [0; 100]
        for metric in metrics:
            max_val = grouped[metric].max()
            if max_val > 0:
                grouped[metric] = grouped[metric] / max_val * 100

        melted = grouped.melt(
            id_vars="question_category",
            value_vars=metrics,
            var_name="Метрика",
            value_name="Значение"
        )

        fig = px.bar(
            melted,
            x="question_category",
            y="Значение",
            color="Метрика",
            barmode="group",
            title="Сводный график метрик качества",
            labels={"question_category": "Категория",
                    "Значение": "Среднее (0–100)"}
        )
        show_plot_with_download_below(fig, "combined_quality_metrics")

    def plot_user_mark_distribution(self):
        if self.data.empty or "user_mark" not in self.data.columns:
            return st.info("Нет данных для оценки пользователей")
        fig = px.histogram(
            self.data,
            x="user_mark",
            nbins=3,
            title="Распределение пользовательских оценок",
            color_discrete_sequence=self.color_sequence
        )
        fig.update_layout(xaxis_title="Оценка", yaxis_title="Количество")
        show_plot_with_download_below(fig, "user_mark_distribution")

    def plot_naive_text_metrics(self):
        metrics = [
            ("sentence_count", "Количество предложений"),
            ("word_count", "Количество слов"),
            ("avg_sentence_len", "Средняя длина предложения"),
            ("unique_word_ratio", "Процент уникальных слов")
        ]
        rows = [st.columns(2), st.columns(2)]
        for i, (colname, label) in enumerate(metrics):
            if colname in self.data.columns:
                with rows[i // 2][i % 2]:
                    fig = px.histogram(
                        self.data,
                        x=colname,
                        title=label,
                        marginal="box",
                        color_discrete_sequence=self.color_sequence
                    )
                    fig.update_layout(showlegend=False)
                    show_plot_with_download_below(fig, f"naive_{colname}")

    def plot_faithfulness_scores(self):
        cols = [
            "faithfulness_score_entailment",
            "faithfulness_score_neutral",
            "faithfulness_score_contradiction"
        ]
        if any(c not in self.data.columns for c in cols):
            return st.info("Отсутствуют показатели faithfulness_score")

        melted = self.data[cols].copy()
        melted["index"] = melted.index
        melted = melted.melt(
            id_vars="index", var_name="Тип", value_name="Значение")

        fig = px.violin(
            melted,
            y="Значение",
            x="Тип",
            box=True,
            points="all",
            color="Тип",
            title="Faithfulness Score — насколько ответ логически соответствует извлечённым документам",
            color_discrete_sequence=self.color_sequence
        )
        fig.update_layout(xaxis_title="Класс соответствия",
                          yaxis_title="Вероятность")
        show_plot_with_download_below(fig, "faithfulness_scores")

    def plot_answer_correctness(self):
        if "answer_correctness_literal" not in self.data.columns or "answer_correctness_neural" not in self.data.columns:
            return st.info("Отсутствуют показатели answer_correctness")

        try:
            import statsmodels.api
            fig = px.scatter(
                self.data,
                x="answer_correctness_literal",
                y="answer_correctness_neural",
                trendline="ols",
                title="Сходство ответа с контекстом (лингвистическое vs семантическое)",
                labels={
                    "answer_correctness_literal": "Literal (лингвистическое)",
                    "answer_correctness_neural": "Neural (семантическое)"
                },
                color_discrete_sequence=self.color_sequence
            )
            fig.update_traces(selector=dict(mode="lines"),
                              line=dict(width=3, color="orange"))
        except ImportError:
            st.warning(
                "Модуль `statsmodels` не установлен — трендлиния не будет отображаться.")
            fig = px.scatter(
                self.data,
                x="answer_correctness_literal",
                y="answer_correctness_neural",
                title="Сходство ответа с контекстом",
                labels={
                    "answer_correctness_literal": "Literal (лингвистическое)",
                    "answer_correctness_neural": "Neural (семантическое)"
                },
                color_discrete_sequence=self.color_sequence
            )

        fig.update_layout(
            xaxis_title="Лингвистическая схожесть",
            yaxis_title="Семантическая схожесть"
        )
        show_plot_with_download_below(fig, "answer_correctness")

    def plot_avg_user_mark_by_category(self):
        if self.data.empty or "question_category" not in self.data.columns or "user_mark" not in self.data.columns:
            return st.info("Нет данных для оценки по категориям")

        df_copy = self.data.copy()

        grouped = df_copy.groupby("question_category")["user_mark"].agg(
            good=lambda x: (x == 1).sum(),
            bad=lambda x: (x == -1).sum()
        ).reset_index()

        melted = grouped.melt(
            id_vars="question_category",
            value_vars=["good", "bad"],
            var_name="Тип оценки",
            value_name="Количество"
        )

        melted["Тип оценки"] = melted["Тип оценки"].map({
            "good": "Положительные",
            "bad": "Отрицательные"
        })

        fig = px.bar(
            melted,
            x="question_category",
            y="Количество",
            color="Тип оценки",
            text_auto=True,
            labels={"question_category": ""},
            color_discrete_sequence=self.color_sequence
        )

        fig.update_layout(xaxis=dict(categoryorder="total descending"))

        show_plot_with_download_below(fig, "user_mark_counts_by_category")


def plot_metric_trend_over_time(df: pd.DataFrame, column: str, color=None, inverse=True, height=160, epsilon=0.01, window=5):
    if df.empty or column not in df.columns or "time_question" not in df.columns:
        st.info("Нет данных для тренда по дням")
        return

    df["time_question"] = pd.to_datetime(df["time_question"])
    df["date"] = df["time_question"].dt.date

    if column == "user_mark":
        daily = df.groupby("date")["user_mark"].apply(
            lambda x: (x < 0).sum()
        ).reset_index(name="value")
    else:
        daily = df.groupby("date")[column].mean().reset_index(name="value")

    daily = daily.sort_values("date").reset_index(drop=True)

    if column != "user_mark":
        daily["rolling"] = daily["value"].rolling(
            window=window, min_periods=1).mean()
    else:
        daily["rolling"] = daily["value"]

    x = pd.to_datetime(daily["date"]).dt.strftime(
        '%d %b').str.replace('.', '', regex=False)
    y = daily["rolling"]

    if color is None:
        color = "#888888"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(size=5),
        name=column
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=20),
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True, key=f"plot_{column}")
