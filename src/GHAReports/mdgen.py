# -*- coding: utf-8 -*-
from io import StringIO
from os import linesep
from textwrap import wrap

MD_FENCE = "```"
MD_HEADER = "#"
MD_HORIZONTAL_RULE = "---"
MD_CODE_BLOCK = "```"
MD_SINGLE_LINE_BLOCKQUOTE = ">"
MD_MULTILINE_BLOCKQUOTE = ">>>"  # GitLab only
MD_INLINE_CODE_HL = "`"
MD_LIST_ELEMENT = "*"
MD_TABLE_ALIGN_LEFT = ":--"
MD_TABLE_ALIGN_RIGHT = "--:"
MD_TABLE_ALIGN_CENTER = ":-:"


MD_STATUSICONS = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏩", "WARN": "⚠"}
alignment_lookup = {"left": MD_TABLE_ALIGN_LEFT, "right": MD_TABLE_ALIGN_RIGHT, "center": MD_TABLE_ALIGN_CENTER}


class MDGen(StringIO):
  def horizontal_ruler(self):
    self.write(f"{linesep}{MD_HORIZONTAL_RULE}{linesep}")

  def header(self, text, level=1):
    self.write(f"{MD_HEADER * level} {text}{linesep * 2}")

  def code_block(self, block, language=""):
    self.write(f"{MD_FENCE}{language}{linesep}{block}{linesep}{MD_FENCE}{linesep * 2}")

  def list(self, items):  # NOQA: A003
    for item in items:
      self.write(f"{MD_LIST_ELEMENT} {item}{linesep}")
    self.write(linesep)

  def ordered_list(self, items):
    for index, item in enumerate(items, 1):
      self.write(f"{index}. {item}{linesep}")
    self.write(linesep)

  def paragraph(self, text):
    self.write(f"{text}{linesep}")

  def table(self, headers, rows, alignments=None, cell_width_in_characters=0):
    def padalignment(st):
      header = alignment_lookup[st[0]]
      return f"{header[:1]}{'-'*st[1]}{header[1:]}"

    self.write("| ")
    self.write(" | ".join(headers))
    self.write(f" |{linesep}")
    header_lens = list(map(lambda s: len(s) - 1, headers))
    if alignments:
      self.write("|")
      aligns = list(map(padalignment, zip(alignments, header_lens)))
      self.write("|".join(aligns))
      self.write(f"|{linesep}")
    else:
      self.write("| ")
      self.write(" | ".join("-" * len(headers)))
      self.write(f" |{linesep}")

    for row in rows:
      self.write("| ")
      for cell in row:
        cell = str(cell)
        if "\n" in cell:
          cell = "<br/>".join(cell.split("\n"))
        if cell_width_in_characters != 0:
          cell = "<br/>".join(wrap(cell, cell_width_in_characters))
        self.write(f"{cell} |")
      self.write(f"{linesep}")
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
