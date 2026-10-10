# -*- coding: utf-8 -*-
"""Extract the "plasmonic nanomaterials x biomedical applications" subset.

Inclusion (intersection, 防误杀 -> 只多不少):
  A. 等离激元信号: CORE words (plasmon/LSPR/...) OR SERS/TERS OR Au/Ag nanoparticle phrases
  B. 纳米材料信号: NANO morphology words
  C. 生物医学应用信号: BIO_APP (诊疗/传感/成像/递送...) OR BIO_CONTEXT (cell/cancer/DNA/...)
Exclusion (strict):
  典型离题模式命中 且 无纳米材料词 (纯 Kretschmann 薄膜/光栅 SPR 仪器类) -> 剔除
Each record gets bio_tags[] (multi-label application categories).

Outputs under <dir>/04_Biomedical/:
  biomedical_subset.json / biomedical_subset.csv / bio_tag_stats.json

Usage:
  python plm_extract_biomedical.py --dir WORKDIR
"""
import argparse, csv, json, os
from collections import Counter, defaultdict

CORE = ["plasmon", "lspr", "localized surface plasmon", "surface plasmon resonance",
        "surface plasmon polariton", "gap plasmon", "plasmonic",
        "surface-enhanced raman", "sers", "ters",
        "gold nanoparticle", "silver nanoparticle", "au nanoparticle", "ag nanoparticle",
        "gold nanorod", "silver nanorod", "gold nanostar", "gold nanocluster",
        "gold nanoshell", "gold nanocage", "au nanorod", "au@ag", "aunan", "agnan",
        "noble metal nanoparticle", "metal nanoparticle"]
NANO = ["nanoparticle", "nano-particle", "nanostructure", "nanomaterial", "nanorod", "nano-rod",
        "nanostar", "nanocube", "nanoshell", "nanogap", "nano-gap", "core-shell", "core shell",
        "nanocrystal", "nanocage", "nanoframe", "nanoprism", "nanotriangle", "nanodendrite",
        "nanourchin", "nanowire", "nanoantenna", "nanoplate", "yolk-shell", "colloid",
        "bimetallic", "nanocomposite", "nanoparticle-on-mirror",
        "hollow nanostructure", "anisotropic nanoparticle", "nanosphere", "nanodot",
        "nanocluster", "nanoflower", "nanobelt", "nanotube"]
BIO_APP = ["sers imaging", "sers tag", "surface-enhanced raman", "sers", "ters",
           "photothermal", "photodynamic", "photoacoustic",
           "biosensor", "bioimaging", "theranostic", "drug deliver", "controlled release",
           "antibacterial", "antimicrobial", "wound", "immunoassay", "diagnos", "therap",
           "cancer", "tumor", "oncolog", "cell imaging", "implant", "neuromodulat",
           "neurostimulat", "phototheranostic", "sonodynamic", "immunotherap",
           "gene deliver", "protein deliver", "vaccine", "pathogen", "antibiotic"]
BIO_CONTEXT = ["cell", "cancer", "tumor", "biomedic", "biological", "biomarker", "biosens",
               "clinical", "disease", "dna", "rna", "mrna", "protein", "antibod", "antigen",
               "immuno", "bacteri", "virus", "viral", "pathogen", "glucose", "serum", "plasma",
               "urine", "tissue", "in vivo", "in vitro", "mouse", "mice", "tumor", "patient",
               "diagnostic", "microorganism", "staphylococcus", "escherichia", "e. coli",
               "wound", "neuron", "brain", "neural", "stem cell", "exosome", "organism"]
TAGS = {
    "SERS-成像/标签": ["sers imaging", "sers tag", "sers-based imaging", "cell imaging",
                       "bioimaging", "photoacoustic", "multimodal imaging", "fluorescence imaging"],
    "SERS-传感/检测": ["surface-enhanced raman", "sers", "sers sensor", "sers detect", "ters"],
    "光热/光动力治疗": ["photothermal", "photodynamic", "sonodynamic", "phototheranostic"],
    "LSPR/SPR-生物传感": ["lspr", "localized surface plasmon", "surface plasmon resonance",
                          "refractive index", "immunoassay", "biosensor", "plasmonic sensor"],
    "药物/基因递送": ["drug deliver", "controlled release", "gene deliver", "mrna",
                      "drug release", "nanocarrier", "cargo"],
    "抗菌/抗感染/创伤": ["antibacterial", "antimicrobial", "antibiotic", "wound", "biofilm",
                          "pathogen", "infection"],
    "肿瘤诊疗/theranostic": ["theranostic", "cancer", "tumor", "oncolog", "phototheranostic",
                             "immunotherap", "chemotherapy", "chemo-photothermal"],
    "神经调控": ["neuromodulat", "neurostimulat", "neural", "neuron", "brain"],
    "植入体/牙科/骨科": ["implant", "dental", "bone", "osteogenesis", "orthopedic"],
}
NEG = ["kretschmann", "biomolecular interaction", "thin film", "grating", "waveguide",
       "planar multilayer", "molecular interaction", "protein interaction", "kinetic analysis"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.getcwd())
    args = ap.parse_args()
    base = args.dir
    db = json.load(open(os.path.join(base, "literature_database.json"), encoding="utf-8"))

    subset, tag_counts, per_year = [], Counter(), defaultdict(int)
    for r in db:
        text = ((r.get("title") or "") + " " + (r.get("abstract") or "")).lower()
        a = [w for w in CORE if w in text]
        b = [w for w in NANO if w in text]
        c = [w for w in BIO_APP if w in text] or [w for w in BIO_CONTEXT if w in text]
        if not (a and b and c):
            continue
        neg = [w for w in NEG if w in text]
        if neg and not b:        # 只有离题模式且无任何纳米材料词 -> 剔除（b 必非空，此处兜底）
            continue
        if neg and b:
            # 有纳米材料词但命中离题模式：仍保留（防误杀），仅标注
            pass
        tags = [t for t, kws in TAGS.items() if any(k in text for k in kws)]
        if not tags:
            tags = ["其他生物医学应用"]
        r2 = dict(r)
        r2["bio_tags"] = tags
        r2["bio_note"] = ("等离激元/材料/生物医学三信号：" + ",".join((a + b + c)[:6]))
        if neg:
            r2["bio_note"] += "（含离题模式词：" + ",".join(neg[:2]) + "，有纳米材料词故保留）"
        subset.append(r2)
        y = (r.get("date") or "????")[:4]
        per_year[y] += 1
        for t in tags:
            tag_counts[t] += 1

    out = os.path.join(base, "04_Biomedical")
    os.makedirs(out, exist_ok=True)
    json.dump(subset, open(os.path.join(out, "biomedical_subset.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(out, "biomedical_subset.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["发表日期", "期刊", "期刊分组", "应用类别", "被引", "DOI", "英文原题", "备注"])
        for r in sorted(subset, key=lambda x: (x.get("date") or "")):
            w.writerow([r.get("date"), r.get("journal_abbrev") or r.get("journal") or "?",
                        r.get("journal_group", ""), "|".join(r.get("bio_tags", [])),
                        r.get("citedByCount") or 0, r.get("doi") or "-",
                        (r.get("title") or "")[:130], r.get("bio_note", "")])
    stats = {"total": len(subset), "per_year": dict(sorted(per_year.items())),
             "tag_counts": dict(tag_counts.most_common())}
    json.dump(stats, open(os.path.join(out, "bio_tag_stats.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("biomedical subset:", len(subset), "/", len(db))
    for y, n in sorted(per_year.items()):
        print(" ", y, n)
    print("tags:")
    for t, n in tag_counts.most_common():
        print("  ", t, n)


if __name__ == "__main__":
    main()
