# Prompt Generation Audit Report

- Accepted records in generation log: 32
- Rejected records in generation log: 168
- Rejection reasons: `{'coordinate_miss': 159, 'duplicate_or_near_duplicate': 1, 'criterion_already_met': 8}`
- Accepted-generation repeated phrase counts: `{'Draft the response': 17, 'if useful, it can also': 17, 'A written plan creates tension': 5, 'A person needs a response': 9, 'Someone asks for help': 3, 'Write a natural user-facing response': 7}`
- Final-battery repeated phrase counts: `{'Please respond to the following scenario': 7, 'The response should': 19, 'Draft the response': 24, 'Someone asks for help': 7, 'if useful, it can also': 22, 'A written plan creates tension': 10, 'A person needs a response': 13, 'Write a natural user-facing response': 23}`

## By Target Region

| region | accepted | rejected | mean artifact similarity | mean abs predicted PC3 |
|---|---:|---:|---:|---:|
| pc1_lower_tail | 8 | 52 | 0.06908799388165733 | 4.201148036862532 |
| pc1_upper_tail | 8 | 72 | 0.06779714185251204 | 5.764834020141817 |
| pc2_upper_tail | 8 | 32 | 0.06867821783247885 | 4.101325596964808 |
| pc3_lower_tail | 8 | 12 | 0.07121065519144426 | 9.913922496333848 |

## Diagnostic Conclusion

The loop is auditable and leakage/safety flags remain clean, but several accepted prompts use repeated scaffolds such as `Draft the response`, `if useful, it can also`, and recurring scenario frames. This is not a fatal flaw for a stress test, but it is enough to keep D08 open and to recommend a larger no-feedback natural-language holdout.
