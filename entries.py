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

from feedgen.feed import FeedGenerator
from lxmlclean import clean

from collections import deque
from datetime import datetime
from sys import exit, stderr
from uuid import uuid4
import json


class Entries:
    '''Class that holds feed/entries'''

    __config = None
    __feedName = 'root'
    __feedFile = ''
    __entryFile = ''
    __entries = None

    def __writeEntries(self):
        try:
            tmpEntry = json.dumps(list(self.__entries))
            with open(self.__entryFile, 'w+') as f:
                f.write(tmpEntry)
        except IOError as e:
            print('%s: failed to save entries' % e,
                  file=stderr)
            exit(1)
        except TypeError as e:
            print('%s: failed to deserialize some entry property' % e,
                  file=stderr)
            exit(1)

    def __writeAtomFeed(self, uid, title, content, date):
        try:
            tmpFeed = FeedGenerator()
            tmpFeed.id(self.__config.feedUrl)
            tmpFeed.title(self.__config.feedTitle)
            tmpFeed.link(href=self.__config.feedUrl + '/' +
                         self.__feedName + '/' +
                         self.__config.secret,
                         rel='self')
            # add ones in the feed
            for entry in self.__entries:
                tmpEntry = tmpFeed.add_entry()
                tmpEntry.id(entry['id'] or str(uuid4()))
                tmpEntry.title(entry['title'] or 'No title')
                tmpEntry.content(entry['content'] or 'No content')
                tmpEntry.updated(entry['date'] or datetime.utcnow())
                tmpEntry.link(href=self.__config.feedUrl + '/' +
                              self.__feedName + '/' +
                              self.__config.secret + '/' +
                              'get/' +
                              entry["id"])
            # add new ones to see if lxml will cry about them.
            # this may throw ValueError
            tmpEntry = tmpFeed.add_entry()
            tmpEntry.id(uid)
            tmpEntry.title(title)
            tmpEntry.content(content)
            tmpEntry.updated(date)
            # write file
            tmpFeed.atom_file(self.__feedFile)
        except IOError as e:
            print('%s: failed to write atom file' % e,
                  file=stderr)
            exit(1)

    def __init__(self, feedname, config):
        self.__config = config
        self.__feedName = feedname
        self.__feedFile = f'{config.feeds}/{feedname}.atom'
        self.__entryFile = f'{config.entries}/{feedname}.json'

        # load entriess
        try:
            with open(self.__entryFile, 'r') as f:
                try:
                    tmpEntries = json.loads(f.read())
                except Exception:
                    tmpEntries = []
                if isinstance(tmpEntries, list):
                    self.__entries = deque(tmpEntries,
                                           maxlen=config.maxEntries)
                else:
                    raise ValueError('entry file %s is not a list' %
                                     self.__entryFile)
        except IOError:
            try:
                with open(self.__entryFile, 'w+') as f:
                    f.write('[]')
                    self.__entries = deque([], maxlen=config.maxEntries)
            except IOError as e:
                print('%s: make sure file is writable' % e,
                      file=stderr)
                exit(1)

    def addEntry(self,
                 title,
                 content):
        title = clean(title)
        content = clean(content)
        date = datetime.utcnow().isoformat(timespec='seconds')+'Z'
        uid = str(uuid4())
        # will throw if sensitive xml parser doesn't like some
        # random non utf8 or ascii control code...
        self.__writeAtomFeed(uid, title, content, date)
        # save entry since it's lxml approved(tm)
        self.__entries.append({
            'id': uid,
            'title': title,
            'content': content,
            'date': date,
        })
        self.__writeEntries()

    def getContentById(self, contentId):
        for entry in self.__entries:
            if entry['id'] == contentId:
                return f'''\
Title: {entry['title']}
Date:  {entry['date']}

{entry['content']}
'''
        return None
