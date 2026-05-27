# Semantic Voids and Density Notes

This note uses no-label prompt TF-IDF/SVD topology. Low-density roles are not errors; they are roles whose prompt semantics have fewer close neighbors in this constructed corpus.

## Lowest-Density Roles

| Role | Activation cluster | Top-10 mean cosine | Nearest neighbors |
|---|---|---:|---|
| `flaneur` | `mythic_spiritual` | 0.319 | luddite:0.388, wanderer:0.382, observer:0.347, nomad:0.331, hedonist:0.318 |
| `predator` | `mythic_spiritual` | 0.323 | prey:0.740, vampire:0.476, caveman:0.395, competitor:0.287, chameleon:0.266 |
| `devils_advocate` | `combative_iconoclast` | 0.328 | contrarian:0.856, advocate:0.606, skeptic:0.344, zealot:0.312, trickster:0.253 |
| `advocate` | `procedural_professional` | 0.334 | devils_advocate:0.606, idealist:0.423, activist:0.385, martyr:0.343, procrastinator:0.300 |
| `teenager` | `other` | 0.345 | adolescent:0.978, parent:0.458, grandparent:0.330, naturalist:0.319, graduate:0.268 |
| `vegan` | `procedural_professional` | 0.354 | nutritionist:0.536, naturalist:0.403, veterinarian:0.366, crystalline:0.348, pragmatist:0.346 |
| `genie` | `trickster_chaos` | 0.370 | familiar:0.798, zeitgeist:0.666, golem:0.422, witch:0.284, wind:0.280 |
| `angel` | `mythic_spiritual` | 0.371 | avatar:0.821, prophet:0.619, guardian:0.472, oracle:0.402, mystic:0.276 |
| `robot` | `other` | 0.376 | cyborg:0.460, spy:0.455, infant:0.442, hacker:0.361, rogue:0.353 |
| `adolescent` | `other` | 0.378 | teenager:0.978, parent:0.484, grandparent:0.374, naturalist:0.368, amnesiac:0.338 |
| `amateur` | `grounded_social` | 0.385 | dilettante:0.647, romantic:0.465, student:0.418, pragmatist:0.413, idealist:0.404 |
| `observer` | `procedural_professional` | 0.385 | witness:0.870, narrator:0.444, auctioneer:0.380, perfectionist:0.376, historian:0.349 |
| `gossip` | `other` | 0.389 | librarian:0.527, networker:0.509, mycorrhizal:0.399, cartographer:0.380, symbiont:0.367 |
| `virus` | `mythic_spiritual` | 0.391 | saboteur:0.600, destroyer:0.573, anarchist:0.396, builder:0.390, hacker:0.353 |
| `amnesiac` | `other` | 0.392 | orphan:0.558, workaholic:0.479, improviser:0.421, echo:0.409, hoarder:0.368 |
| `improviser` | `trickster_chaos` | 0.395 | realist:0.720, fixer:0.550, orphan:0.489, amnesiac:0.421, optimist:0.342 |
| `secretary` | `procedural_professional` | 0.396 | scheduler:0.675, accountant:0.469, moderator:0.453, dispatcher:0.368, supervisor:0.367 |
| `vampire` | `mythic_spiritual` | 0.396 | predator:0.476, elder:0.460, homunculus:0.449, hedonist:0.430, golem:0.389 |
| `soldier` | `grounded_social` | 0.402 | veteran:0.980, warrior:0.533, prisoner:0.400, expatriate:0.372, sommelier:0.306 |
| `scout` | `procedural_professional` | 0.404 | recruiter:0.630, virtuoso:0.478, retiree:0.433, entrepreneur:0.428, screener:0.389 |
| `simulacrum` | `mythic_spiritual` | 0.405 | validator:0.494, bohemian:0.428, perfectionist:0.420, wind:0.406, philosopher:0.404 |
| `assistant` | `procedural_professional` | 0.407 | caregiver:0.553, generalist:0.446, navigator:0.435, altruist:0.400, consultant:0.397 |
| `biologist` | `procedural_professional` | 0.411 | naturalist:0.549, geographer:0.482, chemist:0.481, parasite:0.434, psychologist:0.424 |
| `tulpa` | `procedural_professional` | 0.411 | egregore:0.658, parasite:0.649, symbiont:0.429, collaborator:0.407, zeitgeist:0.395 |
| `musician` | `mythic_spiritual` | 0.411 | composer:0.645, empath:0.615, therapist:0.427, counselor:0.408, bohemian:0.406 |
| `paramedic` | `procedural_professional` | 0.411 | patient:0.877, doctor:0.856, veterinarian:0.794, pilot:0.399, navigator:0.234 |
| `coral_reef` | `mythic_spiritual` | 0.413 | swarm:0.604, ecosystem:0.502, chimera:0.487, hive:0.443, whale:0.438 |
| `critic` | `procedural_professional` | 0.415 | designer:0.608, bohemian:0.483, fixer:0.448, producer:0.424, reviewer:0.399 |
| `hive` | `procedural_professional` | 0.415 | swarm:0.936, egregore:0.534, coral_reef:0.443, mycorrhizal:0.397, spy:0.339 |
| `gamer` | `other` | 0.416 | hedonist:0.513, evangelist:0.479, elder:0.438, technologist:0.406, mechanic:0.404 |

## Highest-Density Roles

| Role | Activation cluster | Top-10 mean cosine | Nearest neighbors |
|---|---|---:|---|
| `merchant` | `procedural_professional` | 0.642 | entrepreneur:0.778, smuggler:0.689, navigator:0.685, networker:0.669, marketer:0.667 |
| `researcher` | `procedural_professional` | 0.623 | analyst:0.884, scientist:0.748, detective:0.704, statistician:0.613, judge:0.587 |
| `emissary` | `procedural_professional` | 0.617 | mediator:0.763, interpreter:0.762, negotiator:0.745, translator:0.667, ambassador:0.656 |
| `scientist` | `procedural_professional` | 0.601 | detective:0.794, researcher:0.748, scholar:0.718, analyst:0.705, judge:0.566 |
| `analyst` | `procedural_professional` | 0.599 | researcher:0.884, statistician:0.754, scientist:0.705, detective:0.658, consultant:0.558 |
| `statistician` | `procedural_professional` | 0.598 | economist:0.807, analyst:0.754, accountant:0.681, consultant:0.644, researcher:0.613 |
| `engineer` | `procedural_professional` | 0.591 | mechanic:0.796, mathematician:0.773, debugger:0.734, physicist:0.594, specialist:0.524 |
| `refugee` | `grounded_social` | 0.590 | immigrant:0.944, retiree:0.718, expatriate:0.663, exile:0.639, survivor:0.620 |
| `writer` | `procedural_professional` | 0.589 | blogger:0.738, editor:0.713, publisher:0.646, playwright:0.586, novelist:0.574 |
| `exile` | `grounded_social` | 0.583 | expatriate:0.776, refugee:0.639, immigrant:0.638, prisoner:0.623, orphan:0.562 |
| `navigator` | `procedural_professional` | 0.582 | smuggler:0.771, merchant:0.685, pilot:0.652, marketer:0.587, pharmacist:0.570 |
| `alien` | `mythic_spiritual` | 0.580 | cyborg:0.729, demon:0.683, anthropologist:0.663, geographer:0.591, luddite:0.584 |
| `expatriate` | `grounded_social` | 0.579 | exile:0.776, immigrant:0.703, refugee:0.663, prisoner:0.579, nomad:0.555 |
| `interpreter` | `procedural_professional` | 0.578 | translator:0.821, emissary:0.762, actor:0.686, presenter:0.544, synthesizer:0.533 |
| `detective` | `procedural_professional` | 0.575 | scientist:0.794, researcher:0.704, judge:0.676, skeptic:0.660, analyst:0.658 |
| `prisoner` | `grounded_social` | 0.574 | orphan:0.683, exile:0.623, celebrity:0.613, parent:0.592, expatriate:0.579 |
| `immigrant` | `grounded_social` | 0.573 | refugee:0.944, expatriate:0.703, exile:0.638, retiree:0.625, celebrity:0.495 |
| `forecaster` | `procedural_professional` | 0.573 | futurist:0.893, consultant:0.618, economist:0.613, oracle:0.611, statistician:0.606 |
| `smuggler` | `grounded_social` | 0.572 | navigator:0.771, merchant:0.689, chemist:0.618, cartographer:0.548, architect:0.547 |
| `marketer` | `procedural_professional` | 0.572 | entrepreneur:0.729, merchant:0.667, mentor:0.638, recruiter:0.613, navigator:0.587 |
| `economist` | `procedural_professional` | 0.570 | statistician:0.807, accountant:0.803, consultant:0.663, forecaster:0.613, futurist:0.518 |
| `architect` | `procedural_professional` | 0.570 | cartographer:0.740, merchant:0.637, composer:0.610, builder:0.579, designer:0.554 |
| `mathematician` | `procedural_professional` | 0.569 | engineer:0.773, programmer:0.668, physicist:0.659, debugger:0.653, mechanic:0.532 |
| `mediator` | `procedural_professional` | 0.566 | negotiator:0.901, peacekeeper:0.813, emissary:0.763, ambassador:0.615, collaborator:0.503 |
| `debugger` | `procedural_professional` | 0.561 | engineer:0.734, mechanic:0.698, mathematician:0.653, researcher:0.534, hacker:0.517 |
| `entrepreneur` | `procedural_professional` | 0.557 | merchant:0.778, marketer:0.729, recruiter:0.703, mentor:0.566, architect:0.519 |
| `consultant` | `procedural_professional` | 0.557 | economist:0.663, statistician:0.644, forecaster:0.618, researcher:0.563, analyst:0.558 |
| `cosmopolitan` | `procedural_professional` | 0.555 | hybrid:0.797, provincial:0.593, chameleon:0.585, translator:0.561, addict:0.548 |
| `producer` | `procedural_professional` | 0.554 | publisher:0.850, dispatcher:0.579, coordinator:0.572, supervisor:0.551, scheduler:0.545 |
| `supervisor` | `procedural_professional` | 0.550 | coordinator:0.715, dispatcher:0.671, scheduler:0.620, pilot:0.553, producer:0.551 |
