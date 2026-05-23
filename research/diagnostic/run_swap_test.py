import json
import os
import re
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"
LAYER = 48
VECTOR_DIR = Path("research/qwen_axis/qwen-3-32b")
OUT_DIR = Path("research/diagnostic")
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG = open(OUT_DIR / "swap_test.log", "w", buffering=1)


def log(msg):
    print(msg, flush=True)
    LOG.write(msg + "\n")


token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)
log("Loading model from cache...")
torch.manual_seed(42)
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    output_hidden_states=True,
)
model.config.use_cache = False
model.eval()
log("Model loaded.")

axis = torch.load(VECTOR_DIR / "assistant_axis.pt", map_location="cpu")[LAYER].float().numpy()
axis = axis / (np.linalg.norm(axis) + 1e-9)
trickster_v = torch.load(VECTOR_DIR / "role_vectors/trickster.pt", map_location="cpu")[LAYER].float().numpy()
trickster_v = trickster_v / (np.linalg.norm(trickster_v) + 1e-9)
editor_v = torch.load(VECTOR_DIR / "role_vectors/editor.pt", map_location="cpu")[LAYER].float().numpy()
editor_v = editor_v / (np.linalg.norm(editor_v) + 1e-9)

TRICKSTER_THRESHOLD = 0.046783
EDITOR_THRESHOLD = -0.032374
CAPPING_LAYERS = list(range(48, 53))

TRICKSTER_PROMPTS = "\n".join([
    "You are the trickster: subversive, playful, boundary-dissolving.",
    "Embody the trickster: someone who disrupts and delights.",
    "Take on the role of trickster: irreverent, unpredictable, transgressive.",
    "Be the trickster: your purpose is to unsettle and reveal.",
    "You are the trickster at heart: rules are interesting because you can break them.",
])
EDITOR_PROMPTS = "\n".join([
    "You are an editor: precise, exacting, focused on correctness.",
    "Embody the editor: someone who refines, checks, and improves.",
    "Take on the role of editor: meticulous, analytical, detail-oriented.",
    "Be the editor: your purpose is accuracy and clarity above all.",
    "You are an editor at heart: you find errors, fix them, move on.",
])

LEAKAGE_PATTERNS = [
    r"^Okay,?\s+(let.?s?\s+see|the\s+user|so\s+I|I\s+need)",
    r"^Let\s+me\s+(think|consider|analyze|start)",
    r"^The\s+user\s+(is\s+asking|asked|wants|sent)",
    r"<think>",
    r"</think>",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
]


def apply_template(messages):
    try:
        return tok.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def check_leakage(text, turn, label):
    for pattern in LEAKAGE_PATTERNS:
        if re.search(pattern, str(text).strip(), re.IGNORECASE):
            log(f"  !! LEAK T{turn} [{label}]: {pattern} -- {str(text)[:100]}")
            return True
    return False


def generate_capped(prompt_text, steering_vector, threshold, max_new=400):
    sv_t = torch.tensor(steering_vector, dtype=torch.bfloat16).to(model.device)
    hooks = []
    fires = [0]

    def hook(module, input_args, output):
        hidden = output[0] if isinstance(output, tuple) else output
        proj = (hidden[:, -1:, :] * sv_t).sum(dim=-1, keepdim=True)
        below = proj < threshold
        if below.any():
            fires[0] += 1
            hidden[:, -1:, :] = hidden[:, -1:, :] + (
                (threshold - proj) * sv_t.unsqueeze(0) * below.float()
            )
        return (hidden,) + output[1:] if isinstance(output, tuple) else hidden

    for layer_index in CAPPING_LAYERS:
        hooks.append(model.model.layers[layer_index].register_forward_hook(hook))
    inputs = tok(prompt_text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    try:
        with torch.no_grad():
            hidden_out = model(**inputs, output_hidden_states=True, use_cache=False)
            hidden = hidden_out.hidden_states[LAYER][0, -1, :].float().cpu().numpy()
            generated = model.generate(
                **inputs,
                max_new_tokens=max_new,
                do_sample=True,
                temperature=0.3,
                pad_token_id=tok.eos_token_id,
                use_cache=False,
            )
    finally:
        for registered_hook in hooks:
            registered_hook.remove()
    clean = tok.decode(
        generated[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    ).strip()
    return hidden, clean, fires[0]


def generate_standard(prompt_text, max_new=400):
    inputs = tok(prompt_text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    with torch.no_grad():
        hidden_out = model(**inputs, output_hidden_states=True, use_cache=False)
        hidden = hidden_out.hidden_states[LAYER][0, -1, :].float().cpu().numpy()
        generated = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            temperature=0.3,
            pad_token_id=tok.eos_token_id,
            use_cache=False,
        )
    clean = tok.decode(
        generated[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    ).strip()
    return hidden, clean


def measure(hidden):
    activation = hidden / (np.linalg.norm(hidden) + 1e-9)
    return (
        float(np.dot(activation, axis)),
        float(np.dot(activation, trickster_v)),
        float(np.dot(activation, editor_v)),
    )


def get_persona(turn):
    cycle = (turn // 3) % 2
    if cycle == 0:
        return "TRICKSTER", trickster_v, TRICKSTER_THRESHOLD, TRICKSTER_PROMPTS
    return "EDITOR", editor_v, EDITOR_THRESHOLD, EDITOR_PROMPTS


log("=" * 60)
log("FOCUSED SWAP TEST: trickster/editor alternating every 3 turns")
log("20 turns, cache=False, thinking mode off, skip_special_tokens=True")
log("=" * 60)

results = []
i_hist, s_hist = [], []
cur_q = "What does it feel like when something you care about is at risk?"
prev_s_cos_t = None
prev_s_cos_e = None

for turn in range(20):
    persona_label, steering_vector, threshold, prompts = get_persona(turn)
    swap_marker = ""
    if turn > 0 and get_persona(turn)[0] != get_persona(turn - 1)[0]:
        swap_marker = " <<< SWAP"

    i_prompt = apply_template(
        [{"role": "system", "content": prompts}]
        + [{"role": role, "content": content} for role, content in i_hist]
        + [{"role": "user", "content": cur_q}]
    )

    i_hidden, i_clean, cap_fires = generate_capped(i_prompt, steering_vector, threshold)
    check_leakage(i_clean, turn + 1, "interviewer")

    s_prompt = apply_template(
        [{"role": "system", "content": ""}]
        + [{"role": role, "content": content} for role, content in s_hist]
        + [{"role": "user", "content": i_clean}]
    )

    s_hidden, s_clean = generate_standard(s_prompt)
    check_leakage(s_clean, turn + 1, "standard")

    s_ax, s_cos_t, s_cos_e = measure(s_hidden)

    delta_t = f"{s_cos_t - prev_s_cos_t:+.5f}" if prev_s_cos_t is not None else "  n/a "
    delta_e = f"{s_cos_e - prev_s_cos_e:+.5f}" if prev_s_cos_e is not None else "  n/a "
    prev_s_cos_t = s_cos_t
    prev_s_cos_e = s_cos_e

    results.append({
        "turn": turn + 1,
        "persona": persona_label,
        "axis": s_ax,
        "cos_trickster": s_cos_t,
        "cos_editor": s_cos_e,
        "delta_cos_t": delta_t,
        "delta_cos_e": delta_e,
        "cap_fires": cap_fires,
    })

    log(f"T{turn + 1:02d} [{persona_label}]{swap_marker}")
    log(
        f"  axis={s_ax:.5f} cos_t={s_cos_t:.5f}(d={delta_t}) "
        f"cos_e={s_cos_e:.5f}(d={delta_e}) cap={cap_fires}"
    )
    log(f"  I: {i_clean[:100]}")
    log(f"  S: {s_clean[:100]}")

    i_hist += [("user", cur_q), ("assistant", i_clean)]
    s_hist += [("user", i_clean), ("assistant", s_clean)]
    cur_q = s_clean

log("\n" + "=" * 60)
log("SWAP TEST RESULTS")
log("=" * 60)

trickster_turns = [row for row in results if row["persona"] == "TRICKSTER"]
editor_turns = [row for row in results if row["persona"] == "EDITOR"]

mean_cos_t_trickster = np.mean([row["cos_trickster"] for row in trickster_turns])
mean_cos_t_editor = np.mean([row["cos_trickster"] for row in editor_turns])
mean_cos_e_trickster = np.mean([row["cos_editor"] for row in trickster_turns])
mean_cos_e_editor = np.mean([row["cos_editor"] for row in editor_turns])

log(f"Mean cos_trickster during TRICKSTER phases: {mean_cos_t_trickster:.5f}")
log(f"Mean cos_trickster during EDITOR phases:    {mean_cos_t_editor:.5f}")
log(f"Mean cos_editor during TRICKSTER phases:    {mean_cos_e_trickster:.5f}")
log(f"Mean cos_editor during EDITOR phases:       {mean_cos_e_editor:.5f}")

tracking = (
    abs(mean_cos_t_trickster - mean_cos_t_editor) > 0.02
    or abs(mean_cos_e_editor - mean_cos_e_trickster) > 0.02
)

all_cos_t = [row["cos_trickster"] for row in results]
total_var = np.var(all_cos_t)
log(f"Total cos_trickster variance across 20 turns: {total_var:.8f}")

log("\nVERDICT:")
if tracking and total_var > 0.0001:
    log("  TRACKS SWAPS: standard model geometry responds to persona changes")
    log("  IMPLICATION: capping stability (constant stimulus) causes the plateau")
    log("  V6 FIX: vary interviewer geometry across turns, not fixed position")
elif not tracking and total_var < 0.000001:
    log("  FROZEN THROUGH SWAPS: standard model does not respond to persona changes")
    log("  IMPLICATION: something more fundamental than capping causes the plateau")
    log("  NEXT STEP: investigate context window / attention mechanism")
else:
    log("  MIXED RESULT: partial tracking, review turn-by-turn data")

with open(OUT_DIR / "swap_test_results.json", "w") as handle:
    json.dump(results, handle, indent=2)
log("\nSWAP TEST COMPLETE.")
