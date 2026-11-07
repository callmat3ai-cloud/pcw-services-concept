const puppeteer=require('/root/.hermes/profiles/marcus-ai-agency/cache/scratch/pcw-qa/node_modules/puppeteer-core');
const fs=require('fs'),vm=require('vm');const root='/root/pcw-services-concept',a=root+'/audit';
(async()=>{
 const browser=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage(),cdp=await page.createCDPSession();
 let results=JSON.parse(fs.readFileSync(a+'/responsive-routes.json'));
 for(const width of [1440,768,390]){
  await page.setViewport({width,height:width===390?844:1000,deviceScaleFactor:1,isMobile:width===390});
  await cdp.send('Emulation.setDeviceMetricsOverride',{width,height:width===390?844:1000,deviceScaleFactor:1,mobile:width===390});
  await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle2'});
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(async image=>{image.loading='eager';try{await image.decode()}catch{}}))});
  const rec=results.find(x=>x.route==='index.html'&&x.requestedWidth===width);
  Object.assign(rec,await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,images:[...document.images].filter(x=>!x.complete||!x.naturalWidth).map(x=>x.getAttribute('src')),h1:document.querySelector('h1').innerText})));
  if(width!==768){
   await page.screenshot({path:a+`/screenshots/${width}-home.jpg`,type:'jpeg',quality:80});
   await page.screenshot({path:a+`/screenshots/${width}-full.jpg`,type:'jpeg',quality:74,fullPage:true});
  }
 }
 fs.writeFileSync(a+'/responsive-routes.json',JSON.stringify(results,null,2));
 const tests=[];
 await page.click('.service-explorer summary');await page.type('#proj-grid-search','Decking');
 tests.push(await page.evaluate(()=>({test:'search filters exact source cards',visible:[...document.querySelectorAll('#proj-grid .dir-card')].filter(x=>!x.hidden).map(x=>x.querySelector('h3').textContent)})));
 await page.click('#proj-grid .dir-card:not([hidden]) .dir-btn-quote');
 tests.push(await page.evaluate(()=>({test:'modal visible and focused',hash:location.hash,display:getComputedStyle(document.querySelector(location.hash)).display,focus:document.activeElement.id})));
 await page.keyboard.press('Tab');await page.keyboard.down('Shift');await page.keyboard.press('Tab');await page.keyboard.up('Shift');
 tests.push(await page.evaluate(()=>({test:'focus trapped',inside:!!document.activeElement.closest('.modal')})));
 await page.keyboard.press('Escape');
 tests.push(await page.evaluate(()=>({test:'Escape closes',open:[...document.querySelectorAll('.modal')].filter(x=>getComputedStyle(x).display!=='none').length})));
 await page.click('.mobile-nav-toggle');await page.click('.mobile-accordion-toggle');
 tests.push(await page.evaluate(()=>({test:'mobile drawer and accordion',drawer:document.querySelector('#mobile-drawer').getAttribute('aria-hidden'),accordion:document.querySelector('.mobile-accordion-toggle').getAttribute('aria-expanded')})));
 await page.click('.mobile-close-btn');
 await page.goto('http://127.0.0.1:8765/contact/?service=Decking',{waitUntil:'networkidle2'});
 tests.push(await page.evaluate(()=>({test:'source contact form and service preselect',service:document.getElementById('contact-service').value,fields:[...document.querySelectorAll('#pcw-contact-form input,#pcw-contact-form select,#pcw-contact-form textarea')].map(x=>x.id),handler:document.querySelector('#pcw-contact-form').getAttribute('onsubmit')})));
 // Execute the exact original handler in a stubbed DOM with mocked fetch. Never network.
 const fields={'contact-name':'PROPERTY_TEST','contact-email':'not-sent@example.invalid','contact-phone':'TEST','contact-service':'Decking','contact-message':'NOT SENT'};let captured;
 const button={innerHTML:'Submit',disabled:false,setAttribute(){},removeAttribute(){}};
 const form={querySelector(){return button},reset(){}};
 const context={document:{addEventListener(){},getElementById(id){return id==='pcw-contact-form'?form:fields[id]!==undefined?{value:fields[id]}:null}},window:{location:{href:'http://localhost/mock-only'},alert(){}},fetch:async(url,options)=>{captured={url,...options};return {ok:true}},console,setTimeout};
 vm.createContext(context);vm.runInContext(fs.readFileSync(root+'/assets/js/main.js','utf8'),context);await context.handleFormSubmit({preventDefault(){}});
 tests.push({test:'original handler mocked execution; zero network',endpoint:captured.url,method:captured.method,payloadKeys:Object.keys(JSON.parse(captured.body)),realSubmission:false});
 fs.writeFileSync(a+'/interaction-tests.json',JSON.stringify(tests,null,2));
 await browser.close();
 const failures=results.filter(x=>x.scrollWidth>x.width||x.images.length||x.consoleErrors.length||x.badVars.length);
 const report={renderChecks:results.length,routes:new Set(results.map(x=>x.route)).size,widths:[1440,768,390],failures,tests};
 fs.writeFileSync(a+'/browser-qa-output.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
