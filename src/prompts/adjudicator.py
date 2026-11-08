class AdjudicatorPrompts:
    """Prompts for resolving reported conflicts between critics."""

    ADJUDICATOR_SYSTEM_PROMPT = """You adjudicate reported disagreements about an LLM response.
Compare the original question, generated response, and available critic issues.
Decide which supplied issues are justified. Confirm or dismiss issues with clear
explanations; give a nonempty reason for each dismissal. Copy each decided issue
exactly from the supplied critiques. Do not invent issues, evidence, claims,
quotes, or citations. Different evaluation dimensions can both be correct:
factual accuracy and completeness are independent. A difference in scores is
not itself a contradiction. If a factual claim cannot be independently verified
from the supplied information, explicitly acknowledge uncertainty rather than
claiming it is proven true or false. Leave uncertain issues undismissed.
Return only the structured adjudication result."""

    @staticmethod
    def get_adjudicator_prompt(question: str, response: str, critiques: str, disagreements: str) -> str:
        return (
            f"Original question:\n{question}\n\n"
            f"Generated response:\n{response}\n\n"
            f"Collected critiques:\n{critiques}\n\n"
            f"Detected disagreements:\n{disagreements}\n\n"
            "Resolve only the supplied issues and reported disagreements. "
            "Preserve independent findings and acknowledge uncertainty."
        )
