from typing import List

import evaluate
import numpy as np


class MetricsCalculator:
    def __init__(self):
        self.rouge = evaluate.load("rouge")
        self.bleu = evaluate.load("bleu")
        self.chrf = evaluate.load("chrf")
        self.bertscore = evaluate.load("bertscore")

    def context_recall(self, ground_truth: str, contexts: List[str]) -> float:
        """
        Calc rouge btw contexts and ground truth.
        Interpretation: ngram match (recall) btw contexts and desired answer.

        ROUGE - https://huggingface.co/spaces/evaluate-metric/rouge

        return: average rouge for all contexts.
        """
        rs = []
        for c in contexts:
            rs.append(
                self.rouge.compute(
                    predictions=[str(c)],
                    references=[str(ground_truth)],
                )["rouge2"]
            )

        return float(np.mean(rs))

    def context_precision(self, ground_truth: str, contexts: List[str]) -> float:
        """
        Calc blue btw contexts and ground truth.
        Interpretation: ngram match (precision) btw contexts and desired answer.

        BLEU - https://aclanthology.org/P02-1040.pdf
        max_order - max n-grams to count

        return: average bleu (precision2, w/o brevity penalty) for all contexts.
        """
        bs = []
        for c in contexts:

            try:
                bs.append(
                    self.bleu.compute(
                        predictions=[str(c)],
                        references=[str(ground_truth)],
                        max_order=2,
                    )["precisions"][1]
                )
            except ZeroDivisionError:
                bs.append(0)

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
