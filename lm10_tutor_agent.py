import streamlit as st
import os

st.set_page_config(page_title="LM-10 Tutor", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #212121; color: #ececec; }
header[data-testid="stHeader"] { background: transparent; }
.chat-wrap { max-width: 840px; margin: 0 auto; padding: 0 1rem 160px 1rem; }
.msg-ai   { display:flex; justify-content:flex-start; margin:12px 0; gap:10px; align-items:flex-start; }
.msg-user { display:flex; justify-content:flex-end;   margin:12px 0; gap:10px; align-items:flex-start; }
.msg-ai .bubble {
    background:#2a2a2a; color:#ececec; padding:14px 18px;
    border-radius:18px 18px 18px 4px; max-width:92%;
    font-size:0.93rem; line-height:1.85; border:1px solid #3a3a3a; white-space:pre-wrap;
}
.msg-user .bubble {
    background:#2f2f2f; color:#ececec; padding:12px 16px;
    border-radius:18px 18px 4px 18px; max-width:80%;
    font-size:0.93rem; line-height:1.6; white-space:pre-wrap;
}
.msg-ai   .av { width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#ab68ff,#7c3aed);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;margin-top:2px; }
.msg-user .av { width:34px;height:34px;border-radius:50%;background:#19c37d;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;color:white;flex-shrink:0;margin-top:2px; }
.box-green  { background:#052e16;border-left:4px solid #4ade80;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#bbf7d0; }
.box-yellow { background:#1c1600;border-left:4px solid #fbbf24;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#fef08a; }
.box-red    { background:#1f0a0a;border-left:4px solid #f87171;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#fca5a5; }
.box-blue   { background:#0f1f2e;border-left:4px solid #38bdf8;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#bae6fd; }
.box-purple { background:#1a1a2e;border-left:4px solid #818cf8;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;color:#c7d2fe; }
.code-sql { background:#111;border-radius:8px;padding:10px 14px;margin:6px 0;font-family:'Courier New',monospace;font-size:0.83rem;color:#fde68a;display:block;border-left:3px solid #f59e0b;white-space:pre; }
.code-py  { background:#111;border-radius:8px;padding:10px 14px;margin:6px 0;font-family:'Courier New',monospace;font-size:0.83rem;color:#a7f3d0;display:block;border-left:3px solid #34d399;white-space:pre; }
.tag-sql { background:#f59e0b22;color:#fde68a;border:1px solid #f59e0b;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-right:4px; }
.tag-py  { background:#34d39922;color:#a7f3d0;border:1px solid #34d399;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-right:4px; }
.progress-bar-wrap { position:fixed;top:0;left:0;right:0;height:3px;z-index:9999;background:#333; }
.progress-bar-fill { height:100%;background:linear-gradient(90deg,#7c3aed,#19c37d);transition:width 0.5s; }
.top-bar { position:sticky;top:0;background:#212121;border-bottom:1px solid #333;padding:10px 0 8px;margin-bottom:6px;z-index:100; }
.top-bar h2 { text-align:center;font-size:0.9rem;font-weight:500;color:#aaa;margin:0; }
.stButton > button { background:#2a2a2a!important;color:#ececec!important;border:1px solid #444!important;border-radius:20px!important;font-size:0.82rem!important;padding:5px 14px!important;transition:all 0.15s!important; }
.stButton > button:hover { background:#3a3a3a!important;border-color:#7c3aed!important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TASK DEFINITIONS
# Each task has:
#   - intro: what the tutor explains before asking
#   - sub_steps: each micro-step has a question, Socratic nudges, code evaluation rules
# ═══════════════════════════════════════════════════════════════════════════════

TASKS = [
    {
        "id": "t1",
        "title": "Step 1 — Compute Cumulative Days",
        "icon": "📅",
        "intro": """Let's start at the very foundation of the pipeline.

<div class='box-purple'>
The <code>claims</code> table stores time as two columns:
• <strong>year</strong> — text like 'Y1', 'Y2', 'Y3' (study year)
• <strong>claim_days</strong> — integer day within that year (1–365)

To do any time-based filtering, we need a <strong>single unified number</strong> called <code>cum_days</code> that represents the overall day since study start.
</div>

For example:
• Year Y1, claim_day 100 → cum_days = <em>what?</em>
• Year Y2, claim_day 50  → cum_days = <em>what?</em>

Think about it before writing any code. What's the arithmetic?""",
        "sub_steps": [
            {
                "ask": "First — explain in plain English (no code yet): how would you convert year='Y2' and claim_days=50 into a single number?",
                "nudges": [
                    "Think of it like this: Y2 means you're in the 2nd year. How many days does that add to your baseline?",
                    "If Y1 starts at day 0 and each year has 365 days, what day does Y2 start on? Then add the claim_days within that year.",
                    "The formula involves: (year_number - 1) × 365. What do you get for Y2? Now add claim_days. Does that make sense?"
                ],
                "check_keywords": ["year","365","multiply","add","minus","subtract","number","convert","days"],
                "check_concept": "year number minus 1 times 365 plus claim_days",
            },
            {
                "ask": "Great! Now write the code.\n<span class='tag-sql'>SQL</span> Try the ALTER TABLE and UPDATE statement\n<span class='tag-py'>Python</span> Try adding a new column to the dataframe",
                "nudges": [
                    "SQL hint: You need to extract the digit from 'Y2'. Which SQL function lets you pull a character out of a string by position? Think SUBSTRING.",
                    "SQL hint: After extracting '2' from 'Y2', you need to cast it to an integer before doing math. What's the SQL function for that?",
                    "Python hint: If year = 'Y2', how do you get the digit '2' from a string in Python? Try indexing the string, then convert to int.",
                ],
                "check_keywords": ["substring","cast","int","alter","update","str","astype","365","year","cum_days"],
                "code_errors": {
                    "missing_cast": ("cast","You're extracting the year digit — but have you converted it from text to integer before multiplying? Text × number won't work in SQL."),
                    "missing_minus1": ("- 1","Remember: Y1 should give 0 extra days (year 1 = no extra years). Do you subtract 1 from the year number?"),
                    "missing_365": ("365","Where does the 365 come in? Each full year has 365 days."),
                    "py_no_int": ("astype(int)","Python tip: string indexing gives you a character, not a number. You need to convert it to int before arithmetic."),
                },
            }
        ]
    },
    {
        "id": "t2",
        "title": "Step 2 — Define the Prediction Time",
        "icon": "🎯",
        "intro": """Now that we have cum_days, we need to pick a <strong>prediction time</strong> for each patient — the moment in time from which we'll look backwards for features and forwards for the outcome.

<div class='box-purple'>
In this assignment, the prediction time is anchored to a <strong>hospitalization event</strong>.
• Hospitalization = plcsrvc = '20' AND valid length-of-stay (los ≠ '')
• We only keep hospitalizations where cum_days is between 365 and 730

Why 365–730? Think about what you need on BOTH sides of the prediction time...
</div>""",
        "sub_steps": [
            {
                "ask": "Why do we restrict prediction times to cum_days BETWEEN 365 and 730? What would go wrong if we allowed cum_days = 50 or cum_days = 900?",
                "nudges": [
                    "Think about what happens BEFORE the prediction time: we need 6 months of feature data. If pred_time = 50, do we have enough history?",
                    "Think about what happens AFTER the prediction time: we need 6 months to measure the outcome. If pred_time = 900 and the study ends at day 1095 (3 years), is there enough follow-up time?",
                    "The study has 3 years of data (days 1–1095). We need 180 days before AND 180 days after. So valid pred_times must be ≥ 180 and ≤ 1095-180 = 915. The assignment uses 365–730. Why might they be even more conservative?"
                ],
                "check_keywords": ["history","future","before","after","window","enough","data","lookback","follow"],
                "check_concept": "need data before and after prediction time",
            },
            {
                "ask": "Now write the code to:\n1. Filter claims to hospitalizations (plcsrvc='20', los not empty)\n2. Keep only those with cum_days between 365 and 730\n3. Call the result pred_time\n\n<span class='tag-sql'>SQL</span> or <span class='tag-py'>Python</span> — your choice!",
                "nudges": [
                    "SQL: Start with SELECT patient_id, cum_days as pred_time ... WHERE plcsrvc = ? AND los <> ?",
                    "SQL: After filtering for hospitalizations, add the cum_days filter. Which SQL operator checks if a value is between two numbers?",
                    "Python: Filter df using boolean indexing. You need two conditions: (df['plcsrvc']=='20') and (df['los']!='') and the cum_days range.",
                ],
                "check_keywords": ["plcsrvc","20","los","365","730","between","pred_time","where","filter"],
                "code_errors": {
                    "missing_los": ("los","Don't forget to filter for valid los (length-of-stay). What does an empty los string mean?"),
                    "missing_plcsrvc": ("plcsrvc","You need to filter for hospitalizations specifically. Which column identifies place of service?"),
                    "missing_range": ("365","The cum_days range filter is missing. When should the prediction time fall in the study timeline?"),
                },
            }
        ]
    },
    {
        "id": "t3",
        "title": "Step 3 — Build the Dependent Variable (Label)",
        "icon": "🏷️",
        "intro": """The dependent variable answers: <strong>is this patient a high utilizer?</strong>

<div class='box-purple'>
Definition: A patient is a <strong>high utilizer</strong> if they have <strong>50 or more claims</strong> in the <strong>6-month window AFTER their prediction time</strong>.

So for each patient + pred_time pair, we need to:
1. Find all claims where cum_days > pred_time AND cum_days ≤ pred_time + 180
2. Count them
3. Label: if count ≥ 50 → 1, else → 0
</div>""",
        "sub_steps": [
            {
                "ask": "Before coding — explain why we only look at claims AFTER the prediction time (not before or both). What are we actually trying to predict?",
                "nudges": [
                    "What is the purpose of a predictive model in healthcare? Are we trying to describe the past, or forecast the future?",
                    "If we included past claims in the label, would the label tell us anything useful for a healthcare manager trying to plan care?",
                    "The whole point is: given what we know UP TO pred_time, can we predict what happens in the NEXT 6 months? So the label must come from the future window."
                ],
                "check_keywords": ["future","predict","after","forecast","next","outcome","label","target"],
                "check_concept": "predicting future utilization from past data",
            },
            {
                "ask": "Now write the code to compute claim_count and high_utilizer (1/0) for each patient.\n\nRemember: future window = cum_days > pred_time AND cum_days ≤ pred_time + 180",
                "nudges": [
                    "SQL: You need to JOIN claims with the pred_time table on patient_id. Then filter claims to the future window. Then GROUP BY patient_id and use COUNT(*).",
                    "SQL: The binary label uses CASE WHEN count(*) >= 50 THEN 1 ELSE 0 END. Where in the query does a CASE WHEN on an aggregate go?",
                    "Python: After merging claims with pred_times, filter rows where cum_days is in the future window. Then use groupby('patient_id').size() and np.where(count >= 50, 1, 0).",
                ],
                "check_keywords": ["count","50","group","join","merge","case when","future","180","pred_time","high_utilizer","label"],
                "code_errors": {
                    "missing_50": ("50","What is the threshold for being a high utilizer? Make sure your CASE WHEN or np.where uses the right cutoff."),
                    "missing_180": ("180","The outcome window is 6 months = 180 days. Is your future window filter using + 180?"),
                    "missing_group": ("group","You need to count claims PER PATIENT. Which SQL clause or pandas method aggregates by patient?"),
                    "wrong_direction": ("pred_time","Make sure you're looking FORWARD from pred_time (cum_days > pred_time), not backward."),
                },
            }
        ]
    },
    {
        "id": "t4",
        "title": "Step 4 — Build Independent Variables (Elixhauser Features)",
        "icon": "🧬",
        "intro": """Now we need features — the input to our model. The assignment uses <strong>Elixhauser comorbidity flags</strong>.

<div class='box-purple'>
Elixhauser comorbidities are 29 standardized disease categories (ELIX1–ELIX29).
For each patient, we create a binary flag: did they have this diagnosis in the 6 months BEFORE pred_time?

• Lookback window: cum_days >= pred_time - 180  AND  cum_days < pred_time
• Output: one row per patient with 29 columns (0 or 1 each)

This transforms a LONG table (many rows per patient) into a WIDE table (one row per patient).
</div>""",
        "sub_steps": [
            {
                "ask": "The diagnoses table has one row per diagnosis per claim. We want one row per patient with 29 binary columns. What SQL technique or Python method does this transformation (long → wide)?",
                "nudges": [
                    "In SQL, when you want to turn row values into column names, what operation is that called? Think about reshaping data...",
                    "SQL hint: We can simulate a PIVOT using MAX(CASE WHEN diagnosis = 'ELIX1' THEN 1 ELSE 0 END). Why does MAX work here? What are the possible values of that CASE WHEN expression?",
                    "Python hint: Look up pd.get_dummies() or pd.pivot_table(). Which one creates binary indicator columns from a categorical column?"
                ],
                "check_keywords": ["pivot","case when","max","get_dummies","wide","binary","indicator","reshape","transpose","one-hot"],
                "check_concept": "pivot or get_dummies to go from long to wide format",
            },
            {
                "ask": "Now write the code. Include:\n1. Join diagnoses + claims + pred_time table\n2. Filter to the lookback window (6 months before pred_time)\n3. Create binary ELIX columns\n4. Group by patient_id",
                "nudges": [
                    "SQL: Your FROM clause needs three tables: diagnoses, claims, and #pat2. Join them on claim_id (diagnoses↔claims) and patient_id (claims↔#pat2).",
                    "SQL: The lookback window filter is: c.cum_days < p.pred_time AND c.cum_days >= p.pred_time - 180. Have you included both sides of this window?",
                    "Python: After merging and filtering to the lookback window, use pd.get_dummies(df['diagnosis']).groupby(df['patient_id']).max() to create the binary features.",
                ],
                "check_keywords": ["join","merge","diagnosis","pred_time","180","group","max","elix","lookback","before","cum_days"],
                "code_errors": {
                    "missing_lookback_end": ("pred_time - 180","You have one side of the lookback window. Remember it needs BOTH: cum_days < pred_time AND cum_days >= pred_time - 180."),
                    "missing_join": ("claim_id","The diagnoses table links to claims via claim_id. Make sure you're joining on the right key."),
                    "missing_group": ("group","After pivoting, you still need to GROUP BY patient_id. Otherwise you get one row per claim, not per patient."),
                    "missing_max": ("max","When using CASE WHEN for the pivot, use MAX() — a patient either had the diagnosis (1) or not (0) during the period."),
                },
            }
        ]
    },
    {
        "id": "t5",
        "title": "Step 5 — Join Features + Labels → Final Dataset",
        "icon": "🔗",
        "intro": """We now have two tables:
• <strong>#Elix</strong> — feature matrix (ELIX flags, one row per patient+pred_time)
• <strong>#dep</strong>  — labels (claim_count + high_utilizer, one row per patient+pred_time)

We need to join them into the final <strong>testClaims</strong> analytic dataset.

<div class='box-purple'>
Key decision: what type of JOIN do you use, and on what columns?
Some patients may be in #Elix but not #dep (no future claims), or vice versa.
Think carefully about which patients you want to keep.
</div>""",
        "sub_steps": [
            {
                "ask": "Should you use INNER JOIN, LEFT JOIN, or OUTER JOIN here? What happens to patients who appear in one table but not the other? Explain your reasoning.",
                "nudges": [
                    "If a patient has ELIX features but no future claims, do they belong in your training dataset? What does 'no future claims' mean for the label?",
                    "An INNER JOIN keeps only patients who appear in BOTH tables. A LEFT JOIN keeps all patients from the left table even if no match in the right. Which gives you cleaner training data?",
                    "Think about it this way: if a patient has no future claims record in #dep, you literally don't know their label. Can you train a model on rows with unknown labels?"
                ],
                "check_keywords": ["inner","both","label","unknown","clean","keep","match","join type"],
                "check_concept": "inner join because you need both features and labels",
            },
            {
                "ask": "Write the JOIN code. Make sure you join on BOTH patient_id AND pred_time — why do you need both columns in the join condition?",
                "nudges": [
                    "A patient can have MULTIPLE prediction times (multiple hospitalizations). If you join only on patient_id, what could go wrong?",
                    "SQL: SELECT e.*, d.claim_count, d.high_utilizer FROM #Elix e ... #dep d ON e.patient_id = d.patient_id AND ...",
                    "Python: use df.merge(dep_df, on=['patient_id', 'pred_time'], how=?). Fill in the how parameter based on your answer above.",
                ],
                "check_keywords": ["patient_id","pred_time","both","inner","merge","join","and"],
                "code_errors": {
                    "missing_pred_time": ("pred_time","You're joining on patient_id — but a patient can have multiple pred_times! You must also join on pred_time to avoid row explosion."),
                    "wrong_join": ("left","A LEFT JOIN keeps unmatched rows from the left table — but those rows have no label. Is that what you want for a training dataset?"),
                    "missing_patient_id": ("patient_id","You need patient_id in your join condition to match rows across the two tables."),
                },
            }
        ]
    },
    {
        "id": "t6",
        "title": "Step 6 — Train/Test Split (Time-Based)",
        "icon": "✂️",
        "intro": """Before modeling, we split our data into train and test sets.

<div class='box-purple'>
⚠️ In healthcare data, you must NEVER split randomly!
The data is temporal — patients have claims across time.
A random split would put a patient's FUTURE data in training and PAST data in testing.
This is called <strong>data leakage</strong> and makes your model look better than it really is.
</div>

The correct approach: sort by pred_time and split chronologically.""",
        "sub_steps": [
            {
                "ask": "Explain in your own words: what is data leakage, and why does a random train/test split cause it in this claims dataset?",
                "nudges": [
                    "Imagine patient #123 has records from year 1 and year 2. If split randomly, year 2 data might be in the training set. What does the model learn from that?",
                    "When you deploy this model in real life, you'll only ever have PAST data to predict the FUTURE. If the model was trained on future data, it's cheating.",
                    "Data leakage = the model has access to information during training that it won't have at prediction time. This inflates your evaluation metrics artificially."
                ],
                "check_keywords": ["future","past","leak","cheat","inflate","random","temporal","time","deploy","real"],
                "check_concept": "random split lets future data train the model which is cheating",
            },
            {
                "ask": "Write the code to do a time-based split: sort by pred_time, use the first 80% as train and the last 20% as test.",
                "nudges": [
                    "Python: First sort the dataframe by pred_time. Then calculate the split index: int(len(df) * 0.8). Then slice.",
                    "SQL: Use ORDER BY pred_time to sort. You can use ROW_NUMBER() OVER (ORDER BY pred_time) and keep rows where row_num <= 80% of total count.",
                    "Python: After sorting, use df.iloc[:split_idx] for train and df.iloc[split_idx:] for test. Make sure you sorted FIRST."
                ],
                "check_keywords": ["sort","pred_time","80","0.8","iloc","order by","row_number","chronological","split"],
                "code_errors": {
                    "missing_sort": ("sort","Have you sorted by pred_time BEFORE splitting? If not, your iloc split is still effectively random."),
                    "wrong_pct": ("0.8","The split should be 80/20. Check your split index calculation."),
                    "missing_iloc": ("iloc","After calculating the split index, use iloc to slice the sorted dataframe into train and test portions."),
                },
            }
        ]
    },
    {
        "id": "t7",
        "title": "Step 7 — Train 3 Classification Models",
        "icon": "🤖",
        "intro": """Now the modeling! We train three classifiers from sklearn:
1. Logistic Regression (with feature scaling)
2. Decision Tree
3. Random Forest

<div class='box-purple'>
⚠️ Important: high utilizers are a MINORITY of patients (maybe 10–15%).
This is called <strong>class imbalance</strong>. Without handling it, models just predict "not high utilizer" for everyone and get 90% accuracy — but catch ZERO high utilizers!

All three models should use <code>class_weight='balanced'</code>.
</div>""",
        "sub_steps": [
            {
                "ask": "Why does Logistic Regression need a StandardScaler but Decision Tree and Random Forest do NOT? What property of these algorithms makes scaling matter (or not)?",
                "nudges": [
                    "Think about how Logistic Regression makes predictions — it multiplies features by coefficients and sums them. What happens if one feature is 0–1 and another is 0–100000?",
                    "Decision Trees split on individual feature thresholds (e.g., ELIX3 > 0.5). Does the absolute scale of the feature change where the split happens?",
                    "Logistic Regression uses gradient descent to find coefficients. Large-scale features dominate the gradient. Scaling puts all features on equal footing."
                ],
                "check_keywords": ["scale","gradient","coefficient","tree","split","threshold","magnitude","range","distance"],
                "check_concept": "logistic regression uses gradients so scale matters, trees use splits so scale doesn't matter",
            },
            {
                "ask": "Write the code for all 3 models. For Logistic Regression use a Pipeline with StandardScaler. All models should handle class imbalance.",
                "nudges": [
                    "Python: from sklearn.pipeline import Pipeline; from sklearn.preprocessing import StandardScaler. Build lr_pipeline = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(...))])",
                    "Don't forget class_weight='balanced' in ALL three models. What happens if you forget it for just one model — will your comparison be fair?",
                    "For Random Forest: n_estimators=100 is a good default. Add random_state=42 for reproducibility. What does n_jobs=-1 do?"
                ],
                "check_keywords": ["pipeline","standardscaler","class_weight","balanced","logisticregression","decisiontree","randomforest","fit","n_estimators"],
                "code_errors": {
                    "missing_pipeline": ("Pipeline","Logistic Regression needs feature scaling. Wrap it in a Pipeline with StandardScaler so scaling is applied consistently to both train and test."),
                    "missing_balanced": ("balanced","class_weight='balanced' is missing from one or more models. Without it, the model will ignore the minority class."),
                    "missing_fit": ("fit","Have you called .fit(X_train, y_train) on each model? Defining the model object doesn't train it."),
                    "no_random_state": ("random_state","Add random_state=42 for reproducibility — so you get the same results every run."),
                },
            }
        ]
    },
    {
        "id": "t8",
        "title": "Step 8 — Evaluate: F1 Score and AUC-ROC",
        "icon": "📊",
        "intro": """With 3 trained models, we need to compare them. For imbalanced classification, we use two metrics:

<div class='box-purple'>
• <strong>F1 Score</strong> — balances Precision (are our predictions correct?) and Recall (do we catch all high utilizers?)
• <strong>AUC-ROC</strong> — measures how well the model <em>ranks</em> high utilizers above non-utilizers across all thresholds

❌ Do NOT use plain Accuracy — if 90% are non-high-utilizers, predicting 0 for everyone gives 90% accuracy but F1 = 0.
</div>""",
        "sub_steps": [
            {
                "ask": "A model predicts 0 (not high utilizer) for every single patient. What is its Accuracy, F1 Score, and AUC? Explain why Accuracy is misleading here.",
                "nudges": [
                    "If 90% of patients are NOT high utilizers, and the model always predicts 0, how many predictions are correct? That's accuracy.",
                    "For F1: Recall = true positives / (true positives + false negatives). If the model never predicts 1, how many true positives does it get? What does that make F1?",
                    "For AUC: A model that always predicts the same score can't rank patients. It gets AUC = 0.5 (random chance). So AUC reveals what Accuracy hides."
                ],
                "check_keywords": ["90","0","f1","auc","0.5","precision","recall","zero","misleading","imbalance","always"],
                "check_concept": "accuracy 90% but F1=0 and AUC=0.5 showing accuracy is useless here",
            },
            {
                "ask": "Write the code to evaluate all 3 models and display a comparison table with F1 and AUC for each.\n\nNote: AUC needs predicted PROBABILITIES (predict_proba), not just class labels.",
                "nudges": [
                    "Python: from sklearn.metrics import f1_score, roc_auc_score. For class labels: model.predict(X_test). For probabilities: model.predict_proba(X_test)[:, 1]",
                    "The [:, 1] when calling predict_proba selects the probability of class 1 (high utilizer). Why do we want the probability of class 1 specifically?",
                    "Build a results DataFrame with pd.DataFrame({'Model': [...], 'F1': [...], 'AUC': [...]}) and sort by F1 Score descending."
                ],
                "check_keywords": ["f1_score","roc_auc_score","predict_proba","[:, 1]","dataframe","compare","sort","f1","auc"],
                "code_errors": {
                    "using_predict_for_auc": ("predict_proba","AUC-ROC requires predicted probabilities, not class labels. Use model.predict_proba(X_test)[:, 1] for AUC."),
                    "missing_col1": ("[:, 1]","predict_proba returns probabilities for BOTH classes [class_0_prob, class_1_prob]. You want [:, 1] to get the probability of being a high utilizer."),
                    "missing_import": ("roc_auc_score","Make sure you import both f1_score and roc_auc_score from sklearn.metrics."),
                },
            }
        ]
    },
    {
        "id": "t9",
        "title": "Step 9 — Threshold Tuning & Calibration",
        "icon": "🎛️",
        "intro": """Our models predict a probability (e.g. 0.35). To get a class label (0 or 1), we apply a threshold. The default is 0.5 — but that's rarely optimal for imbalanced data.

<div class='box-purple'>
<strong>Threshold tuning:</strong> try thresholds from 0.2 to 0.4 and pick the one that maximizes F1.
Lowering the threshold → catch MORE high utilizers (higher recall) but MORE false alarms (lower precision).

<strong>Calibration:</strong> ensures predicted probabilities are trustworthy.
If the model says "70% probability", it should be right ~70% of the time.
Without calibration, probabilities can be systematically too high or too low.
</div>""",
        "sub_steps": [
            {
                "ask": "The default threshold is 0.5. If we lower it to 0.3, what happens to:\n• The number of patients flagged as high utilizers\n• Precision (% of flagged patients who are truly high utilizers)\n• Recall (% of true high utilizers we catch)\n• F1 Score\n\nExplain the trade-off.",
                "nudges": [
                    "Imagine patients with probabilities: [0.45, 0.38, 0.29, 0.52, 0.31]. How many are flagged at threshold=0.5? How many at threshold=0.3?",
                    "When you flag MORE patients, you catch more true high utilizers (recall goes up). But you also flag more healthy patients incorrectly. What does that do to precision?",
                    "F1 = 2 * precision * recall / (precision + recall). If recall increases but precision falls, does F1 go up, down, or it depends?"
                ],
                "check_keywords": ["recall","precision","trade","flag","more","fewer","lower","higher","0.3","threshold","f1"],
                "check_concept": "lower threshold raises recall lowers precision trade-off",
            },
            {
                "ask": "Write the code to:\n1. Try thresholds from 0.2 to 0.5 (step 0.05) and compute F1 for each\n2. Pick the best threshold\n3. Apply it to make final predictions\n\nAlso explain in 1–2 sentences what calibration is and why it matters.",
                "nudges": [
                    "Python: Use a loop — for threshold in np.arange(0.2, 0.5, 0.05): y_pred_tuned = (y_prob >= threshold).astype(int); print(f1_score(y_test, y_pred_tuned))",
                    "To find the best threshold: collect all F1 scores in a list, use np.argmax() to find the index of the highest, then map back to the threshold value.",
                    "Calibration: use CalibratedClassifierCV from sklearn.calibration. It wraps any model and adjusts its probabilities using either 'sigmoid' (Platt scaling) or 'isotonic' regression."
                ],
                "check_keywords": ["threshold","arange","loop","astype","f1_score","calibrat","sigmoid","isotonic","best","argmax","np.where"],
                "code_errors": {
                    "missing_astype": ("astype(int)","After applying the threshold (y_prob >= threshold), you get a boolean array. Convert it to 0/1 integers with .astype(int) before passing to f1_score."),
                    "missing_loop": ("for","To compare thresholds, you need to loop over them. Try: for threshold in np.arange(0.2, 0.5, 0.05)"),
                    "no_calibration_explanation": ("calibrat","Don't forget to explain calibration! A model's probabilities should reflect real-world frequencies — that's what calibration ensures."),
                },
            }
        ]
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATOR — analyses student code/text, returns feedback WITHOUT giving answer
# ═══════════════════════════════════════════════════════════════════════════════
def evaluate(task, sub_step_idx, student_answer, lang, attempt):
    """Returns (quality, feedback_html) where quality in: correct|partial|rethink"""
    sub = task["sub_steps"][sub_step_idx]
    low = student_answer.lower()
    is_code = any(c in student_answer for c in ["(","SELECT","FROM","WHERE","def ","import ","df[","="])

    # Count keyword hits
    hits = sum(1 for kw in sub["check_keywords"] if kw.lower() in low)
    total_kw = len(sub["check_keywords"])

    # Check for code-specific errors if code was submitted
    errors_found = []
    if is_code and "code_errors" in sub:
        for err_key, (pattern, msg) in sub["code_errors"].items():
            if pattern.lower() not in low:
                errors_found.append(msg)

    # Decide quality
    if hits >= max(3, int(total_kw * 0.5)) and len(errors_found) == 0:
        quality = "correct"
    elif hits >= 2 or (is_code and len(errors_found) <= 1):
        quality = "partial"
    else:
        quality = "rethink"

    # Build feedback
    tag = f"<span class='tag-sql'>SQL</span>" if lang == "SQL" else f"<span class='tag-py'>Python</span>"

    if quality == "correct":
        fb = f"""<div class='box-green'>
✅ <strong>Well done!</strong> You've captured the key idea here.
</div>

"""
        if is_code and not errors_found:
            fb += "Your code logic looks solid. "
        fb += "\nReady to move to the next part? Type <strong>next</strong> 👉"

    elif quality == "partial":
        fb = f"""<div class='box-yellow'>
⚠️ <strong>You're on the right track!</strong> You've got part of the answer, but let's sharpen it.
</div>

"""
        # Point out what's missing without giving the answer
        nudge_idx = min(attempt, len(sub["nudges"]) - 1)
        fb += f"""Think about this 👇
<div class='box-blue'>
{sub["nudges"][nudge_idx]}
</div>

"""
        if errors_found:
            fb += "Also check these issues in your code:\n"
            for i, err in enumerate(errors_found[:2]):
                fb += f"\n🔍 Issue {i+1}: {err}"
        fb += "\n\nTry refining your answer!"

    else:  # rethink
        fb = f"""<div class='box-red'>
❌ <strong>Not quite yet.</strong> Let's approach this differently.
</div>

"""
        fb += f"""Here's a question to guide your thinking 👇
<div class='box-blue'>
{sub["nudges"][0]}
</div>

Don't worry — think it through step by step and try again. Or type <strong>hint</strong> for another nudge."""

    return quality, fb


def give_hint(task, sub_step_idx, hint_count):
    sub = task["sub_steps"][sub_step_idx]
    idx = min(hint_count, len(sub["nudges"]) - 1)
    return f"""💡 <strong>Hint {idx + 1}:</strong>
<div class='box-blue'>
{sub["nudges"][idx]}
</div>

Give it another try! The goal is for YOU to figure it out — I'm just pointing the way 🧭"""


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
def init():
    defs = {
        "messages": [], "task_idx": 0, "sub_idx": 0,
        "stage": "welcome", "lang": "Python",
        "hint_count": 0, "attempt": 0,
        "grades": {}, "initialized": False, "awaiting_next": False,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

def ai(t):  st.session_state.messages.append({"role": "ai",   "content": t})
def usr(t): st.session_state.messages.append({"role": "user", "content": t})


# ── Welcome ───────────────────────────────────────────────────────────────────
WELCOME = """🏥 <strong>Welcome to the LM-10 Assignment Tutor!</strong>

I'm your AI guide for <em>HI 780 — LM-10: Predicting High Utilizers from Claims Data</em>.

<div class='box-purple'>
<strong>📋 The Assignment Goal:</strong>
Prepare the <code>testClaims</code> dataset and build models to predict which patients will have <strong>50+ claims in the 6 months AFTER a prediction time</strong>, using 6 months of prior history as features.
</div>

<strong>How I work:</strong>
🔹 I guide you through <strong>9 steps</strong> of the full pipeline
🔹 Each step has concept questions + coding tasks
🔹 I will <strong>evaluate your answers and code</strong>, point out specific errors, and ask follow-up questions
🔹 I will <strong>NEVER give you the answer directly</strong> — I'll ask questions and give hints until you figure it out
🔹 Type <strong>hint</strong> anytime if you're stuck

<strong>Which language do you prefer?</strong>
<span class='tag-sql'>SQL</span> (T-SQL)   or   <span class='tag-py'>Python</span> (pandas / sklearn)

Click a button below or just type your preference!"""

if not st.session_state.initialized:
    ai(WELCOME)
    st.session_state.initialized = True


# ── Present a task/sub-step ───────────────────────────────────────────────────
def present_current():
    t   = TASKS[st.session_state.task_idx]
    si  = st.session_state.sub_idx
    sub = t["sub_steps"][si]
    tag = f"<span class='tag-sql'>SQL</span>" if st.session_state.lang == "SQL" else f"<span class='tag-py'>Python</span>"

    if si == 0:
        # First sub-step: show task intro + first question
        return f"""{t['icon']} <strong>{t['title']}</strong>  {tag}

{t['intro']}

<strong>❓ Question {si+1}:</strong>
{sub['ask']}"""
    else:
        return f"""<strong>❓ Now for the code:</strong>  {tag}

{sub['ask']}"""


# ═══════════════════════════════════════════════════════════════════════════════
# HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
NEXT_W = {"next","continue","ready","go","yes","ok","sure","move on","proceed","got it"}

def handle(raw):
    txt = raw.strip()
    if not txt: return
    usr(txt)
    low = txt.lower()

    # Restart
    if "restart" in low:
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    # Language switch
    if "switch to sql" in low or ("sql" in low and st.session_state.stage == "welcome"):
        st.session_state.lang = "SQL"
        if st.session_state.stage == "welcome":
            st.session_state.stage = "task"
            ai(f"<span class='tag-sql'>SQL</span> mode activated! Let's begin.\n\n{present_current()}")
        else:
            ai("✅ Switched to <span class='tag-sql'>SQL</span> mode!")
        return

    if "switch to python" in low or ("python" in low and st.session_state.stage == "welcome"):
        st.session_state.lang = "Python"
        if st.session_state.stage == "welcome":
            st.session_state.stage = "task"
            ai(f"<span class='tag-py'>Python</span> mode activated! Let's begin.\n\n{present_current()}")
        else:
            ai("✅ Switched to <span class='tag-py'>Python</span> mode!")
        return

    # Welcome fallback
    if st.session_state.stage == "welcome":
        st.session_state.lang = "Python"
        st.session_state.stage = "task"
        ai(f"<span class='tag-py'>Python</span> mode activated! Let's begin.\n\n{present_current()}")
        return

    # Done stage
    if st.session_state.stage == "done":
        ai("You've completed the full LM-10 pipeline! 🎉 Type <strong>restart</strong> to go again, or ask me anything about the assignment.")
        return

    # ── Task stage ─────────────────────────────────────────────────────────
    t   = TASKS[st.session_state.task_idx]
    si  = st.session_state.sub_idx

    # Hint request
    if any(w in low for w in ["hint","help","stuck","confused","don't know","no idea","idk"]):
        hc = st.session_state.hint_count
        ai(give_hint(t, si, hc))
        st.session_state.hint_count = hc + 1
        return

    # Next navigation
    if any(w in low for w in NEXT_W) and st.session_state.awaiting_next:
        st.session_state.awaiting_next = False
        st.session_state.hint_count = 0
        st.session_state.attempt = 0

        # Advance sub-step or task
        if si + 1 < len(t["sub_steps"]):
            st.session_state.sub_idx = si + 1
            ai(present_current())
        else:
            # Move to next task
            next_task_idx = st.session_state.task_idx + 1
            st.session_state.sub_idx = 0
            st.session_state.task_idx = next_task_idx

            if next_task_idx >= len(TASKS):
                # Final scorecard
                st.session_state.stage = "done"
                g = st.session_state.grades
                correct_n = sum(1 for v in g.values() if v == "correct")
                partial_n = sum(1 for v in g.values() if v == "partial")
                score_pct = int(((correct_n + 0.5 * partial_n) / len(TASKS)) * 100)
                icons = {"correct": "✅", "partial": "⚠️", "rethink": "🔄", "": "⬜"}
                rows = "\n".join([
                    f"{icons.get(g.get(t2['id'], ''), '⬜')}  Step {i+1}: {t2['title']}"
                    for i, t2 in enumerate(TASKS)
                ])
                ai(f"""🎓 <strong>LM-10 Pipeline Complete! Your Scorecard:</strong>

{rows}

<div class='box-green'>
<strong>Score: {correct_n}/{len(TASKS)} fully correct — {score_pct}%</strong>
{'🌟 Excellent mastery of the full pipeline!' if score_pct >= 85 else
 '🎉 Great work! Go back and review any ⚠️ steps to strengthen your understanding.' if score_pct >= 55 else
 '💪 Keep at it! Re-read each step explanation and practice the code.'}
</div>

<strong>Full Pipeline Recap:</strong>
1️⃣ cum_days → 2️⃣ pred_time → 3️⃣ Labels → 4️⃣ ELIX features → 5️⃣ Join → 6️⃣ Time split → 7️⃣ 3 Models → 8️⃣ F1/AUC → 9️⃣ Threshold + Calibration

Type <strong>restart</strong> to try again! 🔄""")
            else:
                ai(present_current())
        return

    # ── Evaluate student answer ─────────────────────────────────────────────
    quality, fb = evaluate(t, si, txt, st.session_state.lang, st.session_state.attempt)

    # Store best grade per task (keep "correct" if already achieved)
    prev = st.session_state.grades.get(t["id"], "")
    if quality == "correct" or (quality == "partial" and prev != "correct"):
        st.session_state.grades[t["id"]] = quality

    st.session_state.attempt += 1

    if quality == "correct":
        st.session_state.awaiting_next = True
        total_sub = len(t["sub_steps"])
        if si + 1 < total_sub:
            ai(fb + f"\n\nType <strong>next</strong> to move to the coding part of this step 👉")
        else:
            ai(fb + f"\n\nType <strong>next</strong> for Step {st.session_state.task_idx + 2} 👉")
    else:
        ai(fb)


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════
task_idx = st.session_state.task_idx
total_tasks = len(TASKS)
pct = int((task_idx / total_tasks) * 100) if st.session_state.stage == "task" else (100 if st.session_state.stage == "done" else 0)

st.markdown(f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

step_label = (
    f"Step {task_idx + 1} of {total_tasks} — {TASKS[task_idx]['title']}"
    if st.session_state.stage == "task" and task_idx < total_tasks
    else ("✅ Complete" if st.session_state.stage == "done" else "Choose your language")
)
lang_tag = f"<span class='tag-sql'>SQL</span>" if st.session_state.lang == "SQL" else f"<span class='tag-py'>Python</span>"
st.markdown(f'<div class="top-bar"><h2>🏥 LM-10 Tutor Agent &nbsp;·&nbsp; {step_label} &nbsp;·&nbsp; {lang_tag}</h2></div>', unsafe_allow_html=True)

# Messages
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role = msg["role"]
    bubble = msg["content"]
    if role == "ai":
        st.markdown(f'<div class="msg-ai"><div class="av">🎓</div><div class="bubble">{bubble}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-user"><div class="bubble">{bubble}</div><div class="av">You</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Quick buttons
s = st.session_state.stage
cols = st.columns([1, 1, 1, 1, 4])
if s == "welcome":
    with cols[0]:
        if st.button("🐍 Python"):   handle("python");       st.rerun()
    with cols[1]:
        if st.button("🗄️ SQL"):     handle("sql");           st.rerun()
elif s == "task":
    with cols[0]:
        if st.button("💡 Hint"):     handle("hint");          st.rerun()
    with cols[1]:
        if st.button("▶️ Next"):     handle("next");          st.rerun()
    with cols[2]:
        if st.button("🐍 Python"):   handle("switch to python"); st.rerun()
    with cols[3]:
        if st.button("🗄️ SQL"):     handle("switch to sql"); st.rerun()
elif s == "done":
    with cols[0]:
        if st.button("🔄 Restart"):  handle("restart");       st.rerun()

# Chat input
inp = st.chat_input("Type your answer or code here… (type 'hint' if stuck)")
if inp:
    handle(inp)
    st.rerun()
