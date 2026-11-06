"""Offline preview server. Python3 tools/serve.py [--bind 0.0.0.0] [--port 9264]."""
import argparse,http.server,functools
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--bind',default='127.0.0.1');p.add_argument('--port',type=int,default=9264);args=p.parse_args()
root=Path(__file__).resolve().parent.parent
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
with http.server.ThreadingHTTPServer((args.bind,args.port),handler)as server:
 print(f'Ravedio264: http://{args.bind}:{args.port}/ (Ctrl+C to stop)',flush=True);server.serve_forever()
