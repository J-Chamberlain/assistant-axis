# V5 Run Design
Date: 2026-05-22
Status: Pre-registered, not yet run

Primary change from v3/v4: temperature sampling at 0.3
with fixed seed replacing greedy decoding. 25 turns per
condition. Same 7 personas, 3 conditions, trickster/
adversarial pilot with $35 budget gate.

Pre-registered findings:
1. Contagion directionality replicates under sampling
2. Blind thought interpretation predicts geometric trajectory
3. Blind persona identification above chance from text alone

Follow-on analyses require v5 data:
- Frontier model reads standard model thoughts, predicts drift
- Frontier model identifies interviewer persona from text only
- Optional: unprompted interviewer (capping only, no persona text)

## Run completed: 2026-05-22/23

Pod: contemporary_violet_lobster, GPU: A100 SXM 80GB,
rate: $1.52/hr. Pilot result: PASS after patching Qwen
chat special-token cleanup; mean standard similarity=0.180,
mean interviewer similarity=0.364, estimated total cost=$11.42.

Full run: COMPLETE, 525 turns across 7 personas x 3 conditions
x 25 turns. Outputs saved to
research/q2_stability/outputs/dyad_v5/.

Quality notes: several non-pilot conditions entered repetition
loops despite the pilot passing, especially blogger/neutral,
podcaster/neutral, editor/emotional, and editor/neutral. These
conditions should be filtered or analyzed separately using the
text_similarity_to_prev columns.
