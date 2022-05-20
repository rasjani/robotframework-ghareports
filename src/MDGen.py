# -*- coding: utf-8 -*-
from io import StringIO
from os import linesep

MD_FENCE = "```"
MD_HEADER = "#"
MD_HORIZONTAL_RULE = "---"
MD_CODE_BLOCK = "```"
MD_SINGLE_LINE_BLOCKQUOTE = ">"
MD_MULTILINE_BLOCKQUOTE = ">>>"  # GitLab only
MD_INLINE_CODE_HL = "`"
MD_LIST_ELEMENT = "*"


class MDGen(StringIO):
    def horizontal_rule(self):
        self.write("{linesep}{MD_HORIZONTAL_RULE}{linesep}")

    def header(self, text, level=1):
        self.write(f"{MD_HEADER * level} {text}{linesep * 2}")

    def code_block(self, block, language=""):
        self.write(f"{MD_FENCE}{language}{linesep}{block}{linesep}{MD_FENCE}{linesep * 2}")

    def list(self, items, ordered=False):
        for item in items:
            self.write(f"{MD_LIST_ELEMENT} {item}{linesep}")
        self.write(linesep)

    def ordered_list(self, items):
        for index, item in enumerate(items, 1):
            self.write(f"{index}. {item}{linesep}")
        self.write(linesep)

    def paragraph(self, text):
        self.write(f"{text}{linesep}")

    def table(self, headers, rows):
        self.write("| ")
        self.write(" | ".join(headers))
        self.write(f" |{linesep}")
        self.write("| ")
        self.write(" | ".join("-" * len(headers)))
        self.write(f" |{linesep}")
        for row in rows:
            self.write("| ")
            self.write(" | ".join(str(cell) for cell in row))
            self.write(f" |{linesep}")

        self.write(linesep)

    def link(self, text, url):
        self.write(f"[{text}]({url}){linesep}")


def main():
    mio = MDGen()
    mio.header("Hello, world!")
    mio.header("Testitulokset", 2)
    mio.code_block("print('Hello, world!')", "python")
    mio.table(["Name", "Age"], [["John", "25"], ["Jane", "24"]])
    mio.header("Ruokalista", 2)
    mio.list(["Hernekeitto", "Viina", "Teline", "Johannes"])
    mio.header("Juomalista", 2)
    mio.ordered_list(["Kaljaa", "Kossuu", "Mehuu", "Limppaa"])
    mio.header("Lopuksi", 2)
    mio.paragraph("This is a paragraph.")
    mio.link("KVG!", "https://www.google.com")
    print(mio.getvalue())


if __name__ == "__main__":
    main()
