#!/usr/bin/env python3
# Audit-grade proof doc for the "onboarding pipeline" inference.
# Sources: (1) xlsx "PCS NXT Not Marked" sheet = 93 customer tickets NOT linked to NXT,
#          with curated District/County, Status, Type, Classification, dates.
#          (2) conversations_batch.jsonl = full message bodies (verbatim quotes).
#          (3) Perseus Jira (5).csv = NXT cross-check (does the district appear in NXT / migration?).
import sys, io, json, csv, re, os
from collections import Counter, defaultdict
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
csv.field_size_limit(10**7)
import openpyxl
XLSX=r'C:\Users\rahul.mehta\Downloads\Data for Dallas June 2 2026.xlsx'
JSONL=r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\conversations_batch.jsonl'
NXTCSV=r'C:\Users\rahul.mehta\Downloads\Perseus Jira (5).csv'
OUT=r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\jira-export\NXT_onboarding_pipeline_PROOF.md'

def fix(s):
    if s is None: return ''
    return str(s).replace('â€™',"'").replace('â€“','-').replace('â€œ','"').replace('â€\x9d','"')

# ---- 1. xlsx sheet ----
wb=openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws=wb['PCS NXT Not Marked']
rows=list(ws.iter_rows(values_only=True)); hdr=[fix(h).strip() for h in rows[0]]
C={h:i for i,h in enumerate(hdr)}
def gx(r,name):
    i=C.get(name); return r[i] if (i is not None and i<len(r)) else None
sheet=[r for r in rows[1:] if gx(r,'Ticket ID') is not None]

# ---- 2. JSONL bodies ----
bodies={}
for line in open(JSONL,encoding='utf-8'):
    line=line.strip()
    if not line: continue
    r=json.loads(line); bodies[str(r['ticket_id'])]=r
def first_customer_quote(tid):
    r=bodies.get(str(tid))
    if not r: return ''
    for t in r['turns']:
        if t.get('role')=='customer':
            b=re.sub(r'\s+',' ',(t.get('body_text') or '')).strip()
            b=re.sub(r'CAUTION:.*?safe\.','',b).strip()
            if len(b)>30: return b
    return ''

# ---- 3. NXT cross-check ----
nrows=list(csv.reader(open(NXTCSV,encoding='utf-8-sig'))); ncols=nrows[0]
NKEY=ncols.index('Issue key'); NIT=ncols.index('Issue Type'); NSM=ncols.index('Summary')
ndata=nrows[1:]
def nxt_check(token):
    tok=token.lower()
    hits=[r for r in ndata if tok in ' '.join(r).lower()]
    types=Counter(r[NIT] for r in hits)
    mig=[r[NKEY] for r in hits if re.search('migration',r[NSM],re.I)]
    return len(hits), dict(types), mig

# ---- group by curated district ----
INTERNAL={'Edge District','Simplot'}  # test env + vendor (user-flagged)
bydist=defaultdict(list)
for r in sheet: bydist[fix(gx(r,'District/County*')) or '(blank)'].append(r)

def impl_signal(r):
    t=fix(gx(r,'Type')); cl=fix(gx(r,'Ticket Classification')); subj=fix(gx(r,'Subject'))
    return (t=='Implementation') or ('Implementation' in cl) or ('Implementation' in subj) or ('Import' in subj) or ('migration' in subj.lower())
def dist_token(d):
    # distinctive token for NXT search
    d=re.sub(r'\b(School District|Public Schools|Unified School District|Independent School District|Schools|ISD|USD|District|Regional Vocational Technical|Community School|Academy|County)\b.*','',d,flags=re.I).strip()
    return d.split('#')[0].strip()

O=[]
def w(s=''): O.append(s)
w('# PROOF: Freshdesk Onboarding/Issue Pipeline vs NXT — district-by-district evidence')
w()
w('*Audit companion. Every district below is backed by its Freshdesk ticket IDs, **ticket status**, type, classification, dates, a verbatim customer quote, and an NXT cross-check. Built from three sources, no inference without a citation.*')
w()
w('**Sources**')
w('- **`Data for Dallas June 2 2026.xlsx` → sheet `PCS NXT Not Marked`** — 93 customer (Freshdesk/PCS) tickets **not linked to any NXT item**. Curated columns: District/County, Status, Type, Ticket Classification, Module, Created/Closed time, agent/customer interactions, PCS#. *The sheet name is itself the core evidence: these are customer tickets that did NOT convert to NXT work.*')
w('- **`conversations_batch.jsonl`** — full message bodies for all 93 (verbatim quotes).')
w('- **`Perseus Jira (5).csv`** — NXT cross-check (does the district appear in NXT at all / as a migration?).')
w()

# ---- honest headline ----
allreal=[r for r in sheet if (fix(gx(r,'District/County*')) not in INTERNAL)]
st=Counter(fix(gx(r,'Status')) for r in sheet)
ty=Counter(fix(gx(r,'Type')) for r in sheet)
cl=Counter(fix(gx(r,'Ticket Classification')) or '(blank)' for r in sheet)
real_d=sorted(d for d in bydist if d not in INTERNAL and d!='(blank)')
impl_tickets=[r for r in allreal if impl_signal(r)]
w('## What the evidence actually supports (read this first)')
w(f'- **93 customer tickets** across **{len(bydist)} entities**; after removing internal/test + vendor (**Edge District = {len(bydist.get("Edge District",[]))} tickets**, **Simplot = {len(bydist.get("Simplot",[]))}**), **{len(real_d)} real customer districts** remain.')
w(f'- **Ticket status:** {dict(st)} — **{st.get("Closed",0)} of 93 are Closed.** These are mostly *resolved* support/issue/training tickets, not an open migration backlog.')
w(f'- **Ticket type:** {dict(ty)}. **Ticket classification:** { {k:cl[k] for k in cl} }.')
w(f'- **Implementation/onboarding-flavored tickets** (Type=Implementation, or "Implementation Task" classification, or Import/migration in subject): **{len(impl_tickets)} of {len(allreal)}**. So "mid-onboarding" is accurate for a **subset** — the rest are live-customer issues, training, and questions.')
w('- **Honest read:** this proves a real base of **~{0} active customer districts generating customer-specific work that is NOT tracked in NXT**. It does **not**, by itself, prove a $2–4M *migration* wave — most of these districts appear to be live/active on SC 2.0 and getting support, with only a subset in active implementation. Treat the forward-migration dollar figure as an extrapolation from the separately-evidenced NXT migrations (Dilworth/Washburn), not as something these 93 tickets prove.'.format(len(real_d)))
w()

# ---- summary table ----
w('## Summary table — all districts (real customers)')
w('| District | FD tix | Impl-flavored | Statuses | Appears in NXT? | In NXT migration? |')
w('|---|---|---|---|---|---|')
def summarize(d):
    rs=bydist[d]
    impl=sum(1 for r in rs if impl_signal(r))
    stc=Counter(fix(gx(r,'Status')) for r in rs)
    ststr=', '.join(f'{k} {v}' for k,v in stc.most_common())
    nh,nt,nmig=nxt_check(dist_token(d))
    nxtstr=f'{nh} ({", ".join(f"{k} {v}" for k,v in nt.items())})' if nh else 'no'
    migstr=('YES: '+', '.join(nmig)) if nmig else 'no'
    return impl,ststr,nxtstr,migstr
for d in sorted(real_d, key=lambda x:-len(bydist[x])):
    impl,ststr,nxtstr,migstr=summarize(d)
    w(f'| {d} | {len(bydist[d])} | {impl} | {ststr} | {nxtstr} | {migstr} |')
w()
w('## Internal / non-customer entities (excluded from the count)')
for d in INTERNAL:
    if d in bydist:
        w(f'- **{d}** — {len(bydist[d])} tickets. ' + ('Flagged by you as an internal test environment.' if d=='Edge District' else 'Food-service vendor, not a school district.'))
        for r in bydist[d][:3]:
            w(f'  - FD#{gx(r,"Ticket ID")} [{fix(gx(r,"Status"))}] {fix(gx(r,"Subject"))[:80]}')
w()

# ---- per-district evidence ----
w('## District-by-district evidence (verbatim)')
for d in sorted(real_d, key=lambda x:-len(bydist[x])):
    rs=sorted(bydist[d], key=lambda r:str(gx(r,'Created time')))
    impl,ststr,nxtstr,migstr=summarize(d)
    w(f'\n### {d}  —  {len(bydist[d])} Freshdesk tickets')
    w(f'*Statuses: {ststr} · Implementation-flavored: {impl}/{len(rs)} · NXT: {nxtstr} · NXT migration: {migstr}*')
    w('')
    w('| FD# | Status | Type | Classification | Module | Created | Closed |')
    w('|---|---|---|---|---|---|---|')
    for r in rs:
        ct=gx(r,'Created time'); cl_=gx(r,'Closed time')
        cts=ct.strftime('%Y-%m-%d') if hasattr(ct,'strftime') else (fix(ct)[:10])
        cls=cl_.strftime('%Y-%m-%d') if hasattr(cl_,'strftime') else (fix(cl_)[:10] if cl_ else '—')
        w(f'| {gx(r,"Ticket ID")} | {fix(gx(r,"Status"))} | {fix(gx(r,"Type"))} | {fix(gx(r,"Ticket Classification"))} | {fix(gx(r,"Module*"))} | {cts} | {cls} |')
    # one verbatim quote, prefer an implementation-flavored ticket
    qrow=next((r for r in rs if impl_signal(r) and first_customer_quote(gx(r,'Ticket ID'))), None) or next((r for r in rs if first_customer_quote(gx(r,'Ticket ID'))), None)
    if qrow:
        tid=gx(qrow,'Ticket ID'); q=first_customer_quote(tid)
        w('')
        w(f'> **Verbatim (FD#{tid}, "{fix(gx(qrow,"Subject"))[:70]}"):** "{q[:420]}"')
w()
w('## Methodology & caveats')
w('- "Real customer districts" = curated `District/County` values minus Edge District (internal test, user-flagged) and Simplot (vendor).')
w('- "Impl-flavored" = Type=Implementation OR Classification contains "Implementation" OR subject contains Import/migration. A heuristic — the per-district tables show the raw fields so you can re-judge.')
w('- NXT cross-check matches a distinctive district token against all fields of the NXT export; "In NXT migration" = that token appears in an NXT ticket whose summary contains "migration". Absence is evidence the district has not generated an NXT migration cluster (consistent with the sheet being "NXT Not Marked").')
w('- **Status matters:** 84/93 tickets are Closed — resolved support/issue/training, not open onboarding. The pipeline is real but is NOT a queue of pending $250K migrations; the forward-$ figure is an extrapolation from the two evidenced NXT migrations, not from these tickets.')
w('- Verbatim quotes are the first substantive customer turn from `conversations_batch.jsonl`; CAUTION banners stripped.')

open(OUT,'w',encoding='utf-8').write('\n'.join(O))
print('wrote', OUT, '(', len('\n'.join(O)), 'chars )')
print('real districts:', len(real_d), '| impl-flavored tickets:', len(impl_tickets), '| Closed:', st.get('Closed',0))
