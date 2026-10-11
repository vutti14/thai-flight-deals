import json,base64,sys,subprocess,time,urllib.request,websocket,os
url,out,w,h=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]); full=len(sys.argv)>5 and sys.argv[5]=="full"
pre=sys.argv[6] if len(sys.argv)>6 else ""
port=9333
p=subprocess.Popen(["google-chrome","--headless=new","--no-sandbox","--disable-gpu",f"--remote-debugging-port={port}","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
  for _ in range(50):
    try: tabs=json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
    except Exception: time.sleep(.2)
  t=[x for x in tabs if x['type']=='page'][0]
  ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=30,suppress_origin=True)
  i=[0]; errs=[]
  def call(m,pr={}):
    i[0]+=1; ws.send(json.dumps({"id":i[0],"method":m,"params":pr}))
    while True:
      r=json.loads(ws.recv())
      if r.get("method")=="Runtime.exceptionThrown": errs.append(r["params"]["exceptionDetails"].get("exception",{}).get("description"))
      if r.get("method")=="Runtime.consoleAPICalled" and r["params"]["type"]=="error": errs.append(str(r["params"]["args"]))
      if r.get("id")==i[0]: return r.get("result")
  call("Runtime.enable"); call("Page.enable")
  call("Emulation.setDeviceMetricsOverride",{"width":w,"height":h,"deviceScaleFactor":2 if w<500 else 1,"mobile":w<500})
  call("Page.navigate",{"url":url}); time.sleep(3.5)
  if pre: call("Runtime.evaluate",{"expression":pre}); time.sleep(1.5)
  r=call("Runtime.evaluate",{"expression":"JSON.stringify({sw:document.documentElement.scrollWidth,iw:innerWidth,h:document.documentElement.scrollHeight,wide:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest('.chips,.seg,.tblw,.tabs')).slice(0,8).map(e=>e.tagName+'.'+e.className)})","returnByValue":True})
  info=json.loads(r["result"]["value"]); print(info, "errors:",errs)
  prm={"format":"png"}
  if full:
    prm["captureBeyondViewport"]=True; prm["clip"]={"x":0,"y":0,"width":w,"height":min(info["h"],12000),"scale":1}
  d=call("Page.captureScreenshot",prm); open(out,"wb").write(base64.b64decode(d["data"])); print("saved",out)
finally: p.kill()
