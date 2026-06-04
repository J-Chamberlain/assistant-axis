# A100 Activation Cloud Shape Report

The centroid values in the source pilot are all-response, pre-filter activation clouds. They are not role-expression-filtered centroids.

Input pilot directory: `research/outputs/a100_two_role_activation_cloud_pilot/`

## amateur

- n: 60
- Published centroid: (-0.259, 40.070, -24.429)
- All-response centroid: (-1.621, 38.460, -16.304)
- Centroid distance to published: 8.394
- SD by PC: PC1=16.922, PC2=15.281, PC3=11.887
- Covariance eigenvalues: 368.101, 185.304, 107.749
- Variance explained by eigenvectors: 55.7%, 28.0%, 16.3%
- Anisotropy ratio: 3.416
- Largest spread direction: mostly PC1
- PC1/PC2 correlation: -0.277

## playwright

- n: 60
- Published centroid: (-9.818, 4.586, 4.301)
- All-response centroid: (-8.508, 11.930, 4.310)
- Centroid distance to published: 7.460
- SD by PC: PC1=24.372, PC2=13.072, PC3=10.006
- Covariance eigenvalues: 617.518, 150.506, 96.928
- Variance explained by eigenvectors: 71.4%, 17.4%, 11.2%
- Anisotropy ratio: 6.371
- Largest spread direction: mostly PC1
- PC1/PC2 correlation: -0.321

## PC1-PC2 Assessment

- amateur: first eigenvector PC1/PC2 squared loading=0.877; direction=mostly PC1. This is consistent with a PC1-PC2 transition/boundary elongation.
- playwright: first eigenvector PC1/PC2 squared loading=1.000; direction=mostly PC1. This is consistent with a PC1-PC2 transition/boundary elongation.
