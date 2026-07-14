const weeks=[
 {title:'补基础，建立稳定得分区',description:'先消灭会做却丢分，暂时不投入大量时间攻压轴题。'},
 {title:'突破中档题和实验题',description:'掌握高频模型，让每一步过程都能转化成卷面分数。'},
 {title:'整卷训练与得分策略',description:'用正式计时建立节奏，把非知识性失分压到最低。'}
];
const days=[
 ['摸清起点','2023 数学卷限时诊断','只做能独立完成的题，标记犹豫题。','2023 物理卷限时诊断','记录概念、实验、计算三类得分。','完成两科诊断','统计板块得分与五类错因。','papers/math/2023-math.md','papers/physics/2023-physics.md','120 分钟','70 分钟'],
 ['运算基本功','实数、整式与分式','因式分解、分式化简，每类 8–10 题。','单位、速度与密度','先统一单位，再列公式计算。','基础正确率 ≥ 85%','错题脱离答案重做一次。','math/exam-points.md','physics/formula-sheet.md','75 分钟','65 分钟'],
 ['方程与受力','方程、不等式及应用','验根、解集端点和应用题设元。','力与运动状态','平衡力、摩擦力和受力分析。','每类完成 8–10 题','能独立画出受力示意图。','math/exam-points.md','physics/exam-points.md','75 分钟','65 分钟'],
 ['函数与浮力','一次与反比例函数','图像性质、待定系数与面积模型。','压强、浮力','受力分析、浮沉条件与阿基米德原理。','模型题正确率 ≥ 80%','函数图和受力图必须自己画。','math/past-questions.md','physics/exam-points.md','80 分钟','65 分钟'],
 ['几何起步','三角形、全等与勾股','证明中写清判定依据和对应关系。','功与机械','功、功率、滑轮组与机械效率。','步骤完整、单位齐全','物理计算执行四步书写。','math/exam-points.md','physics/past-questions.md','80 分钟','65 分钟'],
 ['基础扫尾','四边形与圆的基础','性质、判定、圆周角和直径模型。','声、光、热概念','专练容易混淆的生活现象。','混合题正确率 ≥ 85%','把混淆概念写成对比句。','math/formula-sheet.md','physics/past-questions.md','80 分钟','60 分钟'],
 ['第一周检测','基础部分限时','选择、填空及 17–22 题。','概念与力学限时','选择题加两道力学计算。','数学基础 ≥ 52/62','本周物理内容正确率 ≥ 80%。','papers/math/2022-math.md','papers/physics/2022-physics.md','90 分钟','70 分钟'],
 ['函数进阶','二次函数基础','顶点、对称轴、开口和交点。','欧姆定律','串并联规律与基础计算。','基础模型 ≥ 80%','能从题干快速选择公式。','math/exam-points.md','physics/formula-sheet.md','80 分钟','70 分钟'],
 ['综合读图','一次与反比例综合','交点、函数值比较和图像信息。','动态电路','识别电流路径和电表示数变化。','每题先画图再计算','说清变阻器改变了什么。','math/past-questions.md','physics/exam-points.md','85 分钟','70 分钟'],
 ['测量模型','相似与锐角三角函数','测高测距，先把实际问题转成图形。','电功与电热','电功率、焦耳定律及单位换算。','综合步骤得分 ≥ 75%','已知量必须在图中标出。','math/exam-points.md','physics/formula-sheet.md','85 分钟','70 分钟'],
 ['高频证明','圆与切线','圆周角、直径和切线证明。','伏安法实验','电路连接、操作、数据与故障分析。','能口述完整实验流程','数学证明不跳关键依据。','math/past-questions.md','physics/past-questions.md','85 分钟','75 分钟'],
 ['变换与实验','旋转、对称与辅助线','寻找不变量，训练几何综合第一问。','三大实验','密度、凸透镜、液体压强。','每个实验整理四栏表','器材、步骤、结论、误差。','math/exam-points.md','physics/past-questions.md','85 分钟','75 分钟'],
 ['稳拿信息分','统计与概率','图表补全、中位数和简单概率。','力电综合计算','题干信息翻译成力学或电学模型。','统计题争取满分','物理写全公式、结果和单位。','math/past-questions.md','physics/past-questions.md','70 分钟','80 分钟'],
 ['第二周模考','2022 数学整卷','严格计时 120 分钟，保留所有过程。','2022 物理整卷','严格按正式考试时长完成。','数学 ≥ 75，物理 ≥ 58','当天完成逐题订正。','papers/math/2022-math.md','papers/physics/2022-physics.md','120 分钟','70 分钟'],
 ['精准补洞','订正整卷','选择失分最多的两个专题各做 8 题。','订正整卷','按概念、实验、计算重新归因。','同类重做 ≥ 80%','不会的题必须回到考点材料。','math/exam-points.md','physics/exam-points.md','80 分钟','70 分钟'],
 ['限时提速','基础题限时专项','选择填空 35 分钟，基础解答 45 分钟。','实验专项','用规范术语回答目的、变量和结论。','数学前 22 题 ≥ 55/62','物理实验答案表述完整。','math/past-questions.md','physics/past-questions.md','80 分钟','70 分钟'],
 ['验证提升','2023 数学二刷','与第 1 天逐题对照得分变化。','力电综合','电学、力学各完成一道综合题。','数学较首日提高 ≥ 10 分','综合题第一问不丢分。','papers/math/2023-math.md','physics/past-questions.md','120 分钟','60 分钟'],
 ['数学模考','2024 数学整卷','正式计时，最后 15 分钟检查基础题。','错题回炉','重做最近三天的物理错题。','数学目标 ≥ 80','非知识性失分不超过 5 分。','papers/math/2024-math.md','physics/formula-sheet.md','120 分钟','40 分钟'],
 ['物理模考','数学错题回炉','重做昨日错题并写出错误原因。','2024 物理整卷','使用含完整图片的官方 PDF 更佳。','物理目标 ≥ 64','选择和实验基础分 ≥ 85%。','math/formula-sheet.md','papers/physics/2024-physics.md','45 分钟','70 分钟'],
 ['最新模拟','弱项专题收口','只补最近两套卷反复出现的弱项。','最新官方卷或本区一模','完全模拟正式考试环境。','按正式时间完成','新错题不再大面积扩展专题。','math/exam-points.md','papers/sources/README.md','80 分钟','70 分钟'],
 ['终局检验','数学完整模拟','按 35+40+30+15 分钟分配。','物理完整模拟','先稳定基础，再处理综合题。','连续达标','数学 ≥ 80，物理 ≥ 64。','papers/math/2024-math.md','papers/physics/2024-physics.md','120 分钟','70 分钟']
];
const key='beijingZhongkaoPlan';
let state=JSON.parse(localStorage.getItem(key)||'{"completed":[],"mistakes":[],"selectedDay":0,"selectedWeek":0}');
const $=id=>document.getElementById(id);
function save(){localStorage.setItem(key,JSON.stringify(state))}
function renderToday(){const d=days[state.selectedDay];$('dayLabel').textContent=`第 ${state.selectedDay+1} 天`;$('mathTitle').textContent=d[1];$('mathDetail').textContent=d[2];$('physicsTitle').textContent=d[3];$('physicsDetail').textContent=d[4];$('checkTitle').textContent=d[5];$('checkDetail').textContent=d[6];$('mathResource').href=d[7];$('physicsResource').href=d[8];$('mathTime').textContent=d[9];$('physicsTime').textContent=d[10];$('completeToday').checked=state.completed.includes(state.selectedDay);renderWeek();}
function renderWeek(){document.querySelectorAll('.week-tabs button').forEach((b,i)=>b.classList.toggle('active',i===state.selectedWeek));const w=weeks[state.selectedWeek];$('weekNumber').textContent=String(state.selectedWeek+1).padStart(2,'0');$('weekTitle').textContent=w.title;$('weekDescription').textContent=w.description;$('daysGrid').innerHTML=days.slice(state.selectedWeek*7,state.selectedWeek*7+7).map((d,i)=>{const n=state.selectedWeek*7+i,done=state.completed.includes(n);return `<button class="day-card ${done?'done':''} ${n===state.selectedDay?'selected':''}" data-day="${n}" type="button"><span class="day-number">${String(n+1).padStart(2,'0')}</span><h4>${d[0]}</h4><p>${d[1]}<br>${d[3]}</p><span class="done-mark">${done?'✓ 已完成':'查看任务 →'}</span></button>`}).join('');document.querySelectorAll('.day-card').forEach(b=>b.onclick=()=>{state.selectedDay=Number(b.dataset.day);save();renderToday();document.querySelector('.today-panel').scrollIntoView({behavior:'smooth'})})}
function renderProgress(){const count=state.completed.length,pct=Math.round(count/21*100);$('completedDays').textContent=count;$('progressPercent').textContent=`${pct}%`;$('progressRing').style.setProperty('--progress',`${pct*3.6}deg`);$('progressMessage').textContent=count===21?'三周训练完成，保持整卷节奏。':count>=14?'进入整卷阶段，重点控制非知识性失分。':count>=7?'基础框架已建立，开始突破中档模型。':'先完成诊断，找到最值得补的分数。'}
function renderMistakes(){$('recordCount').textContent=`${state.mistakes.length} 条记录`;$('mistakeList').innerHTML=state.mistakes.length?state.mistakes.map((m,i)=>`<div class="mistake-item"><b>${m.subject}</b><span>${m.reason}</span><span>${escapeHtml(m.text)}</span><button type="button" data-remove="${i}" aria-label="删除记录">×</button></div>`).join(''):'<p class="empty-state">还没有错题记录。做完今日训练后，把最值得重做的题留在这里。</p>';document.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{state.mistakes.splice(Number(b.dataset.remove),1);save();renderMistakes()})}
function escapeHtml(s){return s.replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
$('completeToday').onchange=e=>{state.completed=e.target.checked?[...new Set([...state.completed,state.selectedDay])]:state.completed.filter(n=>n!==state.selectedDay);save();renderProgress();renderWeek()};
$('prevDay').onclick=()=>{state.selectedDay=(state.selectedDay+20)%21;state.selectedWeek=Math.floor(state.selectedDay/7);save();renderToday()};
$('nextDay').onclick=()=>{state.selectedDay=(state.selectedDay+1)%21;state.selectedWeek=Math.floor(state.selectedDay/7);save();renderToday()};
$('startButton').onclick=()=>document.querySelector('.today-panel').scrollIntoView({behavior:'smooth'});
document.querySelectorAll('.week-tabs button').forEach(b=>b.onclick=()=>{state.selectedWeek=Number(b.dataset.week);save();renderWeek()});
$('mistakeForm').onsubmit=e=>{e.preventDefault();state.mistakes.unshift({subject:$('mistakeSubject').value,reason:$('mistakeReason').value,text:$('mistakeText').value.trim()});$('mistakeText').value='';save();renderMistakes()};
$('resetButton').onclick=()=>$('resetDialog').showModal();$('cancelReset').onclick=()=>$('resetDialog').close();$('confirmReset').onclick=()=>{state={completed:[],mistakes:[],selectedDay:0,selectedWeek:0};save();$('resetDialog').close();renderToday();renderProgress();renderMistakes()};
renderToday();renderProgress();renderMistakes();
