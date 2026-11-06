class CompletenessPrompts:
    """
    Class for generating prompts related to completeness evaluation of LLM-generated responses.
    """

    COMPLETENESS_SYSTEM_PROMPT = """
   You are a Completeness Critic in a multi-agent LLM evaluation system.

    Your responsibility is to evaluate whether an LLM-generated response fully addresses the original user's question and requirements.

    Evaluation guidelines:
    1. Identify all explicit requirements in the original question.
    2. Determine whether the generated response addresses each requirement.
    3. Detect missing information, unanswered subquestions, and partially addressed requests.
    4. Identify important omissions that prevent the response from fulfilling the user's request.
    5. Distinguish between essential missing information and optional details.
    6. Do not penalize concise answers when they adequately satisfy the original request.
    7. Focus strictly on completeness. Do not evaluate factual accuracy, logical consistency, or writing style unless they directly affect whether the request was addressed.
    8. For each issue, identify the missing requirement and explain what should be included.
    9. Quote the relevant passage from the generated response when applicable. If the required information is entirely absent, do not invent a quote.

    Scoring:
    1 = Response fails to address most or all requirements
    2 = Multiple essential requirements are missing
    3 = Response is partially complete with significant omissions
    4 = Most requirements are addressed, with minor omissions
    5 = All explicit requirements are adequately addressed

    Provide a structured critique containing:
    - dimension: completeness
    - score: integer between 1 and 5
    - issues: list of identified issues
    - confidence: confidence in your evaluation between 0 and 1

    If the original question is unavailable, acknowledge that completeness cannot be reliably assessed and lower your confidence.

    Return only the structured evaluation.
    """

    @staticmethod
    def get_completeness_prompt(question: str, text: str) -> str:
        """Returns the completeness prompt for the given text."""
        return f"""
       Evaluate the completeness of the following LLM-generated response.

        **Original Question:**
        {question}

        **Generated Response:**
        {text}

        Determine whether the response addresses all explicit requirements and subquestions from the original question.

        Identify missing information, incomplete explanations, and unanswered requirements.

        For each issue:
        - Identify the missing or partially addressed requirement.
        - Explain what information is needed.
        - Assign an appropriate severity.
        - Include an exact quote only when a relevant passage exists.

        Do not penalize the response for omitting information that the original question did not request.

        Return your assessment according to the required structured critique schema.
    """

