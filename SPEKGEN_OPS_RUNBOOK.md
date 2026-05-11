# SpekGen Morning Intelligence — Operations Runbook

## What is the Morning Intelligence System?

**Purpose:** Daily 8 AM team briefing on project delivery status + auto-escalation of blocked projects.

**Duration:** ~10-15 seconds to run and deliver memo to entire team.

**Components:**
- Master Registry Sheet (single source of truth for all client metadata)
- Python script (pulls ClickUp tasks, classifies project health, generates memo)
- GitHub Actions (executes script daily at 8 AM UTC-6)
- ClickUp integration (auto-creates escalation tasks for Red/Yellow projects)
- Drive logging dashboard (historical tracking of memo runs)

---

## How to Interpret the Memo

### SECTION 1: THE FRONTLINE (10-second pulse)
```
## 🟢 OPERATIONAL
**VELOCITY:** 88%
```
- **What it means:** Team is healthy. No action required for Green projects.
- **What to do:** Scan direct orders (Section 3) for any yellow/red items.

```
## 🟡 CAUTION (1 projects slowing)
**VELOCITY:** 82%
```
- **What it means:** One project is Yellow (80–85% on-time). Needs monitoring but not critical.
- **What to do:** Check Section 2 for which project, read the War Room.

```
## 🔴 AT RISK (2 projects bleeding)
**VELOCITY:** 71%
```
- **What it means:** Projects are Red (< 80% on-time, or 3+ overdue tasks). Immediate action required.
- **What to do:** Read Section 2 + Section 3. Assign owners to Direct Orders.

---

### SECTION 2: CASUALTIES & BLOCKERS
```
🔴 F24 — Pedro
- **Status:** 65% on time
- **Blockers:** Waiting on Sergio for photos. Payment gateway down.
- **Overdue:** 4 tasks
```
- **Red = War Room:** Tells you exact problems + how many overdue tasks.
- **Yellow = Monitor:** Still operational but trending downward.
- **Green = Omitted:** Doesn't appear in memo (one line in Section 1 only).

---

### SECTION 3: DIRECT ORDERS
```
@Pedro: **RESOLVE** — Photos from Sergio (due 5 PM)
@Gibran: **RESOLVE** — Payment gateway debug (priority HIGH)
```
- **Format:** `@PERSON: **ACTION** — TASK`
- **Owner accountability:** These are auto-generated from ClickUp blockers.
- **No fluff:** Just the action, the person, and the blocker they must resolve.

---

### GREEN PROJECTS (No War Room)
```
## OPERATIONAL (No action required)
HC, GR, LF
```
- **Meaning:** All Green projects summarized in one line.
- **Your job:** Move on. No action needed for these.

---

## Troubleshooting

### "No memo appeared at 8 AM"

**Step 1: Check GitHub Actions**
1. Go to: `https://github.com/{your-repo}/actions`
2. Look for `SpekGen Morning Intelligence` workflow
3. Click the most recent run
4. Check if it **passed** ✅ or **failed** ❌

**Step 2: If failed, read the logs**
- Click the failed run
- Go to "Run SpekGen Morning Intelligence" step
- Read error message

**Common errors:**
- `secrets not found` → GitHub Secrets not configured (Section 4 below)
- `Master Registry Sheet not found` → Wrong sheet ID in secrets
- `ClickUp API Error` → Token expired or list IDs are wrong

**Step 3: If GitHub Actions looks OK, check Drive**
- Open: `SPK-14. LOGS/MORNING_INTELLIGENCE/`
- Look for today's memo file
- If it's there, script worked. (Check Slack/email delivery instead.)

---

### "Memo shows wrong data / missing a client"

**Step 1: Verify Master Registry Sheet**
1. Open: `SPEKGEN - CLIENT REGISTRY`
2. Check that row exists for that client
3. Verify: `Client_Code` | `ClickUp_List_ID` | `Google_Sheet_ID` are correct
4. Save changes if you edited anything

**Step 2: Verify ClickUp list has tasks**
1. Open ClickUp
2. Go to that client's list
3. Check if tasks exist (script won't show tasks if list is empty)

**Step 3: Run locally with --dry-run to debug**
```bash
python spekgen_morning_intelligence.py --dry-run
```
- Memo appears on stdout (not saved to Drive)
- Shows any API errors or missing data
- Use this to verify before running live

---

### "Memo is slow (> 30 seconds)"

**Likely cause:** Pagination issue or too many tasks.

**Check:**
1. Are any clients showing 100+ open + closed tasks?
2. Run: `python spekgen_morning_intelligence.py --dry-run` and time it
3. If local is fast but GitHub Actions is slow → GitHub Actions runner is busy (normal)

**Fix:**
- Reduce `max_workers=4` in script if rate-limited
- Archive old closed tasks in ClickUp (keeps pagination efficient)

---

### "ClickUp auto-escalation tasks aren't being created"

**Step 1: Verify ClickUp token**
- GitHub Secrets → check `CLICKUP_TOKEN` value is correct
- Token should start: `pk_xxx...`

**Step 2: Verify list ID in Master Registry**
- Paste list ID into ClickUp URL: `https://app.clickup.com/api/v2/list/{LIST_ID}/task`
- You should see a response (not 404)

**Step 3: Manual test**
```bash
python spekgen_morning_intelligence.py --dry-run
```
- Creates mock escalation (logs to stdout, doesn't actually create)
- Shows if function is being called

---

## Adding a New Client (Zero Code Changes)

**Example: Adding Vibra Farmacia with 10 locations**

### Step 1: Open Master Registry Sheet
- URL: `https://docs.google.com/spreadsheets/d/{MASTER_REGISTRY_SHEET_ID}`

### Step 2: Add one row per location
| Client_Name | Client_Code | ClickUp_List_ID | Google_Sheet_ID | Account_Manager | Status | Efficiency_Baseline |
|---|---|---|---|---|---|---|
| Vibra Farmacia Mx1 | VF_MX1 | abc123xyz | 1qwerty... | Pedro | Active | 85 |
| Vibra Farmacia Mx2 | VF_MX2 | def456xyz | 1asdfgh... | Gibran | Active | 85 |
| ... | ... | ... | ... | ... | ... | ... |

### Step 3: Run script
```bash
python spekgen_morning_intelligence.py --dry-run
```
- All 10 locations appear in memo automatically
- No code changes needed

### Step 4: Go live
- Script will auto-include these clients in next 8 AM run
- ClickUp escalations auto-created for Red/Yellow projects

---

## Rolling Back (If Script Breaks)

**Scenario:** You pushed a broken change to main branch.

**Quick fix:**
1. Go to GitHub Repo → Actions tab
2. Most recent `SpekGen Morning Intelligence` will show ❌ failed
3. Fix the code locally
4. Commit and push to main (GitHub Actions will auto-retry in ~5 min)

**Manual rollback:**
1. Find last successful run in Actions
2. Note the commit hash
3. `git revert {broken-commit}`
4. Push (Actions will pick up the revert automatically)

**Previous memos are safe:**
- All memos saved to Drive are read-only archives
- Earlier memo from yesterday still exists even if today's fails

---

## Performance Expectations

| Metric | Expected | Warning Threshold |
|---|---|---|
| Runtime | 10–15 sec | > 30 sec |
| Clients fetched | 5 | < 5 means one failed |
| API calls | 50–100 | > 200 means loop issue |
| Memo delivery | 8:00–8:05 AM | > 8:10 AM |
| GitHub Actions uptime | 99.9% | < 99% over 7 days |

---

## Extending the System

### Adding Slack delivery
```python
import slack_sdk

def send_to_slack(memo_text: str):
    client = slack_sdk.WebClient(token=os.getenv("SLACK_TOKEN"))
    client.chat_postMessage(channel="#morning-intel", text=memo_text)
```

### Adding email delivery
```python
import smtplib

def send_email(memo_text: str, recipients: list):
    msg = EmailMessage()
    msg.set_content(memo_text)
    msg["Subject"] = f"SpekGen Morning Intelligence — {date.today()}"
    msg["From"] = "morning-intel@spekgen.mx"
    msg["To"] = recipients
    # Send via your email service
```

### Adding custom metrics
```python
# Store in Master Registry: Last 7-day trend
def update_trend_dashboard(client_health_history: dict):
    # Track Green → Yellow → Red progression
    # Alert if project has been Red for 3+ days
```

---

## Contact & Escalation

**If memo doesn't run:**
- Check GitHub Actions first (most common issue)
- Then check Drive folder exists
- Then check Master Registry is accessible

**If you can't fix it:**
- Message Pedro (owns ClickUp integration)
- Or Gibran (owns Drive integration)

**For feature requests:**
- Add issue to GitHub repo (feature/enhancement label)
- Script is extensible — see "Extending the System" section above

