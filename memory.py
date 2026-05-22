import re
from typing import Dict, List, Any
import database

def calculate_significance_score(content: str) -> float:
    """
    Evaluates the significance of a piece of information to determine if it belongs
    in Short-Term Memory (STM) or Long-Term Memory (LTM).
    
    Sound and Justified Logic:
    - High Significance (LTM, score > 0.7): Facts about the user that persist over time. 
      Examples: "My manager is Alice", "I have a medical condition", "I prefer morning meetings".
      Keywords: "manager", "prefer", "always", "never", "policy", "condition", "role", "name".
    - Low Significance (STM, score <= 0.7): Transactional or ephemeral details.
      Examples: "Book a meeting for tomorrow", "Cancel my leave".
      Keywords: "tomorrow", "next week", "cancel", "book", "schedule", "meeting".
    """
    score = 0.5  # Base score
    
    ltm_keywords = [r'\bmanager\b', r'\bprefer(ence)?\b', r'\balways\b', r'\bnever\b', 
                    r'\bpolicy\b', r'\bcondition\b', r'\brole\b', r'\bname is\b', r'\bmy (?!meeting|leave|request)\b']
    
    stm_keywords = [r'\btomorrow\b', r'\bnext week\b', r'\bcancel\b', r'\bbook\b', 
                    r'\bschedule\b', r'\bmeeting\b', r'\btoday\b', r'\bnow\b']
    
    content_lower = content.lower()
    
    for kw in ltm_keywords:
        if re.search(kw, content_lower):
            score += 0.2
            
    for kw in stm_keywords:
        if re.search(kw, content_lower):
            score -= 0.15
            
    # Bound the score between 0.0 and 1.0
    return max(0.0, min(1.0, score))

def process_and_store_memory(user_id: str, content: str) -> Dict[str, Any]:
    """
    Processes a user input, calculates its significance, and stores it in the appropriate memory tier.
    """
    score = calculate_significance_score(content)
    tier = "LTM" if score > 0.7 else "STM"
    
    memory_id = database.add_memory(user_id, tier, content, score)
    return {
        "id": memory_id,
        "user_id": user_id,
        "tier": tier,
        "content": content,
        "significance_score": round(score, 2)
    }

def get_context_for_user(user_id: str) -> str:
    """
    Retrieves both STM and LTM to inject into the agent's prompt context.
    """
    memories = database.get_memories(user_id)
    
    ltm_list = [m['content'] for m in memories if m['tier'] == 'LTM']
    stm_list = [m['content'] for m in memories if m['tier'] == 'STM'][:5] # Get 5 most recent STMs
    
    context_str = "--- Background Knowledge (LTM) ---\n"
    if ltm_list:
        context_str += "\n".join([f"- {m}" for m in ltm_list])
    else:
        context_str += "None"
        
    context_str += "\n\n--- Recent Context (STM) ---\n"
    if stm_list:
        context_str += "\n".join([f"- {m}" for m in stm_list])
    else:
        context_str += "None"
        
    return context_str
