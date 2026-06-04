#!/usr/bin/env python3
# Pass 1: build in-scope denominator, detect customer-specific candidates (high recall),
# dump full text of candidates for per-ticket reading, and assemble the migration bucket.
import csv, sys, io, re, json, os
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
csv.field_size_limit(10**7)

SRC = r'C:\Users\rahul.mehta\Downloads\Perseus Jira (5).csv'
OUT = r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\jira-export'
os.makedirs(OUT, exist_ok=True)

with open(SRC, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.reader(f))
header, data = rows[0], rows[1:]

H = {}
for i, h in enumerate(header):
    H.setdefault(h, i)
KEY=H['Issue key']; IT=H['Issue Type']; SM=H['Summary']; DESC=H['Description']
AC=495; RES=H['Resolution']; MOD=H['Custom field (Module)']; STAT=H['Status']
SCAT=H['Status Category']; CREATED=H['Created']; RESOLVED=H['Resolved']; LAB=H['Labels']
COMMENT_COLS=[i for i,h in enumerate(header) if h.strip()=='Comment']

def g(r,i): return r[i] if i<len(r) else ''
def comments(r): return ' '.join(g(r,i) for i in COMMENT_COLS)
def text_da(r): return ' '.join([g(r,SM), g(r,DESC), g(r,AC)])
def text_all(r): return ' '.join([g(r,SM), g(r,DESC), g(r,AC), comments(r)])

DEV = {'Story','Enhancement','New Feature'}
dev = [r for r in data if g(r,IT) in DEV]

# ---- known customers + structural patterns (recall-oriented) ----
KNOWN = ['anchorage','mankato','washburn','dilworth','woodforest','texas city','tullahoma',
         'hill city','wadena','deer creek','adams 12','adams12']
known_re = re.compile('|'.join(re.escape(k) for k in KNOWN), re.I)
# structural customer signals
struct_re = re.compile(r'\bISD\b|\bI\.S\.D\b|unified school|public schools|school district|'
                       r'county schools|\bcharter school|\bacademy\b|district migration|sc implementation', re.I)
fd_re = re.compile(r'freshdesk', re.I)
contract_re = re.compile(r'\bcontract\b|\bcontractual\b|\bMOU\b|statement of work|\bSOW\b|\bmandate\b|per (our|the) agreement', re.I)
reqby_re = re.compile(r'requested by|per the district|customer requested|district requested|specific district', re.I)
# inventory seasonal-contract feature = false 'contract' signal
seasonal_re = re.compile(r'seasonal contract|internal vendor', re.I)

def flags(r):
    sm=g(r,SM); da=text_da(r); al=text_all(r)
    fl=[]
    if fd_re.search(da): fl.append('FD_descAC')
    elif fd_re.search(comments(r)): fl.append('FD_commentonly')
    if known_re.search(sm) or known_re.search(da): fl.append('known_customer')
    if struct_re.search(sm): fl.append('struct_summary')
    elif struct_re.search(da): fl.append('struct_desc')
    if contract_re.search(da) and not seasonal_re.search(da): fl.append('contract')
    if reqby_re.search(da): fl.append('reqby')
    return fl

# ---- candidate pools ----
dev_cand=[r for r in dev if flags(r)]
tasks_td=[r for r in data if g(r,IT) in ('Task','Tech-Debt')]
task_cand=[r for r in tasks_td if flags(r)]

# ---- migration program bucket: ALL types naming a migration/known district ----
mig_re=re.compile(r'district migration|\bmigration\b', re.I)
def is_mig(r):
    sm=g(r,SM)
    return bool(known_re.search(sm) or re.search(r'district migration', sm, re.I)
               or (mig_re.search(sm) and not re.search(r'module migration|tfs|azure|data migration tool', sm, re.I)))
mig_all=[r for r in data if is_mig(r)]

print('=== DENOMINATOR ===')
print('dev (Story/Enh/NewFeat):', len(dev))
print('dev candidates (any signal):', len(dev_cand))
print('  flag breakdown:', Counter(fl for r in dev_cand for fl in flags(r)))
print('Task/Tech-Debt total:', len(tasks_td), '| candidates:', len(task_cand))
print()
print('=== MIGRATION BUCKET (all issue types) ===')
print('migration/named-district items:', len(mig_all))
print('  by type:', Counter(g(r,IT) for r in mig_all))
print()

# ---- dump candidate full text for reading ----
def dump(recs, path, title):
    with open(path,'w',encoding='utf-8') as o:
        o.write(f'# {title}\n\nTotal: {len(recs)}\n\n')
        for r in sorted(recs, key=lambda x:g(x,KEY)):
            o.write('='*100+'\n')
            o.write(f'{g(r,KEY)} | {g(r,IT)} | Module={g(r,MOD)} | Status={g(r,STAT)} ({g(r,SCAT)}) | Res={g(r,RES)!r} | flags={flags(r)}\n')
            o.write(f'Created={g(r,CREATED)} Resolved={g(r,RESOLVED)} Labels={g(r,LAB)!r}\n')
            o.write(f'SUMMARY: {g(r,SM)}\n')
            d=g(r,DESC).strip()
            o.write(f'\nDESCRIPTION:\n{d[:2500]}\n' if d else '\nDESCRIPTION: (blank)\n')
            a=g(r,AC).strip()
            o.write(f'\nACCEPTANCE CRITERIA:\n{a[:2000]}\n' if a else '\nACCEPTANCE CRITERIA: (blank)\n')
            cm=comments(r).strip()
            if fd_re.search(cm):
                m=fd_re.search(cm); o.write(f'\nCOMMENT(FD context): ...{cm[max(0,m.start()-150):m.start()+150]}...\n')
            o.write('\n')
    print('wrote', path, len(recs))

dump(dev_cand, os.path.join(OUT,'candidates_dev.md'), 'DEV customer-specific CANDIDATES (read & classify each)')
dump(task_cand, os.path.join(OUT,'candidates_task_techdebt.md'), 'Task/Tech-Debt customer candidates')

# ---- persist base denominator with auto-flags for the audit CSV ----
with open(os.path.join(OUT,'inscope_dev_base.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o)
    w.writerow(['key','issuetype','module','status','status_category','resolution','created','resolved','candidate_flags','summary'])
    for r in dev:
        w.writerow([g(r,KEY),g(r,IT),g(r,MOD),g(r,STAT),g(r,SCAT),g(r,RES),g(r,CREATED),g(r,RESOLVED),'|'.join(flags(r)),g(r,SM)])
print('wrote inscope_dev_base.csv', len(dev))

# migration bucket csv
with open(os.path.join(OUT,'migration_bucket.csv'),'w',encoding='utf-8',newline='') as o:
    w=csv.writer(o)
    w.writerow(['key','issuetype','module','status','resolution','created','summary'])
    for r in sorted(mig_all,key=lambda x:g(x,KEY)):
        w.writerow([g(r,KEY),g(r,IT),g(r,MOD),g(r,STAT),g(r,RES),g(r,CREATED),g(r,SM)])
print('wrote migration_bucket.csv', len(mig_all))
