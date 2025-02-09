from agentbox.box.memfs.memfs_parser import MemFSParser


class MemFSCommand:
    def __init__(self, memfs):
        """
        Initialize with a MemFS instance.
        Also instantiates an internal parser (MemFSParser) which must have a parse() method.
        """
        self.memfs = memfs
        self.parser = MemFSParser()

    async def command(self, input_str):
        """
        Parse the input command string and dispatch to the corresponding MemFS method.
        Returns the result of the operation or an error dictionary if parsing fails.
        """
        parsed = self.parser.parse(input_str)

        # print(parsed)

        if 'error' in parsed:
            # Return parser error if parsing fails.
            return parsed

        cmd = parsed.get('command')

        try:
            if cmd == 'ls':
                # Use the 'path' and 'recursive' keys from the parser.
                path = parsed.get('path') or "/"
                recursive = parsed.get('recursive', False)
                info = parsed.get('info', False)
                return await self.memfs.list_dir(path, recursive=recursive, info=info)
            elif cmd == 'cp':
                src = parsed.get('src')
                dst = parsed.get('dst')
                return await self.memfs.copy(src, dst)
            elif cmd == 'rm':
                path = parsed.get('path')
                return await self.memfs.remove_file(path)
            elif cmd == 'mkdir':
                path = parsed.get('path')
                return await self.memfs.mkdir(path)
            elif cmd == 'rmdir':
                path = parsed.get('path')
                return await self.memfs.rmdir(path)
            elif cmd == 'get':
                path = parsed.get('path')
                return await self.memfs.read_file(path)
            elif cmd == 'put':
                content = parsed.get('content')
                path = parsed.get('path')
                append = parsed.get('append', False)
                return await self.memfs.write_file(path, content, append=append)
            else:
                return {'error': f'Unknown command: {cmd}'}
        except Exception as e:
            return {'error': str(e)}

