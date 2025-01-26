import os
import json
import shutil

import svgpathtools

from combine_svg import (
    genrate_svg, 
    scale_paths,
    translate_paths
)

START_UNICODE = 0x0F0000
SRC_FONT_SIZE = 86
TARGET_FONT_SIZE = 1000
TARGET_FONT_PADDING = 60

phuamdau = [
    "-",
    "b",
    "c",
    "ch",
    "d",
    "dd",
    "g",
    "gi",
    "h",
    "kh",
    "l",
    "m",
    "n",
    "ng",
    "nh",
    "p",
    "ph",
    "qu",
    "r",
    "s",
    "t",
    "th",
    "tr",
    "v",
    "x",
]
dauthanh = ["", "f", "s", "r", "x", "j"]
dauthanh_tac = ["", "j"]
phuamcuoi_bth = ["m", "n", "ng", "nh"]
phuamcuoi_tac = ["c", "ch", "p", "t"]
v11and12 = ["a", "e", "ee", "i", "o", "oa", "oe", "oo", "ow", "u", "uw", "uy"]
v11no12 = [
    "aau",
    "aay",
    "ai",
    "ao",
    "au",
    "ay",
    "eeu",
    "eo",
    "ia",
    "ieeu",
    "iu",
    "oai",
    "oay",
    "oi",
    "ooi",
    "owi",
    "ua",
    "uaay",
    "uee",
    "ui",
    "uooi",
    "uow",
    "uwa",
    "uwi",
    "uwowi",
    "uwowu",
    "uwu",
    "uya",
    "uyu",
]
v12no11 = ["aa", "aw", "iee", "oaw", "uaa", "uoo", "uwow", "uyee"]

template_config = {
    "props": {
        "ascent": 880,
        "descent": 120,
        "em": 1000,
        "encoding": "UnicodeFull",
        "lang": "English (US)",
        "family": "HoufRegularScript",
        "style": "Light",
        "familyname": "HoufRegularScript",
        "fontname": "HoufRegularScript-Light",
        "fullname": "HoufRegularScript Light",
    },
    "glyphs": {
    },
    "sfnt_names": [
        ["English (US)", "Copyright", "Copyright (c) 2014 by Nobody"],
        ["English (US)", "Family", "HoufRegularScript"],
        ["English (US)", "SubFamily", "Light"],
        ["English (US)", "UniqueID", "HoufRegularScript 2014-12-04"],
        ["English (US)", "Fullname", "HoufRegularScript Light"],
        ["English (US)", "Version", "Version 001.000"],
        ["English (US)", "PostScriptName", "HoufRegularScript-Light"],
    ],
    "input": "./svg",
    "output": ["HoufRegularScript-Light.ttf"],
}
code_map = {}

words = []
for pd in phuamdau:
    for va in v11and12:
        for dt in dauthanh:
            words.append(f"{pd}_{va}__{dt}")
        for pc in phuamcuoi_bth:
            for dt in dauthanh:
                words.append(f"{pd}_{va}_{pc}_{dt}")
        for pc in phuamcuoi_tac:
            for dt in dauthanh_tac:
                words.append(f"{pd}_{va}_{pc}_{dt}")

    for va in v11no12:
        for dt in dauthanh:
            words.append(f"{pd}_{va}__{dt}")

    for va in v12no11:
        for pc in phuamcuoi_bth:
            for dt in dauthanh:
                words.append(f"{pd}_{va}_{pc}_{dt}")
        for pc in phuamcuoi_tac:
            for dt in dauthanh_tac:
                words.append(f"{pd}_{va}_{pc}_{dt}")

print(f"Generated {len(words)} words.")

genrated_dir = "generated"

shutil.rmtree(os.path.join(genrated_dir, "svg"), ignore_errors=True)
os.makedirs(os.path.join(genrated_dir, "svg"), exist_ok=True)

scale = (TARGET_FONT_SIZE - 2 * TARGET_FONT_PADDING) / SRC_FONT_SIZE

demo_words = []

for i, word in enumerate(words):
    char_code = START_UNICODE + i
    
    # chars = word.split("_")
    # ready = chars[0] in ["dd"] and chars[1] and chars[3] in ["j", "", "f"]
    # if not ready:
    #     continue
    # if chars[0] == "ch" and chars[2] in ["", "m"] and  chars[3] in ["", "j"]:
    #     print(word, ":", f"&#{char_code};")
    
    # if True:
    #     demo_words.append(word + " : "+ f"&#{char_code};")
    
    try:
        paths = scale_paths(genrate_svg(word=word), scale, scale)
        paths = translate_paths(paths=paths, attrs=[{}] * len(paths), dx=TARGET_FONT_PADDING, dy=TARGET_FONT_PADDING)
    except:
        print(f"Failed on generating word: {word}")
        raise
    
    filepath = os.path.join(genrated_dir, "svg", f"{word}.svg")
    svgpathtools.wsvg(
        paths=paths,
        filename=filepath,
        stroke_widths=[],
        viewbox=f"0 0 {TARGET_FONT_SIZE} {TARGET_FONT_SIZE}",
        attributes=[{"style": "fill:#000"}] * len(paths),
    )
    
    code_map[word] = char_code
    template_config["glyphs"][str(char_code)] = f"{word}.svg"
    
    if i % 500 == 0:
        print(f"Generated {i}/{len(words)} svg files.")
    
with open(os.path.join(genrated_dir, "config.json"), "w") as file:
    json.dump(template_config, file)
    
with open(os.path.join(genrated_dir, "code_map.json"), "w") as file:
    json.dump(code_map, file)
    
print("Generated svg files.")
print("Copy to dest...")
shutil.rmtree(r"C:\PetProjects\Void\Houf-Regular-Script\generated")
shutil.copytree(genrated_dir, r"C:\PetProjects\Void\Houf-Regular-Script\generated")

print("demo words:")
for line in sorted(demo_words):
    print(line)