import os


def push():
    logs = open("CHANGELOG.md", "r").read().split("####")
    for l in logs:
        if "TODO" not in l and "[" in l:
            break

    comments = [f"-m '{c[2:]}'" for i, c in enumerate(l.split("\n")) if i > 1 and c != ""]
    comments = " ".join(comments)
    cmd = f"git add . && git commit {comments} && git push heroku master"
    print(cmd)
    os.system(cmd)


from . import about

# from . import cache
# from .inputs import *
