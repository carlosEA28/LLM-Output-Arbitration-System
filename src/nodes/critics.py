import logging
import time

import httpx
import openai
from google.genai import errors as google_errors
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from pydantic import ValidationError

from src.prompts.consistency import ConsistencyPrompts
from src.arbitration.states import ArbitrationState
from langchain_openai import ChatOpenAI
from src.prompts.accuracy import AccuracyPrompts
from src.prompts.completeness import CompletenessPrompts
from src.arbitration.schemas.critique import CritiqueSchema
from langchain.messages import SystemMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

MAX_LLM_ATTEMPTS = 2
RETRY_DELAY_SECONDS = 1
logger = logging.getLogger(__name__)


class InvalidEvaluationError(ValueError):
    """A structured critique violates the critic's evaluation rules."""


def _failure_category(exc: Exception) -> str:
    if isinstance(exc, ChatGoogleGenerativeAIError) and isinstance(exc.__cause__, google_errors.APIError):
        return _failure_category(exc.__cause__)
    if isinstance(exc, (InvalidEvaluationError, ValidationError, openai.APIResponseValidationError)):
        return "invalid_evaluation"
    if isinstance(exc, (openai.APITimeoutError, httpx.TimeoutException)):
        return "timeout"
    if isinstance(exc, (openai.APIConnectionError, httpx.NetworkError)):
        return "connection"
    if isinstance(exc, openai.RateLimitError):
        return "rate_limit"
    if isinstance(exc, openai.InternalServerError):
        return "server_error"
    if isinstance(exc, google_errors.APIError):
        if exc.code == 429:
            return "rate_limit"
        if exc.code == 408:
            return "timeout"
        if 500 <= exc.code < 600:
            return "server_error"
        if exc.code in (401, 403):
            return "authentication"
        if 400 <= exc.code < 500:
            return "invalid_request"
    if isinstance(exc, (openai.AuthenticationError, openai.PermissionDeniedError)):
        return "authentication"
    if isinstance(exc, (openai.BadRequestError, openai.UnprocessableEntityError)):
        return "invalid_request"
    if isinstance(exc, ValueError):
        return "configuration"
    return "call_error"


TRANSIENT_CATEGORIES = frozenset({"timeout", "connection", "rate_limit", "server_error"})


def _record_failure(name: str, exc: Exception) -> dict:
    logger.warning(
        "critic=%s category=%s exception=%s",
        name, _failure_category(exc), type(exc).__name__,
    )
    return {"failed_critics": [name]}


def _invoke_with_retries(model, messages):
    for attempt in range(MAX_LLM_ATTEMPTS):
        try:
            return model.invoke(messages)
        except Exception as exc:
            if attempt == MAX_LLM_ATTEMPTS - 1 or _failure_category(exc) not in TRANSIENT_CATEGORIES:
                raise
            time.sleep(RETRY_DELAY_SECONDS)


def accuracy_critic(state:ArbitrationState) -> dict:
    original_question = state.get("original_question", "").strip()
    generated_output = state.get("generated_output", "").strip()

    if not original_question or not generated_output:
        raise ValueError("Original question and generated output must be provided in the state.")


    try:
        llm = ChatOpenAI(model_name="gpt-5", streaming=False, temperature=0.1, max_retries=0)
        llm_with_structured_output = llm.with_structured_output(CritiqueSchema)

        sysPrompt = SystemMessage(content=AccuracyPrompts.ACCURACY_SYSTEM_PROMPT)
        prompts = HumanMessage(content=AccuracyPrompts().get_accuracy_prompt(original_question, generated_output))

        llm_response = _invoke_with_retries(llm_with_structured_output, [sysPrompt, prompts])
    except Exception as exc:
        return _record_failure("accuracy_critic", exc)

    return {
    "critiques": [llm_response]
}

def logic_critic(state:ArbitrationState) -> dict:
    original_question = state.get("original_question", "").strip()
    generated_output = state.get("generated_output", "").strip()
    
    if not original_question or not generated_output:
            raise ValueError("Original question and generated output must be provided in the state.")

    try:
        sysPrompt = SystemMessage(content=ConsistencyPrompts.CONSISTENCY_SYSTEM_PROMPT)
        prompts = HumanMessage(content=ConsistencyPrompts.get_consistency_prompt(
            question=original_question, text=generated_output
        ))

        llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", retries=1)
        llm_with_structured_output = llm.with_structured_output(CritiqueSchema)
        llm_response = _invoke_with_retries(llm_with_structured_output, [sysPrompt, prompts])

        if any(issue.quote is not None and issue.quote not in generated_output for issue in llm_response.issues):
            raise InvalidEvaluationError("Logic critique quotes must come from generated_output")

        if (llm_response.score == 5) != (not llm_response.issues):
            raise InvalidEvaluationError("Logic critique score and issues are inconsistent")

    except Exception as exc:
        return _record_failure("logic_critic", exc)
    return {
        "critiques": [llm_response]
    }

def completeness_critic(state:ArbitrationState) -> dict:
    original_question = state.get("original_question", "").strip()
    generated_output = state.get("generated_output", "").strip()

    if not original_question or not generated_output:
        raise ValueError("Original question and generated output must be provided in the state.")

    try:
        sysPrompt = SystemMessage(content=CompletenessPrompts.COMPLETENESS_SYSTEM_PROMPT)
        prompts = HumanMessage(content=CompletenessPrompts().get_completeness_prompt(original_question, generated_output))

        llm = ChatOpenAI(model="gpt-5-mini", streaming=False, max_retries=0)
        llm_with_structured_output = llm.with_structured_output(CritiqueSchema)

        llm_response = _invoke_with_retries(llm_with_structured_output, [sysPrompt, prompts])
    except Exception as exc:
        return _record_failure("completeness_critic", exc)

    return {
        "critiques": [llm_response]
    }
