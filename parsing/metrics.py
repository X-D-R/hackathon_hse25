import re
from typing import List

import evaluate
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers.pipelines import pipeline


class MetricsCalculator:
    def __init__(self):
        self.rouge = evaluate.load("rouge")
        self.bleu = evaluate.load("bleu")
        self.chrf = evaluate.load("chrf")
        self.bertscore = evaluate.load("bertscore")
        self.faithfulness_model = pipeline("text-classification",
                                           model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
                                           top_k=None,
                                           device=-1)
        self.relevance_model = SentenceTransformer("all-MiniLM-L6-v2")

    def context_recall(self, ground_truth: str, contexts: List[str]) -> float:
        """
        Calc rouge btw contexts and ground truth.
        Interpretation: ngram match (recall) btw contexts and desired answer.

        ROUGE - https://huggingface.co/spaces/evaluate-metric/rouge

        return: average rouge for all contexts.
        """
        rs = [self.rouge.compute(
            predictions=[str(c)],
            references=[str(ground_truth)],
        )["rouge2"] for c in contexts]

        return float(np.mean(rs))

    def _safe_bleu_precision(self, context, ground_truth):
        try:
            return self.bleu.compute(
                predictions=[str(context)],
                references=[str(ground_truth)],
                max_order=2,
            )["precisions"][1]
        except ZeroDivisionError:
            return 0

    def context_precision(self, ground_truth: str, contexts: List[str]) -> float:
        """
        Calc blue btw contexts and ground truth.
        Interpretation: ngram match (precision) btw contexts and desired answer.

        BLEU - https://aclanthology.org/P02-1040.pdf
        max_order - max n-grams to count

        return: average bleu (precision2, w/o brevity penalty) for all contexts.
        """
        bs = [self._safe_bleu_precision(c, ground_truth) for c in contexts]

        return float(np.mean(bs))

    def answer_correctness_literal(
            self,
            ground_truth: str,
            answer: str,
            char_order: int = 6,
            word_order: int = 2,
            beta: float = 1,
    ) -> float:
        """
        Calc chrF btw answer and ground truth.
        Interpretation: lingustic match btw answer and desired answer.

        chrF - https://aclanthology.org/W15-3049.pdf
        char_order - n-gram length for chars, default is 6 (from the article)
        word_order - n-gram length for words (chrF++), default is 2 (as it outperforms simple chrF)
        beta - recall weight, beta=1 - simple F1-score

        return: chrF for answ and gt.
        """

        score = self.chrf.compute(
            predictions=[str(answer)],
            references=[str(ground_truth)],
            word_order=word_order,
            char_order=char_order,
            beta=beta,
        )["score"]

        return score

    def answer_correctness_neural(
            self,
            ground_truth: str,
            answer: str,
            model_type: str = "cointegrated/rut5-base",
    ) -> float:
        """
        Calc bertscore btw answer and ground truth.
        Interpretation: semantic cimilarity btw answer and desired answer.

        BertScore - https://arxiv.org/pdf/1904.09675.pdf
        model_type - embeds model  (default t5 as the best from my own research and experience)

        return: bertscore-f1 for answ and gt.
        """

        score = self.bertscore.compute(
            predictions=[str(answer)],
            references=[str(ground_truth)],
            batch_size=1,
            model_type=model_type,
            num_layers=11,
        )["f1"]

        return score[0]

    def naive_text_fluency(self, answer: str) -> dict:
        text_without_links = re.sub(r'http\S+|www\S+', '', answer)
        sentences = re.split(r'[.!?]', text_without_links)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return {
                "avg_sentence_len": 0,
                "unique_word_ratio": 0,
                "word_count": 0,
                "sentence_count": 0
            }
        words = re.findall(r'\b\w+\b', text_without_links.lower())
        metrics = {
            "sentence_count": len(sentences),
            "word_count": len(words),
            "avg_sentence_len": np.mean([len(re.findall(r'\b\w+\b', s)) for s in sentences]),
            "unique_word_ratio": len(set(words)) / len(words) if words else 0
        }
        return metrics

    def faithfulness_score(self, context: str, answer: str) -> dict:
        result = self.faithfulness_model(f"{context} [SEP] {answer}")
        faithfulness_scores = {item['label']: item['score'] for item in result[0]}
        return faithfulness_scores

    def answer_relevance(self, question: str, answer: str) -> float:
        query_embedding = self.relevance_model.encode(question)
        answer_embedding = self.relevance_model.encode(answer)
        similarity = cosine_similarity(
            [query_embedding], [answer_embedding])[0][0]
        return similarity

    def jaccard_similarity(self, set1, set2):
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0

    def cosine_tag_answer(self, tag: str, answer: str) -> float:
        query_embedding = self.relevance_model.encode(
            tag, convert_to_tensor=True)
        answer_embedding = self.relevance_model.encode(
            answer, convert_to_tensor=True)
        similarity = cosine_similarity(query_embedding.reshape(
            1, -1), answer_embedding.reshape(1, -1))[0][0]
        return float(similarity)
