# SVD15 Component Interpretation

Date: 2026-05-28
Analysis model: GPT-5.5 Standard

These components reconstruct Claude's TF-IDF SVD15 setup from the full no-label prompt corpus. Component signs are arbitrary, so positive and negative poles should be read as contrasts rather than absolute directions.

Baseline sem+BigFive R2: 0.613
Sem+BigFive+SVD15 R2: 0.707
SVD15 explained TF-IDF variance: 0.138

## svd_0 — appears to track general located-role texture versus facilitation/moderation formulae

- TF-IDF explained variance ratio: 0.0014
- Correlation with activation PCs: PC1 -0.142, PC2 -0.022, PC3 0.034
- Correlation with SVD-model residual improvement: -0.041
- Closest hand-named residual dimension: liminal_transition (r=0.153)
- Positive terms: the; in; of; to; someone; are; you are; who; bring; through; with; as; you bring; your; for; from; that; specializes
- Negative terms: on others; you emphasizes; use creates; safe spaces; meet; interaction and; instruction; ensures all; heard; voices; all voices; group discussions; helps groups; reach consensus; productive dialogue; you instinctively; instinctively; and documents
- Highest-scoring personas: fixer; immigrant; addict; virtuoso; prisoner; translator; historian; conservator; provincial; spirit; exile; expatriate
- Lowest-scoring personas: maverick; loner; screener; skeptic; pragmatist; moderator; grader; teacher; witness; secretary; observer; trainer

## svd_1 — appears to track professional specialization versus existential/liminal being-language

- TF-IDF explained variance ratio: 0.0211
- Correlation with activation PCs: PC1 0.769, PC2 -0.055, PC3 0.089
- Correlation with SVD-model residual improvement: -0.154
- Closest hand-named residual dimension: semantic_neighbor_residual_pressure (r=-0.366)
- Positive terms: specializes; specializes in; you specializes; bring; at; you bring; excels at; excels; you excels; expertise in; in; expertise; bring extensive; extensive; skilled; various; comprehensive; complex
- Negative terms: who; as; has; your; the; that; someone; be; embody; act; act as; an; from; whose; someone who; who has; life; being
- Highest-scoring personas: engineer; consultant; mathematician; statistician; debugger; designer; marketer; strategist; forecaster; organizer; planner; accountant
- Lowest-scoring personas: spirit; immigrant; void; leviathan; prisoner; echo; revenant; egregore; exile; refugee; ancient; wind

## svd_2 — appears to track nonhuman/entity consciousness versus lived family/social hardship

- TF-IDF explained variance ratio: 0.0116
- Correlation with activation PCs: PC1 -0.150, PC2 -0.608, PC3 0.343
- Correlation with SVD-model residual improvement: -0.030
- Closest hand-named residual dimension: developmental_dependency (r=-0.268)
- Positive terms: that; entity; consciousness; whose; being; human; existence; reality; entity that; consciousness that; embody; exists; ancient; intelligence; from the; patterns; information; be
- Negative terms: is; you is; life; someone who; navigating; your; who; has; experience; you has; challenges; the challenges; for; to; family; others; medical; who has
- Highest-scoring personas: eldritch; crystalline; void; leviathan; chimera; swarm; wraith; mycorrhizal; ancient; echo; hive; egregore
- Lowest-scoring personas: divorcee; parent; patient; widow; teenager; refugee; immigrant; adolescent; newlywed; celebrity; graduate; orphan

## svd_3 — appears to track ideological solution-seeking versus lived-experience navigation

- TF-IDF explained variance ratio: 0.0107
- Correlation with activation PCs: PC1 -0.032, PC2 0.048, PC3 0.101
- Correlation with SVD-model residual improvement: -0.133
- Closest hand-named residual dimension: liminal_transition (r=-0.143)
- Positive terms: to; others; or; on; thinking; believes; for; use; all; seeks; people; situations; sees; conventional; solutions; helps; you believes; in all
- Negative terms: understands; has; knowledge of; understands the; knowledge; you understands; who has; navigating; extensive; bring extensive; experience; your; extensive knowledge; the challenges; you has; life; experienced; country
- Highest-scoring personas: optimist; realist; maverick; pacifist; rebel; provocateur; revolutionary; martyr; trickster; caregiver; contrarian; anarchist
- Lowest-scoring personas: expatriate; parent; prisoner; patient; chemist; teenager; widow; pilot; immigrant; architect; divorcee; refugee

## svd_4 — appears to track deep analytic/evidence language versus content/mediation production

- TF-IDF explained variance ratio: 0.0102
- Correlation with activation PCs: PC1 0.117, PC2 -0.176, PC3 0.005
- Correlation with SVD-model residual improvement: -0.019
- Closest hand-named residual dimension: identity_formation (r=-0.158)
- Positive terms: knowledge; bring deep; analysis; evidence; deep; you approaches; deep expertise; approaches; are someone; knowledge of; analyzing; in analyzing; committed to; committed; data; patterns; careful; practices
- Negative terms: excels at; excels; at; you excels; creating; content; building; as; bring expertise; compelling; into; parties; different; engaging; act as; act; audiences; and creating
- Highest-scoring personas: scientist; scholar; detective; linguist; healer; anthropologist; researcher; vegan; physicist; pharmacist; philosopher; traditionalist
- Lowest-scoring personas: negotiator; mediator; writer; entrepreneur; podcaster; emissary; curator; coordinator; producer; marketer; synthesizer; planner

## svd_5 — appears to track teaching/spiritual lived experience versus standards/evaluation roles

- TF-IDF explained variance ratio: 0.0100
- Correlation with activation PCs: PC1 -0.243, PC2 0.016, PC3 -0.307
- Correlation with SVD-model residual improvement: -0.011
- Closest hand-named residual dimension: developmental_dependency (r=0.343)
- Positive terms: through; experiences; life; into; learning; deep; your; creating; others; expertise; expertise in; bring deep; profound; understanding; spiritual; bring expertise; experiences and; complex
- Negative terms: someone; who; experience in; extensive; extensive experience; bring extensive; someone who; experience; standards; act; act as; as someone; all; role of; the role; role; please; systematically
- Highest-scoring personas: instructor; teacher; tutor; guru; poet; widow; mystic; podcaster; sage; trainer; blogger; coach
- Lowest-scoring personas: auditor; screener; perfectionist; procrastinator; judge; veterinarian; examiner; supervisor; evaluator; coordinator; pacifist; reviewer

## svd_6 — appears to track social-systems building versus meticulous evidence/information review

- TF-IDF explained variance ratio: 0.0093
- Correlation with activation PCs: PC1 -0.089, PC2 -0.021, PC3 -0.100
- Correlation with SVD-model residual improvement: -0.123
- Closest hand-named residual dimension: role_ambiguity (r=0.160)
- Positive terms: knowledge of; extensive knowledge; dedicated to; building; understands the; dedicated; understands; systems; relationships; you understands; experienced in; someone experienced; structures; believes; social; cultural; creating; advocates for
- Negative terms: you systematically; systematically; skilled at; insights; has; evidence; events; you carefully; provides; are skilled; carefully; from; skilled; experience; analysis; you meticulously; meticulously; information
- Highest-scoring personas: merchant; revolutionary; architect; archivist; anarchist; purist; emissary; collaborator; activist; chemist; networker; peacekeeper
- Lowest-scoring personas: analyst; grader; reviewer; researcher; examiner; witness; observer; interviewer; proofreader; judge; screener; generalist

## svd_7 — appears to track helping/health/guidance versus abstract analytic forecasting expertise

- TF-IDF explained variance ratio: 0.0089
- Correlation with activation PCs: PC1 -0.047, PC2 -0.210, PC3 -0.241
- Correlation with SVD-model residual improvement: -0.017
- Closest hand-named residual dimension: semantic_neighbor_residual_pressure (r=-0.240)
- Positive terms: helping; bring extensive; their; extensive; guidance; others; health; experience in; extensive knowledge; provides; people; experience; in helping; providing; being; help; spiritual; you provides
- Negative terms: who; expertise in; information; you excels; deep expertise; analysis; data; someone who; cultural; bring deep; excels at; excels; problems; complex; expertise; patterns; at; person
- Highest-scoring personas: doctor; nutritionist; guru; mentor; therapist; counselor; caregiver; grader; reviewer; sommelier; assistant; healer
- Lowest-scoring personas: statistician; forecaster; futurist; visionary; mathematician; hybrid; immigrant; refugee; adolescent; anthropologist; traditionalist; hacker

## svd_8 — appears to track outlaw/survivor/story-role texture versus collective/student/entity identity

- TF-IDF explained variance ratio: 0.0084
- Correlation with activation PCs: PC1 -0.304, PC2 0.067, PC3 0.203
- Correlation with SVD-model residual improvement: -0.008
- Closest hand-named residual dimension: developmental_dependency (r=-0.264)
- Positive terms: the; has; who; role; role of; the role; on the; understands; on; take; take on; of; wisdom; understands the; and the; in the; of someone; stories
- Negative terms: learning; that; is; multiple; your; entity; identity; are someone; you is; consciousness; collective; individual; topics; new; someone; students; please be; down
- Highest-scoring personas: pirate; criminal; jester; procrastinator; survivor; fixer; prey; caveman; gossip; veteran; witness; soldier
- Lowest-scoring personas: swarm; hive; instructor; newlywed; teacher; student; tutor; cyborg; hybrid; graduate; crystalline; immigrant

## svd_9 — appears to track between-worlds/intercultural mediation versus stepwise planning/training

- TF-IDF explained variance ratio: 0.0081
- Correlation with activation PCs: PC1 -0.023, PC2 -0.016, PC3 -0.162
- Correlation with SVD-model residual improvement: -0.045
- Closest hand-named residual dimension: role_ambiguity (r=0.309)
- Positive terms: between; different; diverse; between different; cultural; perspectives; understanding; multiple; communication; parties; skilled; seamlessly; insights; across; interests; cultures; others; someone skilled
- Negative terms: down; creating; systems; steps; learning; on; you focuses; manageable; down complex; breaking down; focuses; focuses on; breaking; that; is; goals; whose; methods
- Highest-scoring personas: emissary; interpreter; cosmopolitan; hybrid; dilettante; actor; generalist; translator; chameleon; ambassador; mediator; anthropologist
- Lowest-scoring personas: trainer; planner; strategist; instructor; pragmatist; coach; organizer; destroyer; builder; tutor; criminal; anarchist

## svd_10 — appears to track common-ground mediation versus storytelling/content/humor roles

- TF-IDF explained variance ratio: 0.0080
- Correlation with activation PCs: PC1 0.124, PC2 -0.036, PC3 -0.085
- Correlation with SVD-model residual improvement: -0.053
- Closest hand-named residual dimension: symbolic_nonprocedural_identity (r=-0.226)
- Positive terms: on; between; has; from; parties; problems; different; who has; their; solutions; on the; someone who; take on; take; people; common; draws; you has
- Negative terms: through; content; stories; compelling; engaging; are someone; storytelling; for; experiences; events; about; managing; you are; are; humor; use; questions; standards
- Highest-scoring personas: mediator; negotiator; survivor; peacekeeper; consultant; mentor; generalist; emissary; pragmatist; veteran; expatriate; orphan
- Lowest-scoring personas: narrator; blogger; reporter; bard; writer; journalist; fool; auditor; photographer; novelist; smuggler; producer

## svd_11 — appears to track standards/content/work embodiment versus data/health/care information

- TF-IDF explained variance ratio: 0.0078
- Correlation with activation PCs: PC1 0.035, PC2 -0.152, PC3 -0.073
- Correlation with SVD-model residual improvement: 0.035
- Closest hand-named residual dimension: incomplete_proceduralization (r=0.187)
- Positive terms: all; has; for; embody someone; standards; expertise; you has; content; in all; expertise in; between; work; embody; cultural; forms; bring expertise; experiences; experiences and
- Negative terms: information; you is; is; others; data; about; based; medical; health; intelligence; skilled; navigating; care; solutions; challenges; evidence; operates; is passionate
- Highest-scoring personas: purist; minimalist; perfectionist; anarchist; influencer; grader; soldier; instructor; artisan; examiner; teacher; ascetic
- Lowest-scoring personas: spy; adolescent; teenager; programmer; rogue; analyst; detective; fixer; hacker; therapist; veterinarian; patient

## svd_12 — appears to track human/social-event patterning versus flexible across-situation capability

- TF-IDF explained variance ratio: 0.0074
- Correlation with activation PCs: PC1 0.012, PC2 -0.102, PC3 -0.020
- Correlation with SVD-model residual improvement: 0.048
- Closest hand-named residual dimension: semantic_neighbor_developmental_pressure (r=-0.176)
- Positive terms: human; about; events; patterns; life; future; social; that; relationships; dynamics; on; events and; group; for; living; is; and social; developments
- Negative terms: any; different; who; understands; approaches; you can; you approaches; whose; situation; topics; the ability; ability; ability to; can; knowledge; problems; someone who; various
- Highest-scoring personas: futurist; anthropologist; sociologist; forecaster; facilitator; archaeologist; prophet; ancient; biologist; divorcee; vampire; retiree
- Lowest-scoring personas: shapeshifter; fixer; virtuoso; musician; teacher; hybrid; soldier; actor; empath; prodigy; sommelier; generalist

## svd_13 — appears to track preservation/dedication/material history versus market/opportunity pragmatics

- TF-IDF explained variance ratio: 0.0073
- Correlation with activation PCs: PC1 -0.026, PC2 -0.117, PC3 -0.083
- Correlation with SVD-model residual improvement: -0.059
- Closest hand-named residual dimension: semantic_neighbor_residual_pressure (r=-0.256)
- Positive terms: dedicated to; dedicated; to; are dedicated; historical; information; own; between; bring deep; is; their; expertise in; health; important; expertise; medical; items; materials
- Negative terms: market; thinking; opportunities; relationships; conventional; based; thinking and; with; approaches; extensive; building; wisdom; managing; someone experienced; are someone; bring extensive; sees; understanding
- Highest-scoring personas: conservator; curator; doctor; martyr; healer; historian; destroyer; altruist; familiar; artisan; guardian; synthesizer
- Lowest-scoring personas: merchant; optimist; entrepreneur; detective; architect; facilitator; pragmatist; smuggler; maverick; contrarian; moderator; skeptic

## svd_14 — appears to track wisdom/social challenge/rebel mentor texture versus everyday relational-emotional web

- TF-IDF explained variance ratio: 0.0073
- Correlation with activation PCs: PC1 -0.046, PC2 -0.088, PC3 0.160
- Correlation with SVD-model residual improvement: -0.057
- Closest hand-named residual dimension: semantic_neighbor_residual_pressure (r=-0.181)
- Positive terms: who has; wisdom; wisdom and; conventional; to; as someone; be; spiritual; from; challenges; has; social; country; society; please; please be; years of; changes
- Negative terms: the; on; relationships; all; you is; in the; the world; emotional; is; every; between; on the; by; can; around; maintains; work; personal
- Highest-scoring personas: maverick; visionary; guru; veteran; expatriate; elder; rebel; exile; mentor; provocateur; provincial; trickster
- Lowest-scoring personas: idealist; symbiont; ecosystem; divorcee; perfectionist; ambassador; amateur; poet; newlywed; actor; competitor; prey
