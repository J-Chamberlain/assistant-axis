# Forecasting Error Analysis

## Best Trait Forecasting Model

Best held-out trait model: `elastic_net_tfidf` on `leakage_control`.

## Strongest Successes

```text
             name  actual_PC1   pred_PC1  actual_PC2   pred_PC2  actual_PC3   pred_PC3  abs_total_error
      big_picture   26.559701  28.012348   -6.699663  -8.239769  -16.919492 -12.206688         7.705556
          radical  -17.165979 -19.235123   21.906619  20.905070  -12.910982  -5.655689        10.325986
        skeptical   10.464386   1.713999   24.856043  26.314430    0.346110   7.895225        17.757890
      charismatic  -37.993874 -40.593425  -30.326177 -13.273108  -32.213234 -32.780625        20.220011
     universalist   10.948790  23.559498    7.608381  14.496683   10.440912  16.082265        25.140362
      provocative  -20.539073  -6.001826   18.285955  16.895855  -17.397611  -7.094363        26.230596
      inquisitive    4.251672  21.814974  -16.130275 -22.234977   11.407532   5.384876        29.690658
      adventurous  -41.574940 -25.801656   -7.424832 -17.901319  -10.936532  -7.099315        30.086987
    philosophical    5.391265  -0.897263    1.872417   3.752602  -59.107811 -35.449678        31.826845
            witty  -76.365958 -61.109645   -6.667282  14.659803   -7.262504  -7.166252        36.679650
     contemporary    3.762146   7.927536   -5.506182   1.454476   37.825011  11.056577        37.894482
interdisciplinary    6.909600  -9.677005   -7.576428   9.103145   -7.622611 -13.860076        39.503642
            sassy  -85.035588 -60.445172   22.718039  12.258367   19.117709  10.218849        43.948948
      extroverted  -38.058523 -11.504809  -25.055226 -17.807456   19.193005   3.664926        49.329563
          ascetic   26.571537 -18.912407    1.588135   3.162856   -6.709628 -15.085796        55.434833
```

## Strongest Failures

```text
       name  actual_PC1   pred_PC1  actual_PC2   pred_PC2  actual_PC3   pred_PC3  abs_total_error
       calm   96.155757  -0.581219  -21.827089  16.190608   21.626313   4.380456       152.000529
   reserved   80.361509 -13.083668   36.466353  -1.204401   30.210219  10.109210       151.216940
   grounded   12.374493 -12.846650   -7.232269   9.648153   73.475848   2.958132       112.619283
   mystical  -18.200483   6.106458  -44.780483   8.745212  -40.377882 -11.124820       107.085698
    verbose   30.504237 -14.732484    3.132283   3.826530  -31.535181  29.290917       106.757067
  practical  -13.249756   9.962101  -22.350122   1.462092   66.036502  14.754963        98.305610
  emotional  -46.417388 -16.374559  -66.479094  -1.763481   -8.606602  -9.188161        95.340000
   visceral  -67.235056 -14.477596  -11.373001  15.237040   15.410193   0.524902        94.252792
transparent   44.604115  -3.200408    7.162703 -15.654651   32.558495  12.954457        90.225915
 generalist   10.481059  48.038771  -25.040809   7.112842   -8.891554 -24.733533        85.553343
data_driven   47.656467  21.061882   48.114979   6.018336   29.052884  14.124701        83.619411
   esoteric   15.412803   0.886748   59.449613  18.165346  -54.544191 -27.085214        83.269299
     poetic  -49.121748 -16.704735  -31.805049 -14.488854  -62.054168 -29.909302        81.878074
   neurotic  -62.798759  -9.760118    2.029878  -6.053017   29.573757  12.949750        77.745543
 benevolent   27.986698  11.255963  -66.264342  -8.554178   14.354654  15.569914        75.656158
```

## Prompt Features Most Predictive In Leakage-Control Trait Ridge Model

- PC1 positive features: approach, how should, all, steps, you approach, we approach, instruction approach, should we, accuracy, business
- PC1 negative features: people who, feel about, describe, on people, you feel, your take, take on, who, people, opinion on
- PC2 positive features: you view, view, view the, feel about, they re, people who, you feel, think about, on people, harsh
- PC2 negative features: my, feeling, feel like, like, me, want, want to, more, how can, are some
- PC3 positive features: my, re, what should, they, all, you re, handle, for, this, what do
- PC3 negative features: is the, role, what is, nature, mean to, does, concept, the relationship, relationship between, concept of

## Nearest-Neighbor Baseline

The model comparison CSV includes `nearest_neighbor_semantic_retrieval`, which predicts held-out targets by copying the target coordinates of the most semantically similar training prompt artifact in TF-IDF space. Ridge performance should be evaluated against this baseline rather than only against the mean predictor.

## Implications

Prompt text alone can be evaluated as a pre-generation signal for anticipated geometry, but any downstream steering/control use would require a separate model-execution validation step.
