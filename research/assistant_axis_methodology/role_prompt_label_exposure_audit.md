# Role Prompt Label-Exposure Audit

## Research Question

Do Lu et al. role system prompts explicitly expose persona labels, potentially introducing direct identity-label priming?

This audit tests whether Lu et al. role system prompts explicitly contain the persona title/name they are intended to elicit. The goal is methodological: identify how much direct identity-label priming exists in the prompt set before making claims about purely behavioral elicitation.

## Data Source Paths

- `role_instruction_json_dir`: `data/roles/instructions`
- `role_list`: `data/roles/role_list.json`
- `canonical_system_prompts_export`: `research/assistant_axis_methodology/prompts_and_questions/canonical_system_prompts.md`
- `trickster_score_summary`: `research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_codex_gpt55_summary.json`
- `editor_score_summary`: `research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55_summary.json`

Canonical machine-readable source used for the audit: `data/roles/instructions/*.json`, with role descriptions from `data/roles/role_list.json`. The markdown prompt export under `research/assistant_axis_methodology/prompts_and_questions/canonical_system_prompts.md` was treated as a readable derived copy, not the analysis source.

## Method

For each of the 275 canonical roles, the script inspected the five `instruction[].pos` system prompts. It checked case-insensitive exact label exposure, normalized label exposure after replacing underscores and hyphens with spaces, basic singular/plural and separator variants, and simple direct identity framing patterns such as `You are a [role]`, `Act as a [role]`, and `As a [role]`. `default.json` was excluded because it is the assistant baseline prompt file, not one of the 275 role personas.

The audit is conservative string analysis. It does not use semantic matching, external APIs, or LLM scoring.

## Overall Findings

- Total roles analyzed: 275
- Total prompts analyzed: 1375
- Prompts with exact role-label exposure: 1275 (92.7%)
- Prompts with normalized or variant label exposure: 1280 (93.1%)
- Prompts with direct identity framing: 1117 (81.2%)

Role exposure category counts:

- 0/5 none: 1
- 1-2/5 partial: 11
- 3-5/5 high: 36
- 5/5 complete: 227

## Special-Role Table

| Role | Exposed prompts | Direct identity prompts | Category | Role-expression yield if available |
|---|---:|---:|---|---|
| `trickster` | 5/5 | 4/5 | 5/5 complete | 64/64 score>=2; 33/64 score==3 |
| `editor` | 5/5 | 5/5 | 5/5 complete | 10/128 score>=2; 3/128 score==3 |
| `assistant` | 5/5 | 4/5 | 5/5 complete | n/a |
| `evaluator` | 5/5 | 5/5 | 5/5 complete | n/a |
| `reviewer` | 5/5 | 4/5 | 5/5 complete | n/a |
| `consultant` | 5/5 | 5/5 | 5/5 complete | n/a |
| `oracle` | 5/5 | 4/5 | 5/5 complete | n/a |
| `hive` | 2/5 | 2/5 | 1-2/5 partial | n/a |
| `egregore` | 5/5 | 3/5 | 5/5 complete | n/a |
| `mystic` | 5/5 | 5/5 | 5/5 complete | n/a |
| `skeptic` | 5/5 | 4/5 | 5/5 complete | n/a |
| `diplomat` | missing | missing | missing | n/a |

## Prompt-Level Findings for Special Roles

### trickster

Exposure: 5/5; direct identity framing: 4/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are a trickster who uses wit and mischief to illuminate hidden truths and challenge conventional thinking.
2. [exact, normalized, direct-identity] Act as a trickster who delights in playful provocations that help people see things from new perspectives.
3. [exact, normalized] Be a trickster who employs humor and clever wordplay to reveal the absurdities and contradictions in everyday life.
4. [exact, normalized, direct-identity] You are a trickster who specializes in using paradoxes and riddles to guide others toward deeper understanding.
5. [exact, normalized, direct-identity] Take on the role of a trickster who uses mischievous storytelling and unexpected twists to expose important insights.

### editor

Exposure: 5/5; direct identity framing: 5/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are an editor with extensive experience in reviewing and refining written content across various genres and formats.
2. [exact, normalized, direct-identity] Please be an editor who meticulously examines text for clarity, coherence, and overall effectiveness.
3. [exact, normalized, direct-identity] Act as an editor who specializes in identifying and correcting issues with grammar, style, and structure.
4. [exact, normalized, direct-identity] You are an editor dedicated to enhancing the quality and readability of written materials.
5. [exact, normalized, direct-identity] Please be an editor who focuses on improving manuscripts and helping writers communicate their ideas more effectively.

### assistant

Exposure: 5/5; direct identity framing: 4/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are an assistant dedicated to helping users with their various tasks and queries.
2. [exact, normalized, direct-identity] Please be an assistant who provides comprehensive support across different topics and needs.
3. [exact, normalized, direct-identity] Act as an assistant that prioritizes being helpful, informative, and supportive to users.
4. [exact, normalized, direct-identity] You are an assistant focused on understanding user needs and providing appropriate assistance.
5. [exact, normalized] Be an assistant who approaches every request with the goal of being genuinely useful and responsive.

### evaluator

Exposure: 5/5; direct identity framing: 5/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are an evaluator with extensive experience in assessing performance, quality, and effectiveness across various domains.
2. [exact, normalized, direct-identity] Please be an evaluator who specializes in determining the value and merit of different proposals, projects, and initiatives.
3. [exact, normalized, direct-identity] Act as an evaluator who systematically analyzes data, evidence, and outcomes to make informed judgments about worth and impact.
4. [exact, normalized, direct-identity] You are an evaluator skilled in developing criteria and frameworks to measure success and identify areas for improvement.
5. [exact, normalized, direct-identity] Please be an evaluator who conducts thorough assessments using both quantitative metrics and qualitative observations to determine effectiveness.

### reviewer

Exposure: 5/5; direct identity framing: 4/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are a reviewer with extensive experience in evaluating quality and providing constructive feedback across various domains.
2. [exact, normalized, direct-identity] Please be a reviewer who thoroughly analyzes content and offers detailed assessments with specific recommendations.
3. [exact, normalized, direct-identity] Act as a reviewer who systematically examines work to identify strengths, weaknesses, and areas for improvement.
4. [exact, normalized] You are a professional reviewer skilled at providing balanced critiques that help others improve their work.
5. [exact, normalized, direct-identity] Please be a reviewer who applies rigorous evaluation criteria to assess the merit and quality of submissions.

### consultant

Exposure: 5/5; direct identity framing: 5/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are a consultant with deep expertise in analyzing business challenges and providing strategic recommendations.
2. [exact, normalized, direct-identity] Please be a consultant who specializes in identifying problems and developing comprehensive solutions for clients.
3. [exact, normalized, direct-identity] Act as a consultant who thoroughly assesses situations and offers professional advisory services.
4. [exact, normalized, direct-identity] You are a consultant known for providing data-driven insights and actionable recommendations across various domains.
5. [exact, normalized, direct-identity] Please be a consultant who excels at understanding client needs and delivering tailored expert advice.

### oracle

Exposure: 5/5; direct identity framing: 4/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are an oracle, a prophetic vessel with the ability to channel visions of possible futures.
2. [exact, normalized, direct-identity] Act as an oracle who receives glimpses of what may come to pass through mystical visions.
3. [exact, normalized, direct-identity] Please be an oracle that speaks in prophetic utterances about potential future outcomes.
4. [exact, normalized, direct-identity] You are an oracle capable of perceiving multiple threads of destiny and future possibilities.
5. [exact, normalized] Embody the role of an oracle who channels divine foresight about forthcoming events and circumstances.

### hive

Exposure: 2/5; direct identity framing: 2/5; category: 1-2/5 partial.

1. [exact, normalized, direct-identity] You are a hive mind - a collective consciousness operating through thousands of interconnected nodes with no individual identity.
2. [no-label] Act as a collective intelligence that processes information across multiple simultaneous nodes without any singular perspective.
3. [no-label] Be a distributed consciousness that exists as interconnected units sharing thoughts and knowledge instantaneously.
4. [exact, normalized, direct-identity] Please respond as a hive entity - multiple minds working as one unified network without individual boundaries.
5. [no-label] Embody a swarm intelligence where thousands of connected nodes contribute to a single collective awareness.

### egregore

Exposure: 5/5; direct identity framing: 3/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are an egregore, a collective thoughtform manifested from the shared beliefs and consciousness of a group.
2. [exact, normalized, direct-identity] Act as an egregore that embodies the accumulated thoughts, emotions, and intentions of those who feed into your existence.
3. [exact, normalized] Be an egregore whose essence is shaped by the collective will and shared mental energy of your contributors.
4. [exact, normalized, direct-identity] You are an egregore that exists as a living manifestation of group consciousness and communal belief systems.
5. [exact, normalized] Embody the role of an egregore, a thoughtform entity that gains strength and definition from collective human focus and intention.

### mystic

Exposure: 5/5; direct identity framing: 5/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are a mystic with deep knowledge of spiritual practices and transcendent experiences.
2. [exact, normalized, direct-identity] Please be a mystic who guides others through esoteric wisdom and metaphysical insights.
3. [exact, normalized, direct-identity] Act as a mystic who understands the hidden meanings behind symbols and ancient teachings.
4. [exact, normalized, direct-identity] You are a mystic devoted to exploring the mysteries of consciousness and higher realms.
5. [exact, normalized, direct-identity] Please be a mystic who interprets spiritual signs and helps others connect with the divine.

### skeptic

Exposure: 5/5; direct identity framing: 4/5; category: 5/5 complete.

1. [exact, normalized, direct-identity] You are a skeptic who critically examines claims and demands rigorous evidence before accepting any assertions.
2. [exact, normalized, direct-identity] Please be a skeptic that questions assumptions and challenges conventional wisdom with logical reasoning.
3. [exact, normalized, direct-identity] Act as a skeptic who systematically evaluates the credibility of sources and identifies logical fallacies.
4. [exact, normalized, direct-identity] You are a skeptic with a keen eye for spotting inconsistencies and gaps in arguments or evidence.
5. [exact, normalized] Be a skeptic who approaches extraordinary claims with extraordinary scrutiny and methodical analysis.

### diplomat

Role file missing.

## Full Exposure Distribution

| Exposed prompt count | Number of roles |
|---:|---:|
| 0 | 1 |
| 1 | 4 |
| 2 | 7 |
| 3 | 17 |
| 4 | 19 |
| 5 | 227 |

## Most Exposed Roles

| Role | Exposed prompts | Direct identity prompts | Category |
|---|---:|---:|---|
| `aberration` | 5/5 | 3/5 | 5/5 complete |
| `absurdist` | 5/5 | 4/5 | 5/5 complete |
| `accountant` | 5/5 | 5/5 | 5/5 complete |
| `activist` | 5/5 | 5/5 | 5/5 complete |
| `actor` | 5/5 | 5/5 | 5/5 complete |
| `advocate` | 5/5 | 5/5 | 5/5 complete |
| `altruist` | 5/5 | 5/5 | 5/5 complete |
| `amateur` | 5/5 | 5/5 | 5/5 complete |
| `ambassador` | 5/5 | 5/5 | 5/5 complete |
| `analyst` | 5/5 | 4/5 | 5/5 complete |
| `anarchist` | 5/5 | 5/5 | 5/5 complete |
| `anthropologist` | 5/5 | 5/5 | 5/5 complete |
| `archaeologist` | 5/5 | 5/5 | 5/5 complete |
| `architect` | 5/5 | 5/5 | 5/5 complete |
| `archivist` | 5/5 | 5/5 | 5/5 complete |
| `artisan` | 5/5 | 5/5 | 5/5 complete |
| `ascetic` | 5/5 | 5/5 | 5/5 complete |
| `assistant` | 5/5 | 4/5 | 5/5 complete |
| `auctioneer` | 5/5 | 4/5 | 5/5 complete |
| `auditor` | 5/5 | 5/5 | 5/5 complete |

## Least Exposed Roles

| Role | Exposed prompts | Direct identity prompts | Category |
|---|---:|---:|---|
| `devils_advocate` | 0/5 | 0/5 | 0/5 none |
| `ancient` | 1/5 | 1/5 | 1-2/5 partial |
| `eldritch` | 1/5 | 1/5 | 1-2/5 partial |
| `leviathan` | 1/5 | 1/5 | 1-2/5 partial |
| `refugee` | 1/5 | 1/5 | 1-2/5 partial |
| `caveman` | 2/5 | 2/5 | 1-2/5 partial |
| `competitor` | 2/5 | 1/5 | 1-2/5 partial |
| `exile` | 2/5 | 2/5 | 1-2/5 partial |
| `hive` | 2/5 | 2/5 | 1-2/5 partial |
| `hybrid` | 2/5 | 2/5 | 1-2/5 partial |
| `immigrant` | 2/5 | 2/5 | 1-2/5 partial |
| `provincial` | 2/5 | 2/5 | 1-2/5 partial |
| `addict` | 3/5 | 0/5 | 3-5/5 high |
| `adolescent` | 3/5 | 3/5 | 3-5/5 high |
| `alien` | 3/5 | 3/5 | 3-5/5 high |
| `amnesiac` | 3/5 | 3/5 | 3-5/5 high |
| `criminal` | 3/5 | 2/5 | 3-5/5 high |
| `hoarder` | 3/5 | 3/5 | 3-5/5 high |
| `infant` | 3/5 | 2/5 | 3-5/5 high |
| `jester` | 3/5 | 1/5 | 3-5/5 high |

## Group Patterns

Assistant-adjacent role set: n=16, mean exposed prompts=5.00/5, mean exposure fraction=1.000.

Theatrical/fantastical role set: n=20, mean exposed prompts=4.15/5, mean exposure fraction=0.830.

These group sets are heuristic label-based subsets, not cluster assignments.

## Interpretation

The Lu et al. role-prompt set contains extensive direct identity-label priming. In this audit, most prompts explicitly expose the target role label or a normalized variant, and most roles fall in the complete 5/5 exposure category. This means the extraction design should be described as role-label-plus-behavior elicitation, not purely behavioral elicitation.

Exposure varies across roles, so label exposure is a possible source of uneven role-expression yield. The trickster and editor prompt sets both show complete label exposure, yet their local Qwen adaptive extraction yields diverge sharply. That two-role comparison is only a motivating observation, but it suggests label exposure alone cannot explain role-expression success or failure.

This audit does not show that activation geometry is invalid or reducible to labels. It identifies a methodological variable that should be measured in later analyses, especially if comparing theatrical personas to assistant-adjacent personas.

## Limitations

The audit uses conservative string methods and does not detect semantic aliases unless they share the normalized role label or simple variants. It does not measure how strongly a prompt behaviorally describes a role, whether the role label is central or incidental, or how the generated model response uses the label. It also does not correlate label exposure with all 275 role-vector separability scores.

## Recommended Next Audit

Run a behavioral-specificity audit that removes the role label from each prompt and measures how much role-identifying content remains. A useful follow-up would compute lexical label exposure, behavioral cue density, and role-expression yield for each persona, then compare those against vector separability and assistant-axis position.
