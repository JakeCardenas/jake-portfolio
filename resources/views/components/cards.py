from config import site


def posts(entries, *, heading="h2", container_id=""):
    box = (
        f'id="{container_id}" class="view-list"' if container_id else 'class="view-list"'
    )
    cards = "\n".join(
        f"""            <a href="{site.url('posts/' + p['slug'])}" class="post-card">
              <span class="post-thumb">
                <img src="{site.asset(p['image'])}" alt="" loading="lazy" />
              </span>
              <span class="post-body">
                <time class="post-date mono">{p['date']}</time>
                <{heading} class="post-title">{p['title']}</{heading}>
                <p class="post-excerpt">{p['excerpt']}</p>
                <span class="post-meta mono">
                  <span class="post-meta-read">Read</span>
                  <span class="post-meta-sep">·</span>
                  <span>{p['read']}</span>
                </span>
              </span>
            </a>"""
        for p in entries
    )
    return f'          <div {box}>\n{cards}\n          </div>'


def certificates(entries):
    return "\n".join(
        f"""            <a
              class="cert-card"
              href="{c['href']}"
              target="_blank"
              rel="noopener noreferrer"
              style="--rot: {c['rot']}; --ty: {c['ty']}"
              aria-label="{c['aria_label']}"
            >
              <span class="cert-mark">
                <img src="{site.asset(c['logo'])}" alt="{c['logo_alt']}" loading="lazy" />
              </span>
              <span class="cert-title">{c['title']}</span>
              <span class="cert-issuer mono"{f' title="{c["issuer_full"]}"' if c['issuer_full'] else ''}>{c['issuer']}</span>
              <span class="cert-open mono">{LEAF}<span>{c['action']}</span>{LEAF_FLIP}</span>
            </a>"""
        for c in entries
    )


def _leaf(extra=""):
    cls = f"cert-leaf{extra}"
    return (
        f'<svg class="{cls}" viewBox="0 0 13 22" fill="currentColor" aria-hidden="true">'
        '<path d="M0 -4C2.1 -2.6 2.1 2.6 0 4C-2.1 2.6 -2.1 -2.6 0 -4Z" transform="translate(8 5) rotate(46)"/>'
        '<path d="M0 -4.3C2.3 -2.8 2.3 2.8 0 4.3C-2.3 2.8 -2.3 -2.8 0 -4.3Z" transform="translate(4.6 11) rotate(14)"/>'
        '<path d="M0 -4C2.1 -2.6 2.1 2.6 0 4C-2.1 2.6 -2.1 -2.6 0 -4Z" transform="translate(8 17) rotate(-30)"/></svg>'
    )


LEAF = _leaf()
LEAF_FLIP = _leaf(" cert-leaf--flip")
