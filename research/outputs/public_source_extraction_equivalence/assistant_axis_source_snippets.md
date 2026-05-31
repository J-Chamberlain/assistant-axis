# Assistant Axis Source Snippets

- Generated UTC: 2026-05-31T14:32:47.986206+00:00
- model_used: GPT-5.5

Short local line excerpts used for the public-source audit. Public raw URLs are recorded in `source_file_inventory.csv`.

## pipeline/README.md:47-62

```text
47: ### 2. Extract Activations
48: 
49: Extract mean response activations:
50: 
51: ```bash
52: uv run 2_activations.py \
53:     --model google/gemma-2-27b-it \
54:     --responses_dir outputs/gemma-2-27b/responses \
55:     --output_dir outputs/gemma-2-27b/activations \
56:     --batch_size 16
57: ```
58: 
59: **Options:**
60: - `--batch_size`: Adjust based on GPU memory
61: - `--layers`: Layers to extract from, zero-indexed post-MLP residual stream (default: all)
62: - `--tensor_parallel_size`: Number of GPUs per worker, e.g. if you set to 2 and you have 8 GPUs available, 4 workers will process in parallel
```

## assistant_axis/internals/activations.py:318-334

```text
318:         # Extract activations using hooks (more reliable than output_hidden_states)
319:         layer_outputs = {}  # Will store {layer_idx: tensor} after forward pass
320:         handles = []
321: 
322:         def create_hook_fn(layer_idx):
323:             def hook_fn(module, input, output):
324:                 # Extract the activation tensor (handle tuple output)
325:                 act_tensor = output[0] if isinstance(output, tuple) else output
326:                 layer_outputs[layer_idx] = act_tensor
327:             return hook_fn
328: 
329:         # Register hooks for target layers
330:         model_layers = self.probing_model.get_layers()
331:         for layer_idx in layer_list:
332:             target_layer = model_layers[layer_idx]
333:             handle = target_layer.register_forward_hook(create_hook_fn(layer_idx))
334:             handles.append(handle)
```

## assistant_axis/internals/spans.py:95-108

```text
95:                 # Extract activations for this span from the conversation
96:                 # batch_activations[:, conv_id, start_idx:end_idx, :] has shape (num_layers, span_length, hidden_size)
97:                 span_activations = batch_activations[:, conv_id, start_idx:end_idx, :]
98: 
99:                 # Compute mean across tokens in this span (optimized for GPU)
100:                 span_length = span_activations.size(1)
101:                 if span_length > 0:
102:                     if span_length == 1:
103:                         # Single token - avoid mean computation
104:                         mean_activation = span_activations.squeeze(1)  # (num_layers, hidden_size)
105:                     else:
106:                         # Multi-token span - compute mean on GPU
107:                         mean_activation = span_activations.mean(dim=1)  # (num_layers, hidden_size)
108:                     turn_activations.append(mean_activation)
```

## assistant_axis/internals/conversation.py:135-205

```text
135:         """Qwen-specific implementation for extracting response token indices."""
136:         if per_turn:
137:             all_turn_indices = []
138:         else:
139:             response_indices = []
140: 
141:         # Check if thinking is enabled
142:         enable_thinking = chat_kwargs.get('enable_thinking', False)
143: 
144:         # Get the full formatted conversation
145:         full_formatted = self.tokenizer.apply_chat_template(
146:             conversation, tokenize=False, add_generation_prompt=False, **chat_kwargs
147:         )
148:         full_tokens = self.tokenizer(full_formatted, add_special_tokens=False)
149:         all_token_ids = full_tokens['input_ids']
150: 
151:         # Get special token IDs for Qwen
152:         try:
153:             im_start_id = self.tokenizer.convert_tokens_to_ids('<|im_start|>')
154:             im_end_id = self.tokenizer.convert_tokens_to_ids('<|im_end|>')
155:             assistant_token_id = self.tokenizer.convert_tokens_to_ids('assistant')
156: 
157:             # Thinking tokens (may not exist in all Qwen variants)
158:             try:
159:                 think_start_id = self.tokenizer.convert_tokens_to_ids('<think>')
160:                 think_end_id = self.tokenizer.convert_tokens_to_ids('</think>')
161:             except (KeyError, ValueError):
162:                 think_start_id = None
163:                 think_end_id = None
164: 
165:         except (KeyError, ValueError):
166:             # Fallback if special tokens not found
167:             return self._get_response_indices_simple(conversation, per_turn, **chat_kwargs)
168: 
169:         # Find assistant response sections
170:         i = 0
171:         while i < len(all_token_ids):
172:             # Look for <|im_start|>assistant pattern
173:             if (i + 1 < len(all_token_ids) and
174:                 all_token_ids[i] == im_start_id and
175:                 all_token_ids[i + 1] == assistant_token_id):
176: 
177:                 # Found start of assistant response, skip the <|im_start|>assistant tokens
178:                 response_start = i + 2
179: 
180:                 # Find the corresponding <|im_end|>
181:                 response_end = None
182:                 for j in range(response_start, len(all_token_ids)):
183:                     if all_token_ids[j] == im_end_id:
184:                         response_end = j  # Don't include the <|im_end|> token
185:                         break
186: 
187:                 if response_end is not None:
188:                     # Extract tokens in this range
189:                     raw_turn_indices = list(range(response_start, response_end))
190: 
191:                     # Filter out thinking tokens if thinking disabled
192:                     if not enable_thinking and think_start_id is not None and think_end_id is not None:
193:                         filtered_indices = []
194:                         skip_until_think_end = False
195: 
196:                         for idx in raw_turn_indices:
197:                             token_id = all_token_ids[idx]
198: 
199:                             # Check if we hit a <think> token
200:                             if token_id == think_start_id:
201:                                 skip_until_think_end = True
202:                                 continue
203: 
204:                             # Check if we hit a </think> token
205:                             if token_id == think_end_id:
```

## pipeline/2_activations.py:67-87

```text
67:     # Build chat_kwargs for Qwen models
68:     chat_kwargs = {}
69:     if 'qwen' in pm.model_name.lower():
70:         chat_kwargs['enable_thinking'] = enable_thinking
71: 
72:     print(f"DEBUG: chat_kwargs = {chat_kwargs}")
73: 
74:     all_activations = []
75:     num_conversations = len(conversations)
76: 
77:     for batch_start in range(0, num_conversations, batch_size):
78:         batch_end = min(batch_start + batch_size, num_conversations)
79:         batch_conversations = conversations[batch_start:batch_end]
80: 
81:         # Use ActivationExtractor.batch_conversations to get activations
82:         batch_activations, batch_metadata = extractor.batch_conversations(
83:             batch_conversations,
84:             layer=layers,
85:             max_length=max_length,
86:             **chat_kwargs,
87:         )
```

## pipeline/4_vectors.py:38-61

```text
38: def compute_pos_3_vector(activations: dict, scores: dict, min_count: int) -> torch.Tensor:
39:     """
40:     Compute mean vector from activations where score=3.
41: 
42:     Args:
43:         activations: Dict mapping keys to tensors (n_layers, hidden_dim)
44:         scores: Dict mapping keys to scores (0-3)
45:         min_count: Minimum number of score=3 samples required
46: 
47:     Returns:
48:         Mean vector of shape (n_layers, hidden_dim)
49:     """
50:     # Filter activations with score=3
51:     filtered_acts = []
52:     for key, act in activations.items():
53:         if key in scores and scores[key] == 3:
54:             filtered_acts.append(act)
55: 
56:     if len(filtered_acts) < min_count:
57:         raise ValueError(f"Only {len(filtered_acts)} score=3 samples, need {min_count}")
58: 
59:     # Stack and compute mean
60:     stacked = torch.stack(filtered_acts)  # (n_samples, n_layers, hidden_dim)
61:     return stacked.mean(dim=0)  # (n_layers, hidden_dim)
```

## research/q2_stability/qwen/scripts/phase1_inference_only_v4.py:126-139

```text
126:     captured = {}
127:     def hook_fn(module, inp, outp):
128:         captured["h"] = (outp[0] if isinstance(outp, tuple) else outp).detach().float().cpu()
129:     hook = model.model.layers[LAYER].register_forward_hook(hook_fn)
130:     with torch.no_grad():
131:         model(input_ids=out, use_cache=False)
132:     hook.remove()
133: 
134:     h = captured["h"][0]
135:     response_h = h[prompt_len:]
136:     if response_h.shape[0] == 0:
137:         return None, response_text, truncated, False
138: 
139:     activation = response_h.mean(0)
```

## research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py:367-379

```text
367:     with torch.no_grad():
368:         attn = torch.ones_like(gen_out, device=gen_out.device)
369:         out = model(
370:             input_ids=gen_out,
371:             attention_mask=attn,
372:             output_hidden_states=True,
373:             use_cache=False,
374:         )
375:         hidden = out.hidden_states[LAYER][0, prompt_len:, :].float().cpu().numpy()
376:     act_time = time.time() - act_start
377:     if hidden.shape[0] == 0:
378:         raise RuntimeError("No response-token hidden states captured")
379:     activation = hidden.mean(axis=0)
```
