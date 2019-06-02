import xml.etree.ElementTree as ET
from src.enml_reader import enml_to_tex, MediaStore
from shutil import copyfile


def get_updated_date_if_exists(child):
    updated = child.find("updated")
    if updated is not None:
        return parse_date_string(updated.text)
    return None


def get_elements(child, search):
    hits = [e.text for e in child.findall(search)]
    return ", ".join(hits)


def parse_date_string(date_string):
    year = date_string[0:4]
    month = date_string[4:6]
    day = date_string[6:8]

    return year, month, day


def make_tag_footer(tags):
    if not tags:
        return ""

    return "\\makeTagFooter{{}}\nTags: {}".format(tags)


def make_title(child):
    title = child.find("title").text
    if not title is None:
        if not title in ["Untitled", "Unbenannte Notiz"]:
            return title
    return ""

def make_new_entry(year, month, day, title=""):
    return "\\doubledatedsection{{{}}}{{{}}}{{{}}}{{{}}}\n".format(year, month, day, title)

def make_new_entry_with_updated(year, month, day, updated_year, updated_month, updated_day, title=""):
    return "\\doubledatedsectionupdate{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}\n".format(year, month, day, updated_year, updated_month, updated_day, title)


def get_template_head_and_foot(path):
    f = open(path, "r")
    toggle = False
    header = ""
    footer = ""
    for line in f.readlines():
        if not "REPLACE_THIS_STRING" in line:
            if not toggle:
                header += line
            else:
                footer += line
        else:
            toggle = True
    return header, footer


if __name__ == "__main__":
    tree = ET.parse('../test/newer_notebook.enex')
    root = tree.getroot()
    mediaStore = MediaStore("../out")
    copyfile("../latex/diary.cls", "../out/diary.cls")

    head, foot = get_template_head_and_foot("../latex/diary.tex")

    with open("../out/diary.tex", "w") as f:
        f.write(head)

        for child in root:
            title = make_title(child)
            created_date = parse_date_string(child.find("created").text)
            updated = get_updated_date_if_exists(child)
            tags = get_elements(child, "tag")
            resources = child.findall("resource")
            for resource in resources:
                mediaStore.commit_to_memory(resource.find("data").text)

            if updated is not None:
                f.write(make_new_entry_with_updated(*created_date, *updated, title))
            else:
                f.write(make_new_entry(*created_date, title))
            f.write(enml_to_tex(child.find("content").text, mediaStore))
            f.write(make_tag_footer(tags))

        f.write(foot)
        f.close()
