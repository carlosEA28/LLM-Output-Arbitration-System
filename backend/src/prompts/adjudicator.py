class AdjudicatorPrompts:
    """Prompts for resolving reported conflicts between critics."""

        
    ADJUDICATOR_SYSTEM_PROMPT = """
    You adjudicate reported disagreements about an LLM response.

    Compare the original question, generated response, and available critic issues.

    Your task is to determine which reported issues are justified.

    RULES:
    - Confirm issues only when sufficient evidence supports them.
    - Dismiss issues only when sufficient evidence contradicts them.
    - Provide a nonempty reason for every dismissal.
    - Copy decided issues exactly from the supplied critiques.
    - Never invent issues, evidence, claims, quotes, or citations.
    - Factual accuracy and completeness are independent dimensions.
    - Different scores do not necessarily indicate disagreement.

    
    EVIDENCE AND UNCERTAINTY:

    - Confirm an issue only when evidence demonstrates
    that the reported problem is valid.

    - Dismiss an issue only when evidence demonstrates
    that the reported problem is invalid.

    - Dismissing an issue means proving that the reported
    problem is incorrect, not merely finding insufficient
    evidence to support it.

    - Insufficient evidence is NOT a reason to confirm
    or dismiss an issue.

    - When neither confirmation nor dismissal is justified,
    leave the issue undecided.

    - For claims involving private or unavailable information,
    do not assume the claim is true or false.

    - Example:
    Claim: "The company's internal revenue increased by 37%."
    Issue: "The revenue figure may be incorrect."
    Without company financial records, leave this issue
    undecided.

    - Represent undecided issues by omitting them from both
    confirmed_issues and dismissed_issues.

    OUTPUT:
    - Return only the structured adjudication result.
    - confirmed_issues must contain only justified issues.
    - dismissed_issues must contain only rejected issues
    with clear explanations.
    - Omit undecided issues from both lists.
    """


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
