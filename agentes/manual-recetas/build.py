import json, re, os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether, NextPageTemplate, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents

W, H = letter
RED = colors.HexColor('#8E1B1B'); RED2 = colors.HexColor('#C0392B'); NAVY = colors.HexColor('#0F1B2B')
NAVY2 = colors.HexColor('#1B3A5C'); GOLD = colors.HexColor('#C9A227'); CREAM = colors.HexColor('#FBF6EE')
GREY = colors.HexColor('#F2F2F2'); LINE = colors.HexColor('#D9D2C5'); YEL = colors.HexColor('#FFF4CC')
YELB = colors.HexColor('#E0B84A'); TXT = colors.HexColor('#222222'); MUTED = colors.HexColor('#7A7A7A')

def S(name, **kw):
    base = dict(fontName='Helvetica', fontSize=8.6, leading=11, textColor=TXT)
    base.update(kw); return ParagraphStyle(name, **base)
sBody = S('b'); sSmall = S('s', fontSize=7.8, leading=10); sMutedI = S('mi', fontSize=7.8, leading=10, textColor=MUTED, fontName='Helvetica-Oblique')
sDesc = S('d', fontName='Helvetica-Oblique', fontSize=8.8, leading=12)
sTitle = S('t', fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.white)
sIdl = S('i', fontSize=8, leading=10, textColor=GOLD)
sBand = S('band', fontName='Helvetica-Bold', fontSize=8.6, leading=11, textColor=colors.white)
sHead = S('h', fontName='Helvetica-Bold', fontSize=7.8, leading=10, textColor=colors.white)
sStepK = S('k', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=RED)
sSect = S('sec', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.white, alignment=TA_CENTER)
sStaff = S('st', fontName='Helvetica-BoldOblique', fontSize=8.2, leading=11, textColor=colors.HexColor('#7A5A00'))
sSub = S('sub', fontName='Helvetica-Bold', fontSize=7.8, leading=10, textColor=NAVY2)

def esc(t):
    t = (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'(?<=\s)fi(?=\s)', '→', t)
    return t.replace('\n', ' ')
def P(t, st=sBody): return Paragraph(esc(t), st)

CW = W - 1.3 * inch  # content width

def band(text, color, size=None):
    t = Table([[Paragraph(esc(text), sBand)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), color), ('LEFTPADDING', (0, 0), (-1, -1), 7),
                           ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    return t

class Section(Table):
    pass

def section_banner(text, color=RED):
    t = Table([[Paragraph(esc(text), sSect)]], colWidths=[CW], rowHeights=[0.5 * inch])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), color), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    t._toc = (0, text)
    return t

def photo_cell(img, size):
    if img and os.path.exists(img):
        return Image(img, width=size, height=size)
    t = Table([[Paragraph('FOTO PENDIENTE', S('fp', fontName='Helvetica-Bold', fontSize=9, textColor=MUTED, alignment=TA_CENTER))],
               [Paragraph('Tomar foto del plateo estándar', S('fp2', fontSize=7, textColor=MUTED, alignment=TA_CENTER))]],
              colWidths=[size], rowHeights=[size / 2, size / 2])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), GREY), ('BOX', (0, 0), (-1, -1), 0.8, LINE),
                           ('VALIGN', (0, 0), (0, 0), 'BOTTOM'), ('VALIGN', (0, 1), (0, 1), 'TOP')]))
    return t

def recipe_flow(r):
    out = []
    # header band
    hdr = Table([[Paragraph(esc(r['name']), sTitle)], [Paragraph(esc(r['idline']), sIdl)]], colWidths=[CW])
    hdr.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), RED), ('LEFTPADDING', (0, 0), (-1, -1), 9),
                             ('TOPPADDING', (0, 0), (0, 0), 8), ('BOTTOMPADDING', (0, -1), (0, -1), 7),
                             ('TOPPADDING', (0, 1), (0, 1), 0)]))
    hdr._toc = (1, r['name'], r['id'])
    out.append(hdr)
    # photo + info block
    ps = 2.35 * inch
    rw = CW - ps - 0.18 * inch
    info = Table([[P('<b>Alérgenos</b>'.replace('&lt;', '<'), sSmall), P(r['allergens'], sSmall)],
                  [P('GF', sSmall), P(r['gf'], sSmall)],
                  [P('Prep', sSmall), P(r['prep'], sSmall)]], colWidths=[0.75 * inch, rw - 0.75 * inch])
    info.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), GREY), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                              ('LINEBELOW', (0, 0), (-1, -2), 0.4, LINE), ('BOX', (0, 0), (-1, -1), 0.4, LINE),
                              ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    # bold label fix
    for i, lab in enumerate(['Alérgenos', 'GF', 'Prep']):
        info._cellvalues[i][0] = Paragraph(f'<b>{lab}</b>', sSmall)
    right = [info, Spacer(1, 6), P(r['desc'], sDesc)]
    if r.get('staff'):
        st = Table([[Paragraph('STAFF: ' + esc(r['staff']), sStaff)]], colWidths=[rw])
        st.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), YEL), ('BOX', (0, 0), (-1, -1), 0.8, YELB),
                                ('LEFTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
        right += [Spacer(1, 6), st]
    if r.get('photo_note'):
        right += [Spacer(1, 4), P(r['photo_note'], sMutedI)]
    blk = Table([[photo_cell(r.get('img'), ps), right]], colWidths=[ps + 0.18 * inch, rw])
    blk.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0)]))
    out += [Spacer(1, 8), blk, Spacer(1, 10)]

    for sec in r['sections']:
        title, rows = sec['title'], sec['rows']
        if title == 'INGREDIENTES':
            data = [[Paragraph(h, sHead) for h in ['Ingrediente', 'Cantidad', 'Unidad', 'Notas']]]
            style = [('BACKGROUND', (0, 0), (-1, 0), RED), ('GRID', (0, 0), (-1, -1), 0.4, LINE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]
            body = [x for x in rows if x and (x[0] or '') != 'Ingrediente']
            if not body:
                data.append([P(r.get('ing_note', 'Cantidades por confirmar con cocina.'), sMutedI), '', '', ''])
                style.append(('SPAN', (0, 1), (-1, 1)))
            for x in body:
                x = (list(x) + [None] * 4)[:4]
                i = len(data)
                if x[0] and x[1] is None and x[2] is None:
                    data.append([Paragraph('&#9632; ' + esc(re.sub(r'^n+\s*', '', x[0])), sSub), '', '', ''])
                    style += [('SPAN', (0, i), (-1, i)), ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E8EEF5'))]
                else:
                    data.append([P(x[0] or ''), P(x[1] or ''), P(x[2] or ''), P(x[3] or '', sMutedI)])
                    if i % 2 == 0: style.append(('BACKGROUND', (0, i), (-1, i), CREAM))
            t = Table(data, colWidths=[CW * 0.36, CW * 0.15, CW * 0.13, CW * 0.36], repeatRows=1)
            t.setStyle(TableStyle(style))
            out += [band('INGREDIENTES', RED2), t, Spacer(1, 8)]
        elif title == 'PREPARACIÓN PASO A PASO':
            data = [[P(a or '', sStepK), P(b or '')] for a, b in [(list(x) + [None, None])[:2] for x in rows]]
            t = Table(data, colWidths=[CW * 0.2, CW * 0.8])
            st = [('GRID', (0, 0), (-1, -1), 0.4, LINE), ('BACKGROUND', (0, 0), (0, -1), CREAM),
                  ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]
            t.setStyle(TableStyle(st))
            out += [band('PREPARACIÓN PASO A PASO', RED2), t, Spacer(1, 8)]
        elif title == 'PLATEO & ESTÁNDARES':
            data = [[P(a or '', sStepK), P(b or '')] for a, b in [(list(x) + [None, None])[:2] for x in rows]]
            t = Table(data, colWidths=[CW * 0.2, CW * 0.8])
            t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, LINE), ('BACKGROUND', (0, 0), (0, -1), GREY),
                                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
            out += [KeepTogether([band('PLATEO & ESTÁNDARES', NAVY2), t])]
    return out

class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, '_toc'):
            v = f._toc
            if v[0] == 0:
                self.notify('TOCEntry', (0, v[1].title() if False else v[1], self.page))
            else:
                self.notify('TOCEntry', (1, f'{v[2]}  ·  {v[1]}', self.page))

def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(RED); c.rect(0, H - 10, W, 10, fill=1, stroke=0); c.rect(0, 0, W, 34, fill=1, stroke=0)
    c.setFillColor(GOLD); c.rect(0, H - 13, W, 3, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 34); c.drawCentredString(W / 2, H * 0.62, 'THE OYSTER SHACK')
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 21); c.drawCentredString(W / 2, H * 0.62 - 34, 'RECIPE & TRAINING MANUAL')
    c.setFont('Helvetica', 13); c.drawCentredString(W / 2, H * 0.62 - 64, 'Manual de Recetas y Entrenamiento para Staff')
    c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.line(W / 2 - 130, H * 0.62 - 86, W / 2 + 130, H * 0.62 - 86)
    c.setFillColor(colors.white); c.setFont('Helvetica', 9.5)
    for i, l in enumerate(['Versión Noviembre 2026 — con foto de referencia por plato | Confidencial — Solo para uso interno del equipo',
                           'Este manual contiene las recetas oficiales, estándares de plateo y notas de staff.',
                           'Precios verificados en Clover el 19 de noviembre de 2026.',
                           'Preparado por Oversized Media para The Oyster Shack.']):
        c.drawCentredString(W / 2, H * 0.62 - 112 - i * 16, l)
    c.setFont('Helvetica', 8); c.drawString(0.65 * inch, 13, 'CONFIDENTIAL — FOR STAFF USE ONLY'); c.drawRightString(W - 0.65 * inch, 13, 'The Oyster Shack  |  Nov 2026')
    c.restoreState()

def page(c, d):
    c.saveState()
    c.setFillColor(RED); c.rect(0, 0, W, 26, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica', 7.5)
    c.drawString(0.65 * inch, 10, 'THE OYSTER SHACK — RECIPE & TRAINING MANUAL  |  Confidential  |  Nov 2026')
    c.drawRightString(W - 0.65 * inch, 10, f'Página {d.page}')
    c.restoreState()

def build(data, ref, changes, out):
    doc = Doc(out, pagesize=letter, title='The Oyster Shack — Recipe & Training Manual (Nov 2026)',
              author='Oversized Media / Joseph Rodriguez', leftMargin=0.65 * inch, rightMargin=0.65 * inch,
              topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    fr = Frame(doc.leftMargin, doc.bottomMargin, CW, H - doc.topMargin - doc.bottomMargin, id='f')
    doc.addPageTemplates([PageTemplate('cover', [fr], onPage=cover), PageTemplate('body', [fr], onPage=page)])
    story = [NextPageTemplate('body'), PageBreak()]
    # how to use
    story.append(section_banner('CÓMO USAR ESTE MANUAL', NAVY))
    legend = [('CRÍTICO', 'Texto en rojo o advertencias en amarillo = regla que NO se puede romper.'),
              ('STAFF NOTE', 'Banners amarillos = información clave para el servicio.'),
              ('GF', 'Gluten Free. GF* = disponible con modificación (ej: cambiar tostadas por malanga chips).'),
              ('BATCH', 'Preparado en cantidad por adelantado. Verificar disponibilidad antes del servicio.'),
              ('DEL BATCH', 'Servir directamente del contenedor pre-hecho en línea o nevera.'),
              ('HOT / FRÍO', 'Temperatura de servicio — indicado en cada receta.'),
              ('AL MOMENTO', 'Preparar solo cuando el cliente lo ordena — no con anticipación.'),
              ('FOTO', 'Cada receta trae su foto de referencia: así debe salir el plato. Si dice "Foto pendiente", hay que tomarla.')]
    t = Table([[P(a, sStepK), P(b)] for a, b in legend], colWidths=[CW * 0.2, CW * 0.8])
    t.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    story += [Spacer(1, 8), t, Spacer(1, 16), section_banner('NORMAS GENERALES')]
    for n in ['NUNCA servir almeja, mussel u ostra CERRADA — descartar siempre sin excepción.',
              'NUNCA descongelar pescado o mariscos a temperatura ambiente — siempre en nevera.',
              'CONFIRMAR alergias a mariscos, pescado, lácteos y sésamo en cada orden.',
              'ADVERTIR siempre al cliente cuando el plato contiene pescado crudo.',
              'ADVERTIR siempre al cliente cuando el plato o vajilla está extremadamente caliente.',
              'Grupos de 6+ personas tienen 18% de propina automática — recordar al staff al momento de imprimir el ticket.',
              'GF* = disponible sin gluten con modificación — confirmar siempre con el cliente.']:
        story += [Spacer(1, 5), P('• ' + n)]
    # TOC
    toc = TableOfContents()
    toc.levelStyles = [S('toc0', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=RED, spaceBefore=6),
                       S('toc1', fontSize=8.6, leading=11.5, leftIndent=14)]
    ix = section_banner('ÍNDICE', NAVY); del ix._toc
    story += [PageBreak(), ix, Spacer(1, 8), toc]
    cur = None
    for r in data:
        if r['section'] != cur:
            cur = r['section']
            story += [PageBreak(), section_banner(cur), Spacer(1, 10)]
        else:
            story.append(PageBreak())
        story += recipe_flow(r)
    # reference
    story += [PageBreak(), section_banner('REFERENCIA RÁPIDA', NAVY), Spacer(1, 8)]
    for title, head, rows in ref:
        data_ = [[Paragraph(h, sHead) for h in head]] + [[P(a, sStepK), P(b)] for a, b in rows]
        t = Table(data_, colWidths=[CW * 0.22, CW * 0.78], repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY2), ('GRID', (0, 0), (-1, -1), 0.4, LINE),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
        story += [band(title, RED2), t, Spacer(1, 12)]
    story += [PageBreak(), section_banner('CAMBIOS EN ESTA VERSIÓN (vs junio 2026)', NAVY), Spacer(1, 8)]
    for c in changes:
        story += [P('• ' + c), Spacer(1, 4)]
    doc.multiBuild(story)

if __name__ == '__main__':
    d = json.load(open('final.json'))
    build(d['recipes'], d['ref'], d['changes'], d['out'])
