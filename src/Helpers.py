import os


def Style(path: str) -> str:
    if os.path.exists(path):
        with open(path) as file:
            return file.read()
    else:
        print(f"Path '{path}' to style file does not exists")
        return ""
