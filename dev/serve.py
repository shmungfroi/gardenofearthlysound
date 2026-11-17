import http.server, sys, functools
class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.webp':'image/webp'}
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('',int(sys.argv[1])), functools.partial(H, directory=sys.argv[2])).serve_forever()
