import json, pathlib, datetime, urllib.request, xml.etree.ElementTree as ET
p=pathlib.Path(__file__).resolve().parents[1]/'data.json'
d=json.loads(p.read_text(encoding='utf-8'))
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'SpaceScan/1.0'})
 with urllib.request.urlopen(req,timeout=20) as r:return r.read()
news=[]
try:
 root=ET.fromstring(fetch('https://www.nasa.gov/feed/'))
 for x in root.findall('.//item'):
  title=x.findtext('title') or ''
  if any(w in title.lower() for w in ('artemis','orion','moon','sls','lunar')):
   news.append(dict(title=title,url=x.findtext('link') or '',date=x.findtext('pubDate') or '',source='NASA'))
except Exception as e:print('NASA feed:',e)
try:
 feed=json.loads(fetch('https://api.spaceflightnewsapi.net/v4/articles/?limit=40'))
 for x in feed.get('results',[]):
  if any(w in (x.get('title','')+' '+x.get('summary','')).lower() for w in ('spacex','starship','artemis','orion')):
   news.append(dict(title=x.get('title',''),url=x.get('url',''),date=x.get('published_at',''),source=x.get('news_site','Spaceflight News')))
except Exception as e:print('Spaceflight News:',e)
if news:
 unique={x['url']:x for x in news if x['url']}
 d['news']=list(unique.values())[:12]
d['updated']=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
