from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ─────────────────────────────────────────────
#  KNOWLEDGE BASE (BASIS PENGETAHUAN)
# ─────────────────────────────────────────────
# Setiap rule punya: kondisi (dict) dan konklusi (label prioritas + poin + rekomendasi)

RULES = [
    # ─── PRIORITAS: KRITIS ───────────────────────────────────────────────────────
    {
        "id": "R01",
        "desc": "Deadline ≤1 hari AND bobot ≥30%",
        "conditions": {"deadline_hari": "≤1", "bobot_persen": "≥30"},
        "priority": "KRITIS",
        "points": 100,
        "rekomendasi": "Kerjakan SEKARANG. Jangan tunda sama sekali.",
        "warna": "#ef4444",
    },
    {
        "id": "R02",
        "desc": "Deadline ≤1 hari AND sudah dimulai=Tidak",
        "conditions": {"deadline_hari": "≤1", "sudah_dimulai": "tidak"},
        "priority": "KRITIS",
        "points": 100,
        "rekomendasi": "Belum dimulai padahal deadline besok! Mulai segera.",
        "warna": "#ef4444",
    },
    {
        "id": "R03",
        "desc": "Deadline ≤2 hari AND kesulitan=tinggi",
        "conditions": {"deadline_hari": "≤2", "tingkat_kesulitan": "tinggi"},
        "priority": "KRITIS",
        "points": 95,
        "rekomendasi": "Tugas sulit dan deadline sangat dekat. Fokus penuh.",
        "warna": "#ef4444",
    },

    # ─── PRIORITAS: SANGAT TINGGI ────────────────────────────────────────────────
    {
        "id": "R04",
        "desc": "Deadline ≤3 hari AND bobot ≥25%",
        "conditions": {"deadline_hari": "≤3", "bobot_persen": "≥25"},
        "priority": "SANGAT TINGGI",
        "points": 88,
        "rekomendasi": "Segera dikerjakan hari ini juga.",
        "warna": "#f97316",
    },
    {
        "id": "R05",
        "desc": "Deadline ≤3 hari AND tipe=ujian/quiz",
        "conditions": {"deadline_hari": "≤3", "tipe_tugas": "ujian"},
        "priority": "SANGAT TINGGI",
        "points": 90,
        "rekomendasi": "Ujian dekat! Prioritaskan belajar.",
        "warna": "#f97316",
    },
    {
        "id": "R06",
        "desc": "Deadline ≤5 hari AND kesulitan=tinggi AND bobot ≥25%",
        "conditions": {"deadline_hari": "≤5", "tingkat_kesulitan": "tinggi", "bobot_persen": "≥25"},
        "priority": "SANGAT TINGGI",
        "points": 85,
        "rekomendasi": "Tugas berat dengan bobot besar. Mulai lebih awal.",
        "warna": "#f97316",
    },

    # ─── PRIORITAS: TINGGI ───────────────────────────────────────────────────────
    {
        "id": "R07",
        "desc": "Deadline ≤5 hari AND bobot ≥15%",
        "conditions": {"deadline_hari": "≤5", "bobot_persen": "≥15"},
        "priority": "TINGGI",
        "points": 75,
        "rekomendasi": "Kerjakan dalam 1–2 hari ke depan.",
        "warna": "#eab308",
    },
    {
        "id": "R08",
        "desc": "Deadline ≤7 hari AND kesulitan=tinggi",
        "conditions": {"deadline_hari": "≤7", "tingkat_kesulitan": "tinggi"},
        "priority": "TINGGI",
        "points": 72,
        "rekomendasi": "Tugas sulit butuh waktu ekstra. Jangan ditunda.",
        "warna": "#eab308",
    },
    {
        "id": "R09",
        "desc": "Deadline ≤7 hari AND sudah_dimulai=tidak AND bobot ≥10%",
        "conditions": {"deadline_hari": "≤7", "sudah_dimulai": "tidak", "bobot_persen": "≥10"},
        "priority": "TINGGI",
        "points": 70,
        "rekomendasi": "Belum dimulai, ada seminggu lagi. Segera mulai.",
        "warna": "#eab308",
    },

    # ─── PRIORITAS: SEDANG ───────────────────────────────────────────────────────
    {
        "id": "R10",
        "desc": "Deadline ≤10 hari AND bobot ≥20%",
        "conditions": {"deadline_hari": "≤10", "bobot_persen": "≥20"},
        "priority": "SEDANG",
        "points": 55,
        "rekomendasi": "Jadwalkan pengerjaan dalam minggu ini.",
        "warna": "#84cc16",
    },
    {
        "id": "R11",
        "desc": "Deadline ≤7 hari AND kesulitan=sedang",
        "conditions": {"deadline_hari": "≤7", "tingkat_kesulitan": "sedang"},
        "priority": "SEDANG",
        "points": 52,
        "rekomendasi": "Bisa dikerjakan besok, tapi jangan lebih dari itu.",
        "warna": "#84cc16",
    },
    {
        "id": "R12",
        "desc": "Deadline ≤14 hari AND tipe=ujian AND kesulitan=sedang",
        "conditions": {"deadline_hari": "≤14", "tipe_tugas": "ujian", "tingkat_kesulitan": "sedang"},
        "priority": "SEDANG",
        "points": 50,
        "rekomendasi": "Mulai cicil materi belajar.",
        "warna": "#84cc16",
    },

    # ─── PRIORITAS: RENDAH ───────────────────────────────────────────────────────
    {
        "id": "R13",
        "desc": "Deadline ≤14 hari AND kesulitan=rendah",
        "conditions": {"deadline_hari": "≤14", "tingkat_kesulitan": "rendah"},
        "priority": "RENDAH",
        "points": 30,
        "rekomendasi": "Aman. Kerjakan di akhir pekan.",
        "warna": "#22c55e",
    },
    {
        "id": "R14",
        "desc": "Deadline >14 hari AND bobot <15%",
        "conditions": {"deadline_hari": ">14", "bobot_persen": "<15"},
        "priority": "RENDAH",
        "points": 20,
        "rekomendasi": "Masih sangat longgar. Catat saja dulu di planner.",
        "warna": "#22c55e",
    },

    # ─── PRIORITAS: SANGAT RENDAH ────────────────────────────────────────────────
    {
        "id": "R15",
        "desc": "Deadline >14 hari AND kesulitan=rendah AND bobot <10%",
        "conditions": {"deadline_hari": ">14", "tingkat_kesulitan": "rendah", "bobot_persen": "<10"},
        "priority": "SANGAT RENDAH",
        "points": 10,
        "rekomendasi": "Fokus dulu ke tugas lain. Ini belakangan.",
        "warna": "#3b82f6",
    },
]

# Default fallback
DEFAULT_RULE = {
    "id": "R_DEFAULT",
    "desc": "Fallback",
    "conditions": {},
    "priority": "SEDANG",
    "points": 45,
    "rekomendasi": "Pertimbangkan semua faktor sebelum memulai.",
    "warna": "#84cc16",
}

# ─────────────────────────────────────────────
#  INFERENCE ENGINE  (forward chaining)
# ─────────────────────────────────────────────

def check_condition(key, op_val, facts):
    val = facts.get(key)
    if val is None:
        return False

    # numeric comparisons
    if isinstance(val, (int, float)):
        if op_val.startswith("≤"):
            return val <= float(op_val[1:])
        elif op_val.startswith("≥"):
            return val >= float(op_val[1:])
        elif op_val.startswith("<"):
            return val < float(op_val[1:])
        elif op_val.startswith(">"):
            return val > float(op_val[1:])
    # string equality
    return str(val).lower() == str(op_val).lower()


def infer(facts):
    """
    Forward chaining: kembalikan rule pertama yang semua kondisinya terpenuhi.
    Rule dengan poin tertinggi yang match menang.
    """
    matched = []
    fired_rules = []

    for rule in RULES:
        cond_results = {}
        all_met = True
        for key, op_val in rule["conditions"].items():
            result = check_condition(key, op_val, facts)
            cond_results[key] = result
            if not result:
                all_met = False

        fired_rules.append({
            "id": rule["id"],
            "desc": rule["desc"],
            "fired": all_met,
            "conditions_detail": cond_results,
        })

        if all_met:
            matched.append(rule)

    # Pilih rule dengan poin tertinggi
    if matched:
        best = max(matched, key=lambda r: r["points"])
    else:
        best = DEFAULT_RULE

    return best, fired_rules


# ─────────────────────────────────────────────
#  FLASK ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/infer", methods=["POST"])
def infer_route():
    data = request.get_json()
    tasks = data.get("tasks", [])
    results = []

    for t in tasks:
        facts = {
            "nama":             t["nama"],
            "deadline_hari":    float(t["deadline_hari"]),
            "bobot_persen":     float(t["bobot_persen"]),
            "tingkat_kesulitan": t["tingkat_kesulitan"].lower(),
            "tipe_tugas":       t["tipe_tugas"].lower(),
            "sudah_dimulai":    t["sudah_dimulai"].lower(),
        }

        best_rule, fired_rules = infer(facts)

        results.append({
            "nama":        t["nama"],
            "priority":    best_rule["priority"],
            "points":      best_rule["points"],
            "warna":       best_rule["warna"],
            "rekomendasi": best_rule["rekomendasi"],
            "fired_rule":  best_rule["id"],
            "rule_desc":   best_rule["desc"],
            "all_rules":   fired_rules,
            "facts":       facts,
        })

    results.sort(key=lambda x: x["points"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return jsonify(results)


@app.route("/rules")
def get_rules():
    return jsonify(RULES)


if __name__ == "__main__":
    app.run(debug=True, port=5001)