"""paper.html -> 본문 텍스트 추출(base64 제거) + 섹션별 글자수 집계."""
import re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(BASE, "paper_v8_10p.html")
html = open(src, encoding="utf-8").read()

# base64 이미지 src 제거
html = re.sub(r'src="data:image[^"]*"', 'src="[IMG]"', html)
# style/script 제거
html = re.sub(r'<style.*?</style>', '', html, flags=re.S)
html = re.sub(r'<script.*?</script>', '', html, flags=re.S)

# 헤딩을 마크다운으로
def repl_h(m):
    lvl = int(m.group(1)); txt = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    return "\n" + "#" * lvl + " " + txt + "\n"
html = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>', repl_h, html, flags=re.S)
# 표/그림 표시
html = re.sub(r'<table', '\n[TABLE]<table', html)
html = re.sub(r'<figure', '\n[FIGURE]', html)
# 나머지 태그 제거
text = re.sub(r'<[^>]+>', '', html)
text = re.sub(r'\n{3,}', '\n\n', text).strip()

out = os.path.join(BASE, "results", "body_extract.md")
open(out, "w", encoding="utf-8").write(text)

# 섹션별 글자수 (헤딩 단위)
lines = text.split("\n")
sections, cur, buf = [], "(머리말)", []
for ln in lines:
    if ln.startswith("#"):
        sections.append((cur, "".join(buf)))
        cur, buf = ln.strip("# ").strip(), []
    else:
        buf.append(ln)
sections.append((cur, "".join(buf)))

total = 0
print(f"{'섹션':35s} {'글자수':>7s}")
print("-" * 46)
for name, body in sections:
    n = len(body.replace(" ", ""))
    total += n
    if n > 0 or name.startswith(("I","II","III","IV","V","VI")):
        print(f"{name[:34]:35s} {n:7d}")
print("-" * 46)
print(f"{'총 본문(공백제외)':35s} {total:7d}")
print(f"\n추출 파일: {out}")
