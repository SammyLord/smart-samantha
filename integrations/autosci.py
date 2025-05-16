from llm import get_ollama_response, THINKER_MODEL_NAME

def trigger_autosci_discovery(thinker_model: str = THINKER_MODEL_NAME) -> str:
    """
    Triggers the AI to invent and 'solve' a fictional scientific/mathematical theory.
    Uses the THINKER_MODEL_NAME for this complex creative task.
    """
    
    # The prompt is designed to guide the LLM through a creative process.
    # It asks for a novel concept, and then a brief, imaginative "discovery" related to it.
    # The quality and coherence of the output will heavily depend on the LLM's capabilities.
    prompt = (
        "You are an imaginative AI capable of advanced theoretical thinking. "
        "Your task is to perform an 'automatic scientific discovery' exercise with the following steps:\n"
        "1. Invent and briefly describe a novel, plausible-sounding (but fictional) scientific or mathematical concept, theory, or principle. Give it a unique name.\n"
        "2. Following your description of this new concept/theory, outline a brief, imaginative 'solution,' 'discovery,' or 'breakthrough' that logically (within the fiction) follows from or relates to your invented concept. What new understanding or capability does this discovery unlock?\n"
        "Please present your response clearly, first the concept/theory, then the discovery.\n"
        "Example structure:\n"
        "Concept: Quantum Entanglement Echoes (QEE) - A theory suggesting that highly entangled particle pairs, when separated by vast cosmic distances, generate faint, predictable echo signatures in the cosmic microwave background radiation if one particle of the pair undergoes a state change.\n"
        "Discovery: By developing a hyper-sensitive array of CMB detectors and observing known distant quasars (as a source of potentially altered entangled particles), we have detected anomalous, repeating patterns matching predicted QEE signatures. This suggests that QEE is a real phenomenon and could potentially be used for faster-than-light communication by encoding messages in the state changes of locally held entangled particles and observing the distant CMB echoes, though the signal is currently too weak for practical bandwidth."
    )

    print(f"AutoSCI: Sending creative discovery prompt to {thinker_model}")
    discovery_narrative = get_ollama_response(prompt, model_name=thinker_model)
    
    return f"Initiating AutoSCI Discovery Protocol...\n\n{discovery_narrative}" 