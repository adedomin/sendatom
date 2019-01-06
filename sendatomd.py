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

from config import Config
from entries import Entries
from bottle import get, post, error, request, response, static_file, run


config = Config()
entries = {'root': Entries('root', config)}


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


@error(404)
def error404(error):
    response.content_type = 'application/json'
    return '{"status": "error", "msg": "No such route"}'


@get('/add')
@get('/<secret>/add')
@get('/<feed>/<secret>/add')
def addToRootFeedGet(feed='root', secret=''):
    if secret != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    return addToFeed(
        getFeed(feed),
        request.query.get('title', 'No title'),
        request.query.get('content', 'No content'),
    )


@post('/add')
@post('/<secret>/add')
@post('/<feed>/<secret>/add')
def addToRootFeedPost(feed='root', secret=''):
    if secret != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    return addToFeed(
        getFeed(feed),
        request.forms.get('title', 'No title'),
        request.forms.get('content', 'No content'),
    )


@get('/')
@get('/<secret>')
@get('/<feed>/<secret>')
def getRootFeed(feed='root', secret=''):
    if secret != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    return static_file(f'{feed}.atom', root=config.feeds)


@get('/get/content/<contentId>')
@get('/<secret>/get/<contentId>')
@get('/<feed>/<secret>/get/<contentId>')
def getFeedContent(feed='root', secret='', contentId='no-content'):
    if secret != config.secret:
        response.status = 403
        return {'status': 'error', 'msg': 'wrong secret url'}

    content = getFeed(feed).getContentById(contentId)
    if content is None:
        response.status = 404
        return {'status': 'error',
                'msg': 'feed does not contain requested content'}

    response.content_type = 'text/plain;charset=utf-8'
    return content


if __name__ == '__main__':
    run(host=config.interface, port=config.port, debug=True)
