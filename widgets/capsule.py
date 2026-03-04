def render_capsule(label, bg_color):

    text_color = get_text_color(bg_color)

    return f"""
        <span style="
            background:{bg_color};
            color:{text_color};
            padding:4px 12px;
            border-radius:999px;
            font-size:12px;
            font-weight:500;
            margin-right:8px;
            display:inline-block;
        ">
            {label}
        </span>
    """

def get_text_color(color: str):
    color = color.lstrip("#")
    if len(color) == 6:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "#000000" if luminance > 186 else "#FFFFFF"
    return "#FFFFFF"