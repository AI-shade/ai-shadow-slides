# 발표 슬라이드

## 바로 보기 (설치 없이, 휴대폰도 됨)

- 슬라이드: https://ai-shade.github.io/ai-shadow-slides/
- 발표 설계도: https://ai-shade.github.io/ai-shadow-slides/blueprint.html

> 이 GitHub 화면에서 `.html` 파일을 누르면 화면이 아니라 **코드**가 보입니다.
> 화면으로 보려면 위 링크를 쓰세요. 푸시하고 1~2분 뒤에 반영됩니다.

슬라이드 주소를 열면 **17장이 위에서 아래로 한 번에** 보입니다(스크롤).
장을 누르거나 **발표 모드 ▶** 단추(또는 `P` 키)를 누르면 그 장부터 화면 가득 한 장씩 넘깁니다.
1920×1080 고정 화면을 창 크기에 맞춰 비율 그대로 줄여 보여 줍니다.

## 내 컴퓨터에서 열기

1. 초록색 **Code** 버튼 → **Download ZIP** (또는 `git clone`)
2. 압축을 풀고 `index.html`(슬라이드)이나 `blueprint.html`(설계도)을 더블클릭.
   서버가 필요 없습니다.

발표 모드 넘기기: `→` / `←` / 스페이스 (발표 리모컨의 PageDown / PageUp 도 됩니다) · 목록으로: `Esc`.
주소 끝 `#03` 처럼 장 번호를 붙이면 그 장으로 스크롤합니다.

## 구조

```
index.html     장 파일을 순서대로 스크롤로 보여 주고, 발표 모드에서 방향키로 넘김
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

1. `slides/` 안의 파일 하나를 복사해 `18.html` 처럼 이름을 붙입니다.
2. `index.html`의 `slides` 목록에 `'18'`을, `names` 목록에 그 장 이름을 같은 자리에 넣습니다.

내용은 `blueprint.html`(발표 설계도)을 보고 만듭니다. 설계도가 바뀌면 해당 장 파일도 같이 고칩니다.
