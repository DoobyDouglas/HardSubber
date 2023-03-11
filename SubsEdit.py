import pysubs2


def subs_edit(path: str):
    subs = pysubs2.load(path)
    search_char = '{'
    to_delete = [
        i for i, line in enumerate(subs) if search_char not in line.text
    ]
    for i in reversed(to_delete):
        del subs[i]

    subs.save(path)
