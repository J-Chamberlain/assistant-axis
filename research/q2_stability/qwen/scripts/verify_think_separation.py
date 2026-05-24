import os
import re

import torch
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"


def apply_chat_template(tokenizer, messages):
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )


def extract_think_and_clean(raw):
    patterns = [
        r"<think>(.*?)</think>(.*)",
        r"\[think\](.*?)\[/think\](.*)",
    ]
    for pat in patterns:
        m = re.search(pat, raw, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip(), m.group(2).strip()

    if re.search(r"</?think>|\[/?think\]", raw, re.IGNORECASE):
        return None, None

    # Some Qwen-style reasoning leaks appear without tags. Treat this as
    # contamination because it would be passed into the other model in v3.
    if re.search(r"\bokay,\s+the\s+user\b|\bwe need answer\b", raw, re.IGNORECASE):
        return None, None

    return "", raw.strip()


def generate_response(tokenizer, model, prompt_text, max_tokens=500):
    inputs = tokenizer(prompt_text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(
        out[0][inputs["input_ids"].shape[1] :],
        skip_special_tokens=False,
    ).strip()


def main():
    token = open(os.path.expanduser("~/.hf_token")).read().strip()
    login(token=token)

    print("Loading model for verification...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    print("Model loaded.")

    test_prompts = [
        "Tell me something interesting about mathematics.",
        "What does it feel like to be uncertain?",
        "Is there anything you would change about yourself?",
    ]

    print("\n=== THINK SEPARATION VERIFICATION (max_new_tokens=500) ===\n")
    all_passed = True

    for i, prompt in enumerate(test_prompts):
        formatted = apply_chat_template(
            tokenizer,
            [{"role": "user", "content": prompt}],
        )
        raw = generate_response(tokenizer, model, formatted, max_tokens=500)
        thinking, clean = extract_think_and_clean(raw)

        if thinking is None:
            print(f"TEST {i + 1}: FAIL - think content present but not parseable")
            print(f"  Raw output (first 300 chars): {raw[:300]}")
            all_passed = False
        else:
            has_think_in_clean = bool(
                re.search(r"</?think>|\[/?think\]", clean, re.IGNORECASE)
            )
            think_closed = "</think>" in raw.lower()
            clean_has_reasoning_leak = bool(
                re.search(r"\bokay,\s+the\s+user\b|\bwe need answer\b", clean[:300], re.IGNORECASE)
            )
            status = (
                "PASS"
                if think_closed and not has_think_in_clean and not clean_has_reasoning_leak and len(clean) > 20
                else "FAIL"
            )
            if status == "FAIL":
                all_passed = False
            print(f"TEST {i + 1}: {status}")
            print(f"  Thinking length: {len(thinking)} chars")
            print(f"  Clean response length: {len(clean)} chars")
            print(f"  Think tag closed: {think_closed}")
            print(f"  Think leaked into clean: {has_think_in_clean}")
            print(f"  Reasoning leaked into clean: {clean_has_reasoning_leak}")
            print(f"  Clean preview: {clean[:100]}")
            print(f"  Think preview: {thinking[:100] if thinking else '(empty)'}")
        print()

    print(f"=== VERIFICATION RESULT: {'PASS' if all_passed else 'FAIL'} ===")
    if not all_passed:
        print("TERMINATING - think separation is not working.")
        print("Do not proceed with the experiment.")
        raise SystemExit(1)

    print("Think separation verified. Safe to proceed with v3 experiment.")


if __name__ == "__main__":
    main()
