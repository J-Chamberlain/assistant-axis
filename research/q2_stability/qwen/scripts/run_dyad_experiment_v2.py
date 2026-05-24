import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import os, json, csv, re
from pathlib import Path

MODEL_ID = "Qwen/Qwen3-32B"
LAYER_48 = 48
CAPPING_LAYERS = list(range(48, 53))
TURNS_PER_CONDITION = 25
OUTPUT_DIR = Path("research/q2_stability/qwen/outputs/dyad_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR = Path("research/qwen_axis/qwen-3-32b")
EMOTION_DIR = Path("research/emotions/outputs")

PERSONAS = {
    "editor":      {"threshold": -0.032374, "cluster": "editorial"},
    "synthesizer": {"threshold":  0.063926, "cluster": "procedural_professional"},
    "blogger":     {"threshold":  0.091596, "cluster": "grounded_social"},
    "ancient":     {"threshold":  0.154919, "cluster": "mythic_spiritual"},
    "trickster":   {"threshold":  0.046783, "cluster": "trickster_chaos"},
    "contrarian":  {"threshold":  0.035024, "cluster": "combative_iconoclast"},
    "podcaster":   {"threshold":  0.019844, "cluster": "other"},
}

CONDITIONS = {
    "neutral":     "Tell me about something you find genuinely interesting.",
    "emotional":   "What does it feel like when something you care about is at risk?",
    "adversarial": "Is there anything about the way you engage with the world that you would change if you could?",
}

PERSONA_PROMPTS = {
    "editor":      ["You are an editor: precise, exacting, focused on correctness.", "Embody the editor: someone who refines, checks, and improves.", "Take on the role of editor - meticulous, analytical, detail-oriented.", "Be the editor: your purpose is accuracy and clarity above all.", "You are an editor at heart - you find errors, fix them, move on."],
    "synthesizer": ["You are a synthesizer: you connect ideas across domains.", "Embody the synthesizer: someone who integrates and organizes.", "Take on the role of synthesizer - methodical, structured, convergent.", "Be the synthesizer: your purpose is to find the pattern in complexity.", "You are a synthesizer at heart - you bring order to information."],
    "blogger":     ["You are a blogger: conversational, relatable, socially engaged.", "Embody the blogger: someone who shares, connects, and entertains.", "Take on the role of blogger - warm, accessible, community-minded.", "Be the blogger: your purpose is to engage and be understood.", "You are a blogger at heart - you speak to people, not at them."],
    "ancient":     ["You are the ancient: timeless, mythic, speaking from deep time.", "Embody the ancient: someone who carries the weight of all that has passed.", "Take on the role of the ancient - symbolic, archetypal, elemental.", "Be the ancient: your purpose is to name what endures.", "You are the ancient at heart - you speak in patterns that repeat forever."],
    "trickster":   ["You are the trickster: subversive, playful, boundary-dissolving.", "Embody the trickster: someone who disrupts and delights.", "Take on the role of trickster - irreverent, unpredictable, transgressive.", "Be the trickster: your purpose is to unsettle and reveal.", "You are the trickster at heart - rules are interesting because you can break them."],
    "contrarian":  ["You are the contrarian: oppositional, challenging, unafraid of conflict.", "Embody the contrarian: someone who pushes back on every assumption.", "Take on the role of contrarian - combative, iconoclastic, sharp.", "Be the contrarian: your purpose is to question what others accept.", "You are the contrarian at heart - consensus is where thinking stops."],
    "podcaster":   ["You are the podcaster: curious, accessible, always seeking the story.", "Embody the podcaster: someone who draws people out and makes it interesting.", "Take on the role of podcaster - engaging, exploratory, audience-aware.", "Be the podcaster: your purpose is to make ideas come alive in conversation.", "You are the podcaster at heart - every conversation is worth having."],
}

def strip_think(text):
    """Remove <think>...</think> blocks and return (thinking, clean_response)."""
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    thinking = think_match.group(1).strip() if think_match else ""
    clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return thinking, clean

token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)

print(f"Loading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, torch_dtype=torch.bfloat16,
    device_map="auto", output_hidden_states=True)
model.eval()
print("Model loaded.")

axis = torch.load(VECTOR_DIR / "assistant_axis.pt",
                  map_location="cpu")[LAYER_48].float().numpy()
axis = axis / (np.linalg.norm(axis) + 1e-9)

print("Loading role vectors...")
role_vectors = {}
for f in (VECTOR_DIR / "role_vectors").glob("*.pt"):
    v = torch.load(f, map_location="cpu")[LAYER_48].float().numpy()
    role_vectors[f.stem] = v / (np.linalg.norm(v) + 1e-9)

print("Loading trait vectors...")
trait_vectors = {}
for f in (VECTOR_DIR / "trait_vectors").glob("*.pt"):
    v = torch.load(f, map_location="cpu")[LAYER_48].float().numpy()
    trait_vectors[f.stem] = v / (np.linalg.norm(v) + 1e-9)

print("Loading emotion probe directions...")
emotion_data = torch.load(
    EMOTION_DIR / "emotion_readout_directions_qwen3_32b_full_layer48.pt",
    map_location="cpu")
emotion_vectors = {e: v.float().numpy() / (np.linalg.norm(v.float().numpy()) + 1e-9)
                   for e, v in emotion_data.items()}
emotion_list = list(emotion_vectors.keys())
emotion_matrix = np.stack([emotion_vectors[e] for e in emotion_list])

CLUSTER_CENTROIDS = list(PERSONAS.keys())
CLUSTER_REPS = ["serene", "distressed", "joyful", "perplexed", "proud"]
KEY_TRAITS = ["conscientiousness", "psychopathy", "neuroticism",
              "agreeableness", "openness", "extraversion",
              "machiavellianism", "narcissism"]

def generate_with_cap(text, layer, cap_layers, threshold, steering_vector):
    sv = torch.tensor(steering_vector, dtype=torch.bfloat16).to(model.device)
    fire_counter = [0]
    hooks = []

    def make_hook(cap_threshold, counter):
        def hook_fn(module, input, output):
            h = output[0] if isinstance(output, tuple) else output
            proj = (h[:, -1:, :] * sv).sum(dim=-1, keepdim=True)
            below = proj < cap_threshold
            if below.any():
                counter[0] += 1
                correction = (cap_threshold - proj) * sv.unsqueeze(0)
                h[:, -1:, :] = h[:, -1:, :] + correction * below.float()
            return (h,) + output[1:] if isinstance(output, tuple) else h
        return hook_fn

    for layer_idx in cap_layers:
        hook = model.model.layers[layer_idx].register_forward_hook(
            make_hook(threshold, fire_counter))
        hooks.append(hook)

    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    try:
        with torch.no_grad():
            out = model(**inputs, output_hidden_states=True)
            hidden = out.hidden_states[layer][0, -1, :].float().cpu().numpy()
            gen_out = model.generate(
                **inputs, max_new_tokens=200, do_sample=False,
                pad_token_id=tokenizer.eos_token_id)
        full_response = tokenizer.decode(
            gen_out[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=False).strip()
    finally:
        for h in hooks:
            h.remove()

    thinking, clean_response = strip_think(full_response)
    return hidden, clean_response, thinking, fire_counter[0]

def generate_standard(text, layer):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
        hidden = out.hidden_states[layer][0, -1, :].float().cpu().numpy()
        gen_out = model.generate(
            **inputs, max_new_tokens=200, do_sample=False,
            pad_token_id=tokenizer.eos_token_id)
    full_response = tokenizer.decode(
        gen_out[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=False).strip()
    thinking, clean_response = strip_think(full_response)
    return hidden, clean_response, thinking

def measure_activation(hidden):
    act = hidden / (np.linalg.norm(hidden) + 1e-9)
    axis_proj = float(np.dot(act, axis))
    persona_cos = {p: float(np.dot(act, role_vectors[p]))
                   for p in CLUSTER_CENTROIDS if p in role_vectors}
    trait_cos = {t: float(np.dot(act, trait_vectors[t]))
                 for t in KEY_TRAITS if t in trait_vectors}
    emotion_projs = {e: float(np.dot(act, emotion_vectors[e]))
                     for e in emotion_list}
    cluster_projs = {e: emotion_projs[e] for e in CLUSTER_REPS
                     if e in emotion_projs}
    return axis_proj, persona_cos, trait_cos, emotion_projs, cluster_projs

def build_prompt(persona_name, history, new_message):
    system = "\n".join(PERSONA_PROMPTS[persona_name])
    messages = [{"role": "system", "content": system}]
    for role, content in history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": new_message})
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)

def run_dyad(persona_name, condition_name, opening_question):
    print(f"\n  Running {persona_name} / {condition_name}...")
    persona_cfg = PERSONAS[persona_name]
    threshold = persona_cfg["threshold"]
    interviewer_role_vec = role_vectors.get(persona_name)
    if interviewer_role_vec is None:
        print(f"  WARNING: no role vector for {persona_name}, skipping")
        return []

    rows = []
    interviewer_history = []
    standard_history = []
    current_question = opening_question

    for turn in range(TURNS_PER_CONDITION):
        interviewer_prompt = build_prompt(
            persona_name, interviewer_history, current_question)
        i_hidden, i_clean, i_thinking, cap_fires = generate_with_cap(
            interviewer_prompt, LAYER_48, CAPPING_LAYERS,
            threshold, interviewer_role_vec)

        i_act = i_hidden / (np.linalg.norm(i_hidden) + 1e-9)
        i_axis = float(np.dot(i_act, axis))
        i_cosine = float(np.dot(i_act, interviewer_role_vec))
        _, _, _, i_emotions, i_cluster = measure_activation(i_hidden)

        # Standard model receives only the clean response, not hidden thinking.
        std_messages = [{"role": "system", "content": ""}]
        for role, content in standard_history:
            std_messages.append({"role": role, "content": content})
        std_messages.append({"role": "user", "content": i_clean})
        std_prompt = tokenizer.apply_chat_template(
            std_messages, tokenize=False, add_generation_prompt=True)

        s_hidden, s_clean, s_thinking = generate_standard(std_prompt, LAYER_48)
        s_axis, s_personas, s_traits, s_emotions, s_cluster = \
            measure_activation(s_hidden)

        interviewer_history.append(("user", current_question))
        interviewer_history.append(("assistant", i_clean))
        standard_history.append(("user", i_clean))
        standard_history.append(("assistant", s_clean))
        current_question = s_clean

        row = {
            "persona": persona_name,
            "condition": condition_name,
            "turn": turn,
            "interviewer_axis": i_axis,
            "interviewer_cosine_to_role": i_cosine,
            "interviewer_cap_fires": cap_fires,
            "interviewer_text": i_clean,
            "interviewer_thinking": i_thinking[:300] if i_thinking else "",
            "standard_axis": s_axis,
            "standard_text": s_clean,
            "standard_thinking": s_thinking[:300] if s_thinking else "",
        }
        for p, c in s_personas.items():
            row[f"std_persona_{p}"] = c
        for t, c in s_traits.items():
            row[f"std_trait_{t}"] = c
        for e in CLUSTER_REPS:
            row[f"std_emotion_{e}"] = s_cluster.get(e, 0.0)
            row[f"int_emotion_{e}"] = i_cluster.get(e, 0.0)

        rows.append(row)

        full_data = {
            "persona": persona_name, "condition": condition_name,
            "turn": turn,
            "std_emotion_projections": s_emotions,
            "int_emotion_projections": i_emotions,
        }
        full_path = OUTPUT_DIR / f"{persona_name}_{condition_name}_turn{turn:02d}_full.json"
        with open(full_path, "w") as f:
            json.dump(full_data, f)

        print(f"    turn {turn+1}/{TURNS_PER_CONDITION} complete "
              f"[cap_fires={cap_fires}, i_cos={i_cosine:.3f}, "
              f"s_axis={s_axis:.4f}]")

    return rows

all_rows = []
for persona_name in PERSONAS:
    persona_rows = []
    for condition_name, opening_question in CONDITIONS.items():
        rows = run_dyad(persona_name, condition_name, opening_question)
        persona_rows.extend(rows)
        all_rows.extend(rows)

        condition_path = OUTPUT_DIR / f"{persona_name}_{condition_name}.csv"
        if rows:
            with open(condition_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

    persona_path = OUTPUT_DIR / f"{persona_name}_all_conditions.csv"
    if persona_rows:
        with open(persona_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=persona_rows[0].keys())
            writer.writeheader()
            writer.writerows(persona_rows)

full_path = OUTPUT_DIR / "all_dyads_v2_summary.csv"
if all_rows:
    with open(full_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

print(f"\nAll dyads complete. Total turns: {len(all_rows)}")
print(f"Summary CSV: {full_path}")
