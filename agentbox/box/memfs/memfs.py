import json
import asyncio

class MemFS:
    def __init__(self, page):
        """
        Initialize the MemFS interface with a Playwright page object.
        The page is expected to have Pyodide loaded and attached to window.pyodide.
        """
        self.page = page

    async def list_dir(self, directory="/", recursive=False, info=False):
        """
        List the contents of a directory.
        If recursive is True, returns a nested structure.
        If info is True, entries are returned as a list of maps that include a 'name', 'type'
        (either "file" or "dir"), and for files a 'size' key (directories get size null).
        Otherwise, for non-recursive listing a simple list of names is returned,
        and for recursive listing, a nested dict is returned.
        """
        if recursive:
            if info:
                # Recursive listing with info: returns a list of objects with name, type, size and children.
                code = f'''
                () => {{
                    function listRecursiveInfo(path) {{
                        const fs = window.pyodide._module.FS;
                        let result = [];
                        let entries;
                        try {{
                            entries = fs.readdir(path);
                        }} catch(e) {{
                            return "Error reading directory: " + e.message;
                        }}
                        entries.forEach(entry => {{
                            if (entry === "." || entry === "..") return;
                            let fullPath = (path === "/" ? "/" + entry : path + "/" + entry);
                            let item = {{ name: entry }};
                            try {{
                                let stat = fs.stat(fullPath);
                                if ((stat.mode & 0x4000) === 0x4000) {{
                                    item.type = "dir";
                                    item.size = null;
                                    item.children = listRecursiveInfo(fullPath);
                                }} else {{
                                    item.type = "file";
                                    item.size = stat.size;
                                }}
                            }} catch(e) {{
                                item.error = e.message;
                            }}
                            result.push(item);
                        }});
                        return result;
                    }}
                    return listRecursiveInfo({json.dumps(directory)});
                }}
                '''
            else:
                # Recursive listing without info: returns a nested dictionary.
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
            # Non-recursive listing.
            if info:
                # If info is true, return an array of maps with details.
                code = f'''
                () => {{
                    const fs = window.pyodide._module.FS;
                    let result = [];
                    try {{
                        let entries = fs.readdir({json.dumps(directory)});
                        entries.filter(e => e !== "." && e !== "..").forEach(entry => {{
                            let fullPath = {json.dumps(directory)} === "/" ? "/" + entry : {json.dumps(directory)} + "/" + entry;
                            let item = {{ name: entry }};
                            try {{
                                let stat = fs.stat(fullPath);
                                if ((stat.mode & 0x4000) === 0x4000) {{
                                    item.type = "dir";
                                    item.size = null;
                                }} else {{
                                    item.type = "file";
                                    item.size = stat.size;
                                }}
                            }} catch(e) {{
                                item.error = e.message;
                            }}
                            result.push(item);
                        }});
                        return result;
                    }} catch(e) {{
                        return "Error reading directory: " + e.message;
                    }}
                }}
                '''
            else:
                # Non-recursive listing without info: simple array of names.
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

    async def write_file(self, path, content, append=False):
        """
        Write content to a file at the given path using UTF-8 encoding.
        If append is True, the content is appended rather than overwriting the file.
        """
        flag = "a" if append else "w"
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            try {{
                fs.writeFile({json.dumps(path)}, {json.dumps(content)}, {{
                    encoding: "utf8",
                    flags: {json.dumps(flag)}
                }});
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

    async def copy(self, src, dest):
        """
        Copy a file or directory from src to dest inside the MEMFS.
        If src is a directory, it is copied recursively.
        Returns true if the copy was successful, or an error message if an error occurs.
        """
        code = f'''
        () => {{
            const fs = window.pyodide._module.FS;
            function copyRecursively(src, dest) {{
                let stat;
                try {{
                    stat = fs.stat(src);
                }} catch(e) {{
                    return "Error getting stats for " + src + ": " + e.message;
                }}
                // Check if src is a directory: directory bit is 0x4000.
                if ((stat.mode & 0x4000) === 0x4000) {{
                    // Create destination directory.
                    try {{
                        fs.mkdir(dest);
                    }} catch(e) {{
                        // Ignore error if directory already exists.
                        if (!(e && e.errno === 20)) {{
                            return "Error creating directory " + dest + ": " + e.message;
                        }}
                    }}
                    let entries;
                    try {{
                        entries = fs.readdir(src);
                    }} catch(e) {{
                        return "Error reading directory " + src + ": " + e.message;
                    }}
                    for (let i = 0; i < entries.length; i++) {{
                        let entry = entries[i];
                        if (entry === "." || entry === "..") continue;
                        let srcEntry = src === "/" ? "/" + entry : src + "/" + entry;
                        let destEntry = dest === "/" ? "/" + entry : dest + "/" + entry;
                        let result = copyRecursively(srcEntry, destEntry);
                        if (result !== true) {{
                            return result;
                        }}
                    }}
                }} else {{
                    // src is a file. Read it and write it to dest.
                    let content;
                    try {{
                        content = fs.readFile(src, {{ encoding: "binary" }});
                    }} catch(e) {{
                        return "Error reading file " + src + ": " + e.message;
                    }}
                    try {{
                        fs.writeFile(dest, content, {{ encoding: "binary" }});
                    }} catch(e) {{
                        return "Error writing file " + dest + ": " + e.message;
                    }}
                }}
                return true;
            }}
            return copyRecursively({json.dumps(src)}, {json.dumps(dest)});
        }}
        '''
        return await self.page.evaluate(code)
