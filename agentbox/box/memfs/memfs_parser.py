from lark import Lark, Transformer, Token, Tree, v_args

class MemFSParser:
    grammar = r"""
        start: put_cmd | command

        // A command is either a put_cmd (starting with a quoted string)
        // or one of the following commands.
        command: ls_cmd | cp_cmd | rm_cmd | mkdir_cmd | rmdir_cmd | get_cmd

        // The ls command: after "ls" you may have zero or more options followed by an optional path.
        ls_cmd: "ls" option* path?
        option: OPTION

        // The cp command: optionally an RFLAG followed by two paths.
        cp_cmd: "cp" RFLAG? path path
        RFLAG: "-r"

        rm_cmd: "rm" path
        mkdir_cmd: "mkdir" path
        rmdir_cmd: "rmdir" path
        get_cmd: "get" path

        // The put command: a quoted string, an operator, the literal "put", and a path.
        put_cmd: QUOTED_STRING OPERATOR "put" path

        // OPERATOR: ">" for overwrite, ">>" for append.
        OPERATOR: ">" | ">>"

        // Terminals:
        // OPTION: any token that starts with a dash.
        OPTION: /-\S+/
        // A path is any sequence of non-whitespace characters that does not start with a dash or ">".
        path: /[^-\s>][^\s>]*/

        // Terminals for quoted strings (support both double- and single-quoted)
        DOUBLE_QUOTED_STRING: /"(\\.|[^"\\])*"/
        SINGLE_QUOTED_STRING: /'(\\.|[^'\\])*'/
        QUOTED_STRING: DOUBLE_QUOTED_STRING | SINGLE_QUOTED_STRING

        %import common.WS
        %ignore WS
    """

    class MemFSTransformer(Transformer):
        def extract_value(self, arg):
            return str(arg) if isinstance(arg, Token) else arg

        @v_args(inline=True)
        def start(self, result):
            return result

        # --- put command ---
        @v_args(inline=True)
        def put_cmd(self, quoted, operator, path):
            content = self.extract_value(quoted)[1:-1]  # Remove the surrounding quotes
            op = self.extract_value(operator)
            p = self.extract_value(path)
            return {"command": "put", "content": content, "path": p, "append": op == ">>"}

        # --- ls command ---
        def ls_cmd(self, children):
            # children: zero or more option tokens (from the rule "option")
            # followed by an optional path token.
            opts = []
            p = None
            for child in children:
                # The rule "option" will have been transformed to a string.
                if isinstance(child, str) and child.startswith("-"):
                    opts.append(child)
                else:
                    p = self.extract_value(child)
            return {
                "command": "ls",
                "recursive": ("-r" in opts),
                "info": ("-info" in opts),
                "path": p
            }

        @v_args(inline=True)
        def option(self, token):
            return self.extract_value(token)

        # --- cp command ---
        @v_args(inline=True)
        def cp_cmd(self, *args):
            # cp_cmd: "cp" RFLAG? path path
            if len(args) == 3 and self.extract_value(args[0]) == "-r":
                recursive = True
                src = self.extract_value(args[1])
                dst = self.extract_value(args[2])
            else:
                recursive = False
                src = self.extract_value(args[0])
                dst = self.extract_value(args[1])
            return {"command": "cp", "recursive": recursive, "src": src, "dst": dst}

        @v_args(inline=True)
        def RFLAG(self, token):
            return self.extract_value(token)

        # --- Other commands ---
        @v_args(inline=True)
        def rm_cmd(self, path):
            return {"command": "rm", "path": self.extract_value(path)}

        @v_args(inline=True)
        def mkdir_cmd(self, path):
            return {"command": "mkdir", "path": self.extract_value(path)}

        @v_args(inline=True)
        def rmdir_cmd(self, path):
            return {"command": "rmdir", "path": self.extract_value(path)}

        @v_args(inline=True)
        def get_cmd(self, path):
            return {"command": "get", "path": self.extract_value(path)}

        @v_args(inline=True)
        def path(self, token):
            return self.extract_value(token)

        @v_args(inline=True)
        def QUOTED_STRING(self, token):
            return self.extract_value(token)

        @v_args(inline=True)
        def OPERATOR(self, token):
            return self.extract_value(token)

        @v_args(inline=True)
        def OPTION(self, token):
            return self.extract_value(token)

    def _unwrap(self, result):
        while isinstance(result, Tree) and len(result.children) == 1:
            result = result.children[0]
        return result

    def __init__(self):
        self.parser = Lark(
            self.grammar,
            parser="lalr",
            transformer=self.MemFSTransformer()
        )

    def parse(self, command_str: str):
        try:
            result = self.parser.parse(command_str)
            return self._unwrap(result)
        except Exception as e:
            return {"error": str(e), "input": command_str}

# --- Example usage ---
if __name__ == "__main__":
    parser = MemFSParser()
    test_commands = [
        "ls",
        "ls /home/user",
        "ls -info",
        "ls -info /home/user",
        "ls -r -info /home/user",
        "ls -info -r /home/user",
        "ls -r",
        "cp /source/file /destination/file",
        "cp -r /source/dir /destination/dir",
        "rm /home/user/file",
        "mkdir /new/folder",
        "rmdir /old/folder",
        "get /home/user/document.txt",
        "'hello' > put /old/folder/file.txt",
        "\"hello world\" >> put /append/file.txt"
    ]
    for cmd in test_commands:
        print(parser.parse(cmd))

