
import logging

from langchain.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.arbitration.schemas.verdict import AdjudicationSchema
from src.arbitration.states import ArbitrationState
from src.prompts.adjudicator import AdjudicatorPrompts

logger = logging.getLogger(__name__)


def validate_adjudication(
    result: AdjudicationSchema,
    critiques: list,
) -> None:
    available = {
        issue.model_dump_json()
        for critique in critiques
        for issue in critique.issues
    }

    confirmed = {
        issue.model_dump_json()
        for issue in result.confirmed_issues
    }

    dismissed = {
        item.issue.model_dump_json()
        for item in result.dismissed_issues
    }

    if not (confirmed | dismissed) <= available:
        raise ValueError("Adjudication contains unknown issues")

    if confirmed & dismissed:
        raise ValueError(
            "An issue cannot be confirmed and dismissed"
        )


def adjudicator(state: ArbitrationState) -> dict:
    critiques = state.get("critiques", [])

    if not critiques:
        return {"adjudication": None}

    critique_text = "\n".join(
        critique.model_dump_json() for critique in critiques
    )

    messages = [
        SystemMessage(
            content=AdjudicatorPrompts.ADJUDICATOR_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=AdjudicatorPrompts.get_adjudicator_prompt(
                state["original_question"],
                state["generated_output"],
                critique_text,
                "\n".join(state.get("disagreements", [])),
            )
        ),
    ]

    try:
        llm = ChatOpenAI(
            model="gpt-5-mini",
            streaming=False,
            max_retries=2,
        )

        result = llm.with_structured_output(
            AdjudicationSchema
        ).invoke(messages)

        if not isinstance(result, AdjudicationSchema):
            raise ValueError("Invalid adjudication response")

        validate_adjudication(result, critiques)

        return {"adjudication": result}

    except Exception:
        logger.exception("Adjudicator failed")
        return {"adjudication": None}
