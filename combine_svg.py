import svgpathtools as spt
import xml.etree.ElementTree as ET

DAU_THANH_MAP = {"f": "huyen", "s": "sac", "r": "hoi", "x": "nga", "j": "nang"}

BOX_SIZE = 86
PD_WIDTH = 36
VA_LEFT = 36
VA_WIDTH = 50
VA_34_TOP = 23
VA_34_HEIGHT = 63
VA_12_TOP = 3
VA_12_HEIGHT = 42
VA_38_TOP = 23
VA_38_HEIGHT = 31
PC_12_TOP = 42
PC_12_HEIGHT = 42
PC_38_TOP = 54
PC_38_HEIGHT = 32

VP_ALIGN = {
    11: {"va": {"y": 0, "h": BOX_SIZE}, "pc": {"y": 0, "h": 0}},
    34: {"va": {"y": VA_34_TOP, "h": VA_34_HEIGHT}, "pc": {"y": 0, "h": 0}},
    12: {
        "va": {"y": VA_12_TOP, "h": VA_12_HEIGHT},
        "pc": {"y": PC_12_TOP, "h": PC_12_HEIGHT},
    },
    38: {
        "va": {"y": VA_38_TOP, "h": VA_38_HEIGHT},
        "pc": {"y": PC_38_TOP, "h": PC_38_HEIGHT},
    },
}
MORE_PADDING_PD = list(map(
    lambda x: f"phuamdau/11_{x}.svg", 
    ['-', 'b', 'dd', 'g', 'qu', 'ng', 'r', 'ph', 'kh']
))

def read_word(word: str):
    chars = word.split("_")
    pd = f"phuamdau/11_{chars[0]}.svg"
    dt = f"dauthanh/11_{DAU_THANH_MAP[chars[3]]}.svg" if chars[3] else ""

    kind_matrix = [[11, 12], [34, 38]]
    kind = kind_matrix[chars[3] != ""][chars[2] != ""]

    va = f"van/{kind}_{chars[1]}.svg"
    pc = f"phuamcuoi/{kind}_{chars[2]}.svg" if kind in [12, 38] else ""

    return pd, dt, va, pc, kind


def extract_svg_attr(attrs):
    # Extract width and height
    width = attrs.get("width", None)
    height = attrs.get("height", None)
    view_box = list(
        map(float, attrs.get("viewBox", f"0 0 {width} {height}").split(" "))
    )

    return view_box, width, height


def read_svg(svg_path: str):
    if svg_path:
        paths, attrs, svg_attr = spt.svg2paths(svg_path, return_svg_attributes=True)
        view_box, width, height = extract_svg_attr(svg_attr)
        ret =  dict(
            paths=paths, attrs=attrs, view_box=view_box, width=width, height=height
        )
        return ret

    # Empty result
    return dict(paths=[], attrs=[], view_box=[0, 0, 0, 0], width=0, height=0)


def translate_paths(paths, attrs, dx, dy):
    # Apply translation to all path segments
    translated_paths = []
    for i, path in enumerate(paths):
        # Check for a 'transform' attribute
        transform = attrs[i].get("transform")
        if transform:
            # Apply the transformation
            t = spt.parser.parse_transform(transform)
            path = spt.path.transform(path, t)

        for segment in path:
            segment.start += dx + 1j * dy
            segment.end += dx + 1j * dy
            if hasattr(segment, "control1"):
                segment.control1 += dx + 1j * dy
            if hasattr(segment, "control2"):
                segment.control2 += dx + 1j * dy
        
        translated_paths.append(path)
        
    return translated_paths

def scale_paths(paths: list, dx: float, dy: float):
    return [path.scaled(dx, dy) for path in paths]


def genrate_svg(word):
    pd, dt, va, pc, kind = read_word(word)

    pd_svg = read_svg(pd)
    dt_svg = read_svg(dt)
    va_svg = read_svg(va)
    pc_svg = read_svg(pc)

    # Align right(pad: 2), 
    pad = 4 if pd in MORE_PADDING_PD else 1
    pd_paths = translate_paths(
        pd_svg["paths"],
        pd_svg["attrs"],
        dx=-pd_svg["view_box"][0] + max(0, PD_WIDTH - pd_svg["view_box"][2] - pad),
        dy=-pd_svg["view_box"][1] + (BOX_SIZE - pd_svg["view_box"][3]) / 2,
    )

    # Align center, top
    dt_pad_y = {
        'dauthanh/11_nang.svg': 7,
        'dauthanh/11_huyen.svg': -1
    }.get(dt, 0)
    dt_paths = translate_paths(
        dt_svg["paths"],
        dt_svg["attrs"],
        dx=-dt_svg["view_box"][0] + VA_LEFT + (VA_WIDTH - dt_svg["view_box"][2]) / 2,
        dy=-dt_svg["view_box"][1] + dt_pad_y,
    )
    

    # Align center, middle
    va_pad_x = {
        "11_ee": 3,
        "34_eo": 3,
        "34_o": -2,
        "34_oo": 4,
        "34_ui": 1,
        "11_ua": -4,
        "11_ui": 3,
        "34_uy": 5,
        "38_uy": 5,
        "34_uow": 3,
        "38_u": 1,
        "11_uwi": -2,
        "11_i": -6,
        "11_iu": -4,
        "11_oai": -3
    }.get(va[4:-4], 0)
    va_paths = translate_paths(
        va_svg["paths"],
        va_svg["attrs"],
        dx=-va_svg["view_box"][0] + VA_LEFT + (VA_WIDTH - va_svg["view_box"][2]) / 2 + va_pad_x,
        dy=-va_svg["view_box"][1]
        + VP_ALIGN[kind]["va"]["y"]
        + max(0, (VP_ALIGN[kind]["va"]["h"] - va_svg["view_box"][3]) / 2),
    )

    # Align center, bottom
    pc_pad_x = {
        "phuamcuoi/12_p.svg": 5,
        "phuamcuoi/12_c.svg": 2,
        "phuamcuoi/12_nh.svg": 6,
        "phuamcuoi/38_p.svg": 6,
        "phuamcuoi/38_ch.svg": 2,
        "phuamcuoi/38_nh.svg": 8,
    }.get(pc, 0)
    pc_paths = translate_paths(
        pc_svg["paths"],
        pc_svg["attrs"],
        dx=-pc_svg["view_box"][0] + VA_LEFT + (VA_WIDTH - pc_svg["view_box"][2]) / 2 + pc_pad_x,
        dy=-pc_svg["view_box"][1]
        + VP_ALIGN[kind]["pc"]["y"]
        + (VP_ALIGN[kind]["pc"]["h"] - pc_svg["view_box"][3]),
    )

    combined_paths = pd_paths + dt_paths + va_paths + pc_paths

    return combined_paths

def save_paths(paths, filepath):
    spt.wsvg(
        paths=paths,
        filename=filepath,
        stroke_widths=[],
        viewbox="0 0 86 86",
        attributes=[{"style": "fill:#000"}] * len(paths),
    )


if __name__ == "__main__":
    # word = "-_aa_m_r"
    word = "h_aau__f"
    paths = genrate_svg(word)
    save_paths(paths=paths, filepath=f"generated/src/{word}.svg")
