from loguru import logger

from app.schemas import State, WebsiteCoderInput, WebsiteCoderOutput
from app.tools import website_coder


def website_builder_node(state: State) -> State:
    """
    Generates a website .zip file from a given prompt using `website_coder`.

    This node takes the `prompt` from the state, invokes the
    `website_coder` tool, and updates the state with the resulting
    zip file bytes or an error message if the build fails.

    Args:
        state: The current workflow state, containing `prompt`.

    Returns:
        State: An updated copy of the state. If successful, `final_website_zip`
               is populated and `builder_error` is None. If failed,
               `final_website_zip` is None and `builder_error` contains
               the error message.
    """
    logger.info("Starting website builder node...")

    try:
        # 1. Validate state
        if not state.prompt:
            raise ValueError("No prompt found in state. Cannot build website.")

        logger.debug(f"Building website from prompt: {state.prompt[:100]}...")

        # 2. Prepare the input for the website coder
        input_data = WebsiteCoderInput(prompt=state.prompt).model_dump()

        # 3. Invoke the website coder
        output: WebsiteCoderOutput = website_coder.invoke(input_data)

        if not output or not hasattr(output, 'root') or not output.root:
            raise ValueError("Invalid or empty output from website_coder.")

        logger.info("Successfully received website .zip bytes from builder.")
        logger.debug(f"Zip file size: {len(output.root)} bytes")

        # 4. Return the new state on success
        return state.model_copy(
            update={
                "final_website_zip": output.root,
            }
        )

    except Exception as e:
        # 5. Handle any exception during the build process
        error_message = f"Failed during website build: {e}"
        logger.error(error_message, exc_info=True)  # exc_info=True logs the stack trace

        # 6. Return the new state on failure
        return state.model_copy(
            update={
                "final_website_zip": None,  # Ensure zip is empty on failure
            }
        )
