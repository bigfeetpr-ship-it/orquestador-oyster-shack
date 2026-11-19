import json, re, openpyxl
P = json.load(open('parsed.json'))

def parse_info(info):
    s = info.replace('\n', ' ')
    a = re.search(r'Alérgenos:\s*(.*?)\s*(GF:|Prep:|$)', s)
    g = re.search(r'GF:\s*(.*?)\s*(Prep:|Alérgenos:|$)', s)
    p = re.search(r'Prep:\s*(.*?)\s*(GF:|Alérgenos:|$)', s)
    return (a.group(1) if a else '', g.group(1) if g else '', p.group(1) if p else '')

OVR = {  # wrapped-cell fixes
    'HD-06': ('Shellfish, Fish, Dairy (coconut cream)', 'GF — Sí (plateo)', '40 min (batch) / 10–12 min (plateo)'),
    'LC-04': ('Shellfish (imitation crab), Eggs (mayo)', 'Verificar imitation crab', '2–3 min (del batch)'),
    'SPEC-01': ('Gluten (harina), Dairy (mantequilla, mozzarella), Eggs (cilantro mayo)', 'No (plantilla de harina)', '10–12 min'),
    'AF-03': ('Dairy (queso 2.5 cups)', 'GF* (confirmar acompañamiento)', '2 min'),
    'AF-09': ('Sesame (tahini), Citrus (limón)', 'GF* (confirmar acompañamiento)', '2–3 min'),
    'SP-02': ('Shellfish, Dairy (cream cheese, parmesano), Alcohol (vino)', 'No (verificar)', '8–12 min'),
    'LC-03': ('Shellfish, Dairy (salsa), Gluten (tostadas), Alcohol (vino)', 'GF* (sin tostadas)', '8–10 min'),
}
# Clover prices 19 nov 2026 (old -> new noted in changes)
PRICE = {'SP-01': '25', 'SP-02': '26', 'SP-03': '23', 'SU-01': '18', 'SU-02': '22', 'HD-01': '24', 'HD-02': '27',
         'HD-03': '25', 'HD-04': '28', 'HD-04B': '32', 'HD-05': '29', 'HD-06': '38', 'HD-08': '25', 'HD-09': '23',
         'HD-10': '27', 'CV-01': '19', 'CV-02': '19', 'CV-03': '19', 'CV-04': '27', 'TN-01': '28', 'TN-02': '25',
         'TN-03': '24', 'TN-04': '22', 'RAW-01': '18', 'LC-01': '32', 'LC-03': '26', 'LC-04': '15', 'LC-05': '36',
         'LC-07': '42', 'LC-09': '33', 'SPEC-01': '25', 'AF-01': '38', 'AF-02': '15', 'AF-03': '17', 'AF-05': '17',
         'AF-08': '14', 'AF-09': '13'}
PRICE_NOTE = {'SP-03': '$23 (App: $24)', 'SP-01': '$25', 'TN-03': '$24 (86 en Clover hoy)'}
IMG = {'SP-02': 'image1', 'SP-03': 'image2', 'SU-01': 'image3', 'SU-02': 'image4', 'HD-01': 'image5', 'HD-03': 'image6',
       'HD-04': 'image5', 'HD-04B': 'image7', 'HD-05': 'image8', 'HD-06': 'image9', 'HD-08': 'image10', 'HD-09': 'image11',
       'HD-10': 'image12', 'CV-01': 'image13', 'CV-02': 'image14', 'CV-03': 'image15', 'TN-01': 'image16', 'TN-02': 'image17',
       'TN-04': 'image18', 'LC-01': 'image20', 'LC-03': 'image22', 'LC-05': 'image23', 'LC-07': 'image26', 'LC-09': 'image27',
       'SPEC-01': 'image28', 'AF-01': 'image29', 'AF-03': 'image30', 'AF-05': 'image31', 'AF-08': 'image32', 'AF-09': 'image33',
       'LC-02': 'image21', 'WF-02': 'image19', 'RAW-03': 'image24'}
NOTES = {'HD-04': 'Nota: el Recipe Hub usa la misma foto para Wild Mussels y Clams Casserole — confirmar y reemplazar.',
         'HD-01': 'Nota: el Recipe Hub usa la misma foto para Wild Mussels y Clams Casserole — confirmar y reemplazar.',
         'RAW-02': 'La foto que tenía esta receta en el Recipe Hub es del Whole Jonah Crab, no de los claws — por eso no se usó.'}
SECTION = lambda i: ('ESPECIALES' if i.startswith('SPEC') else 'OYSTERS & CLAMS — SPECIALTIES' if i.startswith('SP') else 'SOUPS' if i.startswith('SU') else
                     'HOT DISHES' if i.startswith('HD') else 'CEVICHES & RAW BAR' if i.startswith('CV') else
                     'FRESH TUNA & CRUDOS' if i.startswith(('TN', 'RAW-01')) else 'WHOLE FISH' if i.startswith('WF') else
                     'LOBSTER, CRABS & SHRIMP' if i.startswith(('LC', 'RAW-02', 'RAW-03')) else 'ESPECIALES' if i.startswith('SPEC') else 'AWAY FROM THE SEA')

out = []
for r in P:
    m = re.match(r'ID:\s*(\S+)\s*\|\s*Precio:\s*\$?([^|]*)\|\s*Porción:\s*(.*)', r['idline'])
    rid, oldp, por = m.group(1), m.group(2).strip(), m.group(3).strip()
    a, g, p = OVR.get(rid) or parse_info(r['info'])
    price = PRICE_NOTE.get(rid, '$' + PRICE[rid])
    name = r['name']
    if rid == 'RAW-01': name = 'Wild Salmon Sashimi (Salmon Crudo)'
    out.append(dict(id=rid, name=name, idline=f'ID: {rid} | Precio: {price} | Porción: {por}', oldprice=oldp, newprice=PRICE[rid],
                    allergens=a, gf=g, prep=p, desc=r['desc'], staff=r['staff'], sections=r['sections'],
                    img=f'img/{IMG[rid]}.jpg' if rid in IMG else None, photo_note=NOTES.get(rid), section=SECTION(rid)))

# new recipes from the Recipe Hub (no ingredient table there)
wb = openpyxl.load_workbook('/home/claude/hub/hub.xlsx', data_only=True)
def hub(sheet):
    rows = [[c for c in r if c not in (None, '')] for r in wb[sheet].iter_rows(values_only=True)]
    rows = [r for r in rows if r]
    d = {}; mode = None; steps = []; plate = []; desc = ''
    for r in rows:
        k = str(r[0])
        if k.startswith('DISH DESCRIPTION'): mode = 'desc'; continue
        if k.startswith('PREPARATION METHOD'): mode = 'steps'; continue
        if k.startswith('PLATING'): mode = 'plate'; continue
        if mode == 'desc': desc = k; mode = None
        elif mode == 'steps' and len(r) > 1: steps.append([k, str(r[1])])
        elif mode == 'plate' and len(r) > 1: plate.append([k, str(r[1])])
        elif len(r) > 1: d[k] = str(r[1])
    return d, desc, steps, plate
LBL = {'Plate / Vessel': 'Vajilla', 'Temperature Served': 'Temperatura', 'Visual Standard': 'Visual', 'Sauce / Garnish': 'Garnish'}
def newrec(sheet, rid, name, price, portion=None, ing_note=None):
    d, desc, steps, plate = hub(sheet)
    staff = next((v for k, v in plate if k == 'Staff Notes'), '')
    plate = [[LBL.get(k, k), v] for k, v in plate if k != 'Staff Notes']
    return dict(id=rid, name=name, idline=f'ID: {rid} | Precio: {price} | Porción: {portion or d.get("Portion Size", "")}',
                allergens=d.get('Allergens', ''), gf=d.get('Gluten Free?', ''), prep=d.get('Prep Time', ''), desc=desc, staff=staff,
                sections=[{'title': 'INGREDIENTES', 'rows': []}, {'title': 'PREPARACIÓN PASO A PASO', 'rows': steps},
                          {'title': 'PLATEO & ESTÁNDARES', 'rows': plate}],
                ing_note=ing_note or 'NUEVA EN EL MANUAL — tabla de cantidades por confirmar con cocina (el Recipe Hub solo trae el método).',
                img=f'img/{IMG[rid]}.jpg' if rid in IMG else None, photo_note=NOTES.get(rid), section=SECTION(rid), new=True)
out.append(newrec('🦀 Crab Cakes (Plateo)', 'LC-02', 'Crab Cakes', '$34'))
out.append(newrec('🦀 Stone Crab Claws', 'RAW-03', 'Stone Crab Claws', '$59 (Large o Jumbo)',
                  'Large: 3 muelas | Jumbo: 2 muelas (Clover dice "(2)" en ambas — confirmar)'))
out.append(newrec('🦀 Jonah Crab Claws', 'RAW-02', 'Jonah Crab Claws', '$26',
                  '4 claws sobre hielo (Clover: "Cocktail Jonah Crab Claws (5)" — confirmar)'))
out.append(newrec('🐟 Whole Branzino', 'WF-02', 'Whole Branzino Stuffed', '$55 (1.25–1.49 lb) / $62 (1.5–2.0 lb)'))

ORDER = ['OYSTERS & CLAMS — SPECIALTIES', 'SOUPS', 'HOT DISHES', 'CEVICHES & RAW BAR', 'FRESH TUNA & CRUDOS', 'WHOLE FISH',
         'LOBSTER, CRABS & SHRIMP', 'ESPECIALES', 'AWAY FROM THE SEA']
def idkey(i):
    m = re.match(r'([A-Z]+)-(\d+)(\w*)', i); return (m.group(1), int(m.group(2)), m.group(3))
out.sort(key=lambda r: (ORDER.index(r['section']), 0 if not r['id'].startswith('RAW') or r['section'] == 'FRESH TUNA & CRUDOS' else 1, idkey(r['id'])))

# quick reference built from the recipes
def temp(r):
    for s in r['sections']:
        if s['title'] == 'PLATEO & ESTÁNDARES':
            for row in s['rows']:
                if row and (row[0] or '').startswith('Temperatura'): return (row[1] or '').upper()
    return ''
hot = [r['name'] for r in out if temp(r).startswith('HOT')]
cold = [r['name'] for r in out if temp(r).startswith('FRÍO') or temp(r).startswith('FRIO')]
other = [f"{r['name']} ({temp(r).capitalize()})" for r in out if r['name'] not in hot + cold and temp(r)]
ref = [('TEMPERATURAS DE SERVICIO', ['Temperatura', 'Platos'],
        [('HOT — Inmediato', ', '.join(hot)), ('FRÍO — De nevera', ', '.join(cold))] + ([('Otros', ', '.join(other))] if other else []))]
alg = {}
for key, pats in [('Shellfish', ['shellfish']), ('Fish', ['fish']), ('Dairy', ['dairy']), ('Gluten', ['gluten']),
                  ('Eggs', ['egg']), ('Soy', ['soy']), ('Sesame', ['sesame']), ('Alcohol', ['alcohol']), ('Chili', ['chili'])]:
    names = [r['name'] for r in out if any(re.search(r'\b' + p, r['allergens'].lower()) for p in pats)
             and not (key == 'Fish' and 'shellfish' in r['allergens'].lower() and not re.search(r'(^|[^l])fish', r['allergens'].lower().replace('shellfish', '')))]
    alg[key] = names
ref.append(('ALÉRGENOS POR PLATO (verificar siempre con el cliente)', ['Alérgeno', 'Platos que lo contienen'],
            [(k, ', '.join(v)) for k, v in alg.items() if v]))

changes = []
pc = [f"{r['name']} ${r['oldprice']} → ${r['newprice']}" for r in out if r.get('oldprice') and r['oldprice'] != r['newprice']]
changes.append('Precios actualizados según Clover (19 nov 2026): ' + '; '.join(pc) + '.')
nophoto = [r['name'] for r in out if not r.get('img')]
changes.append(f"Se añadió la foto de referencia del Recipe Hub a {sum(1 for r in out if r.get('img'))} de {len(out)} recetas. "
               f"Faltan fotos de: {', '.join(nophoto)}.")
changes.append('Recetas nuevas (tomadas del Recipe Hub, método y plateo; cantidades por confirmar con cocina): Crab Cakes, Stone Crab Claws, Jonah Crab Claws y Whole Branzino Stuffed.')
changes.append('Salmon Crudo ahora aparece con el nombre de Clover: Wild Salmon Sashimi ($18).')
changes.append('Blue Fin Tuna está marcado 86 en Clover hoy; la receta se deja en el manual.')
changes.append('Se añadió índice con número de página y la referencia rápida de temperaturas y alérgenos se arma ahora desde las recetas (antes salía cortada).')
changes.append('Por confirmar con cocina: Wild Mussels y Clams Casserole tienen la misma foto en el Recipe Hub; porciones de Stone Crab (2 vs 3 muelas) y Jonah Claws (4 vs 5) no coinciden con Clover.')
changes.append('No incluido todavía (no tiene receta en el Recipe Hub actual): Snow Crab, Prawns, Whole Snapper, Hot Salmon, Lobster Thermidor, Shrimp/Mahi/Ceviche Tacos, Whole Jonah Crab, Creamy Garlic Potatoes, Arroz Mariscos y otros.')
json.dump(dict(recipes=out, ref=ref, changes=changes, out='/mnt/user-data/outputs/OysterShack_TrainingManual_2026_Nov.pdf'),
          open('final.json', 'w'), ensure_ascii=False, indent=1)
print(len(out)); print('\n'.join(changes)); print(ref[1])
