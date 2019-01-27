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

from atom import createAtomFeed
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
    __feedLink = ''
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

    def __writeAtomFeed(self):
        try:
            tmpFeed = createAtomFeed(self.__feedLink,
                                     self.__feedName,
                                     self.__feedLink,
                                     self.__config.secret,
                                     self.__entries)
            with open(self.__feedFile, 'w+') as f:
                f.write(tmpFeed)
        except IOError as e:
            print(f'{e}: failed to save feed file',
                  file=stderr)
            exit(1)

    def __init__(self, feedname, config):
        self.__config = config
        self.__feedName = feedname
        self.__feedFile = f'{config.feeds}/{feedname}.atom'
        self.__feedLink = f'{config.feedUrl}/feed/{feedname}'
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
                    print(f'entry file {self.__entryFile} is not a list',
                          file=stderr)
                    exit(1)
        except IOError:
            try:
                with open(self.__entryFile, 'w+') as f:
                    f.write('[]')
                    self.__entries = deque([], maxlen=config.maxEntries)
            except IOError as e:
                print(f'{e}: make sure file is writable',
                      file=stderr)
                exit(1)

        # refresh feed file just in case
        self.__writeAtomFeed()

    def addEntry(self,
                 title,
                 content):
        title = clean(title)
        content = clean(content)
        date = datetime.utcnow().isoformat(timespec='seconds')+'Z'
        uid = str(uuid4())
        self.__entries.appendleft({
            'id': uid,
            'title': title,
            'content': content,
            'date': date,
        })
        self.__writeEntries()
        self.__writeAtomFeed()

    def getItemById(self, item_id):
        for entry in self.__entries:
            if entry['id'] == item_id:
                return f'''\
Title: {entry['title']}
Date:  {entry['date']}

{entry['content']}
'''
        return None
