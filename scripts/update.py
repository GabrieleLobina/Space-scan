import json, pathlib, datetime, urllib.request, xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parents[1]/"data.json"
data=json.loads(P.read_text(encoding="utf-8"))
old_news={n.get("url"):n for n in data.get("news",[])}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"SpaceScan/3.0 (+https://github.com/GabrieleLobina/Space-scan)"})
 with urllib.request.urlopen(req,timeout=25) as response:return response.read()
news=[]
try:
 root=ET.fromstring(fetch("https://www.nasa.gov/feed/"))
 for item in root.findall(".//item"):
  title=item.findtext("title") or ""
  if any(k in title.lower() for k in ("artemis","orion","moon","lunar","space launch system","sls")):
   news.append(dict(title=title,url=item.findtext("link") or "",date=item.findtext("pubDate") or "",source="NASA"))
except Exception as e:print("NASA feed unavailable:",e)
try:
 payload=json.loads(fetch("https://api.spaceflightnewsapi.net/v4/articles/?limit=100"))
 for item in payload.get("results",[]):
  title=item.get("title","")
  summary=item.get("summary","")
  if any(k in (title+" "+summary).lower() for k in ("spacex","starship","super heavy","artemis","orion","falcon 9","falcon heavy")):
   news.append(dict(title=title,url=item.get("url",""),date=item.get("published_at",""),source=item.get("news_site","Spaceflight News")))
except Exception as e:print("Spaceflight News unavailable:",e)
if news:
 unique={}
 for item in news:
  if item["url"]:unique[item["url"]]=item
 # Prefer ISO dated items; preserve NASA entries even if RSS dates are RFC822
 from email.utils import parsedate_to_datetime
 def timestamp(item):
  try:
   value=item.get("date","")
   if "T" in value:return datetime.datetime.fromisoformat(value.replace("Z","+00:00")).timestamp()
   return parsedate_to_datetime(value).timestamp()
  except Exception:return 0
 ordered=sorted(unique.values(),key=timestamp,reverse=True)
 new_urls=[x["url"] for x in ordered if x["url"] not in old_news]
 if new_urls:
  today=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
  data.setdefault("changes",[]).insert(0,dict(date=today,text=f"{len(new_urls)} nuove notizie rilevate nei feed monitorati"))
  data["changes"]=data["changes"][:30]
 data["news"]=ordered[:15]
else:
 print("No feeds available: preserving previous news")
data["updated"]=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
