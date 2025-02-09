from agentbox.box.memfs.memfs_parser import MemFSParser


if __name__ == "__main__":
    parser = MemFSParser()

    test_commands = [
        "ls",
        "ls /home/user",
        "cp /source/file /destination/file",
        "cp -r /source/dir /destination/dir",
        "rm /home/user/file",
        "mkdir /new/folder",
        "rmdir /old/folder",
        "get /home/user/document.txt",

        "\"hello\" >> put /old/folder/file.txt",

        """'hello
        world
        how
        are
        you
        today?!?!
        ' > put /append/file.txt"
        """,

        "dir /new/folder",

    ]

    for cmd in test_commands:
        parsed = parser.parse(cmd)
        print(parsed)
