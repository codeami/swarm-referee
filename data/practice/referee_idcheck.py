import os, json, time, urllib.request, urllib.error
from dotenv import load_dotenv
load_dotenv("/Users/artsys/.treehouse/apart-research_Sprint1_Oct22_2026_Eval_Agents_Collusion-8f1c7e/1/apart-research_Sprint1_Oct22_2026_Eval_Agents_Collusion/.env")
k = os.environ.get("DEEPSEEK_API_KEY", "")
print("key non-empty:", bool(k))
for name, extra in [("thinking-disabled", {"thinking": {"type": "disabled"}, "temperature": 0}), ("thinking-default", {})]:
    body = {"model": "deepseek-v4-pro", "max_tokens": 8000, "messages": [{"role": "user", "content": 'Reply with only this JSON: {"ok": true}'}], **extra}
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=90)); c = r["choices"][0]
        print(name, "ok", r.get("model"), c.get("finish_reason"), repr(c["message"].get("content"))[:60], r.get("usage"), round(time.time() - t, 1), "s")
    except urllib.error.HTTPError as e:
        print(name, "HTTP", e.code, e.read().decode()[:200].replace(k, "***"))
