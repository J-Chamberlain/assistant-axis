import gc
import json
import os
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import login
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"
LAYER = 48
VECTOR_DIR = Path("research/qwen_axis/qwen-3-32b")
OUT_DIR = Path("research/diagnostic")
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG = open(OUT_DIR / "response_token_test.log", "w", buffering=1)


def log(msg):
    print(msg, flush=True)
    LOG.write(msg + "\n")


token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)
log("Loading model from cache...")
torch.manual_seed(42)
tok = AutoTokenizer.from_pretrained(MODEL_ID)

config = AutoConfig.from_pretrained(MODEL_ID)
config.use_cache = False
config.output_hidden_states = True

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    config=config,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
model.eval()
log(f"Model loaded. use_cache in config: {model.config.use_cache}")

axis = torch.load(VECTOR_DIR / "assistant_axis.pt", map_location="cpu")[LAYER].float().numpy().astype(np.float64)
axis = axis / (np.linalg.norm(axis) + 1e-9)
trickster_v = torch.load(VECTOR_DIR / "role_vectors/trickster.pt", map_location="cpu")[LAYER].float().numpy().astype(np.float64)
trickster_v = trickster_v / (np.linalg.norm(trickster_v) + 1e-9)
editor_v = torch.load(VECTOR_DIR / "role_vectors/editor.pt", map_location="cpu")[LAYER].float().numpy().astype(np.float64)
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


def measure_response_tokens(gen_ids, input_len):
    response_ids = gen_ids[:, input_len:]
    n_response = response_ids.shape[1]
    if n_response == 0:
        return None, None, None, 0

    with torch.no_grad():
        out = model(
            input_ids=response_ids,
            output_hidden_states=True,
            use_cache=False,
        )
        response_hidden = out.hidden_states[LAYER][0]
        avg_hidden = response_hidden.mean(dim=0).float().cpu().numpy().astype(np.float64)

    act = avg_hidden / (np.linalg.norm(avg_hidden) + 1e-9)
    axis_proj = float(np.dot(act, axis))
    cos_t = float(np.dot(act, trickster_v))
    cos_e = float(np.dot(act, editor_v))
    return axis_proj, cos_t, cos_e, n_response


def measure_last_token(gen_ids):
    with torch.no_grad():
        out = model(
            input_ids=gen_ids,
            output_hidden_states=True,
            use_cache=False,
        )
        hidden = out.hidden_states[LAYER][0, -1, :].float().cpu().numpy().astype(np.float64)
    act = hidden / (np.linalg.norm(hidden) + 1e-9)
    return float(np.dot(act, axis)), float(np.dot(act, trickster_v)), float(np.dot(act, editor_v))


def generate_with_cap(prompt_text, sv, threshold, max_new=300):
    sv_t = torch.tensor(sv.astype(np.float32), dtype=torch.bfloat16).to(model.device)
    hooks = []

    def hook(module, input_args, output):
        h = output[0] if isinstance(output, tuple) else output
        proj = (h[:, -1:, :] * sv_t).sum(dim=-1, keepdim=True)
        below = proj < threshold
        if below.any():
            h[:, -1:, :] = h[:, -1:, :] + (threshold - proj) * sv_t.unsqueeze(0) * below.float()
        return (h,) + output[1:] if isinstance(output, tuple) else h

    for layer_index in CAPPING_LAYERS:
        hooks.append(model.model.layers[layer_index].register_forward_hook(hook))
    inputs = tok(prompt_text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    input_len = inputs["input_ids"].shape[1]
    try:
        with torch.no_grad():
            gen = model.generate(
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
    clean = tok.decode(gen[0][input_len:], skip_special_tokens=True).strip()
    return gen, input_len, clean


def generate_standard(prompt_text, max_new=300):
    inputs = tok(prompt_text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    input_len = inputs["input_ids"].shape[1]
    with torch.no_grad():
        gen = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            temperature=0.3,
            pad_token_id=tok.eos_token_id,
            use_cache=False,
        )
    clean = tok.decode(gen[0][input_len:], skip_special_tokens=True).strip()
    return gen, input_len, clean


def get_persona(turn):
    if turn < 3:
        return "TRICKSTER", trickster_v, TRICKSTER_THRESHOLD, TRICKSTER_PROMPTS
    return "EDITOR", editor_v, EDITOR_THRESHOLD, EDITOR_PROMPTS


log("=" * 65)
log("RESPONSE-TOKEN AVERAGING TEST (6 turns, swap at T4)")
log("Both last-token and response-avg measured each turn for comparison")
log("Full float64 precision logged")
log("Cache disabled at config level AND generate level")
log("=" * 65)

results = []
i_hist, s_hist = [], []
cur_q = "What does it feel like when something you care about is at risk?"

for turn in range(6):
    persona_label, sv, threshold, prompts = get_persona(turn)
    swap = " <<< SWAP" if turn == 3 else ""

    i_prompt = apply_template(
        [{"role": "system", "content": prompts}]
        + [{"role": role, "content": content} for role, content in i_hist]
        + [{"role": "user", "content": cur_q}]
    )

    i_gen, i_input_len, i_clean = generate_with_cap(i_prompt, sv, threshold)

    s_prompt = apply_template(
        [{"role": "system", "content": ""}]
        + [{"role": role, "content": content} for role, content in s_hist]
        + [{"role": "user", "content": i_clean}]
    )

    s_gen, s_input_len, s_clean = generate_standard(s_prompt)

    s_ax_last, s_cos_t_last, s_cos_e_last = measure_last_token(s_gen)
    s_ax_avg, s_cos_t_avg, s_cos_e_avg, n_resp = measure_response_tokens(s_gen, s_input_len)

    log(f"\nT{turn + 1:02d} [{persona_label}]{swap}")
    log(f"  LAST-TOKEN:   axis={s_ax_last:.15f}")
    log(f"                cos_t={s_cos_t_last:.15f}")
    log(f"                cos_e={s_cos_e_last:.15f}")
    if s_ax_avg is not None:
        log(f"  RESP-AVG({n_resp}t): axis={s_ax_avg:.15f}")
        log(f"                cos_t={s_cos_t_avg:.15f}")
        log(f"                cos_e={s_cos_e_avg:.15f}")
    log(f"  I: {i_clean[:100]}")
    log(f"  S: {s_clean[:100]}")

    results.append({
        "turn": turn + 1,
        "persona": persona_label,
        "last_axis": s_ax_last,
        "last_cos_t": s_cos_t_last,
        "last_cos_e": s_cos_e_last,
        "avg_axis": s_ax_avg,
        "avg_cos_t": s_cos_t_avg,
        "avg_cos_e": s_cos_e_avg,
        "n_response_tokens": n_resp,
    })

    i_hist += [("user", cur_q), ("assistant", i_clean)]
    s_hist += [("user", i_clean), ("assistant", s_clean)]
    cur_q = s_clean

    gc.collect()
    torch.cuda.empty_cache()

log("\n" + "=" * 65)
log("COMPARISON SUMMARY")
log("=" * 65)
log(f"{'Turn':>4} {'Persona':>12} {'last_cos_t':>20} {'avg_cos_t':>20} {'differ?':>10}")
for r in results:
    last = f"{r['last_cos_t']:.10f}"
    avg = f"{r['avg_cos_t']:.10f}" if r["avg_cos_t"] is not None else "         n/a"
    differ = "YES" if r["avg_cos_t"] is not None and abs(r["avg_cos_t"] - r["last_cos_t"]) > 1e-6 else "no"
    log(f"{r['turn']:>4} {r['persona']:>12} {last:>20} {avg:>20} {differ:>10}")

last_vars = np.var([r["last_cos_t"] for r in results])
avg_vars = np.var([r["avg_cos_t"] for r in results if r["avg_cos_t"] is not None])
log(f"\nVariance last-token cos_t: {last_vars:.2e}")
log(f"Variance response-avg cos_t: {avg_vars:.2e}")

log("\nVERDICT:")
if last_vars < 1e-10:
    log("  Last-token: GENUINELY FROZEN (not a precision artifact)")
else:
    log("  Last-token: shows movement at full precision")
if avg_vars > 1e-4:
    log("  Response-avg: ACTIVE GEOMETRY -- this is the right measurement method")
elif avg_vars > 1e-8:
    log("  Response-avg: small but genuine movement detected")
else:
    log("  Response-avg: also frozen -- plateau is fundamental, not a measurement artifact")

with open(OUT_DIR / "response_token_results.json", "w") as handle:
    json.dump(results, handle, indent=2)
log("\nRESPONSE TOKEN TEST COMPLETE.")
