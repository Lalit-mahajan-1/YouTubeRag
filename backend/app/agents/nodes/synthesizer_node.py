from app.agents.state import AgentState
from app.core.logger import get_logger
from app.prompts.synthesizer_prompt import SYNTHESIZER_PROMPT
from app.services.llm_service import llm_service

logger = get_logger(__name__)


async def synthesizer_node(state: AgentState) -> dict:
    """Combines retrieved chunks into a final answer."""

    chunks = state["retrieved_chunks"]
    question = state["question"]

    if not chunks:
        return {
            "final_answer": "I couldn't find relevant information in the playlist to answer your question."
        }

    # Group chunks by video for cleaner context
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[From: {chunk['video_title']}]\n{chunk['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    prompt = SYNTHESIZER_PROMPT.format(question=question, context=context)

    try:
        answer = await llm_service.generate(prompt)
        logger.info("Answer synthesized successfully")
        return {"final_answer": answer.strip()}
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return {"final_answer": "Failed to generate answer. Please try again."}