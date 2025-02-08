import json
import asyncio

from agentbox.box.memfs import MemFS


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Load Pyodide via CDN; ensure it's attached to window.pyodide
        await page.goto('data:text/html,<script src="https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js"></script>')
        await page.evaluate('''async () => {
            window.pyodide = await loadPyodide();
        }''')

        memfs = MemFS(page)

        # Create a directory, write a file, and list its contents.
        success_mkdir = await memfs.mkdir("/testdir")
        print("Created /testdir:", success_mkdir)

        success_write = await memfs.write_file("/testdir/hello.txt", "Hello, World!")
        print("Wrote /testdir/hello.txt:", success_write)

        content = await memfs.read_file("/testdir/hello.txt")
        print("Content of /testdir/hello.txt:", content)

        # List directory non-recursively.
        listing = await memfs.list_dir("/testdir", recursive=False)
        print("Listing of /testdir:", listing)

        # List directory recursively.
        recursive_listing = await memfs.list_dir("/", recursive=True)
        print("Recursive listing of memfs:", recursive_listing)

        # Remove the file and directory.
        removed_file = await memfs.remove_file("/testdir/hello.txt")
        print("Removed /testdir/hello.txt:", removed_file)

        removed_dir = await memfs.rmdir("/testdir")
        print("Removed /testdir:", removed_dir)

        await browser.close()

# Run the example if this module is executed directly.
if __name__ == "__main__":
    asyncio.run(main())