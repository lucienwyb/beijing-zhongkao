const weeks=[
 {title:'补基础，建立稳定得分区',description:'先消灭会做却丢分，暂时不投入大量时间攻压轴题。'},
 {title:'突破中档题和实验题',description:'掌握高频模型，让每一步过程都能转化成卷面分数。'},
 {title:'整卷训练与得分策略',description:'用正式计时建立节奏，把非知识性失分压到最低。'}
];
const days=[
 ['摸清起点'],
 ['运算基本功'],
 ['方程与受力'],
 ['函数与浮力'],
 ['几何起步'],
 ['基础扫尾'],
 ['第一周检测'],
 ['函数进阶'],
 ['综合读图'],
 ['测量模型'],
 ['高频证明'],
 ['变换与实验'],
 ['稳拿信息分'],
 ['第二周模考'],
 ['精准补洞'],
 ['限时提速'],
 ['中档专项'],
 ['数学模考'],
 ['错题回炉'],
 ['压轴保分收口'],
 ['终局检验']
];
const key='beijingZhongkaoPlan';
let state;
try{state=JSON.parse(localStorage.getItem(key)||'{"completed":[],"mistakes":[],"selectedDay":0,"selectedWeek":0}')}catch(e){state=null}
// Defensive normalize: old/corrupted localStorage (out-of-range day, missing
// fields, non-array values, or a non-object payload like "null"/"5"/"[1,2,3]")
// would make mathPlans[state.selectedDay] throw and break the whole page.
// Reject any non-plain-object payload, then clamp indices and ensure types.
if(!state||typeof state!=='object'||Array.isArray(state)){state={completed:[],mistakes:[],selectedDay:0,selectedWeek:0}}
state.completed=Array.isArray(state.completed)?state.completed.filter(n=>Number.isInteger(n)&&n>=0&&n<21):[];
state.mistakes=Array.isArray(state.mistakes)?state.mistakes:[];
state.selectedDay=Number.isInteger(state.selectedDay)&&state.selectedDay>=0&&state.selectedDay<21?state.selectedDay:0;
state.selectedWeek=Number.isInteger(state.selectedWeek)&&state.selectedWeek>=0&&state.selectedWeek<3?state.selectedWeek:0;
const $=id=>document.getElementById(id);
function save(){try{localStorage.setItem(key,JSON.stringify(state))}catch(e){/* iOS Safari private mode / quota: silently ignore */}}
function resourceUrl(path){return path.endsWith('.md')?`html/${path.slice(0,-3)}.html`:path}
function fillLesson(subject,lesson){$(''+subject+'Title').textContent=lesson.title;$(''+subject+'Concept').textContent=lesson.concept;$(''+subject+'Points').textContent=lesson.points;$(''+subject+'Model').textContent=lesson.model;$(''+subject+'Practice').textContent=lesson.practice;$(''+subject+'Check').textContent=lesson.check;$(''+subject+'Resource').href=resourceUrl(lesson.resource);$(''+subject+'Time').textContent=lesson.time}
function renderToday(){const math=mathPlans[state.selectedDay],physics=physicsPlans[state.selectedDay];$('dayLabel').textContent=`第 ${state.selectedDay+1} 天`;fillLesson('math',math);fillLesson('physics',physics);$('completeToday').checked=state.completed.includes(state.selectedDay);renderWeek();}
function renderWeek(){document.querySelectorAll('.week-tabs button').forEach((b,i)=>{const on=i===state.selectedWeek;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on?'true':'false')});const w=weeks[state.selectedWeek];$('weekNumber').textContent=String(state.selectedWeek+1).padStart(2,'0');$('weekTitle').textContent=w.title;$('weekDescription').textContent=w.description;$('daysGrid').innerHTML=days.slice(state.selectedWeek*7,state.selectedWeek*7+7).map((d,i)=>{const n=state.selectedWeek*7+i,done=state.completed.includes(n);return `<button class="day-card ${done?'done':''} ${n===state.selectedDay?'selected':''}" data-day="${n}" type="button" aria-label="第 ${n+1} 天 ${d[0]}${done?' 已完成':''}"><span class="day-number">${String(n+1).padStart(2,'0')}</span><h4>${d[0]}</h4><p>${mathPlans[n].title}<br>${physicsPlans[n].title}</p><span class="done-mark">${done?'✓ 已完成':'查看任务 →'}</span></button>`}).join('');document.querySelectorAll('.day-card').forEach(b=>b.onclick=()=>{state.selectedDay=Number(b.dataset.day);save();renderToday();document.querySelector('.today-panel').scrollIntoView({behavior:'smooth'})})}
function renderProgress(){const count=state.completed.length,pct=Math.round(count/21*100);$('completedDays').textContent=count;$('progressPercent').textContent=`${pct}%`;$('progressMessage').textContent=count===21?'三周训练完成，保持整卷节奏。':count>=14?'进入整卷阶段，重点控制非知识性失分。':count>=7?'基础框架已建立，开始突破中档模型。':'先完成诊断，找到最值得补的分数。'}
function renderMistakes(){$('recordCount').textContent=`${state.mistakes.length} 条记录`;$('mistakeList').innerHTML=state.mistakes.length?state.mistakes.map((m,i)=>`<div class="mistake-item"><b>${escapeHtml(m.subject)}</b><span>${escapeHtml(m.reason)}</span><span>${escapeHtml(m.text)}</span><button type="button" data-remove="${i}" aria-label="删除记录">×</button></div>`).join(''):'<p class="empty-state">还没有错题记录。做完今日训练后，把最值得重做的题留在这里。</p>';document.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{state.mistakes.splice(Number(b.dataset.remove),1);save();renderMistakes()})}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
$('completeToday').onchange=e=>{state.completed=e.target.checked?[...new Set([...state.completed,state.selectedDay])]:state.completed.filter(n=>n!==state.selectedDay);save();renderProgress();renderWeek()};
$('prevDay').onclick=()=>{state.selectedDay=(state.selectedDay+20)%21;state.selectedWeek=Math.floor(state.selectedDay/7);save();renderToday()};
$('nextDay').onclick=()=>{state.selectedDay=(state.selectedDay+1)%21;state.selectedWeek=Math.floor(state.selectedDay/7);save();renderToday()};
$('startButton').onclick=()=>document.querySelector('.today-panel').scrollIntoView({behavior:'smooth'});
document.querySelectorAll('.week-tabs button').forEach(b=>b.onclick=()=>{state.selectedWeek=Number(b.dataset.week);save();renderWeek()});
$('mistakeForm').onsubmit=e=>{e.preventDefault();state.mistakes.unshift({subject:$('mistakeSubject').value,reason:$('mistakeReason').value,text:$('mistakeText').value.trim()});$('mistakeText').value='';save();renderMistakes()};
function doReset(){state={completed:[],mistakes:[],selectedDay:0,selectedWeek:0};save();const d=$('resetDialog');if(d&&typeof d.close==='function')d.close();renderToday();renderProgress();renderMistakes()}
$('resetButton').onclick=()=>{const d=$('resetDialog');if(d&&typeof d.showModal==='function'){d.showModal()}else if(confirm('重置学习进度？\n21 天完成状态和错题记录都会被清空，此操作无法撤销。')){doReset()}};
$('cancelReset').onclick=()=>{const d=$('resetDialog');if(d&&typeof d.close==='function')d.close()};
$('confirmReset').onclick=doReset;
renderToday();renderProgress();renderMistakes();
