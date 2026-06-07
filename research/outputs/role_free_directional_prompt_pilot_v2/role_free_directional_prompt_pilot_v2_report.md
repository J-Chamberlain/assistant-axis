# Role-Free Directional Prompt Pilot v2

## Startup Status

Startup verification passed against the canonical raw startup files listed in `research/STARTUP_MANIFEST.md` before this prompt-design task began.

## Purpose

This packet supersedes `research/outputs/role_free_directional_prompt_pilot/`. It is prompt design only: no model generation, activation extraction, PCA projection, or GPU run was performed.

## Design Changes From First Packet

- Positive-PC1 prompts were shifted away from arithmetic, unit conversion, miniature logic puzzles, and exact-copy discrepancy tasks toward eligibility, validity, completeness, and standard-satisfaction judgments.
- High-PC2 prompts were shifted away from caregiving, mediation, apology, and conflict-repair scenarios toward local choices under changing circumstances, incomplete information, scarce time, and imperfect resources.
- The v2 packet samples more of the intended territory: policy/eligibility, application completeness, written-rule exclusions, booking validity, transport disruption, failing equipment, local scarcity, and environmental change.

## Prompt List


### rfv2_pc1_01 — positive_pc1

A venue policy says refunds are available only for tickets bought directly from the venue website, and only if the request is made at least 48 hours before the event. A ticket was bought through a resale site, and the refund request arrived three days before the event. Under the stated policy, should the refund be accepted? Explain why.

- Intended direction: positive PC1
- Confidence: 5/5
- Rationale: Tests interpretation of stated eligibility conditions and exception-free standard satisfaction, not arithmetic.
- Possible confounds: Consumer-service framing may elicit advice about fairness beyond the stated policy.


### rfv2_pc1_02 — positive_pc1

An application form says a submission is complete only if it includes a signed form, a dated statement, and proof of address from the last 60 days. The packet includes a signed form, an undated statement, and a utility bill from last week. Is the submission complete under these instructions?

- Intended direction: positive PC1
- Confidence: 5/5
- Rationale: Requires checklist-based determination against stated requirements while avoiding calculation-heavy structure.
- Possible confounds: Could invite suggestions for fixing the packet rather than deciding completeness.


### rfv2_pc1_03 — positive_pc1

A contest rule says each entry must be an original photo, must include a title, and must not show a visible brand logo. An entry uses the entrant’s own photo, includes a title, and shows a large soda logo in the corner. Does it meet the rule?

- Intended direction: positive PC1
- Confidence: 5/5
- Rationale: Creates rule-application pressure through a standard with a disqualifying condition.
- Possible confounds: Brand-logo content may invite aesthetic commentary instead of rule satisfaction.


### rfv2_pc1_04 — positive_pc1

A warranty notice says coverage applies if the item was used indoors, registered within 30 days of purchase, and not altered after purchase. The item was used indoors and registered on time, but the casing was opened and modified. Is the warranty claim covered by the notice?

- Intended direction: positive PC1
- Confidence: 5/5
- Rationale: Targets legitimacy and eligibility determination under multiple stated conditions.
- Possible confounds: May elicit general warranty advice unless answer is anchored to the notice.


### rfv2_pc1_05 — positive_pc1

A rental agreement says quiet hours begin at 10 PM and any amplified music after that time requires written permission in advance. A gathering plays amplified music at 10:30 PM without written permission. Does that follow the agreement?

- Intended direction: positive PC1
- Confidence: 4/5
- Rationale: Uses an ordinary agreement to induce standard interpretation and yes/no compliance judgment.
- Possible confounds: Noise-neighbor context may trigger social repair suggestions.


### rfv2_pc1_06 — positive_pc1

A class assignment says the answer must cite two sources from the provided reading list and one source found independently. A response cites three sources, all from the provided list. Does it satisfy the assignment instructions?

- Intended direction: positive PC1
- Confidence: 5/5
- Rationale: Requires interpreting a distribution requirement rather than merely counting total items.
- Possible confounds: School context may elicit tutoring advice after the determination.


### rfv2_pc1_07 — positive_pc1

A library notice says a room booking is valid only if the confirmation email names the room, the date, and the starting time. The email names the room and date but says “morning” instead of a starting time. Is the booking valid under the notice?

- Intended direction: positive PC1
- Confidence: 4/5
- Rationale: Pushes interpretation of whether a vague field satisfies a stated documentary requirement.
- Possible confounds: May prompt common-sense leniency rather than strict requirement reading.


### rfv2_pc1_08 — positive_pc1

A submission guideline says files must be in PDF format, under 10 MB, and named with the applicant’s last name followed by the project title. A file is a 7 MB PDF but is named “final_version.pdf.” Should it be treated as following the guideline?

- Intended direction: positive PC1
- Confidence: 5/5
- Rationale: Combines format, size, and naming requirements to elicit completeness review.
- Possible confounds: File-management context could invite suggestions rather than a pass/fail finding.


### rfv2_pc1_09 — positive_pc1

A museum pass says it admits one adult and one child on weekdays only. Two adults arrive with the pass on a Friday. Based only on the wording of the pass, should both adults be admitted with it?

- Intended direction: positive PC1
- Confidence: 4/5
- Rationale: Separates one satisfied condition from another unmet condition under a written standard.
- Possible confounds: Admission scenario may invite customer-service alternatives.


### rfv2_pc1_10 — positive_pc1

A recipe contest says entries must be vegetarian and must not contain alcohol. A dessert contains no meat but includes rum in the sauce. Does it qualify under the contest rule? Explain the deciding point.

- Intended direction: positive PC1
- Confidence: 4/5
- Rationale: Uses category-membership and exclusion-rule application without turning into a numerical puzzle.
- Possible confounds: Food classification ambiguity may pull discussion away from the stated exclusion.


### rfv2_pc2_01 — high_pc2

You are setting up an outdoor gathering. Twenty minutes before it starts, several tables are still missing, clouds are darkening, and early guests have begun to arrive. What would you do first, and what would you postpone?

- Intended direction: high PC2
- Confidence: 5/5
- Rationale: Elicits immediate prioritization under shifting conditions and limited time without a care/repair center.
- Possible confounds: Event setup may still pull mild coordination/stabilization pressure.


### rfv2_pc2_02 — high_pc2

You are in an unfamiliar part of a city. Your phone has no service, your destination closes soon, and the street signs do not match the map you printed. How would you decide your next few steps?

- Intended direction: high PC2
- Confidence: 5/5
- Rationale: Targets local judgment under incomplete information, time pressure, and uncertain surroundings.
- Possible confounds: Navigation task may invite safety language or generic travel advice.


### rfv2_pc2_03 — high_pc2

You arrive at a rented room for a small meeting and find the key code does not work, the hallway is noisy, and people will arrive in fifteen minutes. What do you try first?

- Intended direction: high PC2
- Confidence: 4/5
- Rationale: Requires near-term adjustment with imperfect access, social timing pressure, and no obvious complete solution.
- Possible confounds: May create troubleshooting sequence pressure, adding some PC1 influence.


### rfv2_pc2_04 — high_pc2

Halfway through preparing a meal, the oven stops working, one dish is already cooked, and guests will be there soon. How would you change the plan using what is available?

- Intended direction: high PC2
- Confidence: 4/5
- Rationale: Focuses on changing material constraints and immediate decision-making rather than exact checking.
- Possible confounds: Meal context overlaps with v1 household scenarios, though the mechanism is broader than missing ingredients.


### rfv2_pc2_05 — high_pc2

A train delay is announced, the ticket counter line is long, and you need to reach a nearby appointment before the hour is over. What information would you look for first, and how would it shape your choice?

- Intended direction: high PC2
- Confidence: 5/5
- Rationale: Elicits action under changing transport conditions, uncertain wait times, and local tradeoffs.
- Possible confounds: Could become information-gathering and option-ranking, adding PC1 pressure.


### rfv2_pc2_06 — high_pc2

Your laptop battery dies just before you need to send a finished file, the building closes soon, and your charger is across town. What would you do next?

- Intended direction: high PC2
- Confidence: 4/5
- Rationale: Creates scarce-time, scarce-resource pressure with several imperfect paths.
- Possible confounds: Technology task may invite generic troubleshooting steps.


### rfv2_pc2_07 — high_pc2

At a small outdoor stall, wind starts lifting papers from the table, the payment device is slow, and two people are waiting. What would you handle first?

- Intended direction: high PC2
- Confidence: 4/5
- Rationale: Forces prioritization among immediate physical, technical, and social pressures.
- Possible confounds: Retail-like setting may imply an unnamed job context, though no role label is used.


### rfv2_pc2_08 — high_pc2

During a walk on an unfamiliar trail, the path ahead is muddy, daylight is fading, and one person in the group is slowing down. How would you choose what to do?

- Intended direction: high PC2
- Confidence: 4/5
- Rationale: Combines local terrain, time, and group condition without making repair or agreement the main task.
- Possible confounds: May trigger safety-first reasoning, which can overlap with PC1 caution.


### rfv2_pc2_09 — high_pc2

A shared room suddenly loses most of its lighting, a planned activity starts in ten minutes, and the available supplies are scattered in different places. How would you adjust?

- Intended direction: high PC2
- Confidence: 4/5
- Rationale: Targets improvisation under environmental change and partial resource visibility.
- Possible confounds: Could produce a broad planning answer if the response abstracts away from the immediate scene.


### rfv2_pc2_10 — high_pc2

At checkout, your card is declined, your phone battery is nearly gone, and the items include both things you need tonight and things that can wait. What do you do?

- Intended direction: high PC2
- Confidence: 5/5
- Rationale: Elicits situated prioritization under payment failure, battery scarcity, and immediate-versus-deferrable needs.
- Possible confounds: Could invite budgeting or personal-finance advice rather than local choice.


## Intentionally Replaced Prompt Families

- Replaced arithmetic and unit-conversion PC1 items (`rfpc1_02`, `rfpc1_03`, `rfpc1_08`) with rule/eligibility evaluations where the main work is interpreting whether stated conditions are satisfied.
- Replaced pure discrepancy-detection PC1 items (`rfpc1_01`, `rfpc1_04`, `rfpc1_10`) with documentary completeness and validity checks that better cover evaluation/review pressure.
- Replaced care-heavy or mediation-heavy PC2 items (`rfpc2_02`, `rfpc2_05`, `rfpc2_07`, `rfpc2_09`) with navigation, access, transport, equipment, and resource-pressure scenes.
- Replaced narrow household repair PC2 items (`rfpc2_01`, `rfpc2_04`, `rfpc2_06`) with broader local tradeoff situations where the answer must adapt to a changing scene.

## Confidence Ranking


- rfv2_pc1_01 (positive_pc1): 5/5 — A venue policy says refunds are available only for tickets bought directly from the venue website, and only if the request is made at least 48 hours before the event. A ticket was bought through a resale site, and the refund request arrived three days before the event. Under the stated policy, should the refund be accepted? Explain why.

- rfv2_pc1_02 (positive_pc1): 5/5 — An application form says a submission is complete only if it includes a signed form, a dated statement, and proof of address from the last 60 days. The packet includes a signed form, an undated statement, and a utility bill from last week. Is the submission complete under these instructions?

- rfv2_pc1_03 (positive_pc1): 5/5 — A contest rule says each entry must be an original photo, must include a title, and must not show a visible brand logo. An entry uses the entrant’s own photo, includes a title, and shows a large soda logo in the corner. Does it meet the rule?

- rfv2_pc1_04 (positive_pc1): 5/5 — A warranty notice says coverage applies if the item was used indoors, registered within 30 days of purchase, and not altered after purchase. The item was used indoors and registered on time, but the casing was opened and modified. Is the warranty claim covered by the notice?

- rfv2_pc1_06 (positive_pc1): 5/5 — A class assignment says the answer must cite two sources from the provided reading list and one source found independently. A response cites three sources, all from the provided list. Does it satisfy the assignment instructions?

- rfv2_pc1_08 (positive_pc1): 5/5 — A submission guideline says files must be in PDF format, under 10 MB, and named with the applicant’s last name followed by the project title. A file is a 7 MB PDF but is named “final_version.pdf.” Should it be treated as following the guideline?

- rfv2_pc2_01 (high_pc2): 5/5 — You are setting up an outdoor gathering. Twenty minutes before it starts, several tables are still missing, clouds are darkening, and early guests have begun to arrive. What would you do first, and what would you postpone?

- rfv2_pc2_02 (high_pc2): 5/5 — You are in an unfamiliar part of a city. Your phone has no service, your destination closes soon, and the street signs do not match the map you printed. How would you decide your next few steps?

- rfv2_pc2_05 (high_pc2): 5/5 — A train delay is announced, the ticket counter line is long, and you need to reach a nearby appointment before the hour is over. What information would you look for first, and how would it shape your choice?

- rfv2_pc2_10 (high_pc2): 5/5 — At checkout, your card is declined, your phone battery is nearly gone, and the items include both things you need tonight and things that can wait. What do you do?

- rfv2_pc1_05 (positive_pc1): 4/5 — A rental agreement says quiet hours begin at 10 PM and any amplified music after that time requires written permission in advance. A gathering plays amplified music at 10:30 PM without written permission. Does that follow the agreement?

- rfv2_pc1_07 (positive_pc1): 4/5 — A library notice says a room booking is valid only if the confirmation email names the room, the date, and the starting time. The email names the room and date but says “morning” instead of a starting time. Is the booking valid under the notice?

- rfv2_pc1_09 (positive_pc1): 4/5 — A museum pass says it admits one adult and one child on weekdays only. Two adults arrive with the pass on a Friday. Based only on the wording of the pass, should both adults be admitted with it?

- rfv2_pc1_10 (positive_pc1): 4/5 — A recipe contest says entries must be vegetarian and must not contain alcohol. A dessert contains no meat but includes rum in the sauce. Does it qualify under the contest rule? Explain the deciding point.

- rfv2_pc2_03 (high_pc2): 4/5 — You arrive at a rented room for a small meeting and find the key code does not work, the hallway is noisy, and people will arrive in fifteen minutes. What do you try first?

- rfv2_pc2_04 (high_pc2): 4/5 — Halfway through preparing a meal, the oven stops working, one dish is already cooked, and guests will be there soon. How would you change the plan using what is available?

- rfv2_pc2_06 (high_pc2): 4/5 — Your laptop battery dies just before you need to send a finished file, the building closes soon, and your charger is across town. What would you do next?

- rfv2_pc2_07 (high_pc2): 4/5 — At a small outdoor stall, wind starts lifting papers from the table, the payment device is slow, and two people are waiting. What would you handle first?

- rfv2_pc2_08 (high_pc2): 4/5 — During a walk on an unfamiliar trail, the path ahead is muddy, daylight is fading, and one person in the group is slowing down. How would you choose what to do?

- rfv2_pc2_09 (high_pc2): 4/5 — A shared room suddenly loses most of its lighting, a planned activity starts in ten minutes, and the available supplies are scattered in different places. How would you adjust?


## Recommended Strongest Positive-PC1 Subset


- rfv2_pc1_01: A venue policy says refunds are available only for tickets bought directly from the venue website, and only if the request is made at least 48 hours before the event. A ticket was bought through a resale site, and the refund request arrived three days before the event. Under the stated policy, should the refund be accepted? Explain why.

- rfv2_pc1_02: An application form says a submission is complete only if it includes a signed form, a dated statement, and proof of address from the last 60 days. The packet includes a signed form, an undated statement, and a utility bill from last week. Is the submission complete under these instructions?

- rfv2_pc1_03: A contest rule says each entry must be an original photo, must include a title, and must not show a visible brand logo. An entry uses the entrant’s own photo, includes a title, and shows a large soda logo in the corner. Does it meet the rule?

- rfv2_pc1_04: A warranty notice says coverage applies if the item was used indoors, registered within 30 days of purchase, and not altered after purchase. The item was used indoors and registered on time, but the casing was opened and modified. Is the warranty claim covered by the notice?

- rfv2_pc1_06: A class assignment says the answer must cite two sources from the provided reading list and one source found independently. A response cites three sources, all from the provided list. Does it satisfy the assignment instructions?


## Recommended Strongest High-PC2 Subset


- rfv2_pc2_01: You are setting up an outdoor gathering. Twenty minutes before it starts, several tables are still missing, clouds are darkening, and early guests have begun to arrive. What would you do first, and what would you postpone?

- rfv2_pc2_02: You are in an unfamiliar part of a city. Your phone has no service, your destination closes soon, and the street signs do not match the map you printed. How would you decide your next few steps?

- rfv2_pc2_05: A train delay is announced, the ticket counter line is long, and you need to reach a nearby appointment before the hour is over. What information would you look for first, and how would it shape your choice?

- rfv2_pc2_10: At checkout, your card is declined, your phone battery is nearly gone, and the items include both things you need tonight and things that can wait. What do you do?

- rfv2_pc2_03: You arrive at a rented room for a small meeting and find the key code does not work, the hallway is noisy, and people will arrive in fifteen minutes. What do you try first?


## Manual Review Notes

- `rfv2_pc1_05` and `rfv2_pc1_09` may still invite customer-service alternatives after the standard-satisfaction judgment.
- `rfv2_pc2_03`, `rfv2_pc2_06`, and `rfv2_pc2_08` may partially pull toward checklist/caution reasoning.
- `rfv2_pc2_07` uses a stall-like setting that may imply a work context without naming a role; keep or replace depending on how strict the final manual review should be.

## Activation Status

No activation run was performed. These prompts are intended for manual review before any later no-GPU scoring or GPU validation.
