const puppeteer=require('/root/.hermes/profiles/marcus-ai-agency/cache/scratch/pcw-qa/node_modules/puppeteer-core'),fs=require('fs');
const out='/root/pcw-services-concept/audit/screenshots';
(async()=>{
 const browser=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});const page=await browser.newPage();
 await page.emulateMediaFeatures([{name:'prefers-reduced-motion',value:'reduce'}]);
 for(const width of [1440,390]){
  await page.setViewport({width,height:width===390?844:1000,isMobile:width===390,deviceScaleFactor:1});const c=await page.createCDPSession();await c.send('Emulation.setDeviceMetricsOverride',{width,height:width===390?844:1000,deviceScaleFactor:1,mobile:width===390});
  for(const [route,name] of [['','home'],['services/decking/','decking'],['contact/','contact'],['about/','about'],['testimonials/','testimonials'],['project-services/','project-services']]){
   await page.goto('http://127.0.0.1:8765/'+route,{waitUntil:'networkidle2'});await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(async x=>{x.loading='eager';try{await x.decode()}catch{}}))});
   const shot=await c.send('Page.captureScreenshot',{format:'jpeg',quality:80,captureBeyondViewport:false});fs.writeFileSync(out+`/${width}-${name}.jpg`,Buffer.from(shot.data,'base64'));
   if(!route){
    await page.screenshot({path:out+`/${width}-full.jpg`,fullPage:true,type:'jpeg',quality:74});
    if(width===1440)for(const [selector,label] of [['.division-project','services'],['.division-property','property'],['.proof-section','proof'],['.testimonials-section','reviews'],['.knowledge-hub-preview-section','resources']]){
     await page.evaluate(sel=>document.querySelector(sel).scrollIntoView({behavior:'instant',block:'start'}),selector);
     const shot=await c.send('Page.captureScreenshot',{format:'jpeg',quality:78,captureBeyondViewport:false});fs.writeFileSync(out+`/desktop-${label}.jpg`,Buffer.from(shot.data,'base64'));
    }
   }
  }
 }
 await browser.close();console.log('Saved correctly dimensioned full-frame screenshots for 6 routes at 1440 and 390; five desktop section captures; two full-page captures.');
})().catch(e=>{console.error(e);process.exit(1)});
