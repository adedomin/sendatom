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

from os import listdir
from os.path import splitext
from json import dumps
from config import Config
from entries import Entries
from bottle import get, post, error, request, response, static_file, run


config = Config()
entries = {}


def getFeed(feedName):
    feedInstance = entries.get(feedName)
    if feedInstance is None:
        entries[feedName] = Entries(feedName, config)
        return entries.get(feedName)
    return feedInstance


def addToFeed(feed, title, content):
    try:
        feed.addEntry(title=title, content=content)
    except Exception as e:
        return {'status': 'error', 'msg': f'Unknown error: {e}'}
    return {'status': 'ok', 'msg': 'success'}


def getSecretParam():
    return request.query.get('secret',
                             request.forms.get('secret',
                                               ''))


@error(404)
def error404(error):
    response.content_type = 'application/json'
    return '{"status": "error", "msg": "No such route"}'


@get('/feed')
@get('/feed/<feed>')
def getRootFeed(feed='root'):
    if getSecretParam() != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    # generate the feed's content if not exist
    getFeed(feed)
    return static_file(f'{feed}.atom', root=config.feeds)


@get('/feed/get-item/<item_id>')
@get('/feed/<feed>/get-item/<item_id>')
def getFeedContent(feed='root', item_id='no-content'):
    if getSecretParam() != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    content = getFeed(feed).getItemById(item_id)
    if content is None:
        response.status = 404
        return {'status': 'error',
                'msg': 'feed does not contain requested content'}

    response.content_type = 'text/plain;charset=utf-8'
    return content


@get('/feed/list-feeds')
def listFeeds():
    feeds = []
    for feed in listdir(config.feeds):
        name, ext = splitext(feed)
        if ext == '.atom':
            feeds.append(name)

    response.content_type = 'application/json'
    return dumps(feeds)


@get('/feed/add-item')
@get('/feed/<feed>/add-item')
@post('/feed/add-item')
@post('/feed/<feed>/add-item')
def addToRootFeedPost(feed='root'):
    if getSecretParam() != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    return addToFeed(getFeed(feed),
                     request.query.get('title',
                                       request.forms.get('title',
                                                         'No title')),
                     request.query.get('content',
                                       request.forms.get('content',
                                                         'No content')))


if __name__ == '__main__':
    run(host=config.interface, port=config.port)
