from langgraph.graph import StateGraph, START, END

from app.agents.analyze_leads import analyze_leads_node
from app.agents.lead_generator import generate_leads_node
from app.schemas.state import State

workflow = StateGraph(State)
workflow.add_node("generate_leads", generate_leads_node)
workflow.add_node("analyze_leads", analyze_leads_node)

workflow.add_edge(START, "generate_leads")
workflow.add_edge("generate_leads", "analyze_leads")
workflow.add_edge("analyze_leads", END)

app = workflow.compile()

if __name__ == "__main__":
    initial_state = State(city="New York", business_type="restaurant")

    final_state = State(**app.invoke(initial_state))

    print(final_state.model_dump_json(indent=2))
