#!/usr/bin/env python3
# EXECUTION of the SC 2.0 customer-cost action plan (DATA/TOC/FP&A/OPS analytical workstreams).
# Produces: district registry (entity resolution), FD->NXT join, the 78 constraint defects,
# effort-band decomposition, cost-to-serve by district, constraint KPI, forward model, triage back-test.
import csv, sys, io, re, os, json
from collections import Counter, defaultdict
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
csv.field_size_limit(10**7)
import openpyxl
NXT=r'C:\Users\rahul.mehta\Downloads\Perseus Jira (5).csv'
XLSX=r'C:\Users\rahul.mehta\Downloads\Data for Dallas June 2 2026.xlsx'
OUT=r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\jira-export\analysis'
os.makedirs(OUT, exist_ok=True)
def fix(s): return ('' if s is None else str(s)).replace('â€™',chr(39)).replace('â€“','-')

# ---------- load NXT ----------
rows=list(csv.reader(open(NXT,encoding='utf-8-sig'))); H=rows[0]; D=rows[1:]
def ci(name,default=None):
    for i,h in enumerate(H):
        if h==name: return i
    return default
KEY=ci('Issue key');IT=ci('Issue Type');SM=ci('Summary');DESC=ci('Description');STAT=ci('Status')
SCAT=ci('Status Category');RES=ci('Resolution');CRE=ci('Created');RSV=ci('Resolved');MOD=ci('Custom field (Module)')
SP=ci('Custom field (Story Points)');AC=495
CMT=[i for i,h in enumerate(H) if h=='Comment']; SPRINT=[i for i,h in enumerate(H) if h=='Sprint']
def g(r,i): return r[i] if (i is not None and i<len(r)) else ''
byk={g(r,KEY):r for r in D}
from datetime import datetime
def parse(s):
    for f in ('%m/%d/%Y %I:%M %p','%m/%d/%Y %H:%M'):
        try: return datetime.strptime(s,f)
        except: pass
    return None
def cycle_days(r):
    a,b=parse(g(r,CRE)),parse(g(r,RSV))
    return round((b-a).days) if (a and b) else None
def ncomments(r): return sum(1 for i in CMT if g(r,i).strip())
def nsprints(r): return len(set(g(r,i) for i in SPRINT if g(r,i).strip()))

# ---------- 27 qualifying (request_type, named customer) ----------
Q={'NXT-63908':('FD','Carl Junction'),'NXT-65504':('FD','Adams 12'),'NXT-65541':('FD',''),'NXT-66821':('FD',''),
 'NXT-67947':('FD',''),'NXT-68249':('FD','Texas City'),'NXT-68256':('FD',''),'NXT-69292':('FD','Hill City ISD'),
 'NXT-69463':('FD','Texas City'),'NXT-69492':('FD','Adams 12'),'NXT-69710':('FD',''),'NXT-70214':('FD',''),
 'NXT-70215':('FD',''),'NXT-70380':('FD',''),'NXT-70381':('FD',''),'NXT-70424':('FD',''),'NXT-70586':('FD',''),
 'NXT-70587':('FD',''),'NXT-71417':('FD',''),'NXT-71744':('FD',''),'NXT-71821':('FD',''),'NXT-72038':('FD','Stillwater'),
 'NXT-72790':('FD','Mankato'),'NXT-73278':('FD','Wadena-Deer Creek'),'NXT-70265':('FD',''),
 'NXT-67479':('direct','Tullahoma'),'NXT-68250':('direct','Texas City')}

# ---------- entity resolution ----------
def entity_class(name):
    n=name.lower()
    if re.search(r'edge (district|county)',n): return 'internal-test'
    if 'cybersoft' in n: return 'internal'
    if 'simplot' in n: return 'vendor'
    if 'training site' in n or n.strip()=='training': return 'internal-training'
    if 'all districts' in n or n.strip() in ('','none'): return 'global/na'
    return 'customer'
def canon(name):
    n=fix(name).lower()
    n=re.sub(r'#?\d+','',n)
    n=re.sub(r'\b(isd|usd|cisd|rsd|r-?x*\b|independent school district|unified school district|public schools|school district|community school district|community schools|vocational technical|regional|schools|school|district|area|county|academy|sd|five star|inc)\b','',n)
    n=re.sub(r'[^a-z ]',' ',n); n=re.sub(r'\s+',' ',n).strip()
    return n or name.lower().strip()

# ---------- load FD RAW Data (2.0 subset) ----------
wb=openpyxl.load_workbook(XLSX, read_only=True, data_only=True); ws=wb['RAW Data']
it=ws.iter_rows(values_only=True); fh=[str(x).strip() if x else '' for x in next(it)]; FC={h:i for i,h in enumerate(fh)}
def fg(r,n):
    i=FC.get(n); return r[i] if (i is not None and i<len(r)) else None
fd=[r for r in it if fg(r,'Ticket ID') is not None]
two=[r for r in fd if '2.0' in fix(fg(r,'Module*'))]
def is_impl(r): return fix(fg(r,'Type'))=='Implementation' or fix(fg(r,'Ticket Classification')) in ('Implementation Task','Migration Testing')

# ---------- migration bucket (from prior categorized csv) ----------
migrows=list(csv.reader(open('jira-export/nxt_migration_program_categorized.csv',encoding='utf-8')))
mh=migrows[0]; md=migrows[1:]; mkey=mh.index('key');mmod=mh.index('module');mtype=mh.index('issuetype');mcat=mh.index('category')

# ===================== 1. DISTRICT REGISTRY =====================
reg=defaultdict(lambda:{'variants':set(),'class':'customer','fd2_0':0,'fd_impl':0,'nxt_dev':0,'nxt_mig':0})
for r in two:
    raw=fix(fg(r,'District/County*'))
    if not raw or raw.lower()=='none': continue
    c=canon(raw); reg[c]['variants'].add(raw); reg[c]['class']=entity_class(raw)
    reg[c]['fd2_0']+=1
    if is_impl(r): reg[c]['fd_impl']+=1
# NXT customer-specific dev attribution
for k,(rt,cust) in Q.items():
    if cust:
        c=canon(cust); reg[c]['variants'].add(cust+' (NXT)'); reg[c]['nxt_dev']+=1
# NXT migration attribution
for r in md:
    sm=g(byk.get(g_:=r[mkey],byk.get(r[mkey],['']*len(H))),SM) if r[mkey] in byk else ''
    for cust in ['Dilworth','Washburn','Mankato','Anchorage','Chequamegon']:
        if cust.lower() in sm.lower():
            c=canon(cust); reg[c]['nxt_mig']+=1; reg[c]['variants'].add(cust+' (mig)'); break
with open(os.path.join(OUT,'district_registry.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['district_id','entity_class','n_variants','variants','fd_2.0_tickets','fd_implementation','nxt_dev_items','nxt_migration_items'])
    for c,v in sorted(reg.items(), key=lambda x:-(x[1]['fd2_0']+x[1]['nxt_mig'])):
        w.writerow([c,v['class'],len(v['variants']),' | '.join(sorted(v['variants']))[:200],v['fd2_0'],v['fd_impl'],v['nxt_dev'],v['nxt_mig']])
cust_reg={c:v for c,v in reg.items() if v['class']=='customer'}

# ===================== 2. FD# -> NXT JOIN =====================
fdsub={str(fg(r,'Ticket ID')):fix(fg(r,'District/County*')) for r in fd}
idpat=re.compile(r'(?:freshdesk\.com/a/tickets/|freshdesk\.com/helpdesk/tickets/|tickets/|FD\s*#?|#)(\d{5,6})',re.I)
join=[]
for r in D:
    blob=' '.join(r)
    if 'freshdesk' not in blob.lower(): continue
    for m in set(idpat.findall(blob)):
        join.append((g(r,KEY),g(r,IT),g(r,MOD),m,fdsub.get(m,'(not in FD export)')))
with open(os.path.join(OUT,'fd_nxt_join.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['nxt_key','nxt_type','nxt_module','fd_ticket','fd_district']); [w.writerow(x) for x in sorted(set(join))]

# ===================== 3. THE 78 CONSTRAINT DEFECTS =====================
defects=[r for r in md if r[mmod] in ('Menu Planning','Eligibility') and r[mtype]=='Bug']
with open(os.path.join(OUT,'constraint_defects_78.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['key','module','status','cycle_days','comments','sprints','summary'])
    for r in defects:
        nr=byk.get(r[mkey])
        if nr: w.writerow([r[mkey],r[mmod],g(nr,STAT),cycle_days(nr),ncomments(nr),nsprints(nr),g(nr,SM)[:90]])

# ===================== 4. EFFORT-BAND DECOMPOSITION =====================
def effort_band(r):
    sp=g(r,SP).strip(); pts=float(sp) if re.match(r'^\d+(\.\d+)?$',sp) else None
    cd=cycle_days(r) or 0; nc=ncomments(r); ns=nsprints(r)
    score=0
    if pts is not None: score+=(2 if pts>=8 else 1 if pts>=3 else 0)
    score+=(2 if cd>=60 else 1 if cd>=14 else 0)
    score+=(2 if nc>=8 else 1 if nc>=3 else 0)
    score+=(1 if ns>=2 else 0)
    return ('L' if score>=5 else 'M' if score>=2 else 'S'), pts, cd, nc, ns
items=[(k,'dev') for k in Q]+[(r[mkey],'migration') for r in md]
band_ct=Counter()
with open(os.path.join(OUT,'effort_bands.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['key','class','issuetype','module','effort_band','story_points','cycle_days','comments','sprints','summary'])
    for k,cls in items:
        r=byk.get(k)
        if not r: continue
        b,pts,cd,nc,ns=effort_band(r); band_ct[(cls,b)]+=1
        w.writerow([k,cls,g(r,IT),g(r,MOD),b,pts,cd,nc,ns,g(r,SM)[:80]])

# ===================== 5. COST-TO-SERVE BY DISTRICT =====================
with open(os.path.join(OUT,'cost_to_serve_by_district.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o); w.writerow(['district_id','segment','fd_2.0_support','fd_implementation','nxt_dev_items','nxt_migration_items','est_nxt_cost_$5k','cohort'])
    for c,v in sorted(cust_reg.items(), key=lambda x:-(x[1]['nxt_mig']*100+x[1]['nxt_dev']*10+x[1]['fd2_0'])):
        cost=(v['nxt_dev']+v['nxt_mig'])*5000
        seg='expensive-few (migration)' if v['nxt_mig']>0 else ('dev-touch' if v['nxt_dev']>0 else 'support-only (cheap tail)')
        w.writerow([c,seg,v['fd2_0'],v['fd_impl'],v['nxt_dev'],v['nxt_mig'],cost,''])

# ===================== 6. KPIs / FORWARD MODEL / TRIAGE BACK-TEST =====================
mig_bugs=[r for r in md if r[mtype]=='Bug']
constraint_pct=len(defects)/len(mig_bugs)*100 if mig_bugs else 0
impl_districts=[c for c,v in cust_reg.items() if v['fd_impl']>0]
expensive=[c for c,v in cust_reg.items() if v['nxt_mig']>=20]   # Dilworth/Washburn scale
any_mig=[c for c,v in cust_reg.items() if v['nxt_mig']>0]
conv_expensive=len(expensive)/len(impl_districts)*100 if impl_districts else 0
conv_any=len(any_mig)/len(impl_districts)*100 if impl_districts else 0

print('================= ANALYSIS RESULTS =================')
print('DISTRICT REGISTRY: %d entities | customers %d · internal/test %d · vendor %d · global %d'%(
    len(reg), sum(1 for v in reg.values() if v['class']=='customer'),
    sum(1 for v in reg.values() if v['class'] in ('internal','internal-test','internal-training')),
    sum(1 for v in reg.values() if v['class']=='vendor'), sum(1 for v in reg.values() if v['class']=='global/na')))
print('  Mankato variants collapsed:', sorted(reg[canon('Mankato')]['variants']))
print('FD#->NXT JOIN: %d distinct (nxt,fd) links | %d NXT issues carry an FD ref'%(len(set(join)), len(set(x[0] for x in join))))
print('CONSTRAINT DEFECTS: %d (Menu Planning %d + Eligibility %d bugs)'%(len(defects),
    sum(1 for r in defects if r[mmod]=='Menu Planning'), sum(1 for r in defects if r[mmod]=='Eligibility')))
print('  median cycle days:', sorted([cycle_days(byk[r[mkey]]) for r in defects if byk.get(r[mkey]) and cycle_days(byk[r[mkey]]) is not None])[len(defects)//2] if defects else 'n/a')
print()
print('EFFORT BANDS (vs flat $5K):')
for cls in ('dev','migration'):
    print('  %s: '%cls + ' '.join('%s=%d'%(b,band_ct[(cls,b)]) for b in 'SML'))
print()
print('CONSTRAINT-LOCATION KPI: %.0f%% of migration bugs in Menu Planning+Eligibility (78/%d)'%(constraint_pct,len(mig_bugs)))
print('FORWARD MODEL:')
print('  implementing customer districts: %d'%len(impl_districts))
print('  with ANY NXT migration cluster: %d (%.1f%%)'%(len(any_mig),conv_any))
print('  with EXPENSIVE (>=20-ticket) migration: %d (%.1f%%)'%(len(expensive),conv_expensive), expensive)
print('  => expected complex migrations per ~100 implementing districts: ~%.0f'%(conv_expensive))
print('  => forward NXT migration $ if next cohort ~ this one: ~%d complex x $230-285K'%max(1,round(conv_expensive/100*len(impl_districts))))
print()
print('TRIAGE BACK-TEST (would the rubric have caught the expensive ones?):')
for c in any_mig:
    v=cust_reg[c]; flag='MIGRATION-PROJECT' if v['nxt_mig']>=20 else 'assisted'
    print('  %-22s nxt_mig=%d fd_impl=%d -> route: %s'%(c,v['nxt_mig'],v['fd_impl'],flag))
print()
print('wrote 5 CSVs to', OUT)
