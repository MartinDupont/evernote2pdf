import xml.etree.ElementTree as ET
from enml_reader import *

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


for child in root:
    print("============== new note ================")
    print(child.find("title").text)
    print("Created: {} {}".format(parseDateString(child.find("created").text), getUpdatedDateIfExists(child)))
    print("Tags: {}".format(getElements(child, "tag")))

    print(ENMLToText(child.find("content").text))
