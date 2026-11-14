#!/usr/bin/env python3
# Contrôle a.absent : GitHub marque class="internal absent" les [[wikilinks]] vers pages inexistantes (1 requête/s)
import json,os,re,time,urllib.request,urllib.parse
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Firefox/130.0"}
pages=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pages_wiki.json')))
res={}
for p in pages:
    q=urllib.parse.quote(p)
    for essai in range(3):
        try:
            h=urllib.request.urlopen(urllib.request.Request("https://github.com/hprzeta/Riemann_Lab/wiki/"+q,headers=UA),timeout=25).read().decode('utf-8','replace'); break
        except Exception as e:
            h=None; time.sleep(5)
    if h is None: res[p]='ERREUR'; continue
    ab=re.findall(r'<a[^>]*class="internal absent"[^>]*>(.*?)</a>',h,re.S)
    if ab: res[p]=[re.sub(r'<[^>]+>','',a)[:40] for a in ab]
    time.sleep(1.05)
json.dump(res,open('absent_scan.json','w'),ensure_ascii=False,indent=1)
print('pages avec liens absents :',len(res)); print(json.dumps(res,ensure_ascii=False))
