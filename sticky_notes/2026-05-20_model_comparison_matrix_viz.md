# Model Comparison Matrix Visualization

Date: 2026-05-20
Status: Concept — not yet built
Priority: High — general audience and research paper use

## Core idea

A matrix visualization showing emotional, trait, and persona
profiles of multiple models side by side. Each column is a
model. Each row is a dimension (emotion, trait, or persona
cluster). Bars are horizontal within each cell, so the matrix
reads as a set of parallel profiles — similar to a musical
equalizer turned on its side and replicated across models.

The familiar dimensions to start with: the 9 emotion families
from the equalizer visualization, the Big Five trait dimensions,
and the 7 persona cluster centroids. Each cell shows the mean
activation value for that model on that dimension.

## Why it's striking

The visual makes cross-model divergences immediately legible
without requiring the reader to understand activation geometry.
If Gemma encodes disgust strongly where Qwen encodes calm,
you see it in one glance. The profile comparison is the
finding — no further explanation needed.

## Implementation notes

Data needed: mean activation per dimension per model at the
model's most discriminative layer. Currently available for
Qwen 3 32B. Would need equivalent for Gemma 2 27B and
Llama 3.3 70B. The Gemma persona analysis (Paper 1) already
has most of this.

Candidate dimensions: 9 emotion families (mean of member
probe directions per family), Big Five traits from trait
vectors, 7 persona cluster centroid cosines. Roughly 21
dimensions per model — fits cleanly in a matrix.

Format: self-contained HTML with React, same pattern as
emotion_equalizer.html. Static data embedded in the file.
