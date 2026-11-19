import pdfplumber, json, re, sys
pdf=pdfplumber.open(sys.argv[1])
recipes=[]; cur=None; section=None; extras=[]
SECT_KNOWN={'INGREDIENTES','PREPARACIÓN PASO A PASO','PLATEO & ESTÁNDARES'}
for pi,p in enumerate(pdf.pages):
    if pi<3: continue
    text=p.extract_text() or ''
    lines=[l.strip() for l in text.split('\n')]
    # section banner lines with ■ at top e.g. "■ OYSTERS & CLAMS — SPECIALTIES"
    tabs=p.find_tables()
    tabs=sorted(tabs,key=lambda t:t.bbox[1])
    # section headers: text lines starting with ■ not STAFF
    for l in lines:
        m=re.match(r'^[■\s]*([A-ZÁÉÍÓÚÑ&,—\- ]{4,})$',l)
    for t in tabs:
        rows=t.extract()
        first=(rows[0][0] or '')
        if '\nID:' in first or re.search(r'\nID: ',first):
            name,idl=first.split('\n',1)
            cur={'name':name.strip(),'idline':idl.strip(),'page':pi+1,'info':rows[1][0] if len(rows)>1 else '','sections':[]}
            # crop region for description/staff
            recipes.append(cur)
            cur['_top']=t.bbox[3]; cur['_page']=p
        elif 'REFERENCIA' in text and pi>=len(pdf.pages)-2:
            extras.append(rows)
        elif cur:
            if first in SECT_KNOWN:
                cur['sections'].append({'title':first,'rows':[[c for c in r] for r in rows[1:]],'page':pi+1})
            else:
                cur['sections'][-1]['rows'].extend(rows)
    # description & staff for recipes started on this page
    for r in recipes:
        if r.get('_page') is p:
            # text between header table bottom and next table top
            nxt=[t.bbox[1] for t in tabs if t.bbox[1]>r['_top']+1]
            bottom=min(nxt) if nxt else p.height-40
            crop=p.crop((0,r['_top'],p.width,bottom)).extract_text() or ''
            desc=[];staff=[]
            for l in crop.split('\n'):
                l=l.strip()
                if not l: continue
                if 'STAFF:' in l or staff:
                    staff.append(re.sub(r'^.*?STAFF:\s*','',l) if not staff else l)
                else: desc.append(l)
            r['desc']=' '.join(desc); r['staff']=' '.join(staff)
            del r['_page']; del r['_top']
json.dump(extras,open('reference.json','w'),ensure_ascii=False,indent=1)
json.dump(recipes,open('parsed.json','w'),ensure_ascii=False,indent=1)
for r in recipes:
    print(r['page'],r['name'],'|',r['idline'][:40],'| sec:',[s['title'] for s in r['sections']])
