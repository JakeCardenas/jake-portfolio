def numbered(number, name, link_label="", link_href=""):
    link = (
        f'\n            <a href="{link_href}" class="num-link mono">{link_label}</a>'
        if link_label
        else ""
    )
    return (
        f'          <div class="num-head">\n'
        f'            <h2 class="num-title">{number} — {name}</h2>{link}\n'
        f"          </div>"
    )


def page(name, lede):
    return (
        f'          <header class="page-head">\n'
        f'            <h1 class="page-title">{name}</h1>\n'
        f'            <p class="page-lede">{lede}</p>\n'
        f"          </header>"
    )
