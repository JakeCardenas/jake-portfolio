from config import site
from resources import content

WIDTH = 1200
HEIGHT = 630


def render():
    stats = (
        (len(content.load("projects")), "PROJECTS"),
        (len(content.load("certifications")), "CERTIFICATES"),
        (len(content.load("posts")), "ARTICLES"),
    )
    cells = "".join(
        f'<div class="cell"><span class="num">{value}</span>'
        f'<span class="label">{label}</span></div>'
        for value, label in stats
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="/css/site.css" />
    <style>
      html, body {{ margin: 0; background: {site.BG_LIGHT}; }}
      body {{
        width: {WIDTH}px;
        height: {HEIGHT}px;
        position: relative;
        overflow: hidden;
        font-family: var(--font-sans);
        color: var(--ink);
      }}
      .dots {{
        position: absolute;
        inset: 0;
        background-image: radial-gradient(circle, rgba(10, 10, 10, 0.9) 1px, transparent 1.6px);
        background-size: 13px 13px;
        opacity: 0.2;
        -webkit-mask-image: radial-gradient(ellipse 70% 80% at 100% 0%, #000 0%, transparent 68%);
        mask-image: radial-gradient(ellipse 70% 80% at 100% 0%, #000 0%, transparent 68%);
      }}
      .dots-bl {{
        -webkit-mask-image: radial-gradient(ellipse 60% 70% at 0% 100%, #000 0%, transparent 66%);
        mask-image: radial-gradient(ellipse 60% 70% at 0% 100%, #000 0%, transparent 66%);
        background-size: 9px 9px;
        opacity: 0.14;
      }}
      .frame {{
        position: absolute;
        inset: 40px;
        border: 1px solid var(--g200);
        border-radius: 16px;
      }}
      .inner {{
        position: relative;
        height: 100%;
        box-sizing: border-box;
        padding: 96px 104px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }}
      .eyebrow {{
        font-family: var(--font-mono);
        font-size: 15px;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--g400);
      }}
      .name {{
        font-family: var(--font-pixel);
        font-size: 92px;
        line-height: 1;
        letter-spacing: -0.01em;
        margin: 26px 0 0;
      }}
      .tagline {{
        max-width: 40rem;
        margin: 26px 0 0;
        font-size: 23px;
        line-height: 1.5;
        color: var(--g600);
      }}
      .foot {{
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
      }}
      .stats {{ display: flex; gap: 0; }}
      .cell {{
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 0 30px;
        border-left: 1px solid var(--g200);
      }}
      .cell:first-child {{ padding-left: 0; border-left: 0; }}
      .num {{ font-family: var(--font-pixel); font-size: 30px; line-height: 1; }}
      .label {{
        font-family: var(--font-mono);
        font-size: 12px;
        letter-spacing: 0.14em;
        color: var(--g400);
      }}
      .url {{
        font-family: var(--font-mono);
        font-size: 16px;
        letter-spacing: 0.04em;
        color: var(--g500);
      }}
    </style>
  </head>
  <body>
    <span class="dots"></span>
    <span class="dots dots-bl"></span>
    <span class="frame"></span>
    <div class="inner">
      <div>
        <div class="eyebrow">{site.JOB_LABEL}</div>
        <h1 class="name">{site.NAME}</h1>
        <p class="tagline">{site.TAGLINE}</p>
      </div>
      <div class="foot">
        <div class="stats">{cells}</div>
        <div class="url">{site.URL.replace('https://', '')}</div>
      </div>
    </div>
  </body>
</html>
"""
