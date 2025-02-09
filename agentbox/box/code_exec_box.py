import uuid
import asyncio
from playwright.async_api import async_playwright
from black import format_str, FileMode

from agentbox.box.box import Box
from agentbox.box.memfs.memfs import MemFS


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

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            memfs = MemFS(page)

            # --- Expose a messaging function ---
            async def send_message(message):
                # This function is invoked from the Pyodide context.
                print("Host received message from Pyodide:", message)

                # process message, such as getting data from kgraph


                # Build a reply dictionary.
                response = {"reply": "Message received", "original": message}
                return response

            await page.expose_function("sendMessage", send_message)

            # Load Pyodide via CDN using a data URL that injects the script
            await page.goto(
                'data:text/html,<script src="https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js"></script>'
            )

            # Evaluate Python code in Pyodide. Passing `code_string` as an argument avoids
            # issues with escaping when embedding it in the JavaScript snippet.

            evaluate_task = asyncio.create_task(
                page.evaluate(
                    """async (code) => {
                    const pyodide = await loadPyodide();
                    try {
                        // Redirect stdout in Pyodide to capture output
                        pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
                        `);
                        pyodide.runPython(`
import json
import js
class Messaging:
    async def send(self, message):
        # Explicitly convert the Python dict to a JSON string,
        # then parse it into a JS object.
        json_message = json.dumps(message)
        js_message = js.JSON.parse(json_message)
        result = await js.sendMessage(js_message)
        try:
            return result.to_py()
        except AttributeError:
            return result
messaging = Messaging()
                        `);
                        
                        // Execute the provided code
                        await pyodide.runPythonAsync(code);
                        // Retrieve captured stdout output
                        const std_output = pyodide.runPython("sys.stdout.getvalue()");
                        return { success: true, output: std_output };
                    } catch (error) {
                        return { success: false, error: `${error.name}: ${error.message}` };
                    }
                    }""",
                    code_string
                )
            )

            try:
                result = await asyncio.wait_for(evaluate_task, timeout=30)
            except asyncio.TimeoutError:
                evaluate_task.cancel()  # Cancel the task if it exceeds the timeout.
                result = {
                    "success": False,
                    "error": "TimeoutError: Pyodide code execution exceeded 30 seconds."
                }

            await browser.close()
            return result
