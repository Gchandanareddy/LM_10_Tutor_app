import streamlit as st
import json
import urllib.request
import urllib.error

st.set_page_config(page_title="LM10 AI Tutor", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #212121; color: #ececec; }
header[data-testid="stHeader"] { background: transparent; }
.chat-wrap { max-width: 860px; margin: 0 auto; padding: 0 1rem 160px 1rem; }
.msg-ai   { display:flex; justify-content:flex-start;  margin:12px 0; gap:10px; align-items:flex-start; }
.msg-user { display:flex; justify-content:flex-end;    margin:12px 0; gap:10px; align-items:flex-start; }
.msg-ai .bubble { background:#2a2a2a; color:#ececec; padding:14px 18px; border-radius:18px 18px 18px 4px; max-width:92%; font-size:0.93rem; line-height:1.88; border:1px solid #3a3a3a; white-space:pre-wrap; }
.msg-user .bubble { background:#2f2f2f; color:#ececec; padding:12px 16px; border-radius:18px 18px 4px 18px; max-width:80%; font-size:0.93rem; line-height:1.6; white-space:pre-wrap; }
.msg-ai .av { width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#ab68ff,#7c3aed);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;margin-top:2px; }
.msg-user .av { width:34px;height:34px;border-radius:50%;background:#19c37d;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;color:white;flex-shrink:0;margin-top:2px; }
.box-green  { background:#052e16;border-left:4px solid #4ade80;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#bbf7d0; }
.box-yellow { background:#1c1600;border-left:4px solid #fbbf24;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#fef08a; }
.box-red    { background:#1f0a0a;border-left:4px solid #f87171;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#fca5a5; }
.box-blue   { background:#0f1f2e;border-left:4px solid #38bdf8;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#bae6fd; }
.box-purple { background:#1a1a2e;border-left:4px solid #818cf8;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#c7d2fe; }
.tag-py  { background:#34d39922;color:#a7f3d0;border:1px solid #34d399;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-right:4px; }
.tag-sql { background:#f59e0b22;color:#fde68a;border:1px solid #f59e0b;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-right:4px; }
.tag-concept { background:#ec489933;color:#f9a8d4;border:1px solid #ec4899;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-right:4px; }
.tag-q { background:#7c3aed33;color:#c4b5fd;border:1px solid #7c3aed;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-right:4px; }
.ai-badge { background:#7c3aed33;color:#c4b5fd;border:1px solid #7c3aed;border-radius:8px;padding:1px 7px;font-size:0.7rem;font-weight:600;margin-left:5px; }
.progress-bar-wrap { position:fixed;top:0;left:0;right:0;height:3px;z-index:9999;background:#333; }
.progress-bar-fill { height:100%;background:linear-gradient(90deg,#7c3aed,#19c37d);transition:width 0.5s; }
.top-bar { position:sticky;top:0;background:#212121;border-bottom:1px solid #333;padding:10px 0 8px;margin-bottom:6px;z-index:100; }
.top-bar h2 { text-align:center;font-size:0.9rem;font-weight:500;color:#aaa;margin:0; }
.stButton > button { background:#2a2a2a!important;color:#ececec!important;border:1px solid #444!important;border-radius:20px!important;font-size:0.82rem!important;padding:5px 14px!important;transition:all 0.15s!important; }
.stButton > button:hover { background:#3a3a3a!important;border-color:#7c3aed!important; }
</style>
""", unsafe_allow_html=True)

def get_api_key():
    try: return st.secrets["ANTHROPIC_API_KEY"]
    except: return st.session_state.get("api_key","")

with st.sidebar:
    st.markdown("### 🔑 API Key")
    k=st.text_input("Anthropic API Key",value=st.session_state.get("api_key",""),type="password",placeholder="sk-ant-...",label_visibility="collapsed")
    if k: st.session_state["api_key"]=k; st.success("✅ Key saved")
    api_key=get_api_key()
    if api_key: st.markdown("<span style='color:#4ade80;font-size:0.82rem'>🤖 AI grading active</span>",unsafe_allow_html=True)
    else:       st.markdown("<span style='color:#fbbf24;font-size:0.82rem'>⚠️ No key — fallback</span>",unsafe_allow_html=True)
    st.markdown("---")
    g=st.session_state.get("grades",{})
    st.markdown(f"**Score:** {sum(1 for v in g.values() if v=='correct')} ✅  {sum(1 for v in g.values() if v=='partial')} ⚠️")
    st.caption("📚 HI 780 — LM10: High Utilizer Prediction")

TASKS=[
  {"id":"t1","qnum":"Step 1","title":"Compute cum_days","icon":"📅",
   "intro":"<strong>LM10: Prepare testClaims to predict high utilization (≥50 claims in 6 months after pred_time)</strong>\n\n<div class='box-purple'>The claims table has <strong>year</strong> (text: 'Y1','Y2','Y3') and <strong>claim_days</strong> (integer day within that year). We need a single number <strong>cum_days</strong>.</div>\n<span class='tag-sql'>🗄️ SQL</span>+<span class='tag-concept'>💬</span>",
   "question":"(1) Explain the formula to convert year='Y2', claim_days=50 into cum_days.\n(2) Write the SQL ALTER TABLE and UPDATE to add cum_days.",
   "answer_guidance":"Formula: (year_number-1)*365+claim_days. Y2,day50=(2-1)*365+50=415. SQL: ALTER TABLE claims ADD cum_days int; UPDATE claims SET cum_days=(cast(substring(year,2,1) as int)-1)*365+cast(claim_days as int). Key: SUBSTRING(year,2,1) extracts '2'; cast to int; subtract 1 then multiply by 365.",
   "hint":"Year 'Y2' = year number 2. Y1=days 1-365, Y2=days 366-730. Formula: extract digit from 'Y2', subtract 1, multiply by 365, add claim_days. SQL: SUBSTRING(year,2,1) gets the character."},
  {"id":"t2","qnum":"Step 2","title":"Define Prediction Time","icon":"🎯",
   "intro":"<div class='box-purple'>pred_time anchored to hospitalization: plcsrvc='20' AND los not empty. Filter to cum_days 365-730 (ensures 6mo history + 6mo future).</div>\n<span class='tag-sql'>🗄️ SQL</span>+<span class='tag-concept'>💬</span>",
   "question":"(1) WHY restrict pred_time to 365-730? What happens if pred_time=50 or pred_time=1000?\n(2) Write SQL to create #pat1 (hospitalizations) and #pat2 (filtered).",
   "answer_guidance":"Need 180 days history BEFORE (features) and 180 days outcome AFTER. pred_time=50: not enough history. pred_time=1000+: not enough future. SQL #pat1: SELECT patient_id,cum_days INTO #pat1 FROM claims WHERE plcsrvc='20' AND los<>''. SQL #pat2: SELECT patient_id,cum_days as pred_time INTO #pat2 FROM #pat1 WHERE cum_days>=365 AND cum_days<=730.",
   "hint":"You need data on BOTH sides: 6 months before for features, 6 months after for the label. If pred_time=50, you only have 50 days of history. If pred_time=1000, you may run past the end of the study."},
  {"id":"t3","qnum":"Step 3","title":"Build the Dependent Variable","icon":"🏷️",
   "intro":"<div class='box-purple'>Label: ≥50 claims in 6 months AFTER pred_time (cum_days>pred_time AND cum_days≤pred_time+180)</div>\n<span class='tag-sql'>🗄️ SQL code required</span>",
   "question":"Write SQL to create #dep: count claims in the future window per patient+pred_time, assign highUtilizer label (≥50=1).",
   "answer_guidance":"SELECT p.patient_id, pred_time, count(*) as claim_count, case when count(*)>=50 then 1 else 0 end as high_utilizer INTO #dep FROM claims c, #pat2 p WHERE p.patient_id=c.patient_id AND c.cum_days>p.pred_time AND c.cum_days<=p.pred_time+180 GROUP BY p.patient_id, pred_time. Key: future window strictly AFTER pred_time; threshold 50; GROUP BY both.",
   "hint":"JOIN claims with #pat2 on patient_id. Filter: cum_days>pred_time AND cum_days<=pred_time+180. GROUP BY patient_id AND pred_time. COUNT(*). CASE WHEN count(*)>=50 THEN 1 ELSE 0 END."},
  {"id":"t4","qnum":"Step 4","title":"Build ELIX Features","icon":"🧬",
   "intro":"<div class='box-purple'>Features: ELIX1-29 binary flags from diagnoses in 6 months BEFORE pred_time (cum_days>=pred_time-180 AND cum_days<pred_time)</div>\n<span class='tag-sql'>🗄️ SQL code required</span>",
   "question":"Write SQL to create #Elix: binary ELIX1-29 columns, one row per patient+pred_time, from the lookback window.",
   "answer_guidance":"SELECT c.patient_id, pred_time, max(case when diagnosis='ELIX1' then 1 else 0 end) as ELIX1, ..., max(case when diagnosis='ELIX29' then 1 else 0 end) as ELIX29 INTO #Elix FROM diagnoses d, claims c, #pat2 p WHERE d.claim_id=c.claim_id AND c.cum_days<p.pred_time AND c.cum_days>=p.pred_time-180 AND p.patient_id=c.patient_id GROUP BY c.patient_id, pred_time. Key: strictly BEFORE pred_time; join via claim_id; GROUP BY both.",
   "hint":"Lookback: cum_days < pred_time AND cum_days >= pred_time-180. Join: diagnoses→claims via claim_id, claims→#pat2 via patient_id. MAX(CASE WHEN diagnosis='ELIX1' THEN 1 ELSE 0 END) for binary pivot."},
  {"id":"t5","qnum":"Step 5","title":"Join Features + Labels","icon":"🔗",
   "intro":"<div class='box-purple'>Join #Elix (features) + #dep (labels) on BOTH patient_id AND pred_time → final table.</div>\n<span class='tag-sql'>🗄️ SQL</span>+<span class='tag-concept'>💬</span>",
   "question":"(1) Write SQL to join #Elix and #dep into dbo.highUtilizationHospitalization.\n(2) Why join on BOTH patient_id AND pred_time?",
   "answer_guidance":"SELECT Elix.*, claim_count, high_utilizer INTO dbo.highUtilizationHospitalization FROM #Elix, #dep WHERE #elix.patient_id=#dep.patient_id AND #elix.pred_time=#dep.pred_time. Must join on both: one patient can have multiple hospitalizations (multiple pred_times). Join on patient_id only → Cartesian product.",
   "hint":"A patient can have multiple hospitalizations in Y2 → multiple pred_times. If you join only on patient_id, each feature row matches every label row for that patient. How many rows does that create for a patient with 3 pred_times?"},
  {"id":"t6","qnum":"Step 6","title":"Train/Test Split — Time-Based","icon":"✂️",
   "intro":"<div class='box-purple'>Must split by time (pred_time order), not randomly. Random split causes temporal data leakage.</div>\n<span class='tag-py'>🐍 Python</span>+<span class='tag-concept'>💬</span>",
   "question":"(1) WHY is time-based split required? What is data leakage here?\n(2) Write Python to prepare X and y — which columns must you drop and why?",
   "answer_guidance":"Time split: all training pred_times before all test pred_times — no future leakage. Random split: same patient's future windows in training, past windows in test — model sees future data. Must drop: patient_id (identifier), pred_time (time identifier), future_claims (DIRECT proxy for the label — leakage!), high_utilizer (label itself). X=df.drop(columns=['patient_id','pred_time','future_claims','high_utilizer']); y=df['high_utilizer'].",
   "hint":"future_claims = number of claims after pred_time = exactly what highUtilizer is derived from. If future_claims is in X, the model predicts the label from the label itself. What is that called?"},
  {"id":"t7","qnum":"Step 7","title":"Train 3 Models with class_weight='balanced'","icon":"🤖",
   "intro":"<div class='box-purple'>High utilizers = minority class (~10-15%). Without handling: model always predicts 0, zero recall. Use class_weight='balanced' for all 3 models.</div>\n<span class='tag-py'>🐍 Python code required</span>",
   "question":"(1) What does class_weight='balanced' do and why is it critical?\n(2) Write Python to train LR (Pipeline+StandardScaler), Decision Tree, Random Forest — all balanced.",
   "answer_guidance":"class_weight='balanced': weights=n_samples/(n_classes*class_count). Minority class gets higher weight so model learns to identify them. LR: Pipeline([('scaler',StandardScaler()),('model',LogisticRegression(max_iter=1000,class_weight='balanced'))]). DT: DecisionTreeClassifier(max_depth=5,class_weight='balanced',random_state=42). RF: RandomForestClassifier(n_estimators=100,class_weight='balanced',random_state=42,n_jobs=-1). All .fit(X_train,y_train).",
   "hint":"class_weight='balanced': if 10% are high utilizers their weight is ~9x. LR MUST use StandardScaler in a Pipeline because it uses gradient descent — feature scale matters. DT/RF don't need scaling (they use thresholds)."},
  {"id":"t8","qnum":"Step 8","title":"Evaluate: F1, AUC + Threshold Tuning","icon":"📊",
   "intro":"<div class='box-purple'>Use F1+AUC, NOT accuracy. Threshold tuning: try 0.3 instead of 0.5. Calibration: are probabilities reliable?</div>\n<span class='tag-py'>🐍 Python</span>+<span class='tag-concept'>💬</span>",
   "question":"(1) Why is F1 better than accuracy for this problem?\n(2) Write Python to evaluate all 3 models + tune RF threshold to 0.3.\n(3) What is model calibration?",
   "answer_guidance":"Accuracy: if 90% non-utilizers, always predict 0 = 90% accuracy but F1=0. F1=2*(P*R)/(P+R) balances precision (correct flag rate) and recall (caught true positives). Code: f1_score(y_test,y_pred); roc_auc_score(y_test,y_prob). Threshold: y_pred_tuned=(y_prob_rf>=0.3).astype(int) — lower threshold increases recall, decreases precision. Calibration: model probability 0.7 should mean patient is high utilizer 70% of the time. Use CalibratedClassifierCV(model,cv=5,method='sigmoid').",
   "hint":"Threshold tuning: y_pred_tuned=(y_prob_rf>=0.3).astype(int). Lower threshold → more patients flagged → recall up, precision down. For calibration: if model says 0.8 for 100 patients but only 40 are actual high utilizers, what is wrong with the model's probabilities?"},
]

def call_claude(title,question,answer_guidance,student_answer,hint_used,api_key):
    is_code=any(c in student_answer for c in ["(","import ","def ","np.","pd.","SELECT","FROM","WHERE","GROUP"])
    type_note="SQL or Python code." if is_code else "Conceptual question — plain English."
    system=f"""Health informatics professor. {type_note} NEVER reveal the answer. Say what is right, what is missing, ask ONE Socratic question. Grade: correct=all key concepts, partial=some right, incorrect=wrong. Return ONLY JSON: {{"grade":"correct|partial|incorrect","feedback":"2-3 sentences","nudge":"one guiding question"}}"""
    user=f"Task: {title}\nQuestion: {question}\nAnswer guidance (do NOT reveal): {answer_guidance}\nStudent: {student_answer}\nHint given: {hint_used}"
    payload=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":500,"system":system,"messages":[{"role":"user","content":user}]}).encode()
    req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=payload,headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"},method="POST")
    with urllib.request.urlopen(req,timeout=30) as resp: data=json.loads(resp.read())
    raw=data["content"][0]["text"].strip()
    if "```" in raw:
        for part in raw.split("```"):
            part=part.strip().lstrip("json").strip()
            try: r=json.loads(part); return r["grade"],r["feedback"],r["nudge"]
            except: continue
    r=json.loads(raw); return r["grade"],r["feedback"],r["nudge"]

KW={"t1":["365","year","substring","cast","cum_days","alter","update"],"t2":["365","730","history","future","plcsrvc","pred_time","los"],"t3":["50","180","count","group by","pred_time","future","case when"],"t4":["elix","lookback","180","pred_time","claim_id","diagnosis","max"],"t5":["patient_id","pred_time","both","cartesian","multiple"],"t6":["leakage","future_claims","drop","time","temporal","patient_id"],"t7":["balanced","class_weight","pipeline","scaler","minority","imbalance","fit"],"t8":["f1","auc","0.3","threshold","recall","precision","calibrat","astype"]}

def fallback(task_id,answer):
    low=answer.lower(); wc=len(answer.split())
    hits=sum(1 for k in KW.get(task_id,[]) if k in low)
    if wc<8: return "incorrect","Too brief.","What is the core concept here?"
    if hits>=3 and wc>=20: return "correct","You've covered the key ideas.",""
    if hits>=2 or wc>=35: return "partial",f"{hits} key concepts found.","What else is important?"
    return "incorrect","Missing core concepts.","What technical challenge does this step address?"

def grade(task,answer,hint_used):
    api_key=get_api_key()
    if api_key and api_key.startswith("sk-"):
        try: return call_claude(task["title"],task["question"],task["answer_guidance"],answer,hint_used,api_key)
        except: pass
    return fallback(task["id"],answer)

def render_fb(gv,fb,nudge,title):
    badge="<span class='ai-badge'>🤖 AI</span>" if (get_api_key() and get_api_key().startswith("sk-")) else "<span class='ai-badge'>⚡ Auto</span>"
    if gv=="correct":
        extra=f"\n\n<div class='box-blue'>💡 {nudge}</div>" if nudge else ""
        return f"<div class='box-green'>✅ {badge} <strong>Great work on {title}!</strong>\n{fb}{extra}</div>\n\nType <strong>next</strong> to continue 👉"
    elif gv=="partial":
        return f"<div class='box-yellow'>⚠️ {badge} <strong>On the right track!</strong>\n{fb}</div>\n\n<div class='box-blue'>💭 <strong>Think about:</strong> {nudge}</div>\n\nRevise or type <strong>hint</strong>."
    return f"<div class='box-red'>❌ {badge} <strong>Not quite yet.</strong>\n{fb}</div>\n\n<div class='box-blue'>💭 <strong>Guiding question:</strong> {nudge}</div>\n\nTry again or type <strong>hint</strong>."

def init():
    defs={"messages":[],"task_idx":0,"stage":"welcome","hint_count":0,"hint_used":False,"grades":{},"initialized":False,"awaiting_next":False,"pending_answer":None}
    for k,v in defs.items():
        if k not in st.session_state: st.session_state[k]=v
init()
def ai(t): st.session_state.messages.append({"role":"ai","content":t})
def usr(t): st.session_state.messages.append({"role":"user","content":t})

WELCOME="""🏥 <strong>Welcome to the LM10 AI Tutor!</strong>\n\nI'm your AI guide for <em>HI 780 — LM10: Predicting High Utilizers from Claims Data</em>.\n\n<div class='box-purple'><strong>📋 8 Steps:</strong>\n1️⃣ cum_days · 2️⃣ pred_time · 3️⃣ Label (≥50 claims) · 4️⃣ ELIX features\n5️⃣ Join features+labels · 6️⃣ Time-based split · 7️⃣ 3 models (balanced) · 8️⃣ F1/AUC+threshold</div>\n\n<div class='box-green'>✨ Add your Anthropic API key in the sidebar for full AI grading.</div>\n\nType <strong>hint</strong> anytime · Type <strong>next</strong> after correct\nClick <strong>Start</strong> 👇"""

if not st.session_state.initialized: ai(WELCOME); st.session_state.initialized=True

def present_task(idx):
    t=TASKS[idx]
    tag="<span class='tag-sql'>🗄️ SQL</span>" if "SQL" in t["intro"] else "<span class='tag-py'>🐍 Python</span>"
    if "+" in t["intro"] and "tag-concept" in t["intro"]: tag+="+<span class='tag-concept'>💬</span>"
    return f"{t['icon']} <strong>Step {idx+1}/8 — {t['title']}</strong>  <span class='tag-q'>{t['qnum']}</span>\n\n{t['intro']}\n\n<strong>❓ Question:</strong>\n{t['question']}"

NEXT_W={"next","continue","ready","go","yes","ok","sure","move on","proceed","got it","start","begin"}

def process_next():
    st.session_state.awaiting_next=False; st.session_state.hint_count=0; st.session_state.hint_used=False
    nxt=st.session_state.task_idx+1; st.session_state.task_idx=nxt
    if nxt>=len(TASKS):
        st.session_state.stage="done"; g=st.session_state.grades
        c=sum(1 for v in g.values() if v=="correct"); p=sum(1 for v in g.values() if v=="partial")
        score=int(((c+0.5*p)/len(TASKS))*100)
        icons={"correct":"✅","partial":"⚠️","incorrect":"❌","":"⬜"}
        rows="\n".join(f"{icons.get(g.get(t2['id'],''),'⬜')}  {t2['icon']} {t2['title']}" for t2 in TASKS)
        ai(f"🎓 <strong>LM10 Complete! Scorecard:</strong>\n\n{rows}\n\n<div class='box-green'><strong>Score: {c}/{len(TASKS)} — {score}%</strong></div>\n\n<strong>Recap:</strong>\n📅 cum_days=(year_num-1)*365+claim_days\n🎯 pred_time: hospitalization 365-730\n🏷️ Label: ≥50 claims in (pred_time, pred_time+180]\n🧬 Features: ELIX in [pred_time-180, pred_time)\n✂️ Time split — never random\n⚖️ class_weight='balanced'\n📊 F1+AUC · threshold 0.3 · calibration\n\nType <strong>restart</strong> to try again 🔄")
    else: ai(present_task(nxt))

def handle(raw):
    txt = raw.strip()
    if not txt:
        return
    low = txt.lower()
    if "restart" in low:
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    if st.session_state.stage == "welcome":
        usr(txt)
        st.session_state.stage = "task"
        ai(f"Let's begin! 🚀\n\n{present_task(0)}")
        return
    if st.session_state.stage == "done":
        usr(txt)
        ai("Complete! Type <strong>restart</strong> to try again.")
        return
    tidx = st.session_state.task_idx
    t = TASKS[tidx]
    if any(w in low for w in ["hint","help","stuck","confused","idk"]):
        usr(txt); st.session_state.hint_used=True; hc=st.session_state.hint_count
        ai(f"💡 <strong>Hint {hc+1} for {t['title']}:</strong>\n<div class='box-blue'>{t['hint']}</div>\nGive it another try 🧭"); st.session_state.hint_count=hc+1; return
    if any(w in low for w in NEXT_W) and st.session_state.awaiting_next:
        usr(txt); process_next(); return
    usr(txt); st.session_state.pending_answer=txt; ai("🤖 <em style='color:#7c3aed'>Grading...</em>")

def grade_pending():
    txt=st.session_state.pending_answer; tidx=st.session_state.task_idx; t=TASKS[tidx]
    msgs=st.session_state.messages
    if msgs and "Grading" in msgs[-1]["content"]: msgs.pop()
    gv,fb,nudge=grade(t,txt,st.session_state.hint_used)
    prev=st.session_state.grades.get(t["id"],"")
    if gv=="correct" or (gv=="partial" and prev!="correct"): st.session_state.grades[t["id"]]=gv
    feedback=render_fb(gv,fb,nudge,t["title"])
    if gv=="correct":
        st.session_state.awaiting_next=True
        nav=f"step {tidx+2}" if tidx+1<len(TASKS) else "final scorecard"
        feedback=feedback.replace("Type <strong>next</strong> to continue 👉",f"Type <strong>next</strong> for {nav} 👉")
    ai(feedback); st.session_state.pending_answer=None

if st.session_state.get("pending_answer"): grade_pending()

tidx=st.session_state.task_idx; total=len(TASKS)
pct=int((tidx/total)*100) if st.session_state.stage=="task" and tidx<total else (100 if st.session_state.stage=="done" else 0)
st.markdown(f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%"></div></div>',unsafe_allow_html=True)
label=(f"{TASKS[tidx]['icon']} {TASKS[tidx]['title']}" if st.session_state.stage=="task" and tidx<total else ("✅ Complete" if st.session_state.stage=="done" else "Ready"))
st.markdown(f'<div class="top-bar"><h2>🏥 LM10 AI Tutor &nbsp;·&nbsp; {label}</h2></div>',unsafe_allow_html=True)
st.markdown('<div class="chat-wrap">',unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"]=="ai": st.markdown(f'<div class="msg-ai"><div class="av">🎓</div><div class="bubble">{msg["content"]}</div></div>',unsafe_allow_html=True)
    else: st.markdown(f'<div class="msg-user"><div class="bubble">{msg["content"]}</div><div class="av">You</div></div>',unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)
s=st.session_state.stage; cols=st.columns([1,1,1,4])
if s=="welcome":
    with cols[0]:
        if st.button("🚀 Start"): handle("start"); st.rerun()
elif s=="task":
    with cols[0]:
        if st.button("💡 Hint"): handle("hint"); st.rerun()
    with cols[1]:
        if st.button("▶️ Next"): handle("next"); st.rerun()
elif s=="done":
    with cols[0]:
        if st.button("🔄 Restart"): handle("restart"); st.rerun()
inp=st.chat_input("Type your answer… (hint / next)")
if inp: handle(inp); st.rerun()
