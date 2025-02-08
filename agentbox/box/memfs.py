import json
import asyncio

class MemFS:
    def __init__(self, page):
        """
        Initialize the MemFS interface with a Playwright page object.
        The page is expected to have Pyodide loaded and attached to window.pyodide.
        """
        self.page = page

    async def list_dir(self, directory="/", recursive=False):
        """
        List the contents of a directory.
        If recursive is True, returns a nested dict with directory trees.
        Otherwise, returns a flat list of names.
        """
        if recursive:
            # Recursively build a nested dictionary of files and directories.
            code = f'''
            () => {{
                function listRecursive(path) {{
                    const fs = window.pyodide._module.FS;
                    let result = {{}};
                    let entries;
                    try {{
                        entries = fs.readdir(path);
                    }} catch(e) {{
                        return "Error reading directory: " + e.message;
                    }}
                    entries.forEach(entry => {{
                        if (entry === "." || entry === "..") return;
                        let fullPath = (path === "/" ? "/" + entry : path + "/" + entry);
                        try {{
                            let stat = fs.stat(fullPath);
                            // Check if the entry is a directory using the directory bit (0x4000)
                            if ((stat.mode & 0x4000) === 0x4000) {{
                                result[entry] = listRecursive(fullPath);
                            }} else {{
                                result[entry] = "file";
                            }}
                        }} catch(e) {{
                            result[entry] = "Error: " + e.message;
                        }}
                    }});
                    return result;
                }}
                return listRecursive({json.dumps(directory)});
            }}
            '''
        else:
            # Simply list the immediate entries (excluding '.' and '..').
            code = f'''
            () => {{
                const fs = window.pyodide._module.FS;
                try {{
                    let entries = fs.readdir({json.dumps(directory)});
                    return entries.filter(e => e !== "." && e !== "..");
                }} catch(e) {{
                    return "Error reading directory: " + e.message;
                }}
            }}
            '''
        return await self.page.evaluate(code)

    async def read_file(self, path):
        """
        Return the content of a file at the given path as a UTF-8 string.
        Returns None if the file does not exist or cannot be read.
        """
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            try {{
                return fs.readFile({json.dumps(path)}, {{encoding: "utf8"}});
            }} catch (e) {{
                return null;
            }}
        }}
        '''
        return await self.page.evaluate(code)

    async def write_file(self, path, content):
        """
        Write the given content to a file at the given path using UTF-8 encoding.
        Returns True if successful, False otherwise.
        """
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            try {{
                fs.writeFile({json.dumps(path)}, {json.dumps(content)}, {{encoding: "utf8"}});
                return true;
            }} catch (e) {{
                return false;
            }}
        }}
        '''
        return await self.page.evaluate(code)

    async def remove_file(self, path):
        """
        Remove (unlink) the file at the given path.
        Returns True if successful, False otherwise.
        """
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            try {{
                fs.unlink({json.dumps(path)});
                return true;
            }} catch (e) {{
                return false;
            }}
        }}
        '''
        return await self.page.evaluate(code)

    async def mkdir(self, path):
        """
        Create a new directory at the given path.
        Returns True if successful, False otherwise.
        """
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            try {{
                fs.mkdir({json.dumps(path)});
                return true;
            }} catch (e) {{
                return false;
            }}
        }}
        '''
        return await self.page.evaluate(code)

    async def rmdir(self, path):
        """
        Remove a directory at the given path.
        Returns True if successful, False otherwise.
        """
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            try {{
                fs.rmdir({json.dumps(path)});
                return true;
            }} catch (e) {{
                return false;
            }}
        }}
        '''
        return await self.page.evaluate(code)
