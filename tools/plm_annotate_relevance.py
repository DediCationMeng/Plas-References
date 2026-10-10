# -*- coding: utf-8 -*-
"""Relevance ANNOTATION for the kept (whitelist) set - title + abstract dual review.

Per skill rule "防误杀": this script NEVER drops records. It only annotates each record
with relevance_tier / relevance_note and produces a review CSV + a DRAFT drop list
(relevance_drops_draft.json) for human confirmation. After human review, move confirmed
items into relevance_drops.json and run plm_relevance_filter.py.

Tiers:
  CORE-MAT   ① 新型等离激元纳米材料（核心概念 x 纳米材料/形貌）
  CORE-BIO   ③ 生物医学应用（等离激元/金银纳米材料 x 诊疗/传感/成像词）
  RELATED    ② LSPR/SPR/gap plasmon 机理（有等离激元核心词但材料维度弱，需复核）
  SUSPECT    典型离题模式命中或核心词缺失（仅列入草稿，人工核实后才剔除）

Usage:
  python plm_annotate_relevance.py --dir WORKDIR
"""
import argparse, csv, json, os, re

CORE = ["plasmon", "lspr", "localized surface plasmon", "surface plasmon resonance",
        "surface plasmon polariton", "gap plasmon", "plasmonic"]
NANO = ["nanoparticle", "nano-particle", "nanostructure", "nanomaterial", "nanorod", "nano-rod",
        "nanostar", "nanocube", "nanoshell", "nanogap", "nano-gap", "core-shell", "core shell",
        "nanocrystal", "nanocage", "nanoframe", "nanoprism", "nanotriangle", "nanodendrite",
        "nanourchin", "nanowire", "nanoantenna", "nanoplate", "yolk-shell", "colloid",
        "gold nanoparticle", "silver nanoparticle", "au nanoparticle", "ag nanoparticle",
        "gold nanorod", "silver nanorod", "bimetallic", "nanocomposite", "nanoparticle-on-mirror",
        "au@ag", "aunan", "agnan", "noble metal nanoparticle", "metal nanoparticle",
        "hollow nanostructure", "anisotropic nanoparticle", "nanosphere", "nanodot"]
BIO = ["sers", "surface-enhanced raman", "ters", "photothermal", "photodynamic", "photoacoustic",
       "biosensor", "bioimaging", "theranostic", "drug deliver", "antibacterial", "antimicrobial",
       "wound", "immunoassay", "diagnos", "therap", "cancer", "tumor", "cell imaging",
       "bioimaging", "imaging", "implant", "neuromodulat", "neurostimulat", "assay", "detect"]
NEG = ["kretschmann", "biomolecular interaction", "surface plasmon resonance imaging",
       "thin film", "grating", "waveguide", "planar multilayer", "molecular interaction",
       "protein interaction", "kinetic analysis", "immunosensor"]


def score(text):
    core = [w for w in CORE if w in text]
    nano = [w for w in NANO if w in text]
    bio = [w for w in BIO if w in text]
    neg = [w for w in NEG if w in text]
    return core, nano, bio, neg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.getcwd())
    args = ap.parse_args()
    base = args.dir
    db_path = os.path.join(base, "literature_database.json")
    db = json.load(open(db_path, encoding="utf-8"))

    counts, rows, draft = {}, [], {"drop": {}, "flag": {}}
    for r in db:
        text = ((r.get("title") or "") + " " + (r.get("abstract") or "")).lower()
        has_abs = bool((r.get("abstract") or "").strip())
        core, nano, bio, neg = score(text)
        if core and nano and bio:
            tier, note = "CORE-BIO", f"核心概念+材料+应用（{','.join((core+nano+bio)[:5])}）"
        elif core and nano:
            tier, note = "CORE-MAT", f"核心概念+材料（{','.join((core+nano)[:5])}）"
        elif core and bio:
            tier, note = "CORE-BIO", f"核心概念+应用（{','.join((core+bio)[:5])}）"
        elif core:
            tier, note = "RELATED", f"核心概念在场但材料维度弱（{','.join(core[:3])}）"
        elif bio and (nano or "sers" in text or "gold" in text or "silver" in text):
            tier, note = "CORE-BIO", "应用词+材料词（无 plasmon 字样）"
        else:
            tier, note = "SUSPECT", "核心词缺失/疑似离题，需人工核实摘要"
        if neg and tier.startswith("CORE"):
            tier, note = "SUSPECT", note + "；命中离题模式：" + ",".join(neg[:3])
        if not has_abs and tier == "SUSPECT":
            note += "（无摘要，仅题名判断）"
        r["relevance_tier"] = tier
        r["relevance_note"] = note
        counts[tier] = counts.get(tier, 0) + 1
        rows.append([r.get("date"), r.get("journal_abbrev") or r.get("journal") or "?",
                     r.get("journal_group", ""), tier, note, r.get("doi") or "-",
                     (r.get("title") or "")[:110]])
        if tier == "SUSPECT":
            draft["drop"][r.get("doi") or r.get("title")] = note

    json.dump(db, open(db_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rep = os.path.join(base, "03_Reports")
    os.makedirs(rep, exist_ok=True)
    with open(os.path.join(rep, "relevance_review.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["发表日期", "期刊", "期刊分组", "相关度层级", "判定依据", "DOI", "英文原题"])
        w.writerows(sorted(rows, key=lambda x: (x[3], x[0] or "")))
    json.dump(draft, open(os.path.join(base, "relevance_drops_draft.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("annotated:", len(db))
    for k in ("CORE-MAT", "CORE-BIO", "RELATED", "SUSPECT"):
        print(f"  {k}: {counts.get(k, 0)}")
    print("draft drop list (NOT applied):", len(draft["drop"]), "-> relevance_drops_draft.json")


if __name__ == "__main__":
    main()
