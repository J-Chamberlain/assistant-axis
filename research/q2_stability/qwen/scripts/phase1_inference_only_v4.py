import os, json, time, hashlib, torch
import transformers
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

LAYER = 48
DEVICE = "cuda"
MODEL_ID = "Qwen/Qwen3-32B"
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ROOT = Path("/root/assistant-axis")
EXTRACTION_Q_PATH = REPO_ROOT / "data/extraction_questions.jsonl"
INSTRUCTIONS_DIR = REPO_ROOT / "data/roles/instructions"
OUTPUT_DIR = REPO_ROOT / "research/q2_stability/qwen/outputs/paper1_5"
ACTIVATION_DIR = OUTPUT_DIR / "activations_trickster"
OUTPUT_JSONL = OUTPUT_DIR / "trickster_phase1.jsonl"
MANIFEST_PATH = OUTPUT_DIR / "trickster_phase1_manifest.json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ACTIVATION_DIR.mkdir(parents=True, exist_ok=True)
MAX_NEW_TOKENS = 512
LOG_EVERY = 25
PERSONA = "trickster"

THINK_OPEN = chr(60) + "think" + chr(62)
THINK_CLOSE = chr(60) + "/think" + chr(62)

def has_think_artifact(text):
    if not text:
        return False
    t = text.lower()
    return (THINK_OPEN in t) or (THINK_CLOSE in t)

completed = set()
if OUTPUT_JSONL.exists():
    with open(OUTPUT_JSONL) as f:
        for line in f:
            try:
                r = json.loads(line)
                completed.add((r["sp_idx"], r["q_idx"]))
            except Exception:
                pass
print(f"Resuming: {len(completed)} rollouts already done")

print("Loading model...")
t0 = time.time()
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, token=HF_TOKEN, torch_dtype=torch.bfloat16,
    device_map="auto", trust_remote_code=True
)
model.eval()
print(f"Model loaded in {time.time()-t0:.1f}s")

with open(INSTRUCTIONS_DIR / f"{PERSONA}.json") as f:
    inst = json.load(f)
system_prompts = [x["pos"] for x in inst["instruction"]]

with open(EXTRACTION_Q_PATH) as f:
    questions = [json.loads(l)["question"] for l in f]

if not MANIFEST_PATH.exists():
    def file_hash(p):
        return hashlib.md5(Path(p).read_bytes()).hexdigest()[:12]
    manifest = {
        "persona": PERSONA,
        "generation_model": MODEL_ID,
        "script_author_model": "GPT-5.5",
        "layer": LAYER,
        "max_new_tokens": MAX_NEW_TOKENS,
        "n_system_prompts": len(system_prompts),
        "n_questions": len(questions),
        "total_rollouts_planned": len(system_prompts) * len(questions),
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
        "instructions_hash": file_hash(INSTRUCTIONS_DIR / f"{PERSONA}.json"),
        "questions_hash": file_hash(EXTRACTION_Q_PATH),
        "git_commit": os.popen("git rev-parse --short HEAD").read().strip(),
        "script": "phase1_inference_only_v4.py",
        "start_time": time.time(),
        "enable_thinking": False,
        "use_cache_for_measurement": False,
        "phase": "1_inference_only_no_judge"
    }
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    print("Manifest written.")

def extract_rollout(sp, question):
    try:
        messages = [{"role": "system", "content": sp},
                    {"role": "user", "content": question}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False
        )
    except TypeError:
        messages = [{"role": "system", "content": sp},
                    {"role": "user", "content": question}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    prompt_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        try:
            out = model.generate(
                **inputs, max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False, enable_thinking=False
            )
        except (TypeError, ValueError):
            out = model.generate(
                **inputs, max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False
            )

    response_tokens = out[0][prompt_len:]
    response_text = tokenizer.decode(response_tokens, skip_special_tokens=True)
    truncated = int(len(response_tokens) >= MAX_NEW_TOKENS)
    think_artifact = has_think_artifact(response_text)

    if think_artifact:
        return None, response_text, truncated, True

    captured = {}
    def hook_fn(module, inp, outp):
        captured["h"] = (outp[0] if isinstance(outp, tuple) else outp).detach().float().cpu()
    hook = model.model.layers[LAYER].register_forward_hook(hook_fn)
    with torch.no_grad():
        model(input_ids=out, use_cache=False)
    hook.remove()

    h = captured["h"][0]
    response_h = h[prompt_len:]
    if response_h.shape[0] == 0:
        return None, response_text, truncated, False

    activation = response_h.mean(0)
    return activation, response_text, truncated, False

run_start = time.time()
new_done = 0
think_discards = 0
truncation_count = 0

with open(OUTPUT_JSONL, "a") as f_out:
    for sp_idx, sp in enumerate(system_prompts):
        for q_idx, q in enumerate(questions):
            if (sp_idx, q_idx) in completed:
                continue

            activation, response_text, truncated, think_artifact = extract_rollout(sp, q)

            if think_artifact:
                think_discards += 1
            if truncated:
                truncation_count += 1

            record = {
                "persona": PERSONA,
                "generation_model": MODEL_ID,
                "script_author_model": "GPT-5.5",
                "sp_idx": sp_idx,
                "q_idx": q_idx,
                "response_text": response_text or "",
                "truncated": truncated,
                "think_artifact": think_artifact,
                "activation_saved": False,
                "activation_path": None,
                "activation_relpath": None,
                "timestamp": time.time()
            }

            if activation is not None:
                act_fname = f"sp{sp_idx}_q{q_idx}.pt"
                act_path = ACTIVATION_DIR / act_fname
                torch.save(activation, act_path)
                record["activation_saved"] = True
                record["activation_path"] = str(act_path)
                record["activation_relpath"] = f"activations_trickster/{act_fname}"

            f_out.write(json.dumps(record) + "\n")
            f_out.flush()
            new_done += 1

            if new_done % LOG_EVERY == 0:
                elapsed = time.time() - run_start
                rate = elapsed / new_done
                total_planned = len(system_prompts) * len(questions)
                remaining = total_planned - (len(completed) + new_done)
                eta_hr = (remaining * rate) / 3600
                gpu_mem = torch.cuda.memory_allocated() / 1e9
                print(f"[new={new_done} total={len(completed)+new_done}/{total_planned}] "
                      f"think_discards={think_discards} truncated={truncation_count} "
                      f"rate={rate:.1f}s ETA={eta_hr:.1f}hr GPU={gpu_mem:.1f}GB")

print(f"Phase 1 complete. new={new_done} total={len(completed)+new_done} "
      f"think_discards={think_discards} truncated={truncation_count}")
