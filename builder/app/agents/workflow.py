import base64

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from app.agents.information_scraper_node import information_scraper_node
from app.agents.page_screenshotter_node import page_screenshotter_node
from app.agents.prompt_generator_node import prompt_generator_node
from app.agents.website_builder_node import website_builder_node
from app.schemas.state import State


def create_compiled_state_graph() -> CompiledStateGraph:
    workflow = StateGraph(State)
    workflow.add_node("information_scraper", information_scraper_node)
    workflow.add_node("page_screenshotter", page_screenshotter_node)
    workflow.add_node("prompt_generator", prompt_generator_node)
    workflow.add_node("website_builder", website_builder_node)

    workflow.set_entry_point("information_scraper")
    workflow.add_edge("information_scraper", "page_screenshotter")
    workflow.add_edge("page_screenshotter", "prompt_generator")
    workflow.add_edge("prompt_generator", "website_builder")
    workflow.set_finish_point("website_builder")

    app = workflow.compile()

    return app


#
#
# async def run_workflow(state: State) -> State:
#     app = make_graph()
#     return await app.invoke(state)


if __name__ == "__main__":
    initial_state = State(initial_website_url="https://iscream-gelato.com")

    final_state = State(**create_compiled_state_graph().invoke(initial_state))

    output_zip_file = "website.zip"

    try:
        with open(output_zip_file, "wb") as f:
            f.write(base64.b64decode(final_state.final_website_zip))

        logger.info(f"Wrote '{output_zip_file}' to current directory.")

    except IOError as e:
        logger.error(f"Failed to write output zip file: {e}")

    print(final_state.model_dump_json(indent=2, exclude={"pages_screenshots"}))
