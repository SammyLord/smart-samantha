from llm import get_ollama_response, THINKER_MODEL_NAME
from problem_solver import solve_with_multi_step_refinement

def trigger_autosci_discovery() -> str:
    """
    Triggers the AI to invent and 'solve' a fictional scientific/mathematical theory
    using the multi-step refinement process.
    """
    
    # This initial prompt frames the task for the multi-step problem solver.
    # It's a "user query" that asks the AI to perform the AutoSCI task.
    initial_autosci_prompt = (
        "Invent a novel, plausible-sounding (but fictional) scientific or mathematical concept, theory, or principle. "
        "Give it a unique name. Then, outline a brief, imaginative 'solution,' 'discovery,' or 'breakthrough' "
        "that logically (within the fiction) follows from or relates to your invented concept. "
        "What new understanding or capability does this discovery unlock? "
        "Present your response clearly, first the concept/theory, then the discovery. "
        "For example: Concept: Quantum Entanglement Echoes (QEE) - A theory suggesting that highly entangled particle pairs, when separated by vast cosmic distances, generate faint, predictable echo signatures in the cosmic microwave background radiation if one particle of the pair undergoes a state change. Discovery: By developing a hyper-sensitive array of CMB detectors and observing known distant quasars, we have detected anomalous, repeating patterns matching predicted QEE signatures, potentially enabling FTL communication via CMB echoes."
    )

    print("AutoSCI: Initiating multi-step refinement for creative discovery.")
    # The solve_with_multi_step_refinement function will handle using the GENERATOR and THINKER models.
    discovery_narrative = solve_with_multi_step_refinement(initial_autosci_prompt)
    
    return f"Initiating AutoSCI Discovery Protocol...\n\n{discovery_narrative}" 