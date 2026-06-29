# formulation-records-dataset

Tooling + samples for **formulation-records-instruct**: a *synthetic*,
de-identified instruction dataset that teaches an LLM to (1) turn messy chemistry
experiment records into a structured schema, (2) normalize names/units, and
(3) explain optimization results in plain language.

By [Formulith](https://www.formulith.com).

> 本專案部分研發由**數位發展部數位產業署 115 年 AI 算力平台**支持。
> Part of this work is supported by the **AI Computing Platform (2026), Administration for Digital Industries, Ministry of Digital Affairs, Taiwan**.


## Contents

- `schema.json` — JSON Schema for a structured formulation record.
- `generate.py` — synthetic data generator (stdlib only; RDKit optional for validation).
- `samples/formulation_records_sample.jsonl` — ~12 starter examples (3 task types).

## Tasks

| task        | input                     | output                                    |
| ----------- | ------------------------- | ----------------------------------------- |
| `extract`   | messy free-text record    | structured JSON (per `schema.json`)       |
| `normalize` | raw name / unit           | canonical SMILES/CAS / SI-style unit      |
| `explain`   | optimizer (BO/XAI) result | plain-language chemist-facing explanation |

## Generate more

```bash
python generate.py --n 500 --out formulation_records_instruct.jsonl
# optional: validate SMILES if RDKit is installed
python generate.py --n 500 --validate --out formulation_records_instruct.jsonl
```

## Important: data provenance

Everything here is **synthetic** (procedurally generated) — it contains **no real
customer data and no proprietary formulations**. Values are illustrative.

## License

CC-BY-4.0 (data). `generate.py` is Apache-2.0.
