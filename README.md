# 발표 슬라이드

1920×1080 고정 화면을 브라우저 창 크기에 맞춰 비율 그대로 줄여 보여 줍니다.

## 여는 법

- **그냥 열기**: `index.html`을 더블클릭해 브라우저로 엽니다. 서버가 필요 없습니다.
- **깃허브 페이지**: 저장소 Settings → Pages → 이 폴더가 있는 브랜치를 고르면
  `https://<계정>.github.io/<저장소>/` 에서 열립니다.

넘기기: `→` / `←` (발표 리모컨의 PageDown / PageUp 도 됩니다).
주소 끝 `#03` 처럼 장 번호를 붙이면 그 장부터 엽니다.

## 구조

```
index.html     장 파일을 순서대로 불러오고 방향키로 넘김
theme.css      색 · 글꼴 · 글자 크기 (여기서만 고침)
slides/01.html 장마다 한 파일 (제목 + 본문)
```

## PPT · PDF로 내보내기 (대회 제출용)

현장 발표는 PPT 파일로 하므로, HTML을 고친 뒤 이것만 돌립니다.

```
pip install playwright python-pptx pillow
python -m playwright install chromium
python export.py
```

`dist/아이SHADOW-발표.pptx` 와 `.pdf` 가 생깁니다. 장마다 그림 한 장이라
운영 PC에 글꼴이 없어도 깨지지 않습니다. 대신 PPT 안에서 글자는 못 고치니,
고칠 땐 HTML을 고치고 다시 돌리세요.

## 장 추가

1. `slides/` 안의 파일 하나를 복사해 `06.html` 처럼 이름을 붙입니다.
2. `index.html`의 `slides` 목록에 `'06'`을 넣습니다.
