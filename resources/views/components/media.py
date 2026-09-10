from config import site

DERIVATIVES = {}


def register(path, digest, widths):
    DERIVATIVES[path] = (digest, widths)


def derivative(path, width):
    digest, _widths = DERIVATIVES[path]
    stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return f"/images/optimized/{stem}-{digest}-{width}.webp"


def img(path, *, sizes="", alt="", cls="", loading="lazy", priority=False, extra=""):
    attrs = [f'class="{cls}"'] if cls else []

    if path in DERIVATIVES:
        _digest, widths = DERIVATIVES[path]
        srcset = ", ".join(f"{derivative(path, w)} {w}w" for w in widths)
        attrs.append(f'src="{derivative(path, widths[-1])}"')
        attrs.append(f'srcset="{srcset}"')
        if sizes:
            attrs.append(f'sizes="{sizes}"')
    else:
        attrs.append(f'src="{site.asset(path)}"')

    attrs.append(f'alt="{alt}"')
    if priority:
        attrs += ['fetchpriority="high"', 'decoding="async"']
    else:
        attrs += [f'loading="{loading}"', 'decoding="async"']
    if extra:
        attrs.append(extra)
    return f"<img {' '.join(attrs)} />"
