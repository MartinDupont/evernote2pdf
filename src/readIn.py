import xml.etree.ElementTree as ET
from enml_reader import *
from src.enml_reader import ENMLToText, MediaStore

tree = ET.parse('../test/test_data.enex')
root = tree.getroot()

def getUpdatedDateIfExists(child):
    updated = child.find("updated")
    if updated is not None:
        return "Updated:" + parseDateString(updated.text)
    return ""


def getElements(child, search):
    hits = [e.text for e in child.findall(search)]
    return ", ".join(hits)


def parseDateString(dateString):
    year = dateString[0:4]
    month = dateString[4:6]
    day = dateString[6:8]

    return "/".join([day, month, year])


mediaStore = MediaStore("../out")

for child in root:
    print("============== new note ================")
    print(child.find("title").text)
    print("Created: {} {}".format(parseDateString(child.find("created").text), getUpdatedDateIfExists(child)))
    print("Tags: {}".format(getElements(child, "tag")))
    thing = child.find("resource")
    if thing:
        mediaStore.commit_to_memory(thing.find("data").text)

    print(ENMLToText(child.find("content").text, mediaStore))
