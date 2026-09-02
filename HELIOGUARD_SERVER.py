#!/usr/bin/env python3
"""HELIOGUARD local static server + resilient NASA DONKI gateway.
Standard-library only. Binds to 127.0.0.1 and does not expose the service to the LAN.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, sys, threading, time, urllib.error, urllib.parse, urllib.request, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT=pathlib.Path(__file__).resolve().parent
CACHE=ROOT/'.helioguard_cache'; CACHE.mkdir(exist_ok=True)
HOST='127.0.0.1'; PORT=int(os.environ.get('HELIOGUARD_PORT','8080'))
ALLOWED={'FLR','CME','GST','SEP','IPS','HSS','MPC','RBE','WSAEnlilSimulations','notifications'}
TTL=15*60

def get_json(url:str, timeout:int=35):
    req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'HELIOGUARD-ARABIA/1.0'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        raw=r.read(); data=json.loads(raw.decode('utf-8'))
        if not isinstance(data,list): raise ValueError('DONKI response is not a JSON array')
        return data, r.status, dict(r.headers)

def cache_file(kind,start,end):
    token=hashlib.sha256(f'{kind}|{start}|{end}'.encode()).hexdigest()[:24]
    return CACHE/f'donki_{token}.json'

def read_cache(kind,start,end):
    f=cache_file(kind,start,end)
    if not f.exists(): return None
    try:
        x=json.loads(f.read_text(encoding='utf-8'))
        if time.time()-x['saved_epoch']<=TTL and isinstance(x['data'],list): return x
    except Exception: pass
    return None

def write_cache(kind,start,end,data,provider):
    cache_file(kind,start,end).write_text(json.dumps({'saved_epoch':time.time(),'savedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'provider':provider,'data':data},ensure_ascii=False),encoding='utf-8')

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def log_message(self,fmt,*args): print('[HELIOGUARD]',fmt%args)
    def send_json(self,status,obj,provider=''):
        body=json.dumps(obj,ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(body)))
        if provider:self.send_header('X-HELIOGUARD-Provider',provider)
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        u=urllib.parse.urlsplit(self.path)
        if u.path!='/api/donki': return super().do_GET()
        q=urllib.parse.parse_qs(u.query); kind=q.get('type',[''])[0]; start=q.get('startDate',[''])[0]; end=q.get('endDate',[''])[0]; key=q.get('api_key',['DEMO_KEY'])[0] or 'DEMO_KEY'
        if kind not in ALLOWED or not start or not end: return self.send_json(400,{'error':'type/startDate/endDate are required'})
        cached=read_cache(kind,start,end)
        if cached: return self.send_json(200,cached['data'],cached.get('provider','LOCAL_CACHE'))
        open_url=f'https://api.nasa.gov/DONKI/{urllib.parse.quote(kind)}?'+urllib.parse.urlencode({'startDate':start,'endDate':end,'api_key':key})
        ccmc_url=f'https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/{urllib.parse.quote(kind)}?'+urllib.parse.urlencode({'startDate':start,'endDate':end})
        providers=[]
        if key!='DEMO_KEY': providers.append(('NASA_OPEN_API',open_url))
        providers.append(('NASA_CCMC_DIRECT',ccmc_url))
        if key=='DEMO_KEY': providers.append(('NASA_OPEN_API_DEMO',open_url))
        errors=[]
        for name,url in providers:
            try:
                data,status,headers=get_json(url); write_cache(kind,start,end,data,name); return self.send_json(200,data,name)
            except urllib.error.HTTPError as e:
                try: detail=e.read().decode('utf-8','replace')[:300]
                except Exception: detail=str(e)
                errors.append(f'{name}: HTTP {e.code} {detail}')
            except Exception as e: errors.append(f'{name}: {e}')
        return self.send_json(502,{'error':'All DONKI upstream providers failed','details':errors})

def main():
    os.chdir(ROOT)
    server=ThreadingHTTPServer((HOST,PORT),Handler)
    url=f'http://{HOST}:{PORT}/index.html'
    print('\nHELIOGUARD ARABIA v1.0.1')
    print('Local DONKI gateway:',url)
    print('Press Ctrl+C to stop.\n')
    threading.Timer(1.0,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__=='__main__': main()
