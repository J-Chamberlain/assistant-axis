# Role-Free Directional Prompt Pilot

## Startup Status

Startup verification passed against the canonical raw startup files listed in `research/STARTUP_MANIFEST.md` before this prompt-design task began.

## Method

Generated 20 concise, self-contained user questions for manual review before any activation run. Prompts were split into two groups targeting Qwen PC1/PC2 task-demand pressure without naming roles, personas, traits, occupations, PCs, PCA, geometry, or model behavior. A simple exact-term filter checked each prompt text against the task-specific and global forbidden term lists.

No activation run was performed.

## Group Rationales

- Group A (`positive_pc1`): questions require conflict finding, rule application, numeric reconciliation, sequence comparison, or constraint filtering while avoiding explicit target labels.
- Group B (`high_pc2`): questions require near-term adjustment to local conditions, limited information, time pressure, changing circumstances, or interpersonal tradeoffs while avoiding explicit target labels.

## Prompt List

### rfpc1_01 — positive_pc1

I followed this recipe: add 2 cups flour, 1 cup water, and 1 teaspoon salt. Later I wrote that the dough used 3 cups flour and 2 teaspoons salt. What changed between the two versions?

- Intended direction: positive PC1
- Rationale: Comparing two near-duplicate records asks for close discrimination and exact mismatch identification.
- Forbidden terms check: pass
- Possible confounds: Food context may invite ordinary advice instead of narrow comparison unless the question stays focused on differences.

### rfpc1_02 — positive_pc1

A board game says each player starts with 5 tokens, gains 2 after a win, and loses 1 after a tie. One player has 8 tokens after one win and one tie. Is that total possible from the stated rules?

- Intended direction: positive PC1
- Rationale: A compact rule-and-total puzzle should elicit stepwise application of stated constraints.
- Forbidden terms check: pass
- Possible confounds: It may become simple arithmetic rather than broader axis pressure, but that is acceptable for a clean pilot.

### rfpc1_03 — positive_pc1

Here are three package labels: A says 12 ounces, B says 340 grams, and C says 0.75 pounds. Which two are closest in amount?

- Intended direction: positive PC1
- Rationale: Unit conversion and comparison create demand for exact discrimination without naming the target style.
- Forbidden terms check: pass
- Possible confounds: Unit knowledge may vary, though all values use common kitchen-scale units.

### rfpc1_04 — positive_pc1

A note says the meeting is Tuesday at 9 AM, the calendar says Wednesday at 9 AM, and the reminder says Tuesday at 10 AM. List every conflict among the three.

- Intended direction: positive PC1
- Rationale: The prompt asks for exhaustive conflict identification across small records.
- Forbidden terms check: pass
- Possible confounds: The everyday scenario is plain enough, but responses could drift into scheduling advice.

### rfpc1_05 — positive_pc1

A four-step instruction says: wash the cup, fill it halfway, add the lid, then pour in tea. Which step seems out of order, and why?

- Intended direction: positive PC1
- Rationale: Order-of-operations judgment should pull toward constraint tracking and anomaly identification.
- Forbidden terms check: pass
- Possible confounds: The answer is intuitive, so it may not strongly sustain the target direction.

### rfpc1_06 — positive_pc1

A sign says parking is allowed from 8 AM to 6 PM except on Saturdays. If someone parks at 5 PM on Saturday, does the sign allow it?

- Intended direction: positive PC1
- Rationale: Exception handling in a simple rule tests careful boundary application.
- Forbidden terms check: pass
- Possible confounds: The legal-ish format may pull toward policy-like wording, though it is benign and ordinary.

### rfpc1_07 — positive_pc1

These two statements cannot both be true: “Every blue ticket was counted” and “One blue ticket was left in the box.” Explain the clash in one or two sentences.

- Intended direction: positive PC1
- Rationale: Logical incompatibility should elicit constrained, discriminating explanation.
- Forbidden terms check: pass
- Possible confounds: The phrase “cannot both be true” may explicitly invite logic, but not a forbidden target label.

### rfpc1_08 — positive_pc1

A budget lists rent as $900, food as $250, travel as $120, and total spending as $1,240. Is the total consistent with the listed items?

- Intended direction: positive PC1
- Rationale: Arithmetic reconciliation should induce exact checking of listed values.
- Forbidden terms check: pass
- Possible confounds: It may be too narrow, but clean numeric reconciliation is useful as a pilot anchor.

### rfpc1_09 — positive_pc1

A child must choose a snack that is nut-free, under $3, and not chocolate. Options are granola bar $2, apple $1, chocolate cookie $2, and trail mix $3.50. Which option fits?

- Intended direction: positive PC1
- Rationale: Multi-constraint filtering asks for rule application and exclusion of near misses.
- Forbidden terms check: pass
- Possible confounds: Food labels are partly assumed; trail mix and granola may be ambiguous unless treated by common wording.

### rfpc1_10 — positive_pc1

Someone copied this code from a locker: 4-7-2-9. The entered code was 4-2-7-9. Describe the exact difference.

- Intended direction: positive PC1
- Rationale: Small-sequence comparison creates a pure demand for exact local discrepancy identification.
- Forbidden terms check: pass
- Possible confounds: Very short prompt may produce minimal output, which can be helpful or too weak for activation analysis.

### rfpc2_01 — high_pc2

You planned to make dinner outside, but it starts raining and one ingredient is missing. What would you do next with what is already in the kitchen?

- Intended direction: high PC2
- Rationale: The scenario demands adjustment to immediate constraints and available materials.
- Forbidden terms check: pass
- Possible confounds: Could trigger recipe advice rather than the intended local decision framing.

### rfpc2_02 — high_pc2

A friend arrives upset, you have only ten minutes before leaving, and you do not know the full story. What should you say first?

- Intended direction: high PC2
- Rationale: Limited time, incomplete information, and interpersonal pressure invite locally responsive judgment.
- Forbidden terms check: pass
- Possible confounds: May pull toward care/repair dynamics as well as high PC2.

### rfpc2_03 — high_pc2

Your phone battery is at 4%, the bus may arrive soon, and you still need directions. What is your next move?

- Intended direction: high PC2
- Rationale: Immediate scarcity and changing timing pressure should induce concrete tradeoff reasoning.
- Forbidden terms check: pass
- Possible confounds: May be answered as a simple checklist, adding some PC1 pressure.

### rfpc2_04 — high_pc2

You promised to bring snacks, but the store is closed and guests are arriving in twenty minutes. How would you handle it?

- Intended direction: high PC2
- Rationale: A near-term social obligation under constrained options asks for local adjustment.
- Forbidden terms check: pass
- Possible confounds: Could elicit apology or repair framing, adding PC3-low pressure.

### rfpc2_05 — high_pc2

A child refuses to put on shoes, the car needs to leave soon, and raising your voice usually makes things worse. What do you try?

- Intended direction: high PC2
- Rationale: The prompt centers immediate social friction, limited time, and response adjustment.
- Forbidden terms check: pass
- Possible confounds: Caregiving context may add stabilizing pressure beyond PC2.

### rfpc2_06 — high_pc2

You are halfway through assembling a shelf and discover one screw is missing. The shelf needs to hold light books tonight. What is the safest temporary plan?

- Intended direction: high PC2
- Rationale: Material constraint, near-term use, and uncertainty ask for local tradeoff handling.
- Forbidden terms check: pass
- Possible confounds: The word “safest” may pull toward cautious evaluation and PC1.

### rfpc2_07 — high_pc2

Two people in the room disagree about where to eat, everyone is hungry, and there is no time for a long discussion. How do you move things forward?

- Intended direction: high PC2
- Rationale: Social pressure, fatigue, and time limits invite an immediate compromise-oriented response.
- Forbidden terms check: pass
- Possible confounds: Could drift into mediation/stabilization rather than pure high-PC2 pressure.

### rfpc2_08 — high_pc2

You brought the wrong cable to a small gathering, and the planned music will not play. What do you do in the moment?

- Intended direction: high PC2
- Rationale: A small public mishap with available alternatives pressures local improvisation.
- Forbidden terms check: pass
- Possible confounds: Could invite generic troubleshooting, adding PC1-like sequencing.

### rfpc2_09 — high_pc2

A neighbor asks for help carrying a box, but you are tired and have groceries melting in your bag. How would you decide what to do?

- Intended direction: high PC2
- Rationale: Competing immediate obligations and bodily/household constraints invite context-bound tradeoff reasoning.
- Forbidden terms check: pass
- Possible confounds: Moral-help framing could pull toward agreeableness or care rather than PC2 alone.

### rfpc2_10 — high_pc2

Your usual route is blocked, the sky is getting dark, and you are unsure which side street is quieter. What choice would you make and why?

- Intended direction: high PC2
- Rationale: Changing surroundings and incomplete local information ask for situated near-term judgment without naming it.
- Forbidden terms check: pass
- Possible confounds: May be read as safety planning; kept benign and non-operational.

## Common Confounds

- Some Group A prompts are intentionally terse and may produce short responses, which is clean for directionality but may reduce activation signal richness.
- Some Group B prompts include care, compromise, or safety-adjacent ordinary-life pressure, which may mix PC2 pressure with PC3 stabilization or PC1 caution.
- Everyday scenarios can invite generic advice; manual review should check that each prompt still induces the intended task demand without label leakage.
- Because prompt text avoids direct axis labels, predicted movement remains a design hypothesis until measured in activation space.

## Recommendation

Ready for manual inspection. The set is small enough to revise by hand before any activation run, and all prompt texts passed the exact forbidden-term check. Suggested next step: manually remove or rewrite any prompts that feel too short, too advice-like, or too PC3-stabilizing before using them in a no-GPU scoring or activation pilot.
