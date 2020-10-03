# SAS TMS

Simple service to serve SAS.Planet sqlite cache tiles as TMS server.

Usage:

  sastms [-p PORT] -d [SAS_DIR]

Default port: 5000. Default dir: current directory.

Tile URL format: http://{host}:{port}/{nameInCache}/{z}/{x}/{y}.{fileExt}

Example URL: http://localhost:5000/osmmapMapnik/0/0/0.png
