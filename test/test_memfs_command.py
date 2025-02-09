import asyncio
from agentbox.box.memfs.memfs import MemFS
from agentbox.box.memfs.memfs_command import MemFSCommand

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

        cmd_exec = MemFSCommand(memfs)

        test_commands = [
            "ls",
            "mkdir /newfolder",

            "\"hello\" >> put /newfolder/file.txt",

            """'hello
        world
        how
        are
        you
        today?!?!
        ' >> put /newfolder/file.txt
        """,

            "get /newfolder/file.txt",

            "mkdir /otherfolder",
            "mkdir /morefolder",

            "ls /",

            "mkdir /newfolder/innerfolder",

            "ls -r /newfolder",

            "\"hello\" >> put /newfolder/file.txt",
            "\"hello\" >> put /newfolder/file.txt",
            "\"hello\" >> put /newfolder/file.txt",
            "\"hello\" >> put /newfolder/file.txt",
            "\"hello\" >> put /newfolder/file.txt",
            "\"hello\" >> put /newfolder/file.txt",

            "get /newfolder/file.txt",

            "ls -info /newfolder",

            "cp /newfolder/file.txt /otherfolder/file.txt",

            "cp -r /newfolder /morefolder",

            "rmdir /newfolder",

            "rm /morefolder/file.txt",

            "dir /new/folder",

        ]

        for cmd in test_commands:
            result = await cmd_exec.command(cmd)
            print(f"{result}: {cmd}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

