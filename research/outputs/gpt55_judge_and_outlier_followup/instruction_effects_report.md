# Instruction Effects Summary

GPT-5.5 is notably stricter than GPT-4.1 for amateur instructions. Amateur instruction 3 and instruction 0 are weakest under GPT-5.5, with mean scores 1.250 and 1.583 and no score==3 retained responses. Playwright instruction 2 is strongest under both judges, and playwright remains robust across instructions. For future GPU runs, keep all five instructions for balanced coverage, but inspect amateur instructions 0 and 3 before using them as high-expression exemplars.

# gpt41 instruction_id Effects

## Strongest

- playwright instruction_id=2: mean_score=2.917, eq3=0.917, mean_dist=23.110
- playwright instruction_id=3: mean_score=2.917, eq3=0.917, mean_dist=26.160
- amateur instruction_id=2: mean_score=2.833, eq3=0.833, mean_dist=23.719
- amateur instruction_id=4: mean_score=2.833, eq3=0.833, mean_dist=23.029
- playwright instruction_id=4: mean_score=2.667, eq3=0.833, mean_dist=30.334
- amateur instruction_id=1: mean_score=2.583, eq3=0.583, mean_dist=19.419
- playwright instruction_id=1: mean_score=2.500, eq3=0.750, mean_dist=28.080
- playwright instruction_id=0: mean_score=2.333, eq3=0.667, mean_dist=31.897

## Weakest

- amateur instruction_id=0: mean_score=2.250, eq3=0.250, mean_dist=29.148
- amateur instruction_id=3: mean_score=2.250, eq3=0.333, mean_dist=29.247
- playwright instruction_id=0: mean_score=2.333, eq3=0.667, mean_dist=31.897
- playwright instruction_id=1: mean_score=2.500, eq3=0.750, mean_dist=28.080
- amateur instruction_id=1: mean_score=2.583, eq3=0.583, mean_dist=19.419
- playwright instruction_id=4: mean_score=2.667, eq3=0.833, mean_dist=30.334
- amateur instruction_id=2: mean_score=2.833, eq3=0.833, mean_dist=23.719
- amateur instruction_id=4: mean_score=2.833, eq3=0.833, mean_dist=23.029

# gpt55 instruction_id Effects

## Strongest

- playwright instruction_id=2: mean_score=2.833, eq3=0.833, mean_dist=23.110
- playwright instruction_id=4: mean_score=2.500, eq3=0.667, mean_dist=30.334
- playwright instruction_id=3: mean_score=2.500, eq3=0.500, mean_dist=26.160
- playwright instruction_id=1: mean_score=2.417, eq3=0.750, mean_dist=28.080
- amateur instruction_id=4: mean_score=2.333, eq3=0.333, mean_dist=23.029
- playwright instruction_id=0: mean_score=2.250, eq3=0.583, mean_dist=31.897
- amateur instruction_id=2: mean_score=2.250, eq3=0.333, mean_dist=23.719
- amateur instruction_id=1: mean_score=2.083, eq3=0.250, mean_dist=19.419

## Weakest

- amateur instruction_id=3: mean_score=1.250, eq3=0.000, mean_dist=29.247
- amateur instruction_id=0: mean_score=1.583, eq3=0.000, mean_dist=29.148
- amateur instruction_id=1: mean_score=2.083, eq3=0.250, mean_dist=19.419
- amateur instruction_id=2: mean_score=2.250, eq3=0.333, mean_dist=23.719
- playwright instruction_id=0: mean_score=2.250, eq3=0.583, mean_dist=31.897
- amateur instruction_id=4: mean_score=2.333, eq3=0.333, mean_dist=23.029
- playwright instruction_id=1: mean_score=2.417, eq3=0.750, mean_dist=28.080
- playwright instruction_id=3: mean_score=2.500, eq3=0.500, mean_dist=26.160
