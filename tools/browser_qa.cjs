const puppeteer = require('/root/.hermes/profiles/marcus-ai-agency/cache/scratch/pcw-qa/node_modules/puppeteer-core');
const fs=require('fs'),path=require('path');
const root='/root/pcw-services-concept',audit=path.join(root,'audit');
const routes=JSON.parse(fs.readFileSync(path.join(audit,'source-inventory.json'))).map(x=>x.file);
(async()=>{
 const browser=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const results=[];
 await Promise.all([1440,768,390].map(async width=>{
  const page=await browser.newPage();await page.setViewport({width,height:width===390?844:1000,deviceScaleFactor:1,isMobile:width===390});const client=await page.createCDPSession();
  await client.send('Emulation.setDeviceMetricsOverride',{width,height:width===390?844:1000,deviceScaleFactor:1,mobile:width===390});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setRequestInterception(true);page.on('request',req=>req.url().includes('/webhook/')?req.abort():req.continue());
  for(const route of routes){
   await page.goto('http://127.0.0.1:8765/'+route,{waitUntil:'networkidle2',timeout:45000});
   await page.evaluate(()=>document.fonts.ready);
   const data=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelector('h1')?.innerText,
    images:[...document.images].filter(x=>!x.complete||!x.naturalWidth).map(x=>x.getAttribute('src')),
    grids:[...document.querySelectorAll('.dir-grid,.service-layout-grid,.contact-layout,.division-grid')].map(x=>({selector:x.className,tracks:getComputedStyle(x).gridTemplateColumns})),
    badVars:[...document.styleSheets].flatMap(s=>{try{return [...s.cssRules].filter(r=>r.selectorText===':root').flatMap(r=>[...r.style].filter(n=>n.startsWith('--')&&!getComputedStyle(document.documentElement).getPropertyValue(n).trim()))}catch{return []}})
   }));
   data.route=route;data.requestedWidth=width;data.consoleErrors=[...errors];errors.length=0;results.push(data);
   fs.writeFileSync(path.join(audit,'responsive-routes.json'),JSON.stringify(results,null,2));
   const shotRoutes={'index.html':'home','about/index.html':'about','contact/index.html':'contact','project-services/index.html':'project-services','services/decking/index.html':'decking','testimonials/index.html':'testimonials'};
   if(shotRoutes[route]&&width!==768){await page.screenshot({path:path.join(audit,'screenshots',`${width}-${shotRoutes[route]}.jpg`),type:'jpeg',quality:78,fullPage:route==='index.html'});}
  }
  await page.close();
 }));
 // Dedicated home interactions, never a real submission.
 const page=await browser.newPage();const c=await page.createCDPSession();await c.send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle2'});
 const tests=[];
 await page.click('.service-explorer summary');await page.type('#proj-grid-search','Decking');
 tests.push(await page.evaluate(()=>({test:'service search',visible:[...document.querySelectorAll('#proj-grid .dir-card')].filter(x=>!x.hidden).map(x=>x.querySelector('h3').textContent)})));
 await page.click('#proj-grid .dir-card:not([hidden]) .dir-btn-quote');
 tests.push(await page.evaluate(()=>({test:'dialog opens',hash:location.hash,display:getComputedStyle(document.querySelector(location.hash)).display,focus:document.activeElement.id})));
 await page.keyboard.press('Tab');await page.keyboard.down('Shift');await page.keyboard.press('Tab');await page.keyboard.up('Shift');
 tests.push(await page.evaluate(()=>({test:'focus remains in dialog',inside:!!document.activeElement.closest('.modal')})));
 await page.keyboard.press('Escape');tests.push(await page.evaluate(()=>({test:'Escape closes',open:[...document.querySelectorAll('.modal')].filter(x=>getComputedStyle(x).display!=='none').length})));
 await page.click('.mobile-nav-toggle');await page.click('.mobile-accordion-toggle');
 tests.push(await page.evaluate(()=>({test:'mobile menu and accordion',drawer:document.querySelector('#mobile-drawer').getAttribute('aria-hidden'),accordion:document.querySelector('.mobile-accordion-toggle').getAttribute('aria-expanded')})));
 await page.click('.mobile-close-btn');
 await page.goto('http://127.0.0.1:8765/contact/?service=Decking',{waitUntil:'networkidle2'});
 tests.push(await page.evaluate(()=>({test:'form service preselect',value:document.querySelector('#contact-service').value,fields:[...document.querySelectorAll('#pcw-contact-form input,#pcw-contact-form select,#pcw-contact-form textarea')].map(x=>x.id),handler:document.querySelector('#pcw-contact-form').getAttribute('onsubmit')})));
 fs.writeFileSync(path.join(audit,'interaction-tests.json'),JSON.stringify(tests,null,2));
 await browser.close();
 const failures=results.filter(x=>x.scrollWidth>x.width||x.images.length||x.consoleErrors.length||x.badVars.length);
 console.log(JSON.stringify({renderChecks:results.length,uniqueRoutes:new Set(results.map(x=>x.route)).size,widths:[1440,768,390],failures,interactions:tests},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
