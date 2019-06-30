import sys

from src.html2tex import config
from src.html2tex.compat import htmlentitydefs


def name2cp(k):
    """Return sname to codepoint"""
    if k == "apos":
        return ord("'")
    return htmlentitydefs.name2codepoint[k]


unifiable_n = {name2cp(k): v for k, v in config.UNIFIABLE.items() if k != "nbsp"}


def hn(tag):
    if tag[0] == "h" and len(tag) == 2:
        try:
            n = int(tag[1])
            if n in range(1, 7):
                return n
        except ValueError:
            return 0


def skipwrap(para, wrap_links, wrap_list_items):
    # If it appears to contain a link
    # don't wrap
    if (len(config.RE_LINK.findall(para)) > 0) and not wrap_links:
        return True
    # If the text begins with four spaces or one tab, it's a code block;
    # don't wrap
    if para[0:4] == "    " or para[0] == "\t":
        return True

    # If the text begins with only two "--", possibly preceded by
    # whitespace, that's an emdash; so wrap.
    stripped = para.lstrip()
    if stripped[0:2] == "--" and len(stripped) > 2 and stripped[2] != "-":
        return False

    # I'm not sure what this is for; I thought it was to detect lists,
    # but there's a <br>-inside-<span> case in one of the tests that
    # also depends upon it.
    if stripped[0:1] in ("-", "*") and not stripped[0:2] == "**":
        return not wrap_list_items

    # If the text begins with a single -, *, or +, followed by a space,
    # or an integer, followed by a ., followed by a space (in either
    # case optionally proceeded by whitespace), it's a list; don't wrap.
    if config.RE_ORDERED_LIST_MATCHER.match(
        stripped
    ) or config.RE_UNORDERED_LIST_MATCHER.match(stripped):
        return True

    return False


def wrapwrite(text):
    text = text.encode("utf-8")
    try:  # Python3
        sys.stdout.buffer.write(text)
    except AttributeError:
        sys.stdout.write(text)


def wrap_read():
    """
    :rtype: str
    """
    try:
        return sys.stdin.read()
    except AttributeError:
        return sys.stdin.buffer.read()


def escape_md(text):
    """
    Escapes markdown-sensitive characters within other markdown
    constructs.
    """
    return config.RE_MD_CHARS_MATCHER.sub(r"\\\1", text)

def make_table_count(count):
    return "||" + " ".join(["c" for i in range(count)]) + "||"

def escape_md_section(text, snob=False):
    """
    Escapes markdown-sensitive characters across whole document sections.
    """
    text = config.RE_MD_BACKSLASH_MATCHER.sub(r"\\\1", text)

    if snob:
        text = config.RE_MD_CHARS_MATCHER_ALL.sub(r"\\\1", text)

    text = config.RE_MD_DOT_MATCHER.sub(r"\1\\\2", text)
    text = config.RE_MD_PLUS_MATCHER.sub(r"\1\\\2", text)
    text = config.RE_MD_DASH_MATCHER.sub(r"\1\\\2", text)

    return text
