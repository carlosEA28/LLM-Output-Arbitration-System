"""Prompts for comparing the critics' explicit findings."""


class DisagreementPrompts:
    DISAGREEMENT_SYSTEM_PROMPT = """You compare independent critiques of the same generated answer.
Report only substantive contradictions between what two critics explicitly claim
about the answer. Each conflict must cite two issue indices from different critics
and explain why both claims cannot be true in the same sense. An issue reported by
one critic and silence from another is not a contradiction. Scores, confidence,
severity, and different evaluation dimensions are not evidence of a contradiction.
In particular, low factual accuracy and high completeness are compatible: a
response can answer every part of a question while giving incorrect facts.
Do not infer an endorsement from a high score or an empty issues list. If the
descriptions can both be true, or their meaning is ambiguous, return no conflict.
Return only conflicts supported by the supplied issue descriptions."""

    @staticmethod
    def get_disagreement_prompt(question: str, answer: str, issue_lines: str) -> str:
        return (
            f"Original question: {question}\n"
            f"Generated answer: {answer}\n"
            f"Critic issues (zero-based indices):\n{issue_lines}"
        )
