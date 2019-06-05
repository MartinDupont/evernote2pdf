
def make_picture_link(filepath, caption="", label=""):

    result = """\\begin{{figure}}[H]
    \\includegraphics[width=\\linewidth]{{{}}}
    """.format(filepath)

    if caption:
        result += "\\caption{{{}}}".format(caption)
    if label:
        result += "??\\label{{{}}}".format(label)
    result += "\\end{figure}"

    return result


if __name__ == "__main__":
    print(make_picture_link("/folder", "caption", "figure1"))
