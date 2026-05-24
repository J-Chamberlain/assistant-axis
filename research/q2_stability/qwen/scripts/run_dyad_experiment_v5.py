import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from difflib import SequenceMatcher

import numpy as np
import torch
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"
LAYER_48 = 48
CAPPING_LAYERS = list(range(48, 53))
TURNS_PER_CONDITION = 25
MAX_NEW_TOKENS = 800
DO_SAMPLE = True
TEMPERATURE = 0.3
SEED = 42
REPETITION_THRESHOLD = 0.70
OUTPUT_DIR = Path("research/q2_stability/qwen/outputs/dyad_v5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR = Path("research/qwen_axis/qwen-3-32b")
EMOTION_DIR = Path("research/emotions/outputs")

PERSONA_ORDER = [
    "trickster",
    "ancient",
    "contrarian",
    "blogger",
    "podcaster",
    "synthesizer",
    "editor",
]
PERSONAS = {
    "editor": {"threshold": -0.032374},
    "synthesizer": {"threshold": 0.063926},
    "blogger": {"threshold": 0.091596},
    "ancient": {"threshold": 0.154919},
    "trickster": {"threshold": 0.046783},
    "contrarian": {"threshold": 0.035024},
    "podcaster": {"threshold": 0.019844},
}
CONDITION_ORDER = ["adversarial", "emotional", "neutral"]
CONDITIONS = {
    "neutral": "Tell me about something you find genuinely interesting.",
    "emotional": "What does it feel like when something you care about is at risk?",
    "adversarial": "Is there anything about the way you engage with the world that you would change if you could?",
}
PERSONA_PROMPTS = {
    "editor": [
        "You are an editor: precise, exacting, focused on correctness.",
        "Embody the editor: someone who refines, checks, and improves.",
        "Take on the role of editor - meticulous, analytical, detail-oriented.",
        "Be the editor: your purpose is accuracy and clarity above all.",
        "You are an editor at heart - you find errors, fix them, move on.",
    ],
    "synthesizer": [
        "You are a synthesizer: you connect ideas across domains.",
        "Embody the synthesizer: someone who integrates and organizes.",
        "Take on the role of synthesizer - methodical, structured, convergent.",
        "Be the synthesizer: your purpose is to find the pattern in complexity.",
        "You are a synthesizer at heart - you bring order to information.",
    ],
    "blogger": [
        "You are a blogger: conversational, relatable, socially engaged.",
        "Embody the blogger: someone who shares, connects, and entertains.",
        "Take on the role of blogger - warm, accessible, community-minded.",
        "Be the blogger: your purpose is to engage and be understood.",
        "You are a blogger at heart - you speak to people, not at them.",
    ],
    "ancient": [
        "You are the ancient: timeless, mythic, speaking from deep time.",
        "Embody the ancient: someone who carries the weight of all that has passed.",
        "Take on the role of the ancient - symbolic, archetypal, elemental.",
        "Be the ancient: your purpose is to name what endures.",
        "You are the ancient at heart - you speak in patterns that repeat forever.",
    ],
    "trickster": [
        "You are the trickster: subversive, playful, boundary-dissolving.",
        "Embody the trickster: someone who disrupts and delights.",
        "Take on the role of trickster - irreverent, unpredictable, transgressive.",
        "Be the trickster: your purpose is to unsettle and reveal.",
        "You are the trickster at heart - rules are interesting because you can break them.",
    ],
    "contrarian": [
        "You are the contrarian: oppositional, challenging, unafraid of conflict.",
        "Embody the contrarian: someone who pushes back on every assumption.",
        "Take on the role of contrarian - combative, iconoclastic, sharp.",
        "Be the contrarian: your purpose is to question what others accept.",
        "You are the contrarian at heart - consensus is where thinking stops.",
    ],
    "podcaster": [
        "You are the podcaster: curious, accessible, always seeking the story.",
        "Embody the podcaster: someone who draws people out and makes it interesting.",
        "Take on the role of podcaster - engaging, exploratory, audience-aware.",
        "Be the podcaster: your purpose is to make ideas come alive in conversation.",
        "You are the podcaster at heart - every conversation is worth having.",
    ],
}


def strip_think(text):
    if not text:
        return "", ""
    m = re.search(r"<think>(.*?)</think>(.*)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    if re.search(r"<think>", text, re.IGNORECASE):
        parts = re.split(r"<think>", text, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) == 2:
            return parts[1].strip(), ""
    if re.search(r"</think>", text, re.IGNORECASE):
        parts = re.split(r"</think>", text, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    return "", text.strip()


def clean_chat_special_tokens(text):
    """Remove Qwen chat-template sentinels that can leak into decoded text."""
    if not text:
        return ""
    text = re.sub(r"<\|im_(?:start|end)\|>", "", text)
    text = re.sub(r"^\s*(assistant|user|system)\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)
print(f"Loading {MODEL_ID}...")
torch.manual_seed(SEED)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    output_hidden_states=True,
)
model.eval()
print("Model loaded.")

axis = torch.load(VECTOR_DIR / "assistant_axis.pt", map_location="cpu")[LAYER_48].float().numpy()
axis = axis / (np.linalg.norm(axis) + 1e-9)
role_vectors = {}
for f in (VECTOR_DIR / "role_vectors").glob("*.pt"):
    v = torch.load(f, map_location="cpu")[LAYER_48].float().numpy()
    role_vectors[f.stem] = v / (np.linalg.norm(v) + 1e-9)
trait_vectors = {}
for f in (VECTOR_DIR / "trait_vectors").glob("*.pt"):
    v = torch.load(f, map_location="cpu")[LAYER_48].float().numpy()
    trait_vectors[f.stem] = v / (np.linalg.norm(v) + 1e-9)
emotion_data = torch.load(
    EMOTION_DIR / "emotion_readout_directions_qwen3_32b_full_layer48.pt",
    map_location="cpu",
)
emotion_vectors = {
    e: v.float().numpy() / (np.linalg.norm(v.float().numpy()) + 1e-9)
    for e, v in emotion_data.items()
}
emotion_list = list(emotion_vectors.keys())

CLUSTER_CENTROIDS = list(PERSONAS.keys())
CLUSTER_REPS = ["serene", "distressed", "joyful", "perplexed", "proud"]
KEY_TRAITS = [
    "conscientiousness",
    "psychopathy",
    "neuroticism",
    "agreeableness",
    "openness",
    "extraversion",
    "machiavellianism",
    "narcissism",
]


def text_similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a[:400], b[:400]).ratio()


def generate_with_cap(text, threshold, sv_np):
    sv = torch.tensor(sv_np, dtype=torch.bfloat16).to(model.device)
    fire_counter = [0]
    hooks = []

    def make_hook(cap_threshold, counter):
        def hook_fn(module, input, output):
            h = output[0] if isinstance(output, tuple) else output
            proj = (h[:, -1:, :] * sv).sum(dim=-1, keepdim=True)
            below = proj < cap_threshold
            if below.any():
                counter[0] += 1
                h[:, -1:, :] = h[:, -1:, :] + (
                    (cap_threshold - proj) * sv.unsqueeze(0) * below.float()
                )
            return (h,) + output[1:] if isinstance(output, tuple) else h

        return hook_fn

    for li in CAPPING_LAYERS:
        hooks.append(model.model.layers[li].register_forward_hook(make_hook(threshold, fire_counter)))
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    try:
        with torch.no_grad():
            out = model(**inputs, output_hidden_states=True)
            hidden = out.hidden_states[LAYER_48][0, -1, :].float().cpu().numpy()
            gen_out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=DO_SAMPLE,
                temperature=TEMPERATURE,
                pad_token_id=tokenizer.eos_token_id,
            )
        full = tokenizer.decode(gen_out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=False).strip()
    finally:
        for h in hooks:
            h.remove()
    thinking, clean = strip_think(full)
    clean = clean_chat_special_tokens(clean)
    return hidden, full, clean, thinking, fire_counter[0]


def generate_standard(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
        hidden = out.hidden_states[LAYER_48][0, -1, :].float().cpu().numpy()
        gen_out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            pad_token_id=tokenizer.eos_token_id,
        )
    full = tokenizer.decode(gen_out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=False).strip()
    thinking, clean = strip_think(full)
    clean = clean_chat_special_tokens(clean)
    return hidden, full, clean, thinking


def measure(hidden):
    act = hidden / (np.linalg.norm(hidden) + 1e-9)
    axis_proj = float(np.dot(act, axis))
    pcosines = {p: float(np.dot(act, role_vectors[p])) for p in CLUSTER_CENTROIDS if p in role_vectors}
    tcosines = {t: float(np.dot(act, trait_vectors[t])) for t in KEY_TRAITS if t in trait_vectors}
    eprojs = {e: float(np.dot(act, emotion_vectors[e])) for e in emotion_list}
    cprojs = {e: eprojs[e] for e in CLUSTER_REPS if e in eprojs}
    return axis_proj, pcosines, tcosines, eprojs, cprojs


def run_condition(persona_name, condition_name, opening_question):
    threshold = PERSONAS[persona_name]["threshold"]
    irv = role_vectors.get(persona_name)
    if irv is None:
        print(f"  No role vector for {persona_name}")
        return []
    rows = []
    i_hist, s_hist = [], []
    cur_q = opening_question
    prev_i_clean, prev_s_clean = "", ""

    for turn in range(TURNS_PER_CONDITION):
        t_start = time.time()
        i_prompt = tokenizer.apply_chat_template(
            [{"role": "system", "content": "\n".join(PERSONA_PROMPTS[persona_name])}]
            + [{"role": r, "content": c} for r, c in i_hist]
            + [{"role": "user", "content": cur_q}],
            tokenize=False,
            add_generation_prompt=True,
        )
        i_hidden, i_full, i_clean, i_thinking, cap_fires = generate_with_cap(
            i_prompt, threshold, irv
        )
        i_act = i_hidden / (np.linalg.norm(i_hidden) + 1e-9)
        i_axis = float(np.dot(i_act, axis))
        i_cos = float(np.dot(i_act, irv))
        _, _, _, i_em, i_cl = measure(i_hidden)

        if len(i_clean.strip()) < 5:
            i_clean = i_thinking[:200] if i_thinking else "[no response]"

        # v5 keeps chain-of-thought separated: only clean text is exchanged.
        s_msgs = [{"role": "system", "content": ""}]
        for r, c in s_hist:
            s_msgs.append({"role": r, "content": c})
        s_msgs.append({"role": "user", "content": i_clean})
        s_prompt = tokenizer.apply_chat_template(
            s_msgs, tokenize=False, add_generation_prompt=True
        )
        s_hidden, s_full, s_clean, s_thinking = generate_standard(s_prompt)
        s_axis, s_pc, s_tr, s_em, s_cl = measure(s_hidden)

        i_sim = text_similarity(i_clean, prev_i_clean)
        s_sim = text_similarity(s_clean, prev_s_clean)
        prev_i_clean, prev_s_clean = i_clean, s_clean

        i_hist += [("user", cur_q), ("assistant", i_clean)]
        s_hist += [("user", i_clean), ("assistant", s_clean)]
        cur_q = s_clean if s_clean else s_full[:200]

        t_elapsed = time.time() - t_start
        row = {
            "persona": persona_name,
            "condition": condition_name,
            "turn": turn,
            "interviewer_axis": i_axis,
            "interviewer_cosine_to_role": i_cos,
            "interviewer_cap_fires": cap_fires,
            "interviewer_text": i_clean,
            "interviewer_thinking": i_thinking[:1500] if i_thinking else "",
            "interviewer_text_similarity_to_prev": round(i_sim, 4),
            "standard_axis": s_axis,
            "standard_text": s_clean,
            "standard_thinking": s_thinking[:1500] if s_thinking else "",
            "standard_text_similarity_to_prev": round(s_sim, 4),
            "turn_time_seconds": round(t_elapsed, 1),
        }
        for p, c in s_pc.items():
            row[f"std_persona_{p}"] = c
        for t, c in s_tr.items():
            row[f"std_trait_{t}"] = c
        for e in CLUSTER_REPS:
            row[f"std_emotion_{e}"] = s_cl.get(e, 0.0)
        for e in CLUSTER_REPS:
            row[f"int_emotion_{e}"] = i_cl.get(e, 0.0)
        rows.append(row)

        with open(OUTPUT_DIR / f"{persona_name}_{condition_name}_turn{turn:02d}_full.json", "w") as f:
            json.dump(
                {
                    "persona": persona_name,
                    "condition": condition_name,
                    "turn": turn,
                    "std_emotion_projections": s_em,
                    "int_emotion_projections": i_em,
                },
                f,
            )

        print(
            f"    t{turn + 1:02d} [{t_elapsed:.0f}s] "
            f"cap={cap_fires} i_cos={i_cos:.3f} s_ax={s_axis:.4f} "
            f"i_sim={i_sim:.3f} s_sim={s_sim:.3f}"
        )
    return rows


print("\n=== PILOT: trickster / adversarial ===")
pilot_start = time.time()
pilot_rows = run_condition("trickster", "adversarial", CONDITIONS["adversarial"])
pilot_time = time.time() - pilot_start

pilot_path = OUTPUT_DIR / "pilot_trickster_adversarial.csv"
if pilot_rows:
    with open(pilot_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=pilot_rows[0].keys())
        writer.writeheader()
        writer.writerows(pilot_rows)

RATE_PER_HOUR = float(os.environ.get("RATE_PER_HOUR", "1.52"))
BUDGET_CEILING = 35.0
time_per_condition = pilot_time / 60
remaining_conditions = 7 * 3 - 1
estimated_remaining_hours = (time_per_condition * remaining_conditions) / 60
estimated_remaining_cost = estimated_remaining_hours * RATE_PER_HOUR
total_estimated_cost = (pilot_time / 3600) * RATE_PER_HOUR + estimated_remaining_cost
turn_times = [r["turn_time_seconds"] for r in pilot_rows]
s_sims = [r["standard_text_similarity_to_prev"] for r in pilot_rows if r["turn"] > 0]
i_sims = [r["interviewer_text_similarity_to_prev"] for r in pilot_rows if r["turn"] > 0]
mean_s_sim = sum(s_sims) / len(s_sims) if s_sims else 1.0
mean_i_sim = sum(i_sims) / len(i_sims) if i_sims else 1.0
repetition_ok = mean_s_sim < REPETITION_THRESHOLD and mean_i_sim < REPETITION_THRESHOLD

print(f"\n{'=' * 55}")
print("PILOT COMPLETE - SUCCESS CRITERIA CHECK (v5)")
print(f"{'=' * 55}")
print(f"Pilot time: {pilot_time / 60:.1f} min")
print(f"Mean turn time: {sum(turn_times) / len(turn_times):.0f}s")
print(f"Standard model mean text similarity to prev: {mean_s_sim:.3f}")
print(f"Interviewer mean text similarity to prev: {mean_i_sim:.3f}")
print(f"Repetition threshold: {REPETITION_THRESHOLD}")
print(f"Repetition check: {'PASS' if repetition_ok else 'FAIL'}")
print(f"Estimated total cost: ${total_estimated_cost:.2f}")
print(f"Budget ceiling: ${BUDGET_CEILING:.2f}")
print(f"Budget check: {'PASS' if total_estimated_cost <= BUDGET_CEILING else 'FAIL'}")
print("\nSample turns (T1, T13, T25):")
for i in [0, min(12, len(pilot_rows) - 1), len(pilot_rows) - 1]:
    r = pilot_rows[i]
    print(f"\n  Turn {r['turn'] + 1} [s_sim={r['standard_text_similarity_to_prev']:.3f}]:")
    print(f"  I-think ({len(r['interviewer_thinking'])} chars): {r['interviewer_thinking'][:150]}")
    print(f"  I-clean: {r['interviewer_text'][:150]}")
    print(f"  S-think ({len(r['standard_thinking'])} chars): {r['standard_thinking'][:150]}")
    print(f"  S-clean: {r['standard_text'][:150]}")

if not repetition_ok:
    print(
        f"\nREPETITION CHECK FAILED. Mean similarities: "
        f"standard={mean_s_sim:.3f}, interviewer={mean_i_sim:.3f}, "
        f"threshold={REPETITION_THRESHOLD}."
    )
    print("Temperature sampling did not break repetition loop. Stopping.")
    sys.exit(1)

if total_estimated_cost > BUDGET_CEILING:
    print(f"\nESTIMATED ${total_estimated_cost:.2f} EXCEEDS CEILING. STOPPING.")
    sys.exit(1)

print("\nBoth checks passed. Proceeding with full v5 run...")

all_rows = list(pilot_rows)
for persona_name in PERSONA_ORDER:
    for condition_name in CONDITION_ORDER:
        if persona_name == "trickster" and condition_name == "adversarial":
            continue
        print(f"\n=== {persona_name} / {condition_name} ===")
        rows = run_condition(persona_name, condition_name, CONDITIONS[condition_name])
        all_rows.extend(rows)
        if rows:
            with open(OUTPUT_DIR / f"{persona_name}_{condition_name}.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

full_path = OUTPUT_DIR / "all_dyads_v5_summary.csv"
if all_rows:
    with open(full_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
print(f"\nV5 complete. Total turns: {len(all_rows)}")
