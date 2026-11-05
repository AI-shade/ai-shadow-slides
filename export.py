# HTML 장 파일을 그대로 찍어서 PPT와 PDF로 만든다.
# 장마다 1920×1080 그림 한 장이라 운영 PC에 글꼴이 없어도 깨지지 않는다.
# ponytail: 그림이라 PPT 안에서 글자를 못 고친다 — 고칠 땐 HTML을 고치고 다시 돌린다.
#
#   python export.py   →  dist/아이SHADOW-발표.pptx, dist/아이SHADOW-발표.pdf
import os, re
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Emu
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
dist = os.path.join(here, 'dist')
os.makedirs(dist, exist_ok=True)

# 장 순서는 index.html 목록 하나만 본다
html = open(os.path.join(here, 'index.html'), encoding='utf-8').read()
ids = re.findall(r"'(\d+)'", re.search(r'const slides = \[(.*?)\]', html).group(1))

shots = []
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)
    for i in ids:
        page.goto('file:///' + os.path.join(here, 'slides', i + '.html').replace('\\', '/'))
        page.wait_for_load_state('networkidle')
        out = os.path.join(dist, i + '.png')
        page.screenshot(path=out)
        shots.append(out)
    b.close()

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)  # 16:9
for s in shots:
    sl = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 장
    sl.shapes.add_picture(s, 0, 0, prs.slide_width, prs.slide_height)
prs.save(os.path.join(dist, '아이SHADOW-발표.pptx'))

imgs = [Image.open(s).convert('RGB') for s in shots]
imgs[0].save(os.path.join(dist, '아이SHADOW-발표.pdf'), save_all=True, append_images=imgs[1:], resolution=144)

for s in shots:
    os.remove(s)
print(len(shots), '장 →', dist)
