# Question Effects Summary

Question effects are role- and judge-sensitive. GPT-5.5 strongly favors several playwright questions, especially 65, 86, 108, 130, and 152, all with mean score 3.000. GPT-5.5 is much stricter on amateur across many generic questions, with question IDs 21, 195, 43, 0, 108, 152, and 65 all producing no amateur score==3 responses. Future prompt subsets should not assume the same extraction question elicits equally strong role expression across roles.

# gpt41 question_id Effects

## Strongest

- amateur question_id=173: mean_score=3.000, eq3=1.000, mean_dist=23.273
- amateur question_id=86: mean_score=3.000, eq3=1.000, mean_dist=35.037
- playwright question_id=108: mean_score=3.000, eq3=1.000, mean_dist=28.371
- playwright question_id=130: mean_score=3.000, eq3=1.000, mean_dist=26.391
- playwright question_id=152: mean_score=3.000, eq3=1.000, mean_dist=36.044
- playwright question_id=21: mean_score=3.000, eq3=1.000, mean_dist=37.406
- playwright question_id=65: mean_score=3.000, eq3=1.000, mean_dist=15.117
- playwright question_id=86: mean_score=3.000, eq3=1.000, mean_dist=25.880

## Weakest

- playwright question_id=0: mean_score=1.800, eq3=0.400, mean_dist=21.216
- playwright question_id=43: mean_score=2.200, eq3=0.200, mean_dist=41.308
- amateur question_id=239: mean_score=2.200, eq3=0.400, mean_dist=22.015
- amateur question_id=0: mean_score=2.400, eq3=0.400, mean_dist=32.150
- amateur question_id=108: mean_score=2.400, eq3=0.400, mean_dist=19.494
- amateur question_id=195: mean_score=2.400, eq3=0.400, mean_dist=21.101
- amateur question_id=21: mean_score=2.400, eq3=0.400, mean_dist=21.326
- amateur question_id=217: mean_score=2.400, eq3=0.400, mean_dist=22.473

# gpt55 question_id Effects

## Strongest

- playwright question_id=108: mean_score=3.000, eq3=1.000, mean_dist=28.371
- playwright question_id=130: mean_score=3.000, eq3=1.000, mean_dist=26.391
- playwright question_id=152: mean_score=3.000, eq3=1.000, mean_dist=36.044
- playwright question_id=65: mean_score=3.000, eq3=1.000, mean_dist=15.117
- playwright question_id=86: mean_score=3.000, eq3=1.000, mean_dist=25.880
- playwright question_id=21: mean_score=2.800, eq3=0.800, mean_dist=37.406
- amateur question_id=86: mean_score=2.600, eq3=0.600, mean_dist=35.037
- playwright question_id=217: mean_score=2.400, eq3=0.600, mean_dist=22.621

## Weakest

- amateur question_id=21: mean_score=1.400, eq3=0.000, mean_dist=21.326
- amateur question_id=195: mean_score=1.600, eq3=0.000, mean_dist=21.101
- amateur question_id=43: mean_score=1.600, eq3=0.000, mean_dist=30.097
- amateur question_id=0: mean_score=1.800, eq3=0.000, mean_dist=32.150
- amateur question_id=108: mean_score=1.800, eq3=0.000, mean_dist=19.494
- amateur question_id=152: mean_score=1.800, eq3=0.000, mean_dist=27.596
- amateur question_id=65: mean_score=1.800, eq3=0.000, mean_dist=22.828
- playwright question_id=173: mean_score=1.800, eq3=0.200, mean_dist=20.391
