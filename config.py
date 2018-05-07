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

from os import environ
from sys import exit
from random import choices
import re
import string


commentRe = re.compile('^\s*#')
blankRe = re.compile('^\s*$')


class Config:
    '''Configuration Singleton'''

    __configFiles = [
        environ['HOME']+'/.config/sendxml.conf',
        '/etc/sendxml.conf',
        '/var/lib/sendxml/sendxml.conf',
        # test only
        './test/sendxml.conf',
    ]
    __secretFile = '/var/lib/sendxml/secret'
    secret = ''
    entries = '/var/lib/sendxml/entries'
    maxEntries = 50
    feeds = '/var/lib/sendxml/feeds'
    feedTitle = 'sendxml feed'
    feedUrl = 'http://localhost'
    interface = '::1'
    port = 23129

    def __init__(self):
        for file in self.__configFiles:
            try:
                with open(file, "r") as f:
                    for line in f:
                        if not commentRe.search(line) \
                           and not blankRe.search(line):
                            conf, value = line.split('=', maxsplit=1)
                            conf = conf.strip()
                            value = value.strip()
                            if conf == 'secret':
                                self.__secretFile = value
                            elif conf == 'entries':
                                self.entries = value
                            elif conf == 'maxEntries':
                                self.maxEntries = int(value)
                            elif conf == 'feeds':
                                self.feeds = value
                            elif conf == 'feedTitle':
                                self.feedTitle = value
                            elif conf == 'feedUrl':
                                self.feedUrl = value
                            elif conf == 'interface':
                                self.interface = value
                            elif conf == 'port':
                                self.port = int(value)
                            else:
                                print('Error: Unknown config key: %s' % conf)
                                exit(1)
                    break
            except IOError:
                continue

        try:
            with open(self.__secretFile, 'r') as f:
                self.secret = f.readline().strip()
            if len(self.secret) == 0:
                print('Warning: secret is disabled')
                print('Warning: to enable secret, ' +
                      'populate %s with a random string' % self.__secretFile)
        except IOError:
            self.secret = ''.join(
                choices(
                    string.ascii_letters + string.digits, k=16
                )
            )
            try:
                with open(self.__secretFile, 'w+') as f:
                    f.write(self.secret)
            except IOError as e:
                print('%s: make sure file is writable or create it' % e)
                exit(1)


if __name__ == "__main__":
    config = Config()
    print(config.secret)
    print(config.entries)
    print(config.maxEntries)
    print(config.feeds)
    print(config.feedTitle)
    print(config.feedUrl)
