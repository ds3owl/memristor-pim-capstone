# -*- coding: utf-8 -*-
"""
build_b5.py — paper_v8_10p.html을 학과 양식(B5) HTML로 변환.
- 용지: B5(182x257mm), 여백 상하15mm/좌우25mm (양식 실측)
- front matter: 표지/속표지/인준서/차례(십진식)/국문요약
- 본문 번호: IEEE(I., A.) -> 한글 십진식(1., 1.1)
- base64 이미지 -> figures/ 파일 참조 (Phase 4에서 재임베드)
출력: paper_b5.html
"""
import re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(BASE, "paper_v8_10p.html"), encoding="utf-8").read()

# ---- 본문 추출: <h1>I. 서론 부터 </body> 직전까지 ----
m = re.search(r'(<h1>\s*I\.\s*서론.*?)</body>', src, re.S)
body = m.group(1)

# ---- 국문요약용 초록 텍스트 추출 ----
ab = re.search(r'<div class="abstract">(.*?)</div>', src, re.S).group(1)
ab = re.sub(r'<h3>.*?</h3>', '', ab, flags=re.S).strip()

# ---- base64 이미지 -> 파일 참조 (등장 순서대로) ----
fig_files = ["figures/material_comparison.png", "figures/bimodal_distribution.png"]
_idx = [0]
def repl_img(mt):
    f = fig_files[_idx[0]] if _idx[0] < len(fig_files) else fig_files[-1]
    _idx[0] += 1
    return f'src="{f}"'
body = re.sub(r'src="data:image/[^"]+"', repl_img, body)

# ---- 헤딩 번호 변환 (단일 순차 스캔으로 H1->sec, H2->sec.sub) ----
ROMAN = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6}
state = {'sec': 0}
def conv_heading(mt):
    inner = mt.group(1) if mt.group(1) is not None else mt.group(2)
    is_h1 = mt.group(1) is not None
    inner = inner.strip()
    if is_h1:
        rm = re.match(r'([IVX]+)\.\s*(.*)', inner, re.S)
        if rm and rm.group(1) in ROMAN:
            state['sec'] = ROMAN[rm.group(1)]
            title = re.sub(r'\s*\([^)]*\)\s*$', '', rm.group(2).strip())
            return f'<h1>{state["sec"]}. {title}</h1>'
        # 참고문헌 등 번호 없는 H1
        plain = re.sub(r'\s*\([^)]*\)\s*$', '', inner)
        return f'<h1>{plain}</h1>'
    else:
        hm = re.match(r'([A-E])\.\s*(.*)', inner, re.S)
        if hm:
            sub = ord(hm.group(1)) - 64
            return f'<h2>{state["sec"]}.{sub} {hm.group(2).strip()}</h2>'
        return f'<h2>{inner}</h2>'
body = re.sub(r'<h1>(.*?)</h1>|<h2>(.*?)</h2>', conv_heading, body, flags=re.S)

# 본문 내 "II장"~"VI장" 참조 -> 숫자
for r,n in [('VI',6),('IV',4),('III',3),('II',2),('V',5)]:
    body = body.replace(f'{r}장', f'{n}장')

# ---- 새 CSS ----
CSS = """
  @page { size: 182mm 257mm; margin: 15mm 25mm 15mm 25mm; }
  * { box-sizing: border-box; }
  body {
    font-family: "함초롬바탕", "바탕", Batang, "Times New Roman", serif;
    font-size: 10.5pt; line-height: 1.6; color: #111; margin: 0;
    background: #8a9099;
  }
  /* 화면: 종이 한 장처럼 보이게 */
  .sheet {
    width: 182mm; min-height: 257mm; padding: 15mm 25mm;
    margin: 8mm auto; background: #fff;
    box-shadow: 0 1px 8px rgba(0,0,0,.45);
  }
  .flow {                      /* 본문(여러 페이지가 이어짐) */
    width: 182mm; padding: 15mm 25mm; margin: 8mm auto;
    background: #fff; box-shadow: 0 1px 8px rgba(0,0,0,.45);
  }
  h1 { font-size: 15pt; font-weight: bold; margin: 9mm 0 4mm; }
  h2 { font-size: 12pt; font-weight: bold; margin: 6mm 0 3mm; }
  h3 { font-size: 11pt; margin: 5mm 0 2mm; }
  p { text-align: justify; margin: 4px 0; text-indent: 1em; }
  p.noindent { text-indent: 0; }
  table { border-collapse: collapse; margin: 6px auto; font-size: 9pt; }
  th, td { border: 1px solid #555; padding: 3px 7px; text-align: center; }
  th { background: #eee; }
  .caption { text-align: center; font-size: 9pt; font-style: italic; color: #444; margin: 3px 0 10px; }
  .figure { text-align: center; margin: 10px 0; page-break-inside: avoid; }
  .figure img { max-width: 95%; border: 1px solid #ccc; }
  .equation { text-align: center; font-style: italic; margin: 6px 0; }
  .keywords { font-size: 9.5pt; color: #333; }
  .references { font-size: 9.5pt; }
  .references ol { padding-left: 20px; }
  .references li { margin: 3px 0; text-align: left; text-indent: 0; }
  /* front matter */
  .cover, .inner, .approval { text-align: center; }
  .cover .deg { font-size: 16pt; font-weight: bold; margin: 18mm 0 28mm; letter-spacing: 4px; }
  .ko-title { font-size: 17pt; font-weight: bold; line-height: 1.6; margin: 8mm 0; }
  .en-title { font-size: 11pt; color: #444; line-height: 1.5; margin: 6mm 0; }
  .fm-info { font-size: 12pt; line-height: 2.2; margin-top: 16mm; }
  .approval .judge { text-align: left; width: 70%; margin: 6mm auto; font-size: 12pt; line-height: 3; }
  .toc h1 { text-align:center; border:none; }
  .toc ul { list-style: none; padding-left: 0; font-size: 10.5pt; }
  .toc li { padding: 2.5px 0; }
  .toc li.s1 { padding-left: 14px; }
  .toc li.s2 { padding-left: 30px; color:#333; }
  @media print {
    body { background: #fff; }
    .sheet, .flow { width: auto; min-height: 0; margin: 0; padding: 0; box-shadow: none; }
    .sheet { page-break-after: always; }
  }
"""

# ---- front matter ----
TITLE_KO = "4종 멤리스터 소재 파라미터를 활용한<br>PIM 환경 웨이퍼 결함 분류 성능 비교 연구"
TITLE_EN = "A Comparative Study of Four Memristive Material Candidates<br>for Processing-In-Memory Wafer Defect Classification"

cover = f"""<section class="sheet cover">
  <div class="deg">학사학위논문</div>
  <div class="ko-title">{TITLE_KO}</div>
  <div class="en-title">{TITLE_EN}</div>
  <div class="fm-info">
    상명대학교 공과대학<br>시스템반도체공학과<br>임 창 우<br><br>2026년　 　월
  </div>
</section>"""

inner = f"""<section class="sheet inner">
  <div class="ko-title" style="margin-top:14mm">{TITLE_KO}</div>
  <div class="en-title">{TITLE_EN}</div>
  <div class="fm-info" style="margin-top:10mm">
    지도교수　이 종 환<br><br>
    이 논문을 학사학위 논문으로 제출함<br><br>
    2026년　 　월<br><br>
    상명대학교 공과대학<br>시스템반도체공학과<br>임 창 우
  </div>
</section>"""

approval = """<section class="sheet approval">
  <div class="ko-title" style="margin-top:30mm">임창우의 학사학위 논문을<br>인준함</div>
  <div class="judge" style="margin-top:24mm">
    심사위원장　　　　　　　　　　(인)<br>
    심사위원　　　　　　　　　　　(인)<br>
    심사위원　　　　　　　　　　　(인)
  </div>
  <div class="fm-info" style="margin-top:20mm">상명대학교 공과대학<br><br>2026년　 　월</div>
</section>"""

toc = """<section class="sheet toc">
  <h1>차　　례</h1>
  <ul>
    <li><b>국문 요약</b></li>
    <li><b>1. 서론</b></li>
    <li class="s1">1.1 연구 배경</li>
    <li class="s1">1.2 선행 연구의 한계</li>
    <li class="s1">1.3 본 연구의 기여</li>
    <li><b>2. 이론적 배경</b></li>
    <li class="s1">2.1 Processing-In-Memory (PIM)</li>
    <li class="s1">2.2 멤리스터 크로스바 어레이</li>
    <li class="s1">2.3 VTEAM 모델</li>
    <li class="s1">2.4 웨이퍼 결함 분류와 CNN</li>
    <li><b>3. 방법론</b></li>
    <li class="s1">3.1 데이터셋</li>
    <li class="s1">3.2 CNN 모델 구조</li>
    <li class="s1">3.3 4종 소재 파라미터</li>
    <li class="s1">3.4 매핑·양자화 및 비이상성 모델</li>
    <li class="s1">3.5 평가 프로토콜</li>
    <li><b>4. 결과</b></li>
    <li class="s1">4.1 Baseline (FP32 software) 성능</li>
    <li class="s1">4.2 4 소재 Ideal vs Realistic 비교</li>
    <li class="s1">4.3 Worst-case 붕괴 현상 분석</li>
    <li class="s1">4.4 결함 유형별 (per-class) F1 분석</li>
    <li><b>5. 논의</b></li>
    <li class="s1">5.1 저항비의 영향</li>
    <li class="s1">5.2 Metallic Nanowire의 본질적 한계</li>
    <li class="s1">5.3 Worst-case 붕괴 현상의 PIM 함의</li>
    <li class="s1">5.4 한계 및 향후 과제</li>
    <li><b>6. 결론</b></li>
    <li><b>참고문헌</b></li>
  </ul>
</section>"""

summary = f"""<section class="sheet summary">
  <h1 style="text-align:center;border:none">국 문 요 약</h1>
  <p class="noindent">{ab}</p>
</section>"""

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>4종 멤리스터 소재 파라미터를 활용한 PIM 환경 웨이퍼 결함 분류 성능 비교 연구</title>
<style>{CSS}</style>
</head>
<body>
{cover}
{inner}
{approval}
{toc}
{summary}
<main class="flow">
{body}
</main>
</body>
</html>"""

open(os.path.join(BASE, "paper_b5.html"), "w", encoding="utf-8").write(html)
print("paper_b5.html 생성, 길이", len(html))
print("본문 글자수(태그제외 근사):", len(re.sub(r'<[^>]+>','',body).replace(' ','')))
