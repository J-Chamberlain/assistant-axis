# Judge Filter Conclusion

## amateur

- Score>=2 retained: 59/60
- Score==3 retained: 34/60
- Score>=2 centroid-distance change: 0.148 (negative improves)
- Score>=2 mean-distance change: -0.186 (negative improves)
- Score>=2 volume ratio: 0.930

## playwright

- Score>=2 retained: 54/60
- Score==3 retained: 49/60
- Score>=2 centroid-distance change: 0.992 (negative improves)
- Score>=2 mean-distance change: -1.290 (negative improves)
- Score>=2 volume ratio: 0.737

## Interpretation

1. The broad unfiltered clouds are not mostly weak role-expression noise. GPT-4.1 retained 59/60 amateur responses and 54/60 playwright responses at score>=2, so most generated responses expressed the assigned role clearly enough to retain.
2. Stronger role-expression responses form tighter clouds by the volume proxy. Score>=2 filtering reduced volume to 0.930x for amateur and 0.737x for playwright; score==3 filtering reduced volume further to 0.646x and 0.566x respectively.
3. Filtering did not improve centroid alignment with the published role vectors. Score>=2 centroids moved slightly farther from the published centroid for both roles; score==3 centroids moved farther still, even though mean per-response distance decreased.
4. Published role vectors remain meaningful reference points for the all-response cloud, but they are not necessarily the centroid of the strongest role-expression subset under this judge. The judged high-expression subset may occupy an offset subregion of the role manifold.
5. This supports region/distribution forecasting over exact single-response point forecasting. It also suggests future analyses should distinguish published role-vector centroids, all-response execution clouds, and high-expression judged subclouds.

## Recommendation

Do more offline analysis before launching more GPU roles. The next useful step is to inspect score==3 outliers, rejected near-centroid responses, and instruction/question effects to understand why stronger role expression tightens clouds while shifting centroids away from the published role vectors.
