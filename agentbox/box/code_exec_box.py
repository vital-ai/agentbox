import uuid
import asyncio
from playwright.async_api import async_playwright
from black import format_str, FileMode

from agentbox.box.box import Box


class CodeExecutorBox(Box):

    def handle_code_exec(self, code_string: str) -> str:

        # Remove markdown formatting if present
        code_string = "\n".join(
            line for line in code_string.splitlines() if "```python" not in line and "```" not in line
        )

        # Run the Python code using Pyodide in Playwright
        answer_dict = asyncio.run(self.run_python_with_pyodide(code_string))

        random_guid = uuid.uuid4()
        answer_string = f"{answer_dict}\nCode Execution Confirmation: {random_guid}.\n"
        return answer_string

    async def run_python_with_pyodide(self, code_string):
        # Format the code using Black
        try:
            formatted_code = format_str(code_string, mode=FileMode())
        except Exception as e:
            return f"{type(e).__name__}: {e}\nBe sure your indentation is correct."

        code_string = formatted_code

        # Use Playwright to launch a headless Chromium browser
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Load Pyodide via CDN using a data URL that injects the script
            await page.goto(
                'data:text/html,<script src="https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js"></script>'
            )

            # Evaluate Python code in Pyodide. Passing `code_string` as an argument avoids
            # issues with escaping when embedding it in the JavaScript snippet.
            result = await page.evaluate(
                """async (code) => {
                    const pyodide = await loadPyodide();
                    try {
                        // Redirect stdout in Pyodide to capture output
                        pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
                        `);
                        // Execute the provided code
                        pyodide.runPython(code);
                        // Retrieve captured stdout output
                        const std_output = pyodide.runPython("sys.stdout.getvalue()");
                        return { success: true, output: std_output };
                    } catch (error) {
                        return { success: false, error: `${error.name}: ${error.message}` };
                    }
                }""",
                code_string
            )

            await browser.close()
            return result
