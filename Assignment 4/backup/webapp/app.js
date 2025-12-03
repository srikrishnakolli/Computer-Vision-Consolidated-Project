// ---------- DOM ----------
const $ = (s)=>document.querySelector(s);
const camInput = $('#camFiles'), panoInput = $('#panoFile');
const camList  = $('#camList'),  panoThumb = $('#panoThumb');
const btnSort  = $('#btnSortName'), btnReverse = $('#btnReverse'), btnClear = $('#btnClear');
const resizeEl = $('#resize'), resizeVal = $('#resizeVal'), saveVis = $('#saveVis');
const btnStitch = $('#btnStitch'), btnCompare = $('#btnCompare'), statusEl = $('#status');
const oursRow = $('#oursRow'), cmpRow = $('#cmpRow'), metricsRow = $('#metricsRow'), matchRow = $('#matchRow');

let camFiles = [];   // [{file, url}] in final order
let panoFile = null;
let lastOursImg = null; // HTMLImageElement of blended panorama

// ---------- OpenCV readiness ----------
function cvReadyOrDie(){
  if (!window.__cv_was_loaded || typeof cv === 'undefined' || !cv.imread) {
    alert('OpenCV.js not ready yet. Wait a second or hard-refresh.');
    throw new Error('OpenCV not ready');
  }
}

// ---------- UI helpers ----------
function setBusy(b){ btnStitch.disabled=b; btnCompare.disabled=b; statusEl.textContent = b ? 'Working…' : ''; }

function addPreview(parent, title, src){
  const box = document.createElement('div'); box.style.display='grid'; box.style.gap='6px';
  const t = document.createElement('div'); t.className='pill'; t.textContent = title;
  const im = document.createElement('img'); im.src = src; im.className='preview';
  box.appendChild(t); box.appendChild(im); parent.appendChild(box);
}

function renderCamList(){
  camList.innerHTML = '';
  camFiles.forEach((item, idx) => {
    const row = document.createElement('div'); row.className='item'; row.draggable=true; row.dataset.index=idx;
    const drag = document.createElement('span'); drag.className='drag'; drag.textContent='↕';
    const img = document.createElement('img'); img.src=item.url;
    const label = document.createElement('div'); label.className='pill'; label.textContent = `${String(idx).padStart(2,'0')} — ${item.file.name}`;
    row.appendChild(drag); row.appendChild(img); row.appendChild(label); camList.appendChild(row);
  });
  enableDragReorder();
}

function enableDragReorder(){
  let dragIndex = null;
  camList.querySelectorAll('.item').forEach(el => {
    el.addEventListener('dragstart', e => { dragIndex = +el.dataset.index; e.dataTransfer.effectAllowed='move'; });
    el.addEventListener('dragover', e => e.preventDefault());
    el.addEventListener('drop', e => {
      e.preventDefault();
      const targetIndex = +el.dataset.index;
      if (dragIndex === null || dragIndex === targetIndex) return;
      const [moved] = camFiles.splice(dragIndex,1);
      camFiles.splice(targetIndex,0,moved);
      renderCamList();
    });
  });
}

function addCamFile(file){ camFiles.push({file, url: URL.createObjectURL(file)}); }
function previewPano(){
  panoThumb.innerHTML = '';
  if (!panoFile) return;
  const img = document.createElement('img'); img.src = URL.createObjectURL(panoFile);
  panoThumb.appendChild(img);
}

// ---------- Image → Mat ----------
async function fileToMat(file, maxDim){
  return new Promise(resolve=>{
    const img = new Image();
    img.onload = ()=>{
      const s = Math.min(1, maxDim / Math.max(img.naturalWidth, img.naturalHeight));
      const w = Math.round(img.naturalWidth * s), h = Math.round(img.naturalHeight * s);
      const c = document.createElement('canvas'); c.width=w; c.height=h;
      c.getContext('2d').drawImage(img,0,0,w,h);
      const mat = cv.imread(c);
      resolve(mat);
    };
    img.src = URL.createObjectURL(file);
  });
}
function matToDataUrl(mat){
  const c = document.createElement('canvas'); c.width=mat.cols; c.height=mat.rows;
  cv.imshow(c, mat);
  return c.toDataURL('image/jpeg', 0.92);
}
function dataUrlToImage(url){ const img = new Image(); img.src = url; return img; }
function ensureBGR(mat){
  if (mat.type() === cv.CV_8UC3) return mat;
  let out = new cv.Mat(); cv.cvtColor(mat, out, cv.COLOR_RGBA2BGR); mat.delete(); return out;
}
function toGray(mat){ let g = new cv.Mat(); cv.cvtColor(mat, g, cv.COLOR_BGR2GRAY); return g; }

// ---------- Feature detectors (primary path) ----------
function createDetectorOrNull(){
  try{
    if (cv.ORB && cv.ORB.create)   return cv.ORB.create(4000);
    if (cv.AKAZE && cv.AKAZE.create) return cv.AKAZE.create();
    if (cv.BRISK && cv.BRISK.create) return cv.BRISK.create();
  }catch(e){}
  return null; // not available → fallback will be used
}
function detectAndDescribe(detector, img){
  const gray = toGray(img);
  const kps = new cv.KeyPointVector();
  const desc = new cv.Mat();
  detector.detectAndCompute(gray, new cv.Mat(), kps, desc, false);
  gray.delete();
  return {kps, desc};
}
function knnMatchRatio(descA, descB, ratio=0.75){
  const bf = new cv.BFMatcher(cv.NORM_HAMMING, false);
  const matches = new cv.DMatchVectorVector();
  bf.knnMatch(descA, descB, matches, 2);
  const good = new cv.DMatchVector();
  for (let i=0;i<matches.size();i++){
    const pair = matches.get(i);
    if (pair.size()>=2){
      const m=pair.get(0), n=pair.get(1);
      if (m.distance < ratio*n.distance) good.push_back(m);
    }
    pair.delete();
  }
  matches.delete(); bf.delete();
  return good;
}
function homographyFromMatches(kpsA,kpsB,good,thr=4.0){
  if (good.size()<12) return {H:null, mask:null};
  const ptsA = new cv.Mat(good.size(),1,cv.CV_32FC2);
  const ptsB = new cv.Mat(good.size(),1,cv.CV_32FC2);
  for (let i=0;i<good.size();i++){
    const m = good.get(i);
    const pa = kpsA.get(m.queryIdx).pt, pb = kpsB.get(m.trainIdx).pt;
    ptsA.floatPtr(i,0)[0]=pa.x; ptsA.floatPtr(i,0)[1]=pa.y;
    ptsB.floatPtr(i,0)[0]=pb.x; ptsB.floatPtr(i,0)[1]=pb.y;
  }
  const mask = new cv.Mat();
  const H = cv.findHomography(ptsA, ptsB, cv.RANSAC, thr, mask);
  ptsA.delete(); ptsB.delete();
  return {H, mask};
}
function drawMatchesSide(a,b,kpa,kpb,good,maxDraw=60){
  const step = Math.max(1, Math.floor(good.size()/maxDraw));
  const ah=a.rows, aw=a.cols, bh=b.rows, bw=b.cols;
  const H = Math.max(ah,bh), W = aw + bw + 10;
  const canvas = new cv.Mat.zeros(H,W,cv.CV_8UC3);
  const a3 = new cv.Mat(), b3 = new cv.Mat();
  cv.cvtColor(a,a3,cv.COLOR_BGR2RGB); cv.cvtColor(b,b3,cv.COLOR_BGR2RGB);
  a3.copyTo(canvas.roi(new cv.Rect(0,0,aw,ah)));
  b3.copyTo(canvas.roi(new cv.Rect(aw+10,0,bw,bh)));
  a3.delete(); b3.delete();
  for (let i=0;i<good.size();i+=step){
    const m=good.get(i);
    const pa=kpa.get(m.queryIdx).pt, pb=kpb.get(m.trainIdx).pt;
    cv.line(canvas, new cv.Point(pa.x,pa.y), new cv.Point(pb.x+aw+10,pb.y), new cv.Scalar(0,255,0,255), 1);
  }
  return canvas;
}

// ---------- Fallback path: GFTT + LK optical flow ----------
function lkHomography(imgA, imgB, maxCorners=2000, quality=0.01, minDist=8, thr=4.0){
  const gA = toGray(imgA), gB = toGray(imgB);
  const ptsA = new cv.Mat();
  cv.goodFeaturesToTrack(gA, ptsA, maxCorners, quality, minDist);
  const ptsB = new cv.Mat(), status = new cv.Mat(), err = new cv.Mat();
  cv.calcOpticalFlowPyrLK(gA, gB, ptsA, ptsB, status, err);

  // Filter correspondences
  const listA=[], listB=[];
  for (let i=0;i<ptsA.rows;i++){
    const ok = status.ucharPtr(i,0)[0] === 1;
    const e  = err.floatPtr(i,0)[0];
    if (ok && e < 30){
      const ax = ptsA.floatPtr(i,0)[0], ay = ptsA.floatPtr(i,0)[1];
      const bx = ptsB.floatPtr(i,0)[0], by = ptsB.floatPtr(i,0)[1];
      listA.push(ax,ay); listB.push(bx,by);
    }
  }
  let H=null, mask=null;
  if (listA.length >= 24){ // 12 points minimum; use more for robustness
    const A = cv.matFromArray(listA.length/2,1,cv.CV_32FC2,listA);
    const B = cv.matFromArray(listB.length/2,1,cv.CV_32FC2,listB);
    mask = new cv.Mat();
    H = cv.findHomography(A,B,cv.RANSAC,thr,mask);
    A.delete(); B.delete();
  }
  // Optional overlay
  let overlay=null;
  if (H && !H.empty()){
    overlay = drawFlowOverlay(imgA, imgB, listA, listB);
  }

  gA.delete(); gB.delete(); ptsA.delete(); ptsB.delete(); status.delete(); err.delete();
  return {H, mask, overlay};
}

function drawFlowOverlay(a,b,listA,listB){
  const ah=a.rows, aw=a.cols, bh=b.rows, bw=b.cols;
  const H = Math.max(ah,bh), W = aw + bw + 10;
  const canvas = new cv.Mat.zeros(H,W,cv.CV_8UC3);
  a.copyTo(canvas.roi(new cv.Rect(0,0,aw,ah)));
  b.copyTo(canvas.roi(new cv.Rect(aw+10,0,bw,bh)));
  for (let i=0;i<listA.length;i+=2){
    const ax=listA[i], ay=listA[i+1];
    const bx=listB[i], by=listB[i+1];
    cv.line(canvas, new cv.Point(ax,ay), new cv.Point(bx+aw+10,by), new cv.Scalar(0,255,0,255), 1);
  }
  return canvas;
}

// ---------- Warping + blending + crop ----------
function warpAllToPanorama(imgs, H_to_ref){
  // compute bounds
  let allPts=[];
  for (let i=0;i<imgs.length;i++){
    const img=imgs[i], H=H_to_ref[i] || cv.Mat.eye(3,3,cv.CV_64F);
    const w=img.cols, h=img.rows;
    const pts=cv.matFromArray(4,1,cv.CV_32FC2,[0,0,w,0,w,h,0,h]);
    const out=new cv.Mat();
    cv.perspectiveTransform(pts,out,H);
    for (let j=0;j<4;j++){
      const x=out.floatPtr(j,0)[0], y=out.floatPtr(j,0)[1];
      allPts.push([x,y]);
    }
    pts.delete(); out.delete();
  }
  const xs=allPts.map(p=>p[0]), ys=allPts.map(p=>p[1]);
  const minx=Math.floor(Math.min(...xs)), maxx=Math.ceil(Math.max(...xs));
  const miny=Math.floor(Math.min(...ys)), maxy=Math.ceil(Math.max(...ys));
  const shift=cv.Mat.eye(3,3,cv.CV_64F);
  shift.doublePtr(0,2)[0]=-minx; shift.doublePtr(1,2)[0]=-miny;
  const W=maxx-minx, Hh=maxy-miny;

  let acc = new cv.Mat.zeros(Hh,W,cv.CV_32FC3);
  let wsum= new cv.Mat.zeros(Hh,W,cv.CV_32FC1);
  let raw = new cv.Mat.zeros(Hh,W,cv.CV_8UC3);

  for (let i=0;i<imgs.length;i++){
    const img=imgs[i];
    const H=H_to_ref[i] || cv.Mat.eye(3,3,cv.CV_64F);
    const Hs=new cv.Mat(); cv.gemm(shift,H,1,new cv.Mat(),0,Hs);

    const warped=new cv.Mat(); cv.warpPerspective(img,warped,Hs,new cv.Size(W,Hh));
    const g=new cv.Mat(); cv.cvtColor(warped,g,cv.COLOR_BGR2GRAY);
    const mask=new cv.Mat(); cv.threshold(g,mask,0,255,cv.THRESH_BINARY); g.delete();

    const dist=new cv.Mat(); cv.distanceTransform(mask,dist,cv.DIST_L2,3);
    const mm=cv.minMaxLoc(dist);
    const weight=new cv.Mat();
    if (mm.maxVal>0) cv.convertScaleAbs(dist,weight,255.0/mm.maxVal); else weight = cv.Mat.zeros(dist.rows, dist.cols, cv.CV_8U);
    dist.delete();

    let wFloat=new cv.Mat(); weight.convertTo(wFloat,cv.CV_32F,1/255.0); weight.delete();
    let w3=new cv.Mat(); cv.merge([wFloat,wFloat,wFloat],w3);

    let warped32=new cv.Mat(); warped.convertTo(warped32,cv.CV_32F);
    let contrib=new cv.Mat(); cv.multiply(warped32,w3,contrib);
    cv.add(acc,contrib,acc);
    let tmp=new cv.Mat(); cv.add(wsum,wFloat,tmp); wsum.delete(); wsum=tmp;

    let mask3=new cv.Mat(); cv.merge([mask,mask,mask],mask3);
    let inv=new cv.Mat(); cv.bitwise_not(mask3,inv);
    let rawTmp=new cv.Mat(); cv.bitwise_and(raw,inv,rawTmp);
    let warped8=new cv.Mat(); warped.convertTo(warped8,cv.CV_8U);
    cv.add(rawTmp,warped8,raw);

    warped.delete(); warped32.delete(); contrib.delete(); mask.delete(); mask3.delete(); inv.delete(); rawTmp.delete(); warped8.delete(); Hs.delete(); w3.delete(); wFloat.delete();
  }

  let blended=new cv.Mat(); let wsum3=new cv.Mat(); cv.merge([wsum,wsum,wsum],wsum3);
  cv.divide(acc, wsum3, blended, 1, cv.CV_32F);
  acc.delete(); wsum3.delete();
  let blended8=new cv.Mat(); blended.convertTo(blended8,cv.CV_8U); blended.delete();

  const cropped = autoCrop(blended8); blended8.delete();
  return {raw, pano: cropped};
}

function autoCrop(imgBGR){
  const gray=new cv.Mat(); cv.cvtColor(imgBGR,gray,cv.COLOR_BGR2GRAY);
  const th=new cv.Mat(); cv.threshold(gray,th,3,255,cv.THRESH_BINARY); gray.delete();
  let contours=new cv.MatVector(), hier=new cv.Mat();
  cv.findContours(th,contours,hier,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE);
  th.delete(); hier.delete();
  if (contours.size()===0){ contours.delete(); return imgBGR; }
  let idx=0, best=0;
  for (let i=0;i<contours.size();i++){ const a=cv.contourArea(contours.get(i)); if (a>best){best=a; idx=i;} }
  const rect=cv.boundingRect(contours.get(idx)); contours.delete();
  const roi=imgBGR.roi(rect); const out=new cv.Mat(); roi.copyTo(out); roi.delete();
  return out;
}

// ---------- Stitch ----------
async function runStitch(){
  cvReadyOrDie();
  if (camFiles.length < 2){ alert('Select at least 2 images'); return; }
  setBusy(true);
  try{
    const maxDim = +resizeEl.value;
    const imgs=[];
    for (const item of camFiles){
      const mat = await fileToMat(item.file, maxDim);
      imgs.push(ensureBGR(mat));
    }

    const ref = Math.floor(imgs.length/2);
    const H_to_ref = Array(imgs.length).fill(null);
    H_to_ref[ref] = cv.Mat.eye(3,3,cv.CV_64F);

    const sampleOverlays=[];

    // Try feature2d first
    let detector = createDetectorOrNull();
    const useFallback = !detector;
    if (!detector) statusEl.textContent = 'Working… (using LK fallback)';

    // Rightwards
    for (let i=ref+1;i<imgs.length;i++){
      let H=null, overlay=null;
      if (!useFallback){
        const fa = detectAndDescribe(detector, imgs[i-1]);
        const fb = detectAndDescribe(detector, imgs[i]);
        const good = knnMatchRatio(fa.desc, fb.desc, 0.75);
        const res = homographyFromMatches(fa.kps, fb.kps, good);
        H = res.H;
        if (saveVis.checked && H && !H.empty()) overlay = drawMatchesSide(imgs[i-1], imgs[i], fa.kps, fb.kps, good, 60);
        fa.kps.delete(); fa.desc.delete(); fb.kps.delete(); fb.desc.delete(); good.delete(); res.mask && res.mask.delete?.();
      } else {
        const r = lkHomography(imgs[i-1], imgs[i]);
        H = r.H; overlay = r.overlay; r.mask && r.mask.delete?.();
      }
      if (!H || H.empty()) throw new Error(`Not enough matches between frames ${i-1} and ${i}`);
      const acc = new cv.Mat(); cv.gemm(H_to_ref[i-1], H, 1, new cv.Mat(), 0, acc);
      H_to_ref[i] = acc; H.delete();
      if (saveVis.checked && overlay){ sampleOverlays.push(overlay); }
    }

    // Leftwards
    for (let i=ref-1;i>=0;i--){
      let H=null, overlay=null;
      if (!useFallback){
        const fa = detectAndDescribe(detector, imgs[i+1]);
        const fb = detectAndDescribe(detector, imgs[i]);
        const good = knnMatchRatio(fa.desc, fb.desc, 0.75);
        const res = homographyFromMatches(fa.kps, fb.kps, good);
        H = res.H;
        if (saveVis.checked && H && !H.empty()) overlay = drawMatchesSide(imgs[i+1], imgs[i], fa.kps, fb.kps, good, 60);
        fa.kps.delete(); fa.desc.delete(); fb.kps.delete(); fb.desc.delete(); good.delete(); res.mask && res.mask.delete?.();
      } else {
        const r = lkHomography(imgs[i+1], imgs[i]);
        H = r.H; overlay = r.overlay; r.mask && r.mask.delete?.();
      }
      if (!H || H.empty()) throw new Error(`Not enough matches between frames ${i+1} and ${i}`);
      const acc = new cv.Mat(); cv.gemm(H_to_ref[i+1], H, 1, new cv.Mat(), 0, acc);
      H_to_ref[i] = acc; H.delete();
      if (saveVis.checked && overlay){ sampleOverlays.push(overlay); }
    }

    // Warp + blend
    const {raw, pano} = warpAllToPanorama(imgs, H_to_ref);

    oursRow.innerHTML=''; matchRow.innerHTML='';
    const rawUrl = matToDataUrl(raw), panoUrl = matToDataUrl(pano);
    addPreview(oursRow, 'panorama_raw.jpg', rawUrl);
    addPreview(oursRow, 'panorama_blend.jpg', panoUrl);
    lastOursImg = dataUrlToImage(panoUrl);

    if (saveVis.checked){
      sampleOverlays.slice(0,3).forEach(m => { addPreview(matchRow, 'matches.jpg', matToDataUrl(m)); m.delete(); });
    }

    // cleanup
    imgs.forEach(m=>m.delete());
    H_to_ref.forEach(H=>H && H.delete());
    raw.delete(); pano.delete();
    detector && detector.delete?.();

  }catch(err){
    console.error(err);
    alert('Stitch failed: ' + err.message);
  }finally{
    setBusy(false);
  }
}

// ---------- Compare ----------
async function runCompare(){
  cvReadyOrDie();
  if (!lastOursImg){ alert('Run Stitch first.'); return; }
  if (!panoFile){ alert('Select your phone panorama.'); return; }
  setBusy(true);
  try{
    const oursMat = await new Promise(res => { lastOursImg.onload = ()=>res(cv.imread(lastOursImg)); if (lastOursImg.complete) res(cv.imread(lastOursImg)); });
    const phoneMat0 = await fileToMat(panoFile, Math.max(oursMat.rows, oursMat.cols));
    const ours = ensureBGR(oursMat), phone = ensureBGR(phoneMat0);

    // match heights
    let A = ours, B = phone;
    if (A.rows !== B.rows){
      const scale = A.rows / B.rows; const Bout = new cv.Mat();
      cv.resize(B, Bout, new cv.Size(Math.round(B.cols*scale), A.rows), 0, 0, cv.INTER_AREA);
      B.delete(); B = Bout;
    }
    const w = Math.min(A.cols, B.cols);
    const Ar = A.roi(new cv.Rect(0,0,w,A.rows));
    const Br = B.roi(new cv.Rect(0,0,w,B.rows));

    // SSIM (fast grayscale global) + PSNR
    const ssim = ssimGray(Ar, Br);
    const psn = psnr(Ar, Br);

    // panel
    const pad=20;
    const panel = new cv.Mat.zeros(Ar.rows, Ar.cols + Br.cols + pad, cv.CV_8UC3);
    Ar.copyTo(panel.roi(new cv.Rect(0,0,Ar.cols,Ar.rows)));
    Br.copyTo(panel.roi(new cv.Rect(Ar.cols+pad,0,Br.cols,Br.rows)));
    const panelUrl = matToDataUrl(panel);

    cmpRow.innerHTML=''; metricsRow.innerHTML='';
    addPreview(cmpRow, 'Our Stitch  |  Phone Panorama', panelUrl);
    const m1 = document.createElement('div'); m1.className='metric'; m1.textContent=`SSIM: ${ssim.toFixed(4)}`;
    const m2 = document.createElement('div'); m2.className='metric'; m2.textContent=`PSNR: ${psn.toFixed(2)} dB`;
    metricsRow.appendChild(m1); metricsRow.appendChild(m2);

    // cleanup
    ours.delete(); phone.delete(); A.delete?.(); B.delete?.(); Ar.delete(); Br.delete(); panel.delete();
  }catch(err){
    console.error(err);
    alert('Compare failed: ' + err.message);
  }finally{
    setBusy(false);
  }
}

// quick SSIM (global grayscale)
function ssimGray(a,b){
  const ag=new cv.Mat(), bg=new cv.Mat();
  cv.cvtColor(a,ag,cv.COLOR_BGR2GRAY); cv.cvtColor(b,bg,cv.COLOR_BGR2GRAY);
  ag.convertTo(ag,cv.CV_32F); bg.convertTo(bg,cv.CV_32F);
  const C1=6.5025, C2=58.5225;
  const muA=cv.mean(ag)[0], muB=cv.mean(bg)[0];
  const tmpA=new cv.Mat(), tmpB=new cv.Mat(), sqA=new cv.Mat(), sqB=new cv.Mat(), prod=new cv.Mat();
  cv.subtract(ag, new cv.Mat(ag.rows,ag.cols,ag.type(), new cv.Scalar(muA)), tmpA);
  cv.subtract(bg, new cv.Mat(bg.rows,bg.cols,bg.type(), new cv.Scalar(muB)), tmpB);
  cv.multiply(tmpA,tmpA,sqA); cv.multiply(tmpB,tmpB,sqB);
  const varA=cv.mean(sqA)[0], varB=cv.mean(sqB)[0];
  cv.multiply(tmpA,tmpB,prod); const cov=cv.mean(prod)[0];
  ag.delete(); bg.delete(); tmpA.delete(); tmpB.delete(); sqA.delete(); sqB.delete(); prod.delete();
  return ((2*muA*muB + C1)*(2*cov + C2)) / ((muA*muA + muB*muB + C1)*(varA + varB + C2));
}
function psnr(a,b){
  const diff=new cv.Mat(); cv.absdiff(a,b,diff); diff.convertTo(diff,cv.CV_32F); cv.multiply(diff,diff,diff);
  const s=cv.sumElems(diff); const mse=(s[0]+s[1]+s[2])/(a.rows*a.cols*3); diff.delete();
  if (mse===0) return 99.0; return 10.0*Math.log10((255*255)/mse);
}

// ---------- Events ----------
camInput.addEventListener('change', e=>{ camFiles=[]; [...e.target.files].forEach(addCamFile); renderCamList(); });
panoInput.addEventListener('change', e=>{ panoFile=e.target.files[0]||null; previewPano(); });
btnSort.addEventListener('click', ()=>{ camFiles.sort((a,b)=>a.file.name.localeCompare(b.file.name, undefined,{numeric:true,sensitivity:'base'})); renderCamList(); });
btnReverse.addEventListener('click', ()=>{ camFiles.reverse(); renderCamList(); });
btnClear.addEventListener('click', ()=>{ camFiles=[]; camInput.value=''; renderCamList(); });
resizeEl.addEventListener('input', ()=> resizeVal.textContent = `${resizeEl.value} px`);

btnStitch.addEventListener('click', runStitch);
btnCompare.addEventListener('click', runCompare);
