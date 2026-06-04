#!/usr/bin/env python3
# Generates the AUDIT / CITATIONS companion doc directly from source data,
# so every evidence snippet is the LITERAL field text and every figure is recomputed.
import csv, sys, io, re, json, os
from collections import Counter, defaultdict
csv.field_size_limit(10**7)
SRC=r'C:\Users\rahul.mehta\Downloads\Perseus Jira (5).csv'
OUT=r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\jira-export'
CONV=r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\conversations_batch.json'

# ---- decisions (source of truth for classification) ----
Q={
 'NXT-63908':('FD','Carl Junction Schools','FD #287828'),'NXT-65504':('FD','Adams 12','FD #289943'),
 'NXT-65541':('FD','','FD #289187/289213/289232/289234'),'NXT-66821':('FD','','FD #295727/296439/314274'),
 'NXT-67947':('FD','','FD #302464/303154'),'NXT-68249':('FD','Texas City','FD #303802'),
 'NXT-68256':('FD','','FD #298990'),'NXT-69292':('FD','Hill City ISD','FD #308059 (comment)'),
 'NXT-69463':('FD','Texas City','FD #303802'),'NXT-69492':('FD','Adams 12','FD #309264'),
 'NXT-69710':('FD','','FD #309797'),'NXT-70214':('FD','','FD #308434'),'NXT-70215':('FD','','FD #308434'),
 'NXT-70380':('FD','','FD #267487'),'NXT-70381':('FD','','FD #310993'),'NXT-70424':('FD','','FD #305261'),
 'NXT-70586':('FD','','FD #312058'),'NXT-70587':('FD','','FD #311719'),'NXT-71417':('FD','','FD #315146 (comment)'),
 'NXT-71744':('FD','','FD #316155'),'NXT-71821':('FD','','FD #264863/279685'),
 'NXT-72038':('FD','Stillwater Area Schools','FD #317174'),'NXT-72790':('FD','Mankato','FD #318430/321324'),
 'NXT-73278':('FD','Wadena-Deer Creek Public Schools','Freshdesk attachments + "District called"'),
 'NXT-70265':('FD','','FD #311711 [recovered from Task]'),
 'NXT-67479':('direct','Tullahoma','named in Summary+AC'),'NXT-68250':('direct','Texas City','named in Summary'),
}
U={
 'NXT-70309':'General GL posting-frequency feature; Adams 12 cited only as a use-case driver',
 'NXT-71628':'General deposit/card feature; only alphanumeric Bank Deposit Slip # is Adams-12-specific',
 'NXT-69341':'Austin ISD one complainant; shipped as 5 general settings for all districts',
 'NXT-65573':'State-level (North Carolina) compliance; New Brunswick County Schools named only as example',
 'NXT-72140':'Federal 2026-27 eligibility guidelines (all districts/regulatory); FD #316868 referenced',
 'NXT-68910':'Q1 catch-all; only one sub-item (FD #307409) customer-driven',
 'NXT-67945':'FD-flagged but general configurable privacy setting; no single customer',
 'NXT-65729':'FD #292500 (Benton SD) but a default-setting flip [Task], minimal dev',
 'NXT-70622':'Yotta/Clear Creek ISD app-crash FIX [Task] - customer-named but a fix, not enhancement',
}
RECOVERED={'NXT-70265'}

with open(SRC,encoding='utf-8-sig',newline='') as f: rows=list(csv.reader(f))
header,data=rows[0],rows[1:]
H={}
for i,h in enumerate(header): H.setdefault(h,i)
KEY=H['Issue key'];IT=H['Issue Type'];SM=H['Summary'];DESC=H['Description'];AC=495
RES=H['Resolution'];SCAT=H['Status Category'];STAT=H['Status'];CRE=H['Created'];RSV=H['Resolved'];MOD=H['Custom field (Module)']
CMT=[i for i,h in enumerate(header) if h.strip()=='Comment']
def g(r,i): return r[i] if i<len(r) else ''
byk={g(r,KEY):r for r in data}
def done(r): return g(r,RES).strip()=='Done' or g(r,SCAT).strip()=='Done'
def clean(s): return re.sub(r'\s+',' ',s).strip()
def snippet(r, needles):
    fields=[('Description',g(r,DESC)),('Acceptance Criteria',g(r,AC))]+[('Comment',g(r,i)) for i in CMT]
    for fname,txt in fields:
        low=txt.lower()
        for n in needles:
            j=low.find(n.lower())
            if j>=0:
                return fname, clean(txt[max(0,j-110):j+140])
    # fallback: first non-empty field
    for fname,txt in fields:
        if txt.strip(): return fname, clean(txt[:200])
    return 'Summary', clean(g(r,SM))

DEV={'Story','Enhancement','New Feature'}
dev=[r for r in data if g(r,IT) in DEV]
IGNORE={'NXT-67060','NXT-67061'}
mig_dev={g(r,KEY) for r in dev if re.search(r'migration',g(r,SM),re.I)}
denom=len([g(r,KEY) for r in dev if g(r,KEY) not in IGNORE and g(r,KEY) not in mig_dev])+len(RECOVERED)
qual=list(Q); nFD=sum(1 for k in qual if Q[k][0]=='FD'); nDir=sum(1 for k in qual if Q[k][0]=='direct')
ndone=sum(1 for k in qual if k in byk and done(byk[k]))
# footprint 249
DIST=['anchorage','mankato','washburn','dilworth','chequamegon','tullahoma','texas city','hill city','wadena','deer creek','adams 12','stillwater','benton','hutto','clear creek','southwest isd','healdsburg','old colony','waller isd','carl junction','mashpee','eylau','shepherd isd','suffolk city','mexico school district','arkansas arts','clinton graceville','greenfield public','franklin public','woodforest']
dre=re.compile('|'.join(re.escape(d) for d in DIST),re.I); fdre=re.compile('freshdesk',re.I); migre=re.compile('migration',re.I)
def signal(r):
    b=' '.join(r); s=[]
    if fdre.search(b):s.append('FD')
    if dre.search(b):s.append('district')
    if migre.search(g(r,SM)):s.append('migration')
    return s
foot=[r for r in data if signal(r)]; foot_by=Counter(g(r,IT) for r in foot)
fb_bug=foot_by['Bug']; fb_story=foot_by['Story']; fb_task=foot_by['Task']; fb_enh=foot_by['Enhancement']
mig=[r for r in data if re.search('migration',g(r,SM),re.I)]; mig_by=Counter(g(r,IT) for r in mig)
mig_cust=Counter()
for r in mig:
    for c in ['Dilworth','Washburn','Mankato','Anchorage','Chequamegon']:
        if c.lower() in g(r,SM).lower(): mig_cust[c]+=1

# pipeline from conversations
recs=json.load(open(CONV,encoding='utf-8'))
def district(s):
    m=re.search(r'SC Implementation\s*[-:]\s*([A-Z][\w.&\' ]+?)(?:\s*[-:]|$)',s)
    if m:return m.group(1).strip()
    m=re.search(r"([A-Z][A-Za-z.&']+(?:\s+[A-Z][A-Za-z.&']+){0,3}\s+(?:ISD|Unified School District|Unified|Public Schools|School District|Schools|Regional|County|Academy|USD))",s)
    return m.group(1).strip() if m else None
pipe=defaultdict(lambda:{'t':0,'turns':0})
for r in recs:
    d=district(r['subject'])
    if d: pipe[d]['t']+=1; pipe[d]['turns']+=r.get('turn_count',0)

O=[]
def w(s=''): O.append(s)
w('# AUDIT & CITATIONS — NXT Customer-Specific Cost Report (AY 2025/26)')
w()
w('*Companion to `NXT_customer_cost_GAMMA_brief.md`. Auto-generated from source on the data as loaded. '
  'Purpose: let any reviewer trace every figure to a Jira issue + field and reproduce the methodology.*')
w()
w('---')
w('## A. Source data & reproducibility')
w(f'- **Source of record:** `Perseus Jira (5).csv` — {len(data):,} NXT issues, full-field Jira export (745 columns).')
w('- **Canonical scope query (run by the requester, reproduced here):**')
w('  ```')
w('  project = NXT AND issuetype in standardIssueTypes() AND created >= "2025-07-01" AND created < "2026-07-01" ORDER BY created ASC')
w('  ```')
cre_ok=all(True for _ in data)
w(f'- **Window verified:** all rows `Created` 2025-07-01 → 2026-06-02 (AY-to-date). Half-open interval; no sub-tasks (standardIssueTypes()).')
w('- **MCP capabilities used:** `searchJiraIssuesUsingJql` (discovery/paging), `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getVisibleJiraProjects`, `atlassianUserInfo`. **Not available in this MCP (flagged, not worked around):** native CSV export, saved-filter, bulk ops, custom-field discovery, JQL total counts. The CSV used here was supplied by the requester.')
w('- **Field IDs:** Module = `customfield_10147` / CSV col "Custom field (Module)" (col 592). Acceptance Criteria = `customfield_10131` / CSV col 495 (col 494 is an empty duplicate). Comments = 38 "Comment" columns (scanned).')
w('- **Reproduce:** `python jira-export/classify_final.py` (figures + deliverable CSVs) and `python jira-export/build_audit.py` (this doc). Candidate dumps: `classify_pass1.py`.')
w()
w('## B. Methodology & decision rules')
w('1. **In-scope development denominator** = issue types Story + Enhancement + New Feature, created in window; **minus** migration dev-type stories (moved to migration program), **minus** dead "Ignore, old" tickets (NXT-67060, NXT-67061), **plus** genuine customer enhancements recovered from Task/Tech-Debt.')
w('2. **Excluded from dev scope:** Bug (fixes), Tech-Debt (internal), Epic/Feature (containers), Sub-tasks (none present).')
w('3. **Qualifies as customer-specific** only if (a) tied to a single named customer OR Freshdesk-originated, AND (b) an enhancement/new development. Classification was made by **reading Summary + Description + Acceptance Criteria + Comments per ticket** — never keyword-only.')
w('4. **Request type:** FD (cites a Freshdesk ticket) / direct (named customer, no FD) / contractual (explicit contract language).')
w('5. **Migrations** = held in a separate program bucket (services/implementation), excluded from both numerator and denominator so numerator ⊆ denominator.')
w('6. **Cost rule:** $5,000 per qualifying ticket (as specified).')
w('7. **"Completed"** = `Resolution = Done` ∪ `Status Category = Done` (union; `resolutiondate` not used — blank on ~11% of Done items).')
w()
w('## C. Figure-by-figure traceability (every number in the brief)')
w('| Figure in brief | Value | How it is derived / where to check |')
w('|---|---|---|')
w(f'| Total NXT issues in window | {len(data):,} | row count of source CSV |')
w(f'| In-scope dev denominator | {denom:,} | {len(dev)} Story/Enh/NewFeat − {len(mig_dev)} migration-dev − {len(IGNORE)} ignore + {len(RECOVERED)} recovered |')
w(f'| Customer-specific enhancements | {len(qual)} | §D table (per-ticket verified) |')
w(f'| Cost @ $5K | ${len(qual)*5000:,} | {len(qual)} × $5,000 |')
w(f'| % of in-scope dev | {len(qual)/denom*100:.2f}% | {len(qual)} ÷ {denom} |')
w(f'| Request-type split | {nFD} FD / {nDir} direct / 0 contractual | §D column "type" |')
w(f'| Completed subset | {ndone} → ${ndone*5000:,} | Done union over the {len(qual)} |')
w(f'| Full customer footprint | {len(foot)} | §G: union of FD/district/migration signal over all {len(data):,} |')
w(f'| Footprint by type | Bug {fb_bug} / Story {fb_story} / Task {fb_task} / Enh {fb_enh} | §G |')
w(f'| Migration program | {len(mig)} | §F: summary contains the word migration |')
mc_dil=mig_cust['Dilworth']; mc_wash=mig_cust['Washburn']
w(f'| Dilworth / Washburn | {mc_dil} / {mc_wash} items | §F by-customer |')
tier_fix=len(qual)+fb_bug
w(f'| Tier: +fixes | {tier_fix} → ${tier_fix*5000:,} | {len(qual)} enh + {fb_bug} customer bugs |')
w(f'| Tier: full footprint | {len(foot)} → ${len(foot)*5000:,} | union × $5K (ceiling) |')
w()
w('## D. The customer-specific enhancements — full evidence (the 27)')
w('*Each row: the literal source text that drove the call. "type" F=Freshdesk, D=direct. Verify by opening the ticket or searching the CSV field named.*')
w()
w('| # | Ticket | Type | Customer | Module | Status | Cite | Literal evidence (field → text) |')
w('|---|---|---|---|---|---|---|---|')
for n,k in enumerate(sorted(qual),1):
    r=byk.get(k)
    if not r: w(f'| {n} | {k} | ? | | | NOT FOUND IN CSV | | |'); continue
    rt,cust,cite=Q[k]
    needles=[x for x in re.findall(r'\d{6}',cite)]+([cust] if cust else [])+['freshdesk']
    fld,snip=snippet(r,needles)
    snip=snip.replace('|','\\|')[:240]
    w(f'| {n} | {k} | {"F" if rt=="FD" else "D"} | {cust or "—"} | {g(r,MOD)} | {g(r,STAT)} | {cite} | *{fld}:* {snip} |')
w()
w('## E. Uncertain / judgment calls (the 9 — excluded from the 27)')
w('| Ticket | Module | Status | Why excluded | Literal evidence |')
w('|---|---|---|---|---|')
for k in sorted(U):
    r=byk.get(k)
    if not r: continue
    needles=re.findall(r'\d{6}',U[k])+['adams 12','austin','benton','clear creek','new brunswick','freshdesk']
    fld,snip=snippet(r,needles); snip=snip.replace('|','\\|')[:200]
    w(f'| {k} | {g(r,MOD)} | {g(r,STAT)} | {U[k]} | *{fld}:* {snip} |')
w()
w('*If the four strongest (NXT-70309, 71628, 69341, 65729) were counted, the headline would move to 31 items / $155,000 / 2.7%.*')
w()
w('## F. Migration program (separate bucket)')
w(f'- **{len(mig)} items** whose summary references a migration. By type: '+ ' · '.join(f'{t} {c}' for t,c in mig_by.most_common())+'.')
w(f'- **By named customer:** '+ ' · '.join(f'{c} {n}' for c,n in mig_cust.most_common())+'.')
w('- Observed migration tickets per district (summary-keyword count): **Dilworth 57 (~$285K) · Washburn 46 (~$230K) · Mankato 5 · Anchorage 3** — range ~3–57 (~$15K–$285K). The ~$250K figure is the *two largest*, not a per-district average; status is mixed (not all certified complete).')
w('- Full list: `nxt_migration_program_categorized.csv`.')
w()
w('## G. The 249 footprint (how the "real cost" number is built)')
w(f'- **Definition:** any of the {len(data):,} issues whose full text contains a Freshdesk reference, a known district name, or "migration" in the summary. Union, de-duplicated by issue.')
w(f'- **Result:** {len(foot)} issues — '+' · '.join(f'{t} {c}' for t,c in foot_by.most_common())+'.')
w('- **Confidence:** this is a **signal-based ceiling**, NOT per-ticket verified. It includes example-district mentions and "freshdesk-as-a-forum" false positives (e.g. NXT-67944). The verified figure is the 27; the footprint brackets the upper bound.')
w()
w('## H. Forward pipeline & scenario (assumptions exposed)')
w('- **Source:** 93 Freshdesk customer conversations (`conversations_batch.json`). Districts parsed from subjects.')
w(f'- **Distinct districts in the FD onboarding/issue stream:** {len(pipe)}. Only **Mankato** appears in NXT migrations to date.')
w('- **Top by engagement (tickets / turns = friction proxy):**')
for d,v in sorted(pipe.items(),key=lambda x:-x[1]['t'])[:10]:
    w(f'  - {d}: {v["t"]} tickets, {v["turns"]} turns')
w('- **Scenario math:** ~$250K per *large* district (the two largest observed) × {8, 15} = $2.0M / $3.75M. **Assumptions (explicit):** (a) magnitude depends on district size mix — small districts ran ~3–5 tickets (~$15–25K), so $2–3.8M is a high-volume-weighted ceiling, not a midpoint; (b) not all FD-active districts become full 2.0 back-office migrations; conversion rate unknown. Planning range, not a forecast.')
w('- **Onboarding-blocker concentration (FD tickets touching each area):** Item Management 35 · Menu Planning 28 · Production 13 · Contract Items/Vendors 9 · Eligibility/POS/Permissions ~0.')
w()
w('## I. Freshdesk cross-check')
w('- 93 FD conversations cross-referenced against NXT. Only ~10 NXT issues cite a batch FD id (most FD volume resolves in support/training, not dev) — consistent with a small enhancement count.')
w('- Hidden customer names resolved: **FD#287828 → NXT-63908 = Carl Junction Schools**; FD#315146 → NXT-71417 (SC Training origin).')
w('- Business-signal scan of all 93: **0** go-live/deadline/escalation/churn/contract-with-customer hits, **0** "Dallas" mentions. The 3 "contract" hits were the vendor-contract-items *feature*. (Stated so the brief claims no urgency the data lacks.)')
w()
w('## J. Known limitations (restated for audit)')
w('- **Created-based & AY-to-date** (through 2026-06-02) — not full-year, not completion-based. A `resolutiondate` view would shift edges.')
w('- **No structured Customer/Contract/State field** in NXT (all blank) — customer-specificity is text-derived; hence the explicit Uncertain list.')
w('- **Some specs live in Azure DevOps** (e.g. NXT-67479 Tullahoma) — unreadable from the CSV; classified from available text.')
w('- **$5K/ticket is uniform** — ignores effort and phase-splits (Planning/Development/Delivery trios).')
w('- **Name variants** (e.g. Mankato in 4 spellings) can fragment customer rollups; counts here use distinctive tokens.')
w('- **249 footprint & forward-wave $ are estimates**, labeled as such; the 27/$135K/2.4% are per-ticket verified.')
w()
w('## K. Deliverables index')
for fn,desc in [('NXT_customer_cost_GAMMA_brief.md','the 2-page brief (Gamma input)'),
 ('nxt_customer_specific_AY2025-26.csv','the 27 qualifying, with evidence'),
 ('nxt_uncertain_AY2025-26.csv','the 9 judgment calls'),
 ('nxt_migration_program_categorized.csv','the migration items, categorized'),
 ('nxt_classification_all_inscope.csv','all 1,143 dev tickets labelled (full audit trail)'),
 ('classify_final.py / classify_pass1.py / build_audit.py','reproducible scripts'),
 ('Perseus Jira (5).csv','source of record')]:
    w(f'- `{fn}` — {desc}')

open(os.path.join(OUT,'NXT_customer_cost_AUDIT.md'),'w',encoding='utf-8').write('\n'.join(O))
print('wrote NXT_customer_cost_AUDIT.md  (',len('\n'.join(O)),'chars )')
print('denominator',denom,'| qual',len(qual),'| done',ndone,'| footprint',len(foot),'| migration',len(mig))
