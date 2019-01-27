#!/usr/bin/python3
# Copyright (c) 2018, Anthony DeDominic <adedomin@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from xml.sax.saxutils import escape
from urllib.parse import quote
from datetime import datetime


def escapeAll(text_el):
    return escape(text_el, {'"': '&quot;', '\'': '&apos;'})


def simpleTag(tag_name, value):
    return f'<{tag_name}>{escapeAll(value)}</{tag_name}>'


def linkTag(href, secret):
    return f'<link href="{escapeAll(f"{href}?secret={quote(secret)}")}"/>'


def entryEl(link, secret, entry):
    return ('<entry>' +
            simpleTag('id', entry['id']) +
            simpleTag('title', entry['title']) +
            linkTag(link + '/get-item/' + entry['id'], secret) +
            simpleTag('updated', entry['date']) +
            simpleTag('content', entry['content']) +
            '</entry>')


def createAtomFeed(ident, title, link, secret, entries):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<feed xmlns="http://www.w3.org/2005/Atom">' +
            simpleTag('id', ident) +
            simpleTag('title', title) +
            linkTag(link, secret) +
            simpleTag('updated', datetime.utcnow()
                                         .isoformat(timespec='seconds')+'Z') +
            ''.join([entryEl(link, secret, entry) for entry in entries]) +
            '</feed>')
