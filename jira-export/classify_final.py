#!/usr/bin/env python3
# Final classification: encodes per-ticket decisions from full reading of candidates,
# computes denominator/numerator/cost/%/breakdowns, categorizes migration program,
# writes deliverable CSVs, prints every figure for the report.
import csv, sys, io, re, os
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
csv.field_size_limit(10**7)
SRC = r'C:\Users\rahul.mehta\Downloads\Perseus Jira (5).csv'
OUT = r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\jira-export'

# ---- QUALIFYING customer-specific DEVELOPMENT (read & confirmed) ----
# req_type: FD | direct ; customer: named single customer or '' ; evidence: cite
Q = {
 'NXT-63908': ('FD','', 'Desc: Freshdesk #287828 (duplicate VI# complaint)','Inventory'),
 'NXT-65504': ('FD','Adams 12','Desc: Freshdesk #289943; "As an Adams 12 parent"','Family Hub'),
 'NXT-65541': ('FD','', 'Desc: Freshdesk #289187/289213/289232/289234 (FO Year Begin feedback)','Accountability'),
 'NXT-66821': ('FD','', 'Desc: Freshdesk #295727/296439/314274 (DC extension)','Eligibility'),
 'NXT-67947': ('FD','', 'Desc: Freshdesk #302464/303154 (menu sort)','Family Hub'),
 'NXT-68249': ('FD','Texas City','Summary "Texas City"; Desc FD #303802 print; Comment FD 303802','Menu Planning'),
 'NXT-68256': ('FD','', 'Desc: Freshdesk #298990 (CEP apps)','Eligibility'),
 'NXT-69292': ('FD','Hill City ISD','Summary "SC Implementation - Hill City ISD #2"; Comment FD #308059','Menu Planning'),
 'NXT-69463': ('FD','Texas City','Desc FD #303802 print (Pre-K 2 of 5 components, Texas City origin)','Menu Planning'),
 'NXT-69492': ('FD','Adams 12','Summary "Adams 12"; Desc FD #309264 Oracle financial exports; AC "sample files for customer approval"','Accountability'),
 'NXT-69710': ('FD','', 'Desc: Freshdesk #309797 (bulk entry partial)','Accountability'),
 'NXT-70214': ('FD','', 'Desc: Freshdesk #308434 (closed period exceptions)','Accountability'),
 'NXT-70215': ('FD','', 'Desc: Freshdesk #308434 (SNP archive)','Accountability'),
 'NXT-70380': ('FD','', 'Desc: Freshdesk #267487 (income surveys auto-process)','Eligibility'),
 'NXT-70381': ('FD','', 'Summary+Desc: FD #310993 (ingredients display)','Family Hub'),
 'NXT-70424': ('FD','', 'Desc: Freshdesk #305261 (serving site)','Accountability'),
 'NXT-70586': ('FD','', 'Desc: Freshdesk #312058 (remove status)','Accountability'),
 'NXT-70587': ('FD','', 'Desc: Freshdesk #311719 (edit check worksheet enrollment)','Accountability'),
 'NXT-71417': ('FD','', 'Comment: committed to FD #315146 (production withdrawal)','Production'),
 'NXT-71744': ('FD','', 'Desc: Freshdesk #316155 (headerless Adult import / PowerSchool)','Platform - Data Exchange'),
 'NXT-71821': ('FD','', 'Desc: Freshdesk #264863/279685 (intermediate site staff menus)','Family Hub'),
 'NXT-72038': ('FD','Stillwater Area Schools','Desc+Comment: FD #317174 Stillwater Area Schools #834 (SCTV Spanish)','SCTV'),
 'NXT-72790': ('FD','Mankato','Desc: FD #318430 + FD #321324 (Mankato); Front-Office-only customer','Item Management'),
 'NXT-73278': ('FD','Wadena-Deer Creek Public Schools','Summary names district; Desc "District called" + FD attachments','Accountability'),
 'NXT-70265': ('FD','', 'Desc: Freshdesk #311711 (ID card barcode template) [recovered from Task]','Account Management'),
 'NXT-67479': ('direct','Tullahoma','Summary+AC "Tullahoma Financials enhancements"; Azure DevOps PBIs','Financials'),
 'NXT-68250': ('direct','Texas City','Summary "Texas City - Snack Pre-K Meal pattern and CACFP" (continuation)','Menu Planning'),
}
RECOVERED = {'NXT-70265'}  # came from Task, not in Story/Enh/NewFeat dev set

# ---- UNCERTAIN (flagged, NOT counted in headline) ----
U = {
 'NXT-65573': 'State-level (North Carolina districts) compliance; names New Brunswick County Schools only as example - not a single customer',
 'NXT-68910': 'Q1 catch-all of small changes; only one item (FD #307409) is FD-driven; rest general',
 'NXT-69341': 'Austin ISD named as one complainant but productized as 5 general settings for all districts',
 'NXT-70309': 'General GL posting-frequency feature; Adams 12 cited only as a use-case driver',
 'NXT-71628': 'General deposit/credit-card feature; only the alphanumeric Bank Deposit Slip # is Adams 12-specific',
 'NXT-72140': 'Federal 2026-27 eligibility guidelines (all districts/regulatory); FD #316868 referenced',
 'NXT-67945': 'FD-flagged but reads as a general configurable eligibility-privacy setting, no single customer',
 'NXT-65729': 'FD #292500 (Benton School District) but a default-setting flip [Task], minimal dev',
 'NXT-70622': 'Yotta/Clear Creek ISD app CRASH fix [Task] - customer-named but a fix, not enhancement',
}

with open(SRC, encoding='utf-8-sig', newline='') as f:
    rows=list(csv.reader(f))
header,data=rows[0],rows[1:]
H={}
for i,h in enumerate(header): H.setdefault(h,i)
KEY=H['Issue key']; IT=H['Issue Type']; SM=H['Summary']; MOD=H['Custom field (Module)']
RES=H['Resolution']; SCAT=H['Status Category']; STAT=H['Status']; CREATED=H['Created']
def g(r,i): return r[i] if i<len(r) else ''
byk={g(r,KEY):r for r in data}
def done(r): return g(r,RES).strip()=='Done' or g(r,SCAT).strip()=='Done'

DEV={'Story','Enhancement','New Feature'}
dev=[r for r in data if g(r,IT) in DEV]

# migration bucket (issue-type-agnostic) -- reuse detection
KNOWN=['anchorage','mankato','washburn','dilworth','chequamegon','tullahoma','texas city',
       'hill city','wadena','deer creek','adams 12','stillwater','benton','hutto','clear creek',
       'talladega','boone county','katy']
known_re=re.compile('|'.join(re.escape(k) for k in KNOWN),re.I)
def is_mig(r):
    sm=g(r,SM)
    return bool(re.search(r'district migration|\bmigration\b',sm,re.I) and not re.search(r'tfs|azure',sm,re.I)) \
           or 'migration' in sm.lower()
mig=[r for r in data if re.search(r'migration',g(r,SM),re.I)]
# categorize migration items
def mig_cat(r):
    sm=g(r,SM).lower()
    if 'woodforest' in sm or 'authorize.net' in sm or 'gateway' in sm: return 'payment-gateway (WoodForest)'
    for c in ['anchorage','mankato','washburn','dilworth','chequamegon']:
        if c in sm: return 'customer-district'
    if 'module migration' in sm or sm.strip() in ('district migration testing','district migration'): return 'generic/infra'
    return 'generic/infra'
mig_by_cat=Counter(mig_cat(r) for r in mig)
mig_cust=Counter()
for r in mig:
    if mig_cat(r)=='customer-district':
        for c in ['Anchorage','Mankato','Washburn','Dilworth','Chequamegon']:
            if c.lower() in g(r,SM).lower(): mig_cust[c]+=1

# ---- denominator ----
IGNORE={'NXT-67060','NXT-67061'}
mig_devtype_keys={g(r,KEY) for r in dev if re.search(r'migration',g(r,SM),re.I)}
denom_keys=[g(r,KEY) for r in dev if g(r,KEY) not in IGNORE and g(r,KEY) not in mig_devtype_keys]
denom = len(denom_keys) + len(RECOVERED)   # add recovered task(s)
print('=== DENOMINATOR (in-scope development) ===')
print('Story/Enh/NewFeat:', len(dev))
print('  minus migration dev-type:', len(mig_devtype_keys))
print('  minus Ignore/old:', len(IGNORE & set(g(r,KEY) for r in dev)))
print('  plus recovered Task:', len(RECOVERED))
print('  => DENOMINATOR =', denom)
print()
qual=list(Q.keys())
print('=== NUMERATOR (customer-specific dev) ===')
print('qualifying tickets:', len(qual))
print('  cost @ $5,000 =', f'${len(qual)*5000:,}')
print('  % of in-scope dev =', f'{len(qual)/denom*100:.2f}%')
print()
print('=== BY REQUEST TYPE ===')
for t,c in Counter(Q[k][0] for k in qual).most_common(): print(f'  {c:3d}  {t}')
print()
print('=== BY MODULE (qualifying) ===')
for m,c in Counter(Q[k][3] for k in qual).most_common(): print(f'  {c:3d}  {m}')
print()
print('=== NAMED CUSTOMERS (qualifying) ===')
nc=Counter(Q[k][1] for k in qual if Q[k][1])
for c,n in nc.most_common(): print(f'  {n:3d}  {c}')
print('  (FD-origin, customer not named in ticket:', sum(1 for k in qual if not Q[k][1]),')')
print()
print('=== COMPLETED CUT (qualifying) ===')
dq=sum(1 for k in qual if k in byk and done(byk[k]))
print(f'  Done (resolution/statuscat): {dq} of {len(qual)}  -> ${dq*5000:,}')
print()
print('=== MIGRATION PROGRAM (separate bucket, all issue types) ===')
print('total migration items:', len(mig))
for cat,c in mig_by_cat.most_common(): print(f'  {c:3d}  {cat}')
print('  by type:', dict(Counter(g(r,IT) for r in mig)))
print('  customer-district migration items by customer:', dict(mig_cust))
print()
print('=== UNCERTAIN (flagged) ===', len(U))

# ---- write deliverables ----
with open(os.path.join(OUT,'nxt_customer_specific_AY2025-26.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['key','request_type','named_customer','module','issuetype','status','resolution','done','created','evidence','summary'])
    for k in sorted(qual):
        r=byk.get(k)
        if not r: continue
        rt,cust,ev,mo=Q[k]
        w.writerow([k,rt,cust,g(r,MOD),g(r,IT),g(r,STAT),g(r,RES),'Y' if done(r) else 'N',g(r,CREATED),ev,g(r,SM)])
with open(os.path.join(OUT,'nxt_uncertain_AY2025-26.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['key','module','issuetype','status','reason','summary'])
    for k in sorted(U):
        r=byk.get(k)
        if r: w.writerow([k,g(r,MOD),g(r,IT),g(r,STAT),U[k],g(r,SM)])
with open(os.path.join(OUT,'nxt_migration_program_categorized.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['key','category','issuetype','module','status','created','summary'])
    for r in sorted(mig,key=lambda x:g(x,KEY)):
        w.writerow([g(r,KEY),mig_cat(r),g(r,IT),g(r,MOD),g(r,STAT),g(r,CREATED),g(r,SM)])
# full audit: all dev with label
with open(os.path.join(OUT,'nxt_classification_all_inscope.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['key','label','request_type','module','issuetype','status','summary'])
    for r in dev:
        k=g(r,KEY)
        if k in Q: lab,rt='customer-specific',Q[k][0]
        elif k in U: lab,rt='uncertain',''
        elif k in mig_devtype_keys: lab,rt='migration',''
        elif k in IGNORE: lab,rt='dropped-ignore',''
        else: lab,rt='general-product',''
        w.writerow([k,lab,rt,g(r,MOD),g(r,IT),g(r,STAT),g(r,SM)])
print('\nwrote 4 deliverable CSVs to', OUT)
