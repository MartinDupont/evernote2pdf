from enum import Enum


def make_picture_link(filepath, caption="", label=""):

    result = """\\begin{{figure}}[h!]
    \\includegraphics[width=\\linewidth]{{{}}}
    """.format(filepath)

    if caption:
        result += "\\caption{{{}}}".format(caption)
    if label:
        result += "??\\label{{{}}}".format(label)
    result += "\\end{{figure}}"

    return result


def makeTextBlock(text):
    return text


class ContentType(Enum):
    TEXT = 1
    IMAGE = 2

class ContentBlock:
    def __init__(self, type, rawText):
        self.type = type
        self.rawText = rawText

    def toLatex(self):
        if self.type is ContentType.TEXT:
            return makeTextBlock(self.rawText)

        elif self.type is ContentType.IMAGE:
            return makePictureLink(self.rawText)
        else:
            return ""






if __name__ == "__main__":
    print(makePictureLink("/folder", "caption", "figure1"))
