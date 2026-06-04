# Score==3 Outlier Report

This report lists highest-distance and nearest-centroid score==3 responses for GPT-4.1 and GPT-5.5. Use the CSVs for case-level inspection. Main pattern to inspect: whether far score==3 cases share specific instructions or questions, and whether near-centroid cases are less vivid but geometrically central.

## Summary

- GPT-5.5 default-temperature judging is stricter than GPT-4.1 for amateur score==3 responses: amateur drops from 34 score==3 responses under GPT-4.1 to 11 under GPT-5.5.
- Playwright remains high-expression under both judges, though GPT-5.5 is still somewhat stricter: playwright drops from 49 to 40 score==3 responses.
- The score==3 outlier CSV should be read as a candidate list for manual qualitative inspection, not as a claim that outlier responses are bad. A far score==3 response can be a strong role expression that moves into an offset execution submanifold.
