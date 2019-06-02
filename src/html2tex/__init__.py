# coding: utf-8
"""html2text: Turn HTML into equivalent Markdown-structured text."""
from __future__ import division, unicode_literals

import re
import sys
from textwrap import wrap

from src.html2tex import config
from src.html2tex.compat import HTMLParser, urlparse
from src.html2tex.format_latex import make_picture_link
from src.html2tex.utils import (
    dumb_css_parser,
    element_style,
    escape_md,
    escape_md_section,
    google_fixed_width_font,
    google_has_height,
    google_list_style,
    google_text_emphasis,
    hn,
    list_numbering_start,
    name2cp,
    pad_tables_in_text,
    skipwrap,
    unifiable_n,
)

try:
    chr = unichr
    nochr = unicode("")
except NameError:
    # python3 uses chr
    nochr = str("")

__version__ = (2018, 1, 9)


# TODO:
# Support decoded entities with UNIFIABLE.


class HTML2Tex(HTMLParser.HTMLParser):
    def __init__(self, out=None, baseurl="", bodywidth=config.BODY_WIDTH):
        """
        Input parameters:
            out: possible custom replacement for self.outtextf (which
                 appends lines of text).
            baseurl: base URL of the document we process
        """
        kwargs = {}
        if sys.version_info >= (3, 4):
            kwargs["convert_charrefs"] = False
        HTMLParser.HTMLParser.__init__(self, **kwargs)

        # Config options
        self.split_next_td = False
        self.td_count = 0
        self.table_start = False
        self.unicode_snob = config.UNICODE_SNOB  # covered in cli
        self.escape_snob = config.ESCAPE_SNOB  # covered in cli
        self.links_each_paragraph = config.LINKS_EACH_PARAGRAPH
        self.body_width = bodywidth  # covered in cli
        self.skip_internal_links = config.SKIP_INTERNAL_LINKS  # covered in cli
        self.inline_links = config.INLINE_LINKS  # covered in cli
        self.protect_links = config.PROTECT_LINKS  # covered in cli
        self.google_list_indent = config.GOOGLE_LIST_INDENT  # covered in cli
        self.ignore_links = config.IGNORE_ANCHORS  # covered in cli
        self.ignore_images = config.IGNORE_IMAGES  # covered in cli
        self.images_as_html = config.IMAGES_AS_HTML  # covered in cli
        self.images_to_alt = config.IMAGES_TO_ALT  # covered in cli
        self.images_with_size = config.IMAGES_WITH_SIZE  # covered in cli
        self.ignore_emphasis = config.IGNORE_EMPHASIS  # covered in cli
        self.bypass_tables = config.BYPASS_TABLES  # covered in cli
        self.ignore_tables = config.IGNORE_TABLES  # covered in cli
        self.ul_item_mark = "\\item"  # covered in cli
        self.emphasis_opening = "\\textit{"  # covered in cli
        self.strong_opening = "\\textbf{"
        self.strikethrough_opening = "\\sout{"
        self.single_line_break = config.SINGLE_LINE_BREAK  # covered in cli
        self.use_automatic_links = config.USE_AUTOMATIC_LINKS  # covered in cli
        self.hide_strikethrough = False  # covered in cli
        self.mark_code = config.MARK_CODE
        self.wrap_list_items = config.WRAP_LIST_ITEMS  # covered in cli
        self.wrap_links = config.WRAP_LINKS  # covered in cli
        self.pad_tables = config.PAD_TABLES  # covered in cli
        self.default_image_alt = config.DEFAULT_IMAGE_ALT  # covered in cli
        self.tag_callback = None
        self.open_quote = "``" #config.OPEN_QUOTE  # covered in cli
        self.close_quote = "''" #config.CLOSE_QUOTE  # covered in cli

        if out is None:
            self.out = self.outtextf
        else:
            self.out = out

        # empty list to store output characters before they are "joined"
        self.outtextlist = []

        self.quiet = 0
        self.p_p = 0  # number of newline character to print before next output
        self.outcount = 0
        self.start = True
        self.space = False
        self.a = []
        self.astack = []
        self.maybe_automatic_link = None
        self.empty_link = False
        self.absolute_url_matcher = re.compile(r"^[a-zA-Z+]+://")
        self.acount = 0
        self.list = []
        self.blockquote = 0
        self.pre = False
        self.startpre = False
        self.code = False
        self.quote = False
        self.br_toggle = ""
        self.lastWasNL = False
        self.lastWasList = False
        self.style = 0
        self.style_def = {}
        self.tag_stack = []
        self.emphasis = 0
        self.drop_white_space = 0
        self.inheader = False
        self.abbr_title = None  # current abbreviation definition
        self.abbr_data = None  # last inner HTML (for abbr being defined)
        self.abbr_list = {}  # stack of abbreviations to write later
        self.baseurl = baseurl
        self.stressed = False
        self.preceding_stressed = False
        self.preceding_data = None
        self.current_tag = None

        config.UNIFIABLE["nbsp"] = "&nbsp_place_holder;"

    def feed(self, data):
        data = data.replace("</' + 'script>", "</ignore>")
        HTMLParser.HTMLParser.feed(self, data)

    def handle(self, data):
        self.feed(data)
        self.feed("")
        markdown = self.optwrap(self.close())
        if self.pad_tables:
            return pad_tables_in_text(markdown)
        else:
            return markdown

    def outtextf(self, s):
        self.outtextlist.append(s)
        if s:
            self.lastWasNL = s[-1] == "\n"

    def close(self):
        HTMLParser.HTMLParser.close(self)

        self.pbr()
        self.o("", 0, "end")

        outtext = nochr.join(self.outtextlist)

        if self.unicode_snob:
            nbsp = chr(name2cp("nbsp"))
        else:
            nbsp = chr(32)
        outtext = outtext.replace("&nbsp_place_holder;", nbsp)

        # Clear self.outtextlist to avoid memory leak of its content to
        # the next handling.
        self.outtextlist = []

        return outtext

    def handle_charref(self, c):
        self.handle_data(self.charref(c), True)

    def handle_entityref(self, c):
        ref = self.entityref(c)

        # ref may be an empty string (e.g. for &lrm;/&rlm; markers that should
        # not contribute to the final output).
        # self.handle_data cannot handle a zero-length string right after a
        # stressed tag or mid-text within a stressed tag (text get split and
        # self.stressed/self.preceding_stressed gets switched after the first
        # part of that text).
        if ref:
            self.handle_data(ref, True)

    def handle_starttag(self, tag, attrs):
        self.handle_tag(tag, attrs, 1)

    def handle_endtag(self, tag):
        self.handle_tag(tag, None, 0)

    def previousIndex(self, attrs):
        """
        :type attrs: dict

        :returns: The index of certain set of attributes (of a link) in the
        self.a list. If the set of attributes is not found, returns None
        :rtype: int
        """
        if "href" not in attrs:
            return None
        i = -1
        for a in self.a:
            i += 1
            match = False

            if "href" in a and a["href"] == attrs["href"]:
                if "title" in a or "title" in attrs:
                    if (
                            "title" in a
                            and "title" in attrs
                            and a["title"] == attrs["title"]
                    ):
                        match = True
                else:
                    match = True

            if match:
                return i

    def handle_emphasis(self, start, tag_style, parent_style):
        """
        Handles various text emphases
        """
        tag_emphasis = google_text_emphasis(tag_style)
        parent_emphasis = google_text_emphasis(parent_style)

        # handle Google's text emphasis
        strikethrough = "line-through" in tag_emphasis and self.hide_strikethrough

        # google and others may mark a font's weight as `bold` or `700`
        bold = False
        for bold_marker in config.BOLD_TEXT_STYLE_VALUES:
            bold = bold_marker in tag_emphasis and bold_marker not in parent_emphasis
            if bold:
                break

        italic = "italic" in tag_emphasis and "italic" not in parent_emphasis
        fixed = (
                google_fixed_width_font(tag_style)
                and not google_fixed_width_font(parent_style)
                and not self.pre
        )

        if start:
            # crossed-out text must be handled before other attributes
            # in order not to output qualifiers unnecessarily
            if bold or italic or fixed:
                self.emphasis += 1
            if strikethrough:
                self.quiet += 1
            if italic:
                self.o(self.emphasis_opening)
                self.drop_white_space += 1
            if bold:
                self.o(self.strong_opening)
                self.drop_white_space += 1
            if fixed:
                self.o("`")
                self.drop_white_space += 1
                self.code = True
        else:
            if bold or italic or fixed:
                # there must not be whitespace before closing emphasis mark
                self.emphasis -= 1
                self.space = False
            if fixed:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o("`")
                self.code = False
            if bold:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o("}")
            if italic:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o("}")
            # space is only allowed after *all* emphasis marks
            if (bold or italic) and not self.emphasis:
                self.o(" ")
            if strikethrough:
                self.quiet -= 1

    def handle_tag(self, tag, attrs, start):
        self.current_tag = tag
        # attrs is None for endtags
        if attrs is None:
            attrs = {}
        else:
            attrs = dict(attrs)

        if self.tag_callback is not None:
            if self.tag_callback(self, tag, attrs, start) is True:
                return

        # first thing inside the anchor tag is another tag
        # that produces some output
        # todo
        if (
                start
                and self.maybe_automatic_link is not None
                and tag not in ["p", "div", "style", "dl", "dt"]
                and (tag != "img" or self.ignore_images)
        ):
            self.o("[") #
            self.maybe_automatic_link = None
            self.empty_link = False


        if hn(tag): # Headers ! # todo
            self.p()
            if start:
                self.inheader = True
                self.o(hn(tag) * "#" + " ")
            else:
                self.inheader = False
                return  # prevent redundant emphasis marks on headers

        if tag in ["p", "div"]: # todo
            if self.astack and tag == "div":
                pass
            else:
                self.p()

        if tag == "br" and start:
            # if self.blockquote > 0:
            #     self.o("  \n> ")
            # else:
            #self.o("  \\newline")
            self.o("  \n")


        if tag == "hr" and start:
            self.p()
            self.o("\\hrule")
            self.p()

        if tag in ["head", "style", "script"]: # todo
            if start:
                self.quiet += 1
            else:
                self.quiet -= 1

        if tag == "style": # todo
            if start:
                self.style += 1
            else:
                self.style -= 1

        if tag in ["body"]: # todo
            self.quiet = 0  # sites like 9rules.com never close <head>

        if tag == "blockquote": # todo
            if start:
                self.p()
                self.o("> ", 0, 1)
                self.start = True
                self.blockquote += 1
            else:
                self.blockquote -= 1
                self.p()

        def no_preceding_space(self):
            return self.preceding_data and re.match(r"[^\s]", self.preceding_data[-1])

        if tag in ["em", "i", "u"] and not self.ignore_emphasis:
            if start:
                if no_preceding_space(self):
                    emphasis = " " + self.emphasis_opening
                else:
                    emphasis = self.emphasis_opening
            else:
                emphasis = "}"

            self.o(emphasis)
            if start:
                self.stressed = True

        if tag in ["strong", "b"] and not self.ignore_emphasis:
            if start:
                if no_preceding_space(self):
                    strong = " " + self.strong_opening
                else:
                    strong = self.strong_opening
            else:
                strong = "}"

            self.o(strong)
            if start:
                self.stressed = True

        if tag in ["del", "strike", "s"]:
            if start and no_preceding_space(self):
                strike = self.strikethrough_opening
            else:
                strike = "}"

            self.o(strike)
            if start:
                self.stressed = True

        if tag in ["kbd", "code", "tt"] and not self.pre: # todo
            self.o("")
            self.code = not self.code

        if tag == "abbr": # todo
            if start:
                self.abbr_title = None
                self.abbr_data = ""
                if "title" in attrs:
                    self.abbr_title = attrs["title"]
            else:
                if self.abbr_title is not None:
                    self.abbr_list[self.abbr_data] = self.abbr_title
                    self.abbr_title = None
                self.abbr_data = ""

        if tag == "q":
            if not self.quote:
                self.o(self.open_quote)
            else:
                self.o(self.close_quote)
            self.quote = not self.quote

        def link_url(self, link, title=""):
            url = urlparse.urljoin(self.baseurl, link)
            title = ' "{}"'.format(title) if title.strip() else ""
            self.o("]({url}{title})".format(url=escape_md(url), title=title))

        if tag == "a" and not self.ignore_links: #todo
            if start:
                if (
                        "href" in attrs
                        and attrs["href"] is not None
                        and not (self.skip_internal_links and attrs["href"].startswith("#"))
                ):
                    self.astack.append(attrs)
                    self.maybe_automatic_link = attrs["href"]
                    self.empty_link = True
                    if self.protect_links:
                        attrs["href"] = "<" + attrs["href"] + ">"
                else:
                    self.astack.append(None)
            else:
                if self.astack:
                    a = self.astack.pop()
                    if self.maybe_automatic_link and not self.empty_link:
                        self.maybe_automatic_link = None
                    elif a:
                        if self.empty_link:
                            self.o("[")
                            self.empty_link = False
                            self.maybe_automatic_link = None
                        if self.inline_links:
                            try:
                                title = a["title"] if a["title"] else ""
                                title = escape_md(title)
                            except KeyError:
                                link_url(self, a["href"], "")
                            else:
                                link_url(self, a["href"], title)
                        else:
                            i = self.previousIndex(a)
                            if i is not None:
                                a = self.a[i]
                            else:
                                self.acount += 1
                                a["count"] = self.acount
                                a["outcount"] = self.outcount
                                self.a.append(a)
                            self.o("][" + str(a["count"]) + "]")

        if tag == "img" and start and not self.ignore_images:
            if "src" in attrs:
                if not self.images_to_alt:
                    attrs["href"] = attrs["src"]
                alt = attrs.get("alt") or self.default_image_alt

                self.o(make_picture_link(attrs["src"], alt))

                # If we have images_with_size, write raw html including width,
                # height, and alt attributes
                #if "width" in attrs:
                #    self.o("width='" + attrs["width"] + "' ")
                #if "height" in attrs:
                #    self.o("height='" + attrs["height"] + "' ")
                return


        if tag == "dl" and start: #todo
            self.p()
        if tag == "dt" and not start: #todo
            self.pbr()
        if tag == "dd" and start: #todo
            self.o("    ")
        if tag == "dd" and not start: #todo
            self.pbr()

        if tag in ["ol", "ul"]:
            if start:
                if tag == "ol":
                    self.o("\\begin{enumerate}")
                else:
                    self.o("\\begin{itemize}")
            else:
                if tag == "ol":
                    self.o("\\end{enumerate}")
                else:
                    self.o("\\end{itemize}")

        if tag == "li":
            if start:
                self.o(self.ul_item_mark + " ")

        if tag in ["table", "tr", "td", "th"]: #todo
            if self.ignore_tables:
                if tag == "tr":
                    if start:
                        pass
                    else:
                        self.soft_br()
                else:
                    pass

            elif self.bypass_tables:
                if start:
                    self.soft_br()
                if tag in ["td", "th"]:
                    if start:
                        self.o("<{}>\n\n".format(tag))
                    else:
                        self.o("\n</{}>".format(tag))
                else:
                    if start:
                        self.o("<{}>".format(tag))
                    else:
                        self.o("</{}>".format(tag))

            else:
                if tag == "table":
                    if start:
                        self.table_start = True
                        if self.pad_tables:
                            self.o("<" + config.TABLE_MARKER_FOR_PAD + ">")
                            self.o("  \n")
                    else:
                        if self.pad_tables:
                            self.o("</" + config.TABLE_MARKER_FOR_PAD + ">")
                            self.o("  \n")
                if tag in ["td", "th"] and start:
                    if self.split_next_td:
                        self.o("| ")
                    self.split_next_td = True

                if tag == "tr" and start:
                    self.td_count = 0
                if tag == "tr" and not start:
                    self.split_next_td = False
                    self.soft_br()
                if tag == "tr" and not start and self.table_start:
                    # Underline table header
                    self.o("|".join(["---"] * self.td_count))
                    self.soft_br()
                    self.table_start = False
                if tag in ["td", "th"] and start:
                    self.td_count += 1

        if tag == "pre": #todo
            if start:
                self.startpre = True
                self.pre = True
            else:
                self.pre = False
                if self.mark_code:
                    self.out("\n[/code]")
            self.p()

    # TODO: Add docstring for these one letter functions
    def pbr(self):
        "Pretty print has a line break"
        if self.p_p == 0:
            self.p_p = 1

    def p(self):
        "Set pretty print to 1 or 2 lines"
        self.p_p = 1 if self.single_line_break else 2

    def soft_br(self):
        "Soft breaks"
        self.pbr()
        self.br_toggle = "  "

    def o(self, data, puredata=0, force=0):
        """handle_tag
        Deal with indentation and whitespace
        """
        if self.abbr_data is not None:
            self.abbr_data += data

        if not self.quiet:
            if puredata and not self.pre:
                # This is a very dangerous call ... it could mess up
                # all handling of &nbsp; when not handled properly
                # (see entityref)
                data = re.sub(r"\s+", r" ", data)
                if data and data[0] == " ":
                    self.space = True
                    data = data[1:]
            if not data and not force:
                return

            if self.startpre:
                # self.out(" :") #TODO: not output when already one there
                if not data.startswith("\n") and not data.startswith("\r\n"):
                    # <pre>stuff...
                    data = "\n" + data
                if self.mark_code:
                    self.out("\n[code]")
                    self.p_p = 0

            bq = ">" * self.blockquote
            if not (force and data and data[0] == ">") and self.blockquote:
                bq += " "

            if self.pre:
                if not self.list:
                    bq += "    "
                # else: list content is already partially indented
                for i in range(len(self.list)):
                    bq += "    "
                data = data.replace("\n", "\n" + bq)

            if self.startpre:
                self.startpre = False
                if self.list:
                    # use existing initial indentation
                    data = data.lstrip("\n")

            if self.start:
                self.space = False
                self.p_p = 0
                self.start = False

            if force == "end":
                # It's the end.
                self.p_p = 0
                self.out("\n")
                self.space = False

            if self.p_p:
                self.out((self.br_toggle + "\n" + bq) * self.p_p)
                self.space = False
                self.br_toggle = ""

            if self.space:
                if not self.lastWasNL:
                    self.out(" ")
                self.space = False

            if self.a and (
                    (self.p_p == 2 and self.links_each_paragraph) or force == "end"
            ):
                if force == "end":
                    self.out("\n")

                newa = []
                for link in self.a:
                    if self.outcount > link["outcount"]:
                        self.out(
                            "   ["
                            + str(link["count"])
                            + "]: "
                            + urlparse.urljoin(self.baseurl, link["href"])
                        )
                        if "title" in link:
                            self.out(" (" + link["title"] + ")")
                        self.out("\n")
                    else:
                        newa.append(link)

                # Don't need an extra line when nothing was done.
                if self.a != newa:
                    self.out("\n")

                self.a = newa

            if self.abbr_list and force == "end":
                for abbr, definition in self.abbr_list.items():
                    self.out("  *[" + abbr + "]: " + definition + "\n")

            self.p_p = 0
            self.out(data)
            self.outcount += 1

    def handle_data(self, data, entity_char=False):
        if not data:
            # Data may be empty for some HTML entities. For example,
            # LEFT-TO-RIGHT MARK.
            return

        if self.stressed:
            data = data.strip()
            self.stressed = False
            self.preceding_stressed = True
        elif self.preceding_stressed:
            if (
                    re.match(r"[^\s.!?]", data[0])
                    and not hn(self.current_tag)
                    and self.current_tag not in ["a", "code", "pre"]
            ):
                # should match a letter or common punctuation
                data = " " + data
            self.preceding_stressed = False

        if self.style:
            self.style_def.update(dumb_css_parser(data))

        if self.maybe_automatic_link is not None:
            href = self.maybe_automatic_link
            if (
                    href == data
                    and self.absolute_url_matcher.match(href)
                    and self.use_automatic_links
            ):
                self.o("<" + data + ">")
                self.empty_link = False
                return
            else:
                self.o("[")
                self.maybe_automatic_link = None
                self.empty_link = False

        if not self.code and not self.pre and not entity_char:
            data = escape_md_section(data, snob=self.escape_snob)
        self.preceding_data = data
        self.o(data, 1)

    def charref(self, name):
        if name[0] in ["x", "X"]:
            c = int(name[1:], 16)
        else:
            c = int(name)

        if not self.unicode_snob and c in unifiable_n:
            return unifiable_n[c]
        else:
            try:
                return chr(c)
            except ValueError:  # invalid unicode
                return ""

    def entityref(self, c):
        if not self.unicode_snob and c in config.UNIFIABLE:
            return config.UNIFIABLE[c]
        else:
            try:
                name2cp(c)
            except KeyError:
                return "&" + c + ";"
            else:
                if c == "nbsp":
                    return config.UNIFIABLE[c]
                else:
                    return chr(name2cp(c))

    def google_nest_count(self, style):
        """
        Calculate the nesting count of google doc lists

        :type style: dict

        :rtype: int
        """
        nest_count = 0
        if "margin-left" in style:
            nest_count = int(style["margin-left"][:-2]) // self.google_list_indent

        return nest_count

    def optwrap(self, text):
        """
        Wrap all paragraphs in the provided text.

        :type text: str

        :rtype: str
        """
        if not self.body_width:
            return text

        result = ""
        newlines = 0
        # I cannot think of a better solution for now.
        # To avoid the non-wrap behaviour for entire paras
        # because of the presence of a link in it
        if not self.wrap_links:
            self.inline_links = False
        for para in text.split("\n"):
            if len(para) > 0:
                if not skipwrap(para, self.wrap_links, self.wrap_list_items):
                    indent = ""
                    if para.startswith("  " + self.ul_item_mark):
                        indent = "    "  # For list items.
                    wrapped = wrap(
                        para,
                        self.body_width,
                        break_long_words=False,
                        subsequent_indent=indent,
                    )
                    result += "\n".join(wrapped)
                    if indent or para.endswith("  "):
                        result += "  \n"
                        newlines = 1
                    else:
                        result += "\n\n"
                        newlines = 2
                else:
                    # Warning for the tempted!!!
                    # Be aware that obvious replacement of this with
                    # line.isspace()
                    # DOES NOT work! Explanations are welcome.
                    if not config.RE_SPACE.match(para):
                        result += para + "\n"
                        newlines = 1
            else:
                if newlines < 2:
                    result += "\n"
                    newlines += 1
        return result


def html2text(html, baseurl="", bodywidth=None):
    if bodywidth is None:
        bodywidth = config.BODY_WIDTH
    h = HTML2Text(baseurl=baseurl, bodywidth=bodywidth)

    return h.handle(html)
