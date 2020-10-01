#!/usr/bin/env python3
import sys
import os
import re
import sqlite3
import mimetypes
from flask import Flask, request, Response, abort

import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('-s', dest='port', metavar='PORT', type=int, help='port')
argparser.add_argument('-d', dest='sas_root', metavar='SAS_DIR', type=str, help='SAS directory', default='.')
args = argparser.parse_args()

cachedir = os.path.join(args.sas_root, 'cache_sqlite')
if not os.path.isdir(cachedir):
  print ("cache_sqlite directory not found")
  sys.exit(1)

sdir = lambda d,z,x,y: os.path.join(d,"z%d"%(z+1),str(x>>10),str(y>>10))
sname = lambda d,z,x,y: os.path.join(sdir(d,z,x,y),"%d.%d.sqlitedb" % (x>>8,y>>8))

def get_tile(d, z, x, y):
  dbname = sname(d, z, x, y)
  if not os.path.isfile(dbname):
    return None
  db = sqlite3.connect(dbname)
  cc = db.cursor()
  cc.execute("SELECT b FROM t WHERE x=? AND y=?", (x,y))
  m = cc.fetchall()
  db.close()
  if len(m) < 1:
    return None
  if len(m) > 1:
    raise BaseException("multi-version?")
  return m[0]

mime = mimetypes.MimeTypes()
app = Flask(__name__)

@app.route('/', methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def serve(path):
  try:
    agent = request.headers['user-agent']
  except KeyError:
    return abort(403)
  if re.search('JOSM', agent):
    return abort(403)
  m = re.match('([^/]+)/(\d+)/(\d+)/(\d+)\.(\w+)', path)
  if not m:
    return abort(404)
  name = m.group(1)
  z = int(m.group(2))
  x = int(m.group(3))
  y = int(m.group(4))
  ext = m.group(5)
  d = os.path.join(cachedir, name)
  b = get_tile(d, z, x, y)
  if not b:
    return abort(404)
  mimetype = mime.guess_type("test.%s" % ext)[0]
  return Response(b, mimetype=mimetype)

if __name__ == '__main__':
  app.run(port=args.port)
