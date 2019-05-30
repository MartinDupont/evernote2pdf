#!/bin/python
# -*- coding: utf-8 -*-
"""Stole this from: https://github.com/CarlLee/ENML_PY, MIT license applies. """
import os
from bs4 import BeautifulSoup
import html2tex
import hashlib
import binascii

MIME_TO_EXTESION_MAPPING = {
    'image/png': '.png',
    'image/jpg': '.jpg',
    'image/jpeg': '.jpg',
    'image/gif': '.gif'
}

REPLACEMENTS = [
    ("&quot;", "\""),
    ("&amp;apos;", "'"),
    ("&apos;", "'"),
    ("&amp;", "&"),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&laquo;", "<<"),
    ("&raquo;", ">>"),
    ("&#039;", "'"),
    ("&#8220;", "\""),
    ("&#8221;", "\""),
    ("&#8216;", "\'"),
    ("&#8217;", "\'"),
    ("&#9632;", ""),
    ("&#8226;", "-")]


def ENMLToHTML(content, store, pretty=True, header=True, **kwargs):
    """
    converts ENML string into HTML string
    :param header: If True, note is wrapped in a <HTML><BODY> block.
    :type header: bool
    :param media_filter: optional callable objENMLToTextect used to filter undesired resources.
    Returns True if the resource must be kept in HTML, False otherwise.
    :type media_fiter: callable object with prototype: `bool func(hash_str, mime_type)`
    """
    soup = BeautifulSoup(content, "html.parser")

    todos = soup.find_all('en-todo')
    for todo in todos:
        checkbox = soup.new_tag('input')
        checkbox['type'] = 'checkbox'
        checkbox['disabled'] = 'true'
        if todo.has_attr('checked'):
            checkbox['checked'] = todo['checked']
        todo.replace_with(checkbox)

    if 'media_filter' in kwargs:
        media_filter = kwargs['media_filter']
        for media in filter(
                lambda media: not media_filter(media['hash'], media['type']),
                soup.find_all('en-media')):
            media.extract()

    all_media = soup.find_all('en-media')
    for media in all_media:
        resource_url = store.save(media['hash'], media['type'])
        new_tag = soup.new_tag('img')
        new_tag['src'] = resource_url
        media.replace_with(new_tag)

    note = soup.find('en-note')
    if note:
        if header:
            html = soup.new_tag('html')
            html.append(note)
            note.name = 'body'
        else:
            html = note
            note.name = 'div'

        output = html.prettify().encode('utf-8') if pretty else str(html)
        return output

    return content


def ENMLToTex(content, store, pretty=True, header=True):
    """
    converts ENML string into HTML string then converts HTML string to plain text
    :param header: If True, note is wrapped in a <HTML><BODY> block.
    :type header: bool
    :param media_filter: optional callable object used to filter undesired resources.
    Returns True if the resource must be kept in HTML, False otherwise.
    :type media_fiter: callable object with prototype: `bool func(hash_str, mime_type)`
    """
    text_maker = html2tex.HTML2Tex()
    text_maker.images_as_html = True

    html = ENMLToHTML(content, store, pretty, header, media_filter=images_media_filter).decode('utf-8')
    text = text_maker.handle(html)
    for entity, replacement in REPLACEMENTS:
        text = text.replace(entity, replacement)
    return text


class MediaStore:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.dataStore = {}

    def commit_to_memory(self, data):
        bytes = binascii.a2b_base64(data)
        hash = hashlib.md5(bytes).hexdigest()
        self.dataStore[hash] = data

    def save(self, hash_str, mime_type):
        """
        save the specified hash and return the saved file's URL
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        data = self.dataStore[hash_str]
        bytes = binascii.a2b_base64(data)
        file_path = self.path + '/'  + hash_str + MIME_TO_EXTESION_MAPPING[mime_type]
        f = open(file_path, "wb")
        f.write(bytes)
        f.close()
        return file_path

def images_media_filter(hash_str, mime_type):
    """Helper usable with `ENMLToHTML` `media_filter` parameter to filter-out
    resources that are not images so that output HTML won't contain
    such invalid element <IMG src="path/to/document.pdf/>
    """
    return mime_type in MIME_TO_EXTESION_MAPPING
