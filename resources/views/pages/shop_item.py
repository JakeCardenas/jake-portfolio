import os

from config import site
from resources.views.components import icons, media
from resources.views.pages.shop import PUBLIC

SHOT_SIZES = "(min-width: 640px) 344px, calc(100vw - 3rem)"


def render(item):
    shot = (
        media.img(item["shot"], sizes=SHOT_SIZES, alt=item["name"], priority=True)
        if item["shot"] in media.DERIVATIVES
        else icons.DOC
    )
    sections = "\n".join(
        f'            {s["heading"]}\n            {s["body"]}'
        for s in item["desc_sections"]
    )
    return f"""        <section class="section shop-item reveal">
          <a href="{site.url('shop')}" class="sd-back mono">{icons.BACK} shop</a>
          <div class="sd-grid">
            <div class="sd-image">
              {shot}
            </div>
            <div class="sd-info">
              <span class="sd-kind mono">{item['kind']}</span>
              <h1 class="sd-title">{item['name']}</h1>
              <p class="sd-price">Free</p>
              <div class="sd-actions">
                <a href="/{item['file']}" download class="sd-download">Download free {icons.DOWNLOAD}</a>
              </div>
              <p class="sd-delivery mono">
                <svg viewBox="0 0 24 24" fill="none" class="sd-check" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Instant digital delivery
              </p>
            </div>
          </div>
          <div class="sd-desc">
            <p>{item['desc_intro']}</p>
{sections}
          </div>
        </section>
"""
