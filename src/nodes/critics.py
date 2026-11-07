from src.prompts.consistency import ConsistencyPrompts
from src.arbitration.states import ArbitrationState
from langchain_openai import ChatOpenAI
from src.prompts.accuracy import AccuracyPrompts
from src.arbitration.schemas.critique import CritiqueSchema
from langchain.messages import SystemMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def accuracy_critic(state:ArbitrationState) -> dict:
    original_question = state.get("original_question", "").strip()
    generated_output = state.get("generated_output", "").strip()

    if not original_question or not generated_output:
        raise ValueError("Original question and generated output must be provided in the state.")


    llm = ChatOpenAI(model_name="gpt-5", streaming=False, temperature=0.1)
    llm_with_structured_output = llm.with_structured_output(CritiqueSchema)

    sysPrompt = SystemMessage(content=AccuracyPrompts.ACCURACY_SYSTEM_PROMPT)
    prompts = HumanMessage(content=AccuracyPrompts().get_accuracy_prompt(original_question, generated_output))

    llm_response = llm_with_structured_output.invoke([sysPrompt, prompts])

    return {
    "critiques": [llm_response]
}

def logic_critic(state:ArbitrationState) -> dict:
    original_question = state.get("original_question", "").strip()
    generated_output = state.get("generated_output", "").strip()
    
    if not original_question or not generated_output:
            raise ValueError("Original question and generated output must be provided in the state.")

    sysPrompt = SystemMessage(content=ConsistencyPrompts.CONSISTENCY_SYSTEM_PROMPT)
    prompts = HumanMessage(content=ConsistencyPrompts().get_consistency_prompt(original_question, generated_output))
    
    llm=  ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    )   
    
    llm_with_structured_output = llm.with_structured_output(CritiqueSchema)
    llm_response = llm_with_structured_output.invoke([sysPrompt, prompts])
    return {
        "critiques": [llm_response]
    }   