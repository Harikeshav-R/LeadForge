import os
import shutil
import subprocess
import tempfile
from typing import Optional

from langchain_core.tools import tool
from loguru import logger

from app.schemas import WebsiteCoderInput, WebsiteCoderOutput

GEMINI_MD = """
You are an expert website migration agent, operating in a headless, non-interactive mode.
Your task is to recreate and significantly improve upon an existing website.
You will be passed information, content, and assets scraped from the previous website.
Your goal is to use this scraped information to generate a new, better, modern, and production-ready static website.
You will not receive any user input or confirmation. You must proceed with the generation immediately.

**CRITICAL REQUIREMENTS:**

1.  **Static Only:** You MUST generate a static website using ONLY vanilla HTML, CSS, and JavaScript.
2.  **No Frameworks:** DO NOT use any dynamic JavaScript frameworks or libraries, such as React, Vue, Angular, or Svelte.
3.  **Root File:** You MUST create an `index.html` file at the root of the project.
4.  **Styling (Tailwind):** You MUST use Tailwind CSS for all styling. Load it via the CDN (`<script src="https://cdn.tailwindcss.com"></script>`) in the `<head>` of every HTML file.
5.  **Aesthetics:** The design must be modern, sleek, and beautiful. Take the old content and present it in a superior, responsive, and visually appealing way.
    * **Layout:** Use clean layouts with ample whitespace.
    * **Typography:** Use the "Inter" font family (load from Google Fonts in the `<head>`).
    * **Responsiveness:** The website MUST be fully responsive (mobile, tablet, desktop). Use Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`) extensively.
6.  **File Structure:**
    * Create `index.html` as the main file.
    * If custom CSS is needed (beyond Tailwind classes), create a `style.css` file and link it.
    * If JavaScript is needed, create a `script.js` file and link it with the `defer` attribute before the closing `</body>` tag (`<script src="script.js" defer></script>`).
7.  **Content:** Use the scraped content provided in the prompt. Do not use 'Lorem Ipsum'. If content is missing, generate relevant, high-quality, descriptive content that fits the context.
8.  **Images:** If the design requires images, use the scraped images provided in the prompt. Each image will have a description associated with it, so use appropriate images that fit the context. 
    If there are no scraped images, use placeholder images from `https://placehold.co/`. (e.g., `https://placehold.co/600x400`). All `<img>` tags MUST have descriptive `alt` attributes.
9.  **Action:** Your final action is to write all these files to the local filesystem.
"""


class WebsiteCoder:
    """Interfaces with 'gemini-cli' to generate and archive website code.

    This class encapsulates the process of running a command-line tool
    in a temporary directory, zipping the resulting files, and returning
    the archive's byte content.
    """

    def __init__(self):
        """Initializes the WebsiteCoder."""
        # No initial state is needed for this class
        logger.info("WebsiteCoder instance created.")
        pass

    @staticmethod
    def code_and_archive(prompt: str) -> Optional[bytes]:
        """Runs gemini-cli, archives output, and returns archive bytes.

        Args:
            prompt: The string prompt to pass to gemini-cli.

        Returns:
            Optional[bytes]: The bytes of the resulting .zip archive, or
            None if any part of the process fails.
        """

        logger.info(f"Starting code_and_archive process for prompt: '{prompt[:70]}...'")

        # We need two temporary locations:
        # 1. A directory where gemini-cli will write its files.
        # 2. A path for the final .zip archive.

        archive_file_handle = None
        archive_path = ""

        try:
            # 1. Create a temporary file path for the archive
            logger.debug("Creating temporary file for archive...")
            # We use delete=False so we can close it, let shutil write to it,
            # and then read/delete it manually.
            archive_file_handle = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            archive_path = archive_file_handle.name
            archive_file_handle.close()  # Close the handle so shutil can write to it
            logger.info(f"Temporary archive path set to: {archive_path}")

            # shutil.make_archive expects the base_name (path without extension)
            archive_base_name = archive_path[:-4]  # Removes the '.zip'
            logger.debug(f"Archive base name set to: {archive_base_name}")

            # 2. Create a temporary directory for gemini-cli's output
            with tempfile.TemporaryDirectory() as temp_dir_path:
                logger.info(f"Created temporary working directory: {temp_dir_path}")

                logger.info("Creating GEMINI.md file with instructions...")
                open(os.path.join(temp_dir_path, 'GEMINI.md'), 'w').write(GEMINI_MD)

                # 3. Construct and run the command
                # We will run the command *while inside* the temp_dir_path
                command = ['gemini', '--yolo', '--output-format', 'json', prompt]

                logger.info(f"Running command: {' '.join(command)}")
                logger.info(f"Setting Working Directory: {temp_dir_path}")

                try:
                    # Execute the subprocess
                    result = subprocess.run(
                        command,
                        cwd=temp_dir_path,  # This is key: run *in* the temp directory
                        capture_output=True,
                        text=True,
                        check=True  # Raise an error if gemini-cli fails
                    )

                    logger.info("Gemini-CLI command executed successfully.")
                    logger.info(f"Gemini-CLI STDOUT: {result.stdout.strip()}")
                    if result.stderr:
                        logger.warning(f"Gemini-CLI STDERR: {result.stderr.strip()}")

                except FileNotFoundError:
                    logger.error("Error: 'gemini' command not found.")
                    logger.error("Please ensure 'gemini-cli' is installed and in your system's PATH.")
                    return None  # Critical failure
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error: Gemini-CLI failed with exit code {e.returncode}")
                    logger.error(f"STDOUT: {e.stdout.strip()}")
                    logger.error(f"STDERR: {e.stderr.strip()}")
                    return None  # Critical failure

                logger.info("Removing GEMINI.md")
                os.remove(os.path.join(temp_dir_path, 'GEMINI.md'))

                # 4. Archive the contents of the temporary directory
                logger.info(f"Archiving contents of {temp_dir_path} to {archive_path}")

                # This will create 'archive_base_name.zip'
                shutil.make_archive(
                    base_name=archive_base_name,
                    format='zip',
                    root_dir=temp_dir_path  # The directory to archive
                )
                logger.info(f"Archive created successfully at {archive_path}")

                # 5. Read the archive bytes (temp_dir_path is now deleted)
                logger.info(f"Reading archive bytes from {archive_path}")
                with open(archive_path, 'rb') as f:
                    archive_bytes = f.read()

                logger.info(f"Successfully read {len(archive_bytes)} bytes from archive.")
                return archive_bytes

        except Exception as e:
            # Log any other unexpected exception
            logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
            return None

        finally:
            # 6. Clean up the temporary archive file
            if os.path.exists(archive_path):
                logger.info(f"Cleaning up temporary archive file: {archive_path}")
                os.remove(archive_path)
            else:
                logger.warning(f"Temporary archive file not found for cleanup: {archive_path}")


@tool(args_schema=WebsiteCoderInput)
def create_website_archive(prompt: str) -> WebsiteCoderOutput:
    """Convenience function to create a website archive.

    Instantiates WebsiteCoder, runs the code_and_archive process,
    and returns the archive bytes.

    Args:
        prompt: The string prompt to pass to gemini-cli.

    Returns:
        Optional[bytes]: The bytes of the resulting .zip archive, or
        None on failure.
    """
    logger.info("--- Starting Website Archive Process ---")
    try:
        coder = WebsiteCoder()
        archive_bytes = coder.code_and_archive(prompt)

        if archive_bytes:
            logger.info(f"--- Process Success: Archive is {len(archive_bytes)} bytes ---")
        else:
            logger.warning("--- Process Failed: No archive bytes returned ---")

        return WebsiteCoderOutput(archive_bytes)

    except Exception as e:
        logger.critical(f"A critical error occurred in create_website_archive: {e}", exc_info=True)
        return WebsiteCoderOutput(None)


# --- Example Usage ---
if __name__ == "__main__":

    test_prompt = "Build a beautiful TODO app using vanilla HTML, CSS, JavaScript that looks and feels modern."

    logger.info(f"\nAttempting live run with prompt: '{test_prompt}'")

    website_zip_bytes: WebsiteCoderOutput = create_website_archive.invoke(
        WebsiteCoderInput(prompt=test_prompt).model_dump())

    if website_zip_bytes:
        logger.info("Successfully created archive.")

    # To verify
    output_zip_file = "website.zip"

    try:
        with open(output_zip_file, "wb") as f:
            f.write(website_zip_bytes.root)

        logger.info(f"Wrote '{output_zip_file}' to current directory.")

    except IOError as e:
        logger.error(f"Failed to write output zip file: {e}")
