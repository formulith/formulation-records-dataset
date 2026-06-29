#!/usr/bin/env python3
"""Synthetic generator for formulation-records-instruct.

Produces instruction examples for 3 tasks: extract / normalize / explain.
Stdlib only. If RDKit is installed and --validate is passed, SMILES are checked.
NOTE: output is fully synthetic — no real or customer data.
"""
import argparse, json, random

INHIBITORS = [
    ("benzotriazole", "95-14-7", "c1ccc2[nH]nnc2c1"),
    ("5-methylbenzotriazole", "136-85-6", "Cc1ccc2[nH]nnc2c1"),
    ("imidazole", "288-32-4", "c1c[nH]cn1"),
    ("tetrazole", "288-94-8", "c1nnn[nH]1"),
    ("EDTA", "60-00-4", "OC(=O)CN(CC(=O)O)CCN(CC(=O)O)CC(=O)O"),
]
MAINS = [("hydrogen peroxide","7722-84-1","OO"),
         ("phosphoric acid","7664-38-2","OP(=O)(O)O"),
         ("acetic acid","64-19-7","CC(=O)O")]
UNIT_RAW = {"wt%": ["wt%","weight percent","%w/w"], "mol/L": ["M","mol/L","molar"],
            "ppm": ["ppm","mg/L"]}
OBJ = [("etch_rate","nm/min"),("selectivity","ratio"),("defect_count","#/wafer")]

def rec(i):
    main = random.choice(MAINS)
    inh = random.choice(INHIBITORS)
    return {
      "record_id": f"SYN-{i:05d}",
      "project": random.choice(["copper_etchant","cmp_slurry","photoresist"]),
      "components": [
        {"role":"main","identifier":{"smiles":main[2],"cas":main[1],"common_name":main[0]},
         "concentration":{"value":round(random.uniform(1,30),1),"unit":"wt%"}},
        {"role":"inhibitor","identifier":{"smiles":inh[2],"cas":inh[1],"common_name":inh[0]},
         "concentration":{"value":round(random.uniform(0.05,2),2),"unit":"wt%"}},
      ],
      "process":{"temperature_C":random.choice([25,30,40,50]),"time_s":random.choice([30,60,120])},
      "objectives":[{"name":o[0],"value":round(random.uniform(1,500),1),"unit":o[1]} for o in OBJ],
      "feasible": random.random() < 0.05,  # mirrors the near-0 strict-feasible regime
      "provenance":{"source_doc":"synthetic","extracted_by":"generator","validated":True},
    }

def messy(r):
    c = r["components"]
    return (f'Exp {r["record_id"]}: {c[0]["identifier"]["common_name"]} '
            f'{c[0]["concentration"]["value"]}{random.choice(UNIT_RAW["wt%"])}, '
            f'+ {c[1]["identifier"]["common_name"]} {c[1]["concentration"]["value"]}%, '
            f'{r["process"]["temperature_C"]}C/{r["process"]["time_s"]}s. '
            f'etch {r["objectives"][0]["value"]} nm/min.')

def explain(r):
    return (f'Recommended because the inhibitor concentration sits near the '
            f'feasible boundary for {r["project"]}; raising it further is predicted '
            f'to trade etch rate for selectivity. Suggested next: hold main at '
            f'{r["components"][0]["concentration"]["value"]}wt%, vary inhibitor +/-0.2wt%.')

def examples(i):
    r = rec(i)
    yield {"task":"extract","input":messy(r),"output":r}
    yield {"task":"normalize",
           "input":f'{r["components"][1]["identifier"]["common_name"]} ; "{random.choice(UNIT_RAW["mol/L"])}"',
           "output":{"smiles":r["components"][1]["identifier"]["smiles"],
                     "cas":r["components"][1]["identifier"]["cas"],"unit":"mol/L"}}
    yield {"task":"explain","input":{"result":"BO recommendation","record":r["record_id"]},
           "output":explain(r)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--out", default="formulation_records_instruct.jsonl")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    random.seed(a.seed)
    check = None
    if a.validate:
        try:
            from rdkit import Chem
            check = lambda s: Chem.MolFromSmiles(s) is not None
        except Exception:
            print("RDKit not available; skipping validation"); check = None
    n = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for i in range(a.n):
            for ex in examples(i):
                if check and ex["task"]=="extract":
                    for c in ex["output"]["components"]:
                        s = c["identifier"]["smiles"]
                        if s and not check(s): c["identifier"]["smiles"]=None
                f.write(json.dumps(ex, ensure_ascii=False)+"\n"); n += 1
    print(f"wrote {n} examples to {a.out}")

if __name__ == "__main__":
    main()
