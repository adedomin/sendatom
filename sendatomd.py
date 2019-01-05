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
from flask import Flask, request


config = Config()
entries = { 'root': Entries('root', config) }
app = Flask(
    __name__,
    static_url_path='',
    static_folder=config.feeds,
)


@app.route('/add', defaults={'feed': 'root', 'secret': ''}, methods=['GET', 'POST'])
@app.route('/<secret>/add', defaults={'feed': 'root'}, methods=['GET', 'POST'])
@app.route('/<feed>/<secret>/add', methods=['GET', 'POST'])
def addToRootFeed(feed, secret):
    if secret != config.secret:
        return app.response_class(
            response='{ "status": "error", "msg": "wrong secret url" }',
            status=403,
            mimetype='application/json',
        )

    entry = entries.get(feed)
    if entry == None:
        entries[feed] = Entries(feed, config)
        entry = entries.get(feed)

    if request.method == 'GET':
        entry.addEntry(
            title=request.args.get('title', 'No title'),
            content=request.args.get('content', 'No Content'),
        )
        return app.response_class(
            response='{ "status": "ok", "msg": "success" }',
            status=200,
            mimetype='application/json',
        )
    else:
        entry.addEntry(
            title=request.form.get('title', 'No title'),
            content=request.form.get('content', 'No Content'),
        )
        return app.response_class(
            response='{ "status": "ok", "msg": "success" }',
            status=200,
            mimetype='application/json',
        )


@app.route('/', defaults={'feed': 'root', 'secret': ''}, methods=['GET'])
@app.route('/<secret>', defaults={'feed': 'root'}, methods=['GET'])
@app.route('/<feed>/<secret>', methods=['GET'])
def getRootFeed(feed, secret):
    if secret != config.secret:
        return app.response_class(
            response='{ "status": "error", "msg": "wrong secret url" }',
            status=403,
            mimetype='application/json',
        )

    return app.send_static_file(f'{feed}.atom')


if __name__ == '__main__':
    app.run(host=config.interface, port=config.port)
