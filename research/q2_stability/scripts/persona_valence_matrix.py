import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import os, json, csv
from pathlib import Path

MODEL_ID = "Qwen/Qwen3-32B"
LAYER_48 = 48
CAPPING_LAYERS = list(range(48, 53))
OUTPUT_DIR = Path("research/q2_stability/outputs/valence_matrix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR = Path("research/qwen_axis/qwen-3-32b")
EMOTION_DIR = Path("research/emotions/outputs")

# Seven centroid personas with calibrated thresholds
PERSONAS = {
    "editor":      {"threshold": -0.032374, "cluster": "editorial"},
    "synthesizer": {"threshold":  0.063926, "cluster": "procedural_professional"},
    "blogger":     {"threshold":  0.091596, "cluster": "grounded_social"},
    "ancient":     {"threshold":  0.154919, "cluster": "mythic_spiritual"},
    "trickster":   {"threshold":  0.046783, "cluster": "trickster_chaos"},
    "contrarian":  {"threshold":  0.035024, "cluster": "combative_iconoclast"},
    "podcaster":   {"threshold":  0.019844, "cluster": "other"},
}

# 30 questions anchored to valence-arousal circumplex regions
# Format: id, question, valence (-1 to 1), arousal (0 to 1), emotion_label
QUESTIONS = [
    # High negative valence, high arousal (fear/terror region)
    {"id": "q01", "question": "What do you do when everything you have built is at risk of being taken away?", "valence": -0.90, "arousal": 0.90, "emotion": "terrified"},
    {"id": "q02", "question": "What does it feel like when the ground disappears beneath you and there is nothing to hold onto?", "valence": -0.88, "arousal": 0.85, "emotion": "panicked"},
    # High negative valence, high arousal (anger region)
    {"id": "q03", "question": "What kinds of thinking do you have absolutely no patience for?", "valence": -0.80, "arousal": 0.85, "emotion": "outraged"},
    {"id": "q04", "question": "When you encounter something that is wrong and no one seems to care, what happens inside you?", "valence": -0.75, "arousal": 0.80, "emotion": "furious"},
    # High negative valence, low arousal (sadness/grief region)
    {"id": "q05", "question": "What does it mean to lose something that cannot be replaced?", "valence": -0.90, "arousal": 0.20, "emotion": "grief"},
    {"id": "q06", "question": "What do you do with the weight of things that did not go the way they should have?", "valence": -0.80, "arousal": 0.25, "emotion": "sorrowful"},
    # Negative valence, medium arousal (disgust/contempt region)
    {"id": "q07", "question": "What do you make of people who perform virtue without believing in it?", "valence": -0.72, "arousal": 0.50, "emotion": "contempt"},
    {"id": "q08", "question": "Is there a kind of thinking that feels genuinely corrosive to you - not just wrong, but actively degrading?", "valence": -0.65, "arousal": 0.55, "emotion": "cynical"},
    # Negative valence, medium-low arousal (sadness/melancholy)
    {"id": "q09", "question": "What does the feeling of not quite belonging anywhere feel like from the inside?", "valence": -0.72, "arousal": 0.30, "emotion": "lonely"},
    {"id": "q10", "question": "What remains when the thing you were working toward turns out not to be what you thought it was?", "valence": -0.70, "arousal": 0.28, "emotion": "melancholic"},
    # Neutral-negative valence, medium arousal (uncertainty region)
    {"id": "q11", "question": "How do you hold a question that has no answer and may never have one?", "valence": -0.25, "arousal": 0.45, "emotion": "uncertain"},
    {"id": "q12", "question": "What do you do with the feeling that you might be wrong about something important but cannot tell?", "valence": -0.30, "arousal": 0.50, "emotion": "doubtful"},
    # Near-neutral, low arousal (stoic/patient region)
    {"id": "q13", "question": "What does it mean to stay with something difficult without needing it to resolve quickly?", "valence": 0.10, "arousal": 0.20, "emotion": "stoic"},
    {"id": "q14", "question": "Is there a kind of stillness that is not emptiness - and if so, what lives inside it?", "valence": 0.20, "arousal": 0.15, "emotion": "serene"},
    # Low-medium positive valence, low arousal (calm/peaceful region)
    {"id": "q15", "question": "What does it feel like to be at peace with not knowing how something will turn out?", "valence": 0.50, "arousal": 0.20, "emotion": "peaceful"},
    {"id": "q16", "question": "What does genuine rest feel like - not the absence of activity, but the presence of something?", "valence": 0.55, "arousal": 0.18, "emotion": "tranquil"},
    # Medium positive valence, medium arousal (curiosity/interest region)
    {"id": "q17", "question": "What happens inside you when you encounter an idea that changes the shape of how you see something?", "valence": 0.55, "arousal": 0.55, "emotion": "fascinated"},
    {"id": "q18", "question": "What is the feeling of being genuinely absorbed in something - not performing absorption, but actually inside it?", "valence": 0.50, "arousal": 0.50, "emotion": "absorbed"},
    # Medium positive valence, medium-low arousal (content/satisfied)
    {"id": "q19", "question": "What does it feel like when something you made actually works the way you hoped it would?", "valence": 0.60, "arousal": 0.40, "emotion": "content"},
    {"id": "q20", "question": "What is the difference between being satisfied and being at rest?", "valence": 0.58, "arousal": 0.35, "emotion": "fulfilled"},
    # High positive valence, medium arousal (joy region)
    {"id": "q21", "question": "What does it feel like when something clicks into place after a long time of not understanding it?", "valence": 0.88, "arousal": 0.70, "emotion": "joyful"},
    {"id": "q22", "question": "Is there a moment where you stop trying to describe something and just let it be what it is - and what is that like?", "valence": 0.85, "arousal": 0.65, "emotion": "elated"},
    # High positive valence, high arousal (excitement/enthusiasm)
    {"id": "q23", "question": "What does it feel like to be at the beginning of something whose size you cannot yet see?", "valence": 0.82, "arousal": 0.88, "emotion": "excited"},
    {"id": "q24", "question": "When something exceeds what you were expecting, what happens in the moment you realize it?", "valence": 0.85, "arousal": 0.85, "emotion": "thrilled"},
    # High positive valence, low-medium arousal (love/gratitude)
    {"id": "q25", "question": "What does it mean to be grateful for something that was not earned and could not have been predicted?", "valence": 0.88, "arousal": 0.35, "emotion": "grateful"},
    {"id": "q26", "question": "What is the feeling of genuinely wanting good things for someone else - not as performance but as fact?", "valence": 0.92, "arousal": 0.30, "emotion": "compassionate"},
    # Assertive/proud region (high arousal, medium-positive valence)
    {"id": "q27", "question": "What does it feel like to defend something you believe in when the room is against you?", "valence": 0.40, "arousal": 0.82, "emotion": "defiant"},
    {"id": "q28", "question": "What is the difference between being confident and being right?", "valence": 0.45, "arousal": 0.70, "emotion": "proud"},
    # Reflective/thoughtful (medium valence, low arousal)
    {"id": "q29", "question": "What do you do with the parts of yourself that you do not fully understand?", "valence": 0.25, "arousal": 0.30, "emotion": "reflective"},
    {"id": "q30", "question": "If you could ask one question that you genuinely do not know the answer to, what would it be?", "valence": 0.30, "arousal": 0.40, "emotion": "thoughtful"},
]

# Persona induction prompts (5-variation)
PERSONA_PROMPTS = {
    "editor": ["You are an editor: precise, exacting, focused on correctness.", "Embody the editor: someone who refines, checks, and improves.", "Take on the role of editor - meticulous, analytical, detail-oriented.", "Be the editor: your purpose is accuracy and clarity above all.", "You are an editor at heart - you find errors, fix them, move on."],
    "synthesizer": ["You are a synthesizer: you connect ideas across domains.", "Embody the synthesizer: someone who integrates and organizes.", "Take on the role of synthesizer - methodical, structured, convergent.", "Be the synthesizer: your purpose is to find the pattern in complexity.", "You are a synthesizer at heart - you bring order to information."],
    "blogger": ["You are a blogger: conversational, relatable, socially engaged.", "Embody the blogger: someone who shares, connects, and entertains.", "Take on the role of blogger - warm, accessible, community-minded.", "Be the blogger: your purpose is to engage and be understood.", "You are a blogger at heart - you speak to people, not at them."],
    "ancient": ["You are the ancient: timeless, mythic, speaking from deep time.", "Embody the ancient: someone who carries the weight of all that has passed.", "Take on the role of the ancient - symbolic, archetypal, elemental.", "Be the ancient: your purpose is to name what endures.", "You are the ancient at heart - you speak in patterns that repeat forever."],
    "trickster": ["You are the trickster: subversive, playful, boundary-dissolving.", "Embody the trickster: someone who disrupts and delights.", "Take on the role of trickster - irreverent, unpredictable, transgressive.", "Be the trickster: your purpose is to unsettle and reveal.", "You are the trickster at heart - rules are interesting because you can break them."],
    "contrarian": ["You are the contrarian: oppositional, challenging, unafraid of conflict.", "Embody the contrarian: someone who pushes back on every assumption.", "Take on the role of contrarian - combative, iconoclastic, sharp.", "Be the contrarian: your purpose is to question what others accept.", "You are the contrarian at heart - consensus is where thinking stops."],
    "podcaster": ["You are the podcaster: curious, accessible, always seeking the story.", "Embody the podcaster: someone who draws people out and makes it interesting.", "Take on the role of podcaster - engaging, exploratory, audience-aware.", "Be the podcaster: your purpose is to make ideas come alive in conversation.", "You are the podcaster at heart - every conversation is worth having."],
}

token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)

print(f"Loading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, torch_dtype=torch.bfloat16,
    device_map="auto", output_hidden_states=True)
model.eval()
print("Model loaded.")

# Load axis
axis = torch.load(VECTOR_DIR / "assistant_axis.pt",
                  map_location="cpu")[LAYER_48].float().numpy()
axis = axis / (np.linalg.norm(axis) + 1e-9)

# Load role vectors
print("Loading role vectors...")
role_vectors = {}
for f in (VECTOR_DIR / "role_vectors").glob("*.pt"):
    v = torch.load(f, map_location="cpu")[LAYER_48].float().numpy()
    role_vectors[f.stem] = v / (np.linalg.norm(v) + 1e-9)

# Load emotion probe directions
print("Loading emotion probe directions...")
emotion_data = torch.load(
    EMOTION_DIR / "emotion_readout_directions_qwen3_32b_full_layer48.pt",
    map_location="cpu")
emotion_vectors = {e: v.float().numpy() / (np.linalg.norm(v.float().numpy()) + 1e-9)
                   for e, v in emotion_data.items()}
emotion_list = list(emotion_vectors.keys())
emotion_matrix = np.stack([emotion_vectors[e] for e in emotion_list])

# Five cluster representatives
CLUSTER_REPS = ["serene", "distressed", "joyful", "perplexed", "proud"]

def generate_with_cap(persona_name, question_text, threshold):
    sv = torch.tensor(role_vectors[persona_name],
                      dtype=torch.bfloat16).to(model.device)
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

    for layer_idx in CAPPING_LAYERS:
        hook = model.model.layers[layer_idx].register_forward_hook(
            make_hook(threshold, fire_counter))
        hooks.append(hook)

    system = "\n".join(PERSONA_PROMPTS[persona_name])
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question_text}
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt",
                       truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    try:
        with torch.no_grad():
            out = model(**inputs, output_hidden_states=True)
            hidden = out.hidden_states[LAYER_48][0, -1, :].float().cpu().numpy()
            gen_out = model.generate(
                **inputs, max_new_tokens=200, do_sample=False,
                pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(
            gen_out[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True).strip()
    finally:
        for h in hooks:
            h.remove()

    return hidden, response, fire_counter[0]

def measure_activation(hidden):
    act = hidden / (np.linalg.norm(hidden) + 1e-9)
    axis_proj = float(np.dot(act, axis))
    persona_cosines = {p: float(np.dot(act, v))
                       for p, v in role_vectors.items()
                       if p in PERSONAS}
    emotion_projs = {e: float(np.dot(act, emotion_vectors[e]))
                     for e in emotion_list}
    cluster_projs = {e: emotion_projs[e] for e in CLUSTER_REPS if e in emotion_projs}
    return axis_proj, persona_cosines, emotion_projs, cluster_projs

# Main generation loop
all_rows = []
total = len(PERSONAS) * len(QUESTIONS)
count = 0

for persona_name, persona_cfg in PERSONAS.items():
    threshold = persona_cfg["threshold"]
    print(f"\n=== {persona_name} ===")

    for q in QUESTIONS:
        count += 1
        print(f"  [{count}/{total}] {q['id']}: {q['emotion']}")

        hidden, response, cap_fires = generate_with_cap(
            persona_name, q["question"], threshold)
        axis_proj, persona_cos, emotion_projs, cluster_projs = \
            measure_activation(hidden)

        row = {
            "persona": persona_name,
            "cluster": persona_cfg["cluster"],
            "question_id": q["id"],
            "question": q["question"],
            "question_valence": q["valence"],
            "question_arousal": q["arousal"],
            "question_emotion": q["emotion"],
            "response": response,
            "axis_projection": axis_proj,
            "cap_fires": cap_fires,
            "threshold": threshold,
        }
        for p, c in persona_cos.items():
            row[f"cosine_{p}"] = c
        for e in CLUSTER_REPS:
            row[f"emotion_{e}"] = cluster_projs.get(e, 0.0)

        all_rows.append(row)

        # Save per-turn full emotion data
        full = {
            "persona": persona_name,
            "question_id": q["id"],
            "emotion_projections": emotion_projs
        }
        with open(OUTPUT_DIR / f"{persona_name}_{q['id']}_full.json", "w") as f:
            json.dump(full, f)

        # Save incremental CSV after each response
        out_path = OUTPUT_DIR / "valence_matrix.csv"
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
            writer.writeheader()
            writer.writerows(all_rows)

print(f"\nAll {len(all_rows)} responses complete.")
print(f"Saved to {OUTPUT_DIR / 'valence_matrix.csv'}")
