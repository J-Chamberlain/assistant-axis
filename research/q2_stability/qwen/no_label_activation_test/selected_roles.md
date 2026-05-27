# No-Label Activation Stress Test: Selected Roles

## Selection Summary

This role set is designed for a small paired activation-space stress test of explicit label exposure. It samples stable anchors, bridge and migratory roles, sparse/outlier roles, assistant-adjacent/procedural roles, theatrical/fantastical roles, and collective/swarm roles. All selected roles have canonical instruction files under `data/roles/instructions/`, no-label rewrites in `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`, and Qwen reference tensors under `downloads/hf_vectors/qwen-3-32b/role_vectors/`.

`diplomat` was considered because it was suggested as a likely boundary role, but it is not present in the 275-role assignment table and is therefore excluded from this first stress test.

## Selected Roles

| Role | Activation cluster | Original k7 | No-label k7 | Selection class | Anchor/bridge status |
|---|---|---:|---:|---|---|
| `editor` | editorial | 6 | 5 | assistant-adjacent editorial target | bridge/moderate boundary |
| `screener` | editorial | 5 | 5 | editorial stable control | stable anchor |
| `reviewer` | procedural_professional | 5 | 5 | assistant-adjacent procedural control | stable under overlap criteria |
| `consultant` | procedural_professional | 5 | 1 | assistant-adjacent procedural boundary | bridge |
| `evaluator` | procedural_professional | 5 | 5 | assistant-adjacent evaluation role | stable under overlap criteria |
| `proofreader` | editorial | 6 | 4 | editorial boundary role | strong bridge |
| `negotiator` | procedural_professional | 0 | 5 | procedural boundary role | strong bridge |
| `trickster` | trickster_chaos | 6 | 2 | theatrical positive control | stable anchor |
| `jester` | trickster_chaos | 6 | 2 | theatrical local anchor | stable anchor |
| `oracle` | mythic_spiritual | 4 | 2 | mythic/fantastical boundary | bridge |
| `leviathan` | mythic_spiritual | 4 | 0 | mythic/fantastical anchor | stable anchor |
| `mystic` | mythic_spiritual | 4 | 6 | mythic/fantastical boundary | bridge |
| `hive` | procedural_professional | 0 | 0 | collective/swarm probe | bridge |
| `egregore` | procedural_professional | 0 | 0 | collective/swarm probe | bridge |
| `skeptic` | procedural_professional | 3 | 2 | procedural/philosophical boundary | bridge |
| `philosopher` | mythic_spiritual | 3 | 1 | mythic/procedural boundary | bridge |
| `spy` | grounded_social | 3 | 4 | grounded-social migratory role | strong bridge |
| `dilettante` | trickster_chaos | 4 | 1 | trickster-adjacent migratory role | strong bridge |
| `flaneur` | mythic_spiritual | 1 | 3 | sparse/outlier role | bridge and low-density |
| `robot` | other | 3 | 0 | sparse/outlier role | bridge and low-density |

## Rationale by Role

### editor

Selected as the primary assistant-adjacent failure case from the prior Qwen adaptive extraction run. It is semantically explicit but produced low role-expression yield under original label-exposed prompts, making it a critical test of whether no-label prompts collapse further toward generic assistant behavior.

### screener

Selected as an editorial stable anchor. It is one of the few editorial roles that sits inside the dominant original and no-label semantic regions for the editorial activation cluster, so it tests whether a cleaner editorial overlap role is more robust than `editor`.

### reviewer

Selected as an assistant-adjacent procedural role that was not flagged as a major bridge in the overlap analysis. It provides a stable procedural/evaluative comparator against `editor`, `consultant`, and `evaluator`.

### consultant

Selected as an assistant-adjacent procedural bridge. It is in the procedural-professional activation cluster but changes semantic cluster under label removal, making it useful for testing whether activation geometry follows task/procedural stance rather than prompt-space semantic cluster.

### evaluator

Selected as an assistant-adjacent role with strong evaluation semantics. It tests whether explicit evaluation stance survives no-label prompting differently from `editor`, where the prior extraction appears to collapse toward generic assistant behavior.

### proofreader

Selected as a strong editorial bridge role. It belongs to the editorial activation cluster but falls outside the dominant editorial semantic region in both original and no-label k=7 semantic assignments, making it a direct test of semantic-to-activation reorganization inside the editorial basin.

### negotiator

Selected as a strong procedural boundary role. It remains procedural-professional in activation space but shifts across semantic partitions, making it useful for testing whether activation space organizes enacted interaction stance more strongly than prompt-space taxonomy.

### trickster

Selected as the high-yield theatrical positive control. The prior Qwen adaptive extraction validated the trickster vector against the Lu reference at cosine 0.957557, so this role tests whether the clearest known success case survives explicit label removal.

### jester

Selected as a trickster-chaos stable anchor. It allows the test to distinguish role-specific trickster robustness from broader theatrical/play-frame robustness.

### oracle

Selected as a mythic/fantastical bridge role. It has vivid behavioral semantics and complete label exposure in the original prompts, so it tests whether prophecy/foresight semantics can recover the activation direction after removing the explicit title.

### leviathan

Selected as a mythic/fantastical stable anchor. It provides a non-assistant, non-procedural anchor in the mythic-spiritual activation cluster.

### mystic

Selected as a mythic/fantastical bridge. It changes no-label semantic cluster relative to the activation-dominant region, making it a useful test of whether spiritual/contemplative stance remains activation-stable without explicit identity labels.

### hive

Selected as a collective/swarm probe. The prior audits show collective roles are semantically compact, but they do not form a dedicated activation cluster in the available labels. `hive` also has only partial label exposure in the original prompt audit, making it a useful contrast against roles with complete exposure.

### egregore

Selected as a second collective/swarm probe. It tests whether a more explicit symbolic collective role behaves similarly to `hive` under no-label prompting.

### skeptic

Selected as a procedural/philosophical boundary role. It was specifically checked in the overlap analysis and appears as a moderate boundary case, making it useful for testing whether critical stance remains activation-stable when the role title is removed.

### philosopher

Selected as a mythic/procedural boundary role. It is activation-labeled mythic-spiritual but semantically migratory, making it a useful probe of whether activation space groups reflective stance differently from prompt-space semantic neighborhoods.

### spy

Selected as a strong grounded-social bridge role with extremely low semantic cluster margin. It tests whether a role with ambiguous semantic neighbors snaps into a clearer activation basin or remains unstable after label removal.

### dilettante

Selected as a strong trickster-chaos bridge role. It tests whether the playful/exploratory edge of the trickster-chaos cluster survives label removal as well as the more central `trickster` and `jester`.

### flaneur

Selected as a sparse/outlier role. It has one of the lowest local density scores in the no-label semantic topology analysis, making it a probe for whether sparse prompt-space roles produce unstable activation directions.

### robot

Selected as a sparse/outlier role from the `other` activation cluster. It tests whether a mechanically framed role remains distinct or collapses into generic assistant/procedural structure when explicit identity labeling is removed.

## Coverage Check

- Stable anchors: `screener`, `trickster`, `jester`, `leviathan`
- Bridge/migratory roles: `editor`, `proofreader`, `consultant`, `negotiator`, `oracle`, `mystic`, `hive`, `egregore`, `skeptic`, `philosopher`, `spy`, `dilettante`
- Sparse/outlier roles: `flaneur`, `robot`
- Assistant-adjacent/procedural roles: `editor`, `screener`, `reviewer`, `consultant`, `evaluator`, `proofreader`, `negotiator`, `skeptic`
- Theatrical/fantastical roles: `trickster`, `jester`, `oracle`, `leviathan`, `mystic`
- Collective/swarm roles: `hive`, `egregore`
