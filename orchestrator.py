import re
import random
from typing import TypedDict, Annotated, Sequence, Any
from langgraph.graph import StateGraph, END
import memory
import database
import agents

# Define State
class HRState(TypedDict):
    user_id: str
    query: str
    context: str
    intent: str
    confidence: float
    response: str
    routing_path: str
    status: str
    error_message: str

def classify_intent_node(state: HRState) -> HRState:
    """Classifies the intent based on keywords and assigns a confidence score."""
    query = state['query'].lower()
    
    # Mock classification logic
    if re.search(r'\b(schedule|meeting|calendar|book)\b', query):
        intent = "Scheduling"
        confidence = 0.9 + (random.random() * 0.05)
    elif re.search(r'\b(leave|time off|vacation|pto)\b', query):
        intent = "Leave"
        confidence = 0.95
    elif re.search(r'\b(policy|compliance|rules|guidelines)\b', query):
        intent = "Compliance"
        confidence = 0.85
    else:
        # Ambiguous or unknown
        intent = "Clarification"
        confidence = 0.4
        
    state['intent'] = intent
    state['confidence'] = confidence
    state['routing_path'] = "classify_intent"
    return state

def inject_memory_node(state: HRState) -> HRState:
    """Retrieves and injects STM/LTM context."""
    user_id = state['user_id']
    # Process the current query into memory
    memory.process_and_store_memory(user_id, state['query'])
    
    # Retrieve updated context
    context = memory.get_context_for_user(user_id)
    state['context'] = context
    state['routing_path'] += " -> inject_memory"
    return state

def execute_agent_node(state: HRState) -> HRState:
    """Executes the appropriate agent based on the intent."""
    intent = state['intent']
    confidence = state['confidence']
    
    state['routing_path'] += f" -> execute_{intent.lower()}_agent"
    
    if confidence < 0.5:
        # Too low confidence, ask for clarification regardless of classification
        agent_result = agents.clarification_agent(state['query'], state['context'])
        state['intent'] = "Clarification" # Override intent for audit
    else:
        if intent == "Scheduling":
            agent_result = agents.scheduling_agent(state['query'], state['context'])
        elif intent == "Leave":
            agent_result = agents.leave_agent(state['query'], state['context'])
        elif intent == "Compliance":
            agent_result = agents.compliance_agent(state['query'], state['context'])
        else:
            agent_result = agents.clarification_agent(state['query'], state['context'])
            
    if agent_result['status'] == 'error':
        # Fallback if agent failed
        agent_result = agents.fallback_agent(state['query'], state['context'])
        
    state['response'] = agent_result['response']
    state['status'] = agent_result['status']
    if agent_result['status'] == 'error' or agent_result['status'] == 'fallback':
         state['error_message'] = "Agent execution encountered an issue."
    
    return state

def audit_log_node(state: HRState) -> HRState:
    """Logs the interaction to the append-only database."""
    database.log_audit(
        user_id=state['user_id'],
        intent=state['intent'],
        confidence=state.get('confidence', 0.0),
        routing_path=state['routing_path'],
        status=state.get('status', 'unknown'),
        error_message=state.get('error_message', None)
    )
    return state

# Build the LangGraph
workflow = StateGraph(HRState)

# Add nodes
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("inject_memory", inject_memory_node)
workflow.add_node("execute_agent", execute_agent_node)
workflow.add_node("audit_log", audit_log_node)

# Add edges
workflow.set_entry_point("classify_intent")
workflow.add_edge("classify_intent", "inject_memory")
workflow.add_edge("inject_memory", "execute_agent")
workflow.add_edge("execute_agent", "audit_log")
workflow.add_edge("audit_log", END)

# Compile graph
app = workflow.compile()

def process_request(user_id: str, query: str) -> dict:
    """Entry point to process a request through the orchestrator."""
    initial_state = HRState(
        user_id=user_id,
        query=query,
        context="",
        intent="",
        confidence=0.0,
        response="",
        routing_path="start",
        status="pending",
        error_message=""
    )
    
    try:
        final_state = app.invoke(initial_state)
        return final_state
    except Exception as e:
        # Global fallback handling
        database.log_audit(
            user_id=user_id,
            intent="Unknown",
            confidence=0.0,
            routing_path="error",
            status="error",
            error_message=str(e)
        )
        return {
            "response": "A critical system error occurred. Please contact support.",
            "intent": "Error",
            "confidence": 0.0
        }
