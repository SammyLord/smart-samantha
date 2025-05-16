from llm import get_ollama_response, GENERATOR_MODEL_NAME, THINKER_MODEL_NAME
import re

DEFAULT_NUM_INITIAL_IDEAS = 5
DEFAULT_NUM_PROTOTYPES = 5 # Number of prototypes to generate for the selected idea
MAX_EVOLUTION_STEPS = 2    # Number of times to iteratively refine the chosen prototype

def generate_initial_ideas(user_query: str, num_ideas: int = DEFAULT_NUM_INITIAL_IDEAS, generator_model: str = GENERATOR_MODEL_NAME) -> list[str]:
    """Generates a list of initial broad ideas to solve the user's query."""
    prompt = (
        f"The user has the following query: \"{user_query}\".\n"
        f"Please brainstorm {num_ideas} distinct, concise, and actionable high-level ideas or approaches to address this query. "
        f"Each idea should be a potential strategic direction. "
        f"Present each idea on a new line, starting with a number and a period (e.g., '1. ...', '2. ...')."
    )
    
    response_text = get_ollama_response(prompt, model_name=generator_model)
    ideas = []
    for line in response_text.split('\n'):
        match = re.match(r"^\d+\.\s*(.+)", line.strip())
        if match:
            ideas.append(match.group(1).strip())
            
    if not ideas or len(ideas) < num_ideas / 2:
        ideas.extend([i.strip() for i in response_text.split('\n') if i.strip() and not i.strip().isnumeric()])
        ideas = list(dict.fromkeys(ideas))
    if not ideas:
        return [response_text]
    return ideas[:num_ideas]

def select_best_approach(user_query: str, initial_ideas: list[str], thinker_model: str = THINKER_MODEL_NAME) -> str:
    """Selects the most promising conceptual approach from the initial ideas."""
    if not initial_ideas:
        # This case should ideally be handled by the orchestrator, 
        # but as a safeguard, return a simple statement.
        return f"No initial ideas provided to select from for query: {user_query}"

    ideas_formatted = "\n".join([f"- Idea {idx+1}: {idea}" for idx, idea in enumerate(initial_ideas)])
    
    prompt = (
        f"The user's original query is: \"{user_query}\".\n\n"
        f"Here are several brainstormed high-level ideas to address this query:\n{ideas_formatted}\n\n"
        f"Your task is to analyze these ideas and select or synthesize the single most promising and effective conceptual approach to pursue. "
        f"Clearly articulate this chosen approach as a concise guiding principle or a refined idea. "
        f"This output will be used to generate more detailed prototypes, so it needs to be a clear instruction or concept. "
        f"Do not try to fully answer the user\'s query yet. Just state the chosen approach clearly."
        f"For example, if ideas were about fixing a bug, your output might be: 'Focus on reproducing the bug in a minimal environment and then use a debugger to trace the execution path.'"
    )
    
    selected_approach_text = get_ollama_response(prompt, model_name=thinker_model)
    return selected_approach_text.strip()


def generate_prototypes_for_approach(selected_approach: str, num_prototypes: int = DEFAULT_NUM_PROTOTYPES, generator_model: str = GENERATOR_MODEL_NAME) -> list[str]:
    """Generates concrete prototypes or detailed implementations for a selected approach."""
    prompt = (
        f"The chosen strategic approach to explore is: \"{selected_approach}\".\n"
        f"Please generate {num_prototypes} distinct, concrete prototypes or detailed elaborations based on this approach. "
        f"Each prototype should be a specific way to implement or expand on the given approach. "
        f"Present each prototype on a new line, starting with a number and a period (e.g., '1. ...', '2. ...')."
        f"Make them practical and actionable examples."
    )
    response_text = get_ollama_response(prompt, model_name=generator_model)
    prototypes = []
    for line in response_text.split('\n'):
        match = re.match(r"^\d+\.\s*(.+)", line.strip())
        if match:
            prototypes.append(match.group(1).strip())
            
    if not prototypes or len(prototypes) < num_prototypes / 2:
        prototypes.extend([i.strip() for i in response_text.split('\n') if i.strip() and not i.strip().isnumeric()])
        prototypes = list(dict.fromkeys(prototypes))
    if not prototypes:
        return [response_text] # Return raw response as a single prototype if parsing fails
    return prototypes[:num_prototypes]


def evolve_prototype_to_solution(user_query: str, selected_approach: str, prototypes: list[str], thinker_model: str = THINKER_MODEL_NAME, max_steps: int = MAX_EVOLUTION_STEPS) -> str:
    """Selects the best prototype and iteratively evolves it into a final solution."""
    if not prototypes:
        return f"No prototypes were generated for the approach: '{selected_approach}'. Cannot evolve."

    # Step 1: Select the best initial prototype
    prototypes_formatted = "\n".join([f"- Prototype {idx+1}: {p}" for idx, p in enumerate(prototypes)])
    selection_prompt = (
        f"The user's original query is: \"{user_query}\".\n"
        f"The guiding conceptual approach chosen is: \"{selected_approach}\".\n\n"
        f"Here are several prototypes based on this approach:\n{prototypes_formatted}\n\n"
        f"Which single prototype is the most promising starting point to develop a full solution for the user's query? "
        f"Respond with ONLY the full text of the chosen prototype."
    )
    current_best_solution = get_ollama_response(selection_prompt, model_name=thinker_model).strip()
    print(f"Problem Solver: Initial best prototype selected: {current_best_solution[:100]}...")

    # Step 2: Iteratively evolve the selected prototype
    for i in range(max_steps):
        print(f"Problem Solver: Evolution step {i+1}/{max_steps}...")
        evolution_prompt = (
            f"The user's original query is: \"{user_query}\".\n"
            f"The overall guiding approach is: \"{selected_approach}\".\n"
            f"The current version of the proposed solution/answer is:\n\"{current_best_solution}\"\n\n"
            f"Please critically evaluate and refine this current version to make it a more complete, accurate, and helpful final answer to the user's original query. "
            f"Incorporate any necessary details, improve clarity, and ensure it fully addresses the query. "
            f"Your output should be the new, improved version of the solution/answer."
        )
        current_best_solution = get_ollama_response(evolution_prompt, model_name=thinker_model).strip()
        print(f"Problem Solver: Evolved solution (step {i+1}): {current_best_solution[:100]}...")
        
    return current_best_solution


def solve_with_multi_step_refinement(user_query: str) -> str:
    """Orchestrates the multi-step LLM problem-solving approach."""
    print(f"Problem Solver: Stage 1 - Generating initial ideas for query: {user_query}")
    initial_ideas = generate_initial_ideas(user_query)
    if not initial_ideas:
        print("Problem Solver: No initial ideas generated. Falling back to direct simple response.")
        return get_ollama_response(user_query, model_name=GENERATOR_MODEL_NAME)
    print(f"Problem Solver: Generated {len(initial_ideas)} initial ideas.")

    print("Problem Solver: Stage 2 - Selecting best approach from initial ideas.")
    selected_approach = select_best_approach(user_query, initial_ideas)
    if not selected_approach or "No initial ideas provided" in selected_approach: # Basic check
        print(f"Problem Solver: Could not select a best approach. Original ideas: {initial_ideas}. Falling back.")
        return get_ollama_response(user_query, model_name=THINKER_MODEL_NAME) # Fallback to thinker with original query
    print(f"Problem Solver: Selected approach: {selected_approach}")

    print("Problem Solver: Stage 3 - Generating prototypes for the selected approach.")
    prototypes = generate_prototypes_for_approach(selected_approach)
    if not prototypes:
        print(f"Problem Solver: No prototypes generated for approach '{selected_approach}'. Using approach as response.")
        return selected_approach # Or try to directly answer with thinker based on selected_approach
    print(f"Problem Solver: Generated {len(prototypes)} prototypes.")

    print("Problem Solver: Stage 4 - Selecting and evolving the best prototype into a final solution.")
    final_solution = evolve_prototype_to_solution(user_query, selected_approach, prototypes)
    print("Problem Solver: Multi-step refinement complete.")
    return final_solution

# Old function, to be replaced by solve_with_multi_step_refinement
# def solve_with_two_tier_llm(user_query: str) -> str:
#     print(f"Problem Solver: Generating ideas for query: {user_query}")
#     generated_ideas = generate_ideas(user_query) # This would now be generate_initial_ideas
#     if not generated_ideas:
#         print("Problem Solver: No ideas generated, falling back to direct response.")
#         return get_ollama_response(user_query, model_name=GENERATOR_MODEL_NAME)
#     print(f"Problem Solver: Generated {len(generated_ideas)} ideas. Evaluating...")
#     final_solution = evaluate_ideas(user_query, generated_ideas) # This would now be select_best_approach and more
#     print("Problem Solver: Evaluation complete.")
#     return final_solution 