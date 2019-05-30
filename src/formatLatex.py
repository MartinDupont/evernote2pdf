from enum import Enum

def makePictureLink(filepath, caption="", label = ""):
    template = """
        \\begin{{figure}}[h!]
        \includegraphics[width=\linewidth]{}
        \caption{}
        \label{}
        \end{{figure}}
    """

    return template.format(filepath, caption, label)

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
