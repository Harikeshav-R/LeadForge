from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.analyze_leads import analyze_leads_node
from app.agents.lead_generator import generate_leads_node
from app.schemas.state import State


def make_graph() -> CompiledStateGraph:
    workflow = StateGraph(State)
    workflow.add_node("generate_leads", generate_leads_node)
    workflow.add_node("analyze_leads", analyze_leads_node)

    workflow.set_entry_point("generate_leads")
    workflow.add_edge("generate_leads", "analyze_leads")
    workflow.set_finish_point("analyze_leads")

    app = workflow.compile()

    return app


#
#
# async def run_workflow(state: State) -> State:
#     app = make_graph()
#     return await app.invoke(state)


if __name__ == "__main__":
    initial_state = State(city="Columbus, Ohio", business_type="restaurant")

    final_state = State(**make_graph().invoke(initial_state))

    print(final_state.model_dump_json(indent=2, exclude={"leads": {"__all__": {"screenshots"}}}))
