import { chromium } from 'playwright';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = dirname(fileURLToPath(import.meta.url));
const escape = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const browser = await chromium.launch(process.env.CHROME_EXECUTABLE ? {executablePath:process.env.CHROME_EXECUTABLE} : {});
try {
  const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:2});
  if(process.argv[2] === '--url') {
    await page.goto(process.argv[3],{waitUntil:'networkidle'});
    await page.waitForTimeout(6000);
    await page.screenshot({path:process.argv[4],clip:{x:0,y:0,width:1440,height:650}});
  } else {
    const names = ['postgres','redis','kafka','rabbitmq','prometheus','grafana','nginx','otel','buildkit','kubernetes'];
    await mkdir(resolve(root,'assets'),{recursive:true});
    for(const name of names) {
      const evidence=JSON.parse(await readFile(resolve(root,'evidence',`${name}.json`),'utf8'));
      if(!evidence.passed) throw Error(`Cannot illustrate an unpassed lab: ${name}`);
      const assertions=evidence.events.filter(e=>e.assertion).map(e=>{
        if(e.assertion.startsWith('EndpointSlice') && e.actual?.items) return {...e,actual:e.actual.items.flatMap(i=>i.endpoints.map(ep=>ep.conditions))};
        if(e.assertion==='application lifecycle logs') return {...e,actual:e.actual.split('\n').filter(line=>line.startsWith('{')).join('\n')};
        return e;
      });
      const html=`<!doctype html><html lang="en"><meta charset="utf-8"><title>${name} — recorded experiment</title><style>
      *{box-sizing:border-box} body{margin:0;background:#F5F6F2;color:#17211D;font:22px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:64px} main{max-width:1240px;margin:auto} small{font:18px monospace;color:#176B55} h1{font-size:42px;line-height:1.15;margin:18px 0} p{color:#5D6964;font-size:20px} article{background:#fff;border:1px solid #D8DFDA;border-left:5px solid #176B55;margin:24px 0;padding:24px}h2{font-size:24px;margin:0 0 12px}pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;font:18px/1.5 'SFMono-Regular',Consolas,monospace}</style><main><small>EMMINEX TECHDOCS · EXECUTION EVIDENCE</small><h1>${escape(name)}: recorded assertions</h1><p>Captured from the runnable lab’s test report. This is an evidence view, not the tool’s own interface.<br>Run started: ${escape(evidence.started_at)}</p>${assertions.map(e=>`<article><h2>${escape(e.assertion)}</h2><pre>${escape(typeof e.actual==='string'?e.actual:JSON.stringify(e.actual,null,2))}</pre></article>`).join('')}</main></html>`;
      await writeFile(resolve(root,'assets',`${name}-evidence.html`),html);
      await page.setContent(html,{waitUntil:'load'});
      const height = await page.locator('main').evaluate(el => Math.ceil(el.getBoundingClientRect().bottom + 64));
      await page.setViewportSize({width:1440,height});
      await page.screenshot({path:resolve(root,'assets',`${name}-evidence.png`),fullPage:true});
      console.log(`Captured ${name} execution evidence at 2x resolution`);
    }
  }
} finally { await browser.close(); }
