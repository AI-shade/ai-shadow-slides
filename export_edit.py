# HTML 장을 "글자를 고칠 수 있는" PPT로 바꾼다 (export.py는 통짜 그림).
# 칸·선은 도형, 글자는 글상자, 그림·그라데이션·화살표만 그림으로 넣는다.
# ponytail: 위치는 브라우저가 맑은 고딕으로 그린 자리를 옮긴 것 — 디자인 글꼴(Pretendard)은 PPT에서 따로 바꾼다.
#
#   python export_edit.py  →  dist/아이SHADOW-발표-편집용.pptx
import os, re, io
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

here = os.path.dirname(os.path.abspath(__file__))
dist = os.path.join(here, 'dist')
os.makedirs(dist, exist_ok=True)
html = open(os.path.join(here, 'index.html'), encoding='utf-8').read()
ids = re.findall(r"'(\d+)'", re.search(r'const slides = \[(.*?)\]', html).group(1))

PX = 6350  # EMU per px (1920px = 13.333in)

JS = r"""
() => {
  const out = {shapes: [], texts: [], pics: []};
  const consumed = new Set();
  let n = 0;
  const isInline = el => getComputedStyle(el).display.startsWith('inline') && !['IMG','svg'].includes(el.tagName);
  const visible = (el, cs) => cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0;
  function runs(el, acc, nodes) {
    for (const c of el.childNodes) {
      if (c.nodeType === 3) {
        if (c.textContent.trim() === '' && !/\s/.test(c.textContent)) continue;
        const cs = getComputedStyle(c.parentElement);
        acc.push({t: c.textContent.replace(/\s+/g, ' '), size: parseFloat(cs.fontSize),
                  w: +cs.fontWeight, color: cs.color, need: false});
        nodes.push(c);
      } else if (c.nodeType === 1) {
        if (c.tagName === 'BR') { acc.push({br: true}); continue; }
        const cs = getComputedStyle(c);
        if (!visible(c, cs)) continue;
        if (isInline(c)) { consumed.add(c); runs(c, acc, nodes); }
      }
    }
  }
  for (const el of document.querySelectorAll('body, body *')) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const box = {x: r.left, y: r.top, w: r.width, h: r.height};
    const pic = ['IMG', 'svg'].includes(el.tagName) || cs.backgroundImage.includes('gradient');
    if (el.closest('svg') && el.tagName !== 'svg') continue;
    if (pic) { el.dataset.pic = ++n; out.pics.push({id: n, ...box, kids: el.tagName !== 'IMG' && el.tagName !== 'svg' ? 0 : 1}); }
    else if (el !== document.body) {
      const b = s => ({w: parseFloat(cs[`border${s}Width`]), c: cs[`border${s}Color`], st: cs[`border${s}Style`]});
      out.shapes.push({...box, bg: cs.backgroundColor, rad: parseFloat(cs.borderTopLeftRadius) || 0,
        b: ['Top','Right','Bottom','Left'].map(b)});
    }
    if (consumed.has(el) || isInline(el) || pic && el.tagName !== 'DIV') continue;
    const acc = [], nodes = [];
    runs(el, acc, nodes);
    if (!acc.some(a => a.t && a.t.trim())) continue;
    // 앞뒤 공백 정리
    const tx = acc.filter(a => a.t !== undefined);
    tx[0].t = tx[0].t.replace(/^\s+/, ''); tx[tx.length-1].t = tx[tx.length-1].t.replace(/\s+$/, '');
    const rg = document.createRange();
    rg.setStartBefore(nodes[0]); rg.setEndAfter(nodes[nodes.length-1]);
    const tr = rg.getBoundingClientRect();
    let mx = 0;  // 목록 번호(::marker)는 글자가 아니라서 따로 붙인다
    if (el.tagName === 'LI' && cs.listStyleType !== 'none' && cs.display === 'list-item') {
      const k = [...el.parentElement.children].indexOf(el) + 1;
      acc.unshift({t: el.parentElement.tagName === 'OL' ? k + '. ' : '• ', size: parseFloat(cs.fontSize), w: +cs.fontWeight, color: cs.color});
      mx = parseFloat(cs.fontSize) * 1.4;
    }
    out.texts.push({x: tr.left - mx, y: tr.top, w: tr.width + mx, h: tr.height, runs: acc,
      align: cs.textAlign, lh: parseFloat(cs.lineHeight) / parseFloat(cs.fontSize) || 1.3,
      ls: parseFloat(cs.letterSpacing) || 0});
  }
  return out;
}
"""

def rgb(s):
    v = [float(x) for x in re.findall(r'[\d.]+', s)]
    if len(v) < 3: return None
    a = v[3] if len(v) > 3 else 1
    if a == 0: return None
    return RGBColor(*[round(c * a + 255 * (1 - a)) for c in v[:3]])  # 흰 바탕에 섞음

def e(v): return Emu(round(v * PX))

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(1920 * PX), Emu(1080 * PX)

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)
    for i in ids:
        page.goto('file:///' + os.path.join(here, 'slides', i + '.html').replace('\\', '/'))
        page.wait_for_load_state('networkidle')
        # PPT엔 Pretendard가 없으니 어디나 있는 맑은 고딕으로 다시 배치한 뒤 잰다
        page.add_style_tag(content='*{font-family:"Malgun Gothic" !important}')
        page.evaluate('document.fonts.ready')
        d = page.evaluate(JS)
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        sp = sl.shapes
        bg = sl.background.fill; bg.solid(); bg.fore_color.rgb = RGBColor(255, 255, 255)

        # 1) 칸 · 선
        for s in d['shapes']:
            fill = rgb(s['bg'])
            bs = [x for x in s['b'] if x['w'] > 0 and x['st'] != 'none' and rgb(x['c'])]
            same = len(bs) == 4 and len({(x['w'], x['c']) for x in bs}) == 1
            if fill or same:
                shp = sp.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if s['rad'] else MSO_SHAPE.RECTANGLE,
                                   e(s['x']), e(s['y']), e(s['w']), e(s['h']))
                if s['rad']:
                    shp.adjustments[0] = min(0.5, s['rad'] / min(s['w'], s['h']))
                if fill: shp.fill.solid(); shp.fill.fore_color.rgb = fill
                else: shp.fill.background()
                if same:
                    w = bs[0]['w']
                    # 테두리는 안쪽 선 기준이라 반 굵기만큼 안으로
                    shp.left, shp.top = e(s['x'] + w / 2), e(s['y'] + w / 2)
                    shp.width, shp.height = e(s['w'] - w), e(s['h'] - w)
                    shp.line.color.rgb = rgb(bs[0]['c']); shp.line.width = e(w)
                else: shp.line.fill.background()
                shp.shadow.inherit = False
            if not same:
                for k, x in enumerate(s['b']):
                    if x['w'] <= 0 or x['st'] == 'none' or not rgb(x['c']): continue
                    w = x['w']
                    xy = [(s['x'], s['y'], s['w'], w), (s['x'] + s['w'] - w, s['y'], w, s['h']),
                          (s['x'], s['y'] + s['h'] - w, s['w'], w), (s['x'], s['y'], w, s['h'])][k]
                    ln = sp.add_shape(MSO_SHAPE.RECTANGLE, *map(e, xy))
                    ln.fill.solid(); ln.fill.fore_color.rgb = rgb(x['c']); ln.line.fill.background()
                    ln.shadow.inherit = False

        # 2) 그림 (img · svg · 그라데이션 · 화살표) — 그 요소만 남기고 투명 배경으로 찍는다
        for pc in d['pics']:
            sel = f'[data-pic="{pc["id"]}"]'
            kids = 'visible' if pc['kids'] else 'hidden'
            st = page.add_style_tag(content=f'* {{visibility:hidden !important}} {sel} {{visibility:visible !important}} {sel} * {{visibility:{kids} !important}} html,body{{background:transparent !important}}')
            png = page.screenshot(clip={'x': pc['x'], 'y': pc['y'], 'width': pc['w'], 'height': pc['h']}, omit_background=True)
            st.evaluate('s => s.remove()')
            sp.add_picture(io.BytesIO(png), e(pc['x']), e(pc['y']), e(pc['w']), e(pc['h']))

        # 3) 글자 — 맨 위에
        for t in d['texts']:
            slack = t['w'] * 0.04 + 8  # 글꼴 폭 차이로 줄이 넘어가지 않게 여유
            x = t['x'] - (slack / 2 if t['align'] == 'center' else slack if t['align'] in ('right', 'end') else 0)
            tb = sp.add_textbox(e(x), e(t['y']), e(t['w'] + slack), e(t['h']))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.TOP
            para = tf.paragraphs[0]
            def setp(pp):
                pp.alignment = {'center': PP_ALIGN.CENTER, 'right': PP_ALIGN.RIGHT, 'end': PP_ALIGN.RIGHT}.get(t['align'], PP_ALIGN.LEFT)
                pp.line_spacing = t['lh'] * 0.85  # PPT 줄 간격 배수는 브라우저보다 넓게 잡힌다
            setp(para)
            for r in t['runs']:
                if r.get('br'):
                    para = tf.add_paragraph(); setp(para); continue
                if not r['t']: continue
                run = para.add_run(); run.text = r['t']
                f = run.font
                f.name = '맑은 고딕'; f.size = Pt(r['size'] * 0.5); f.bold = r['w'] >= 600
                c = rgb(r['color'])
                if c: f.color.rgb = c
    b.close()

out = os.path.join(dist, '아이SHADOW-발표-편집용.pptx')
prs.save(out)
print(len(ids), '장 →', out)
