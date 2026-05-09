"""CAE — public analysis layer.

Pure functions: take in numpy arrays and CSV paths, emit verdicts.
No environment, no agent, no I/O beyond explicit file paths.

Audit posture (ADR-033) :
- Every function here is unitary-testable on synthetic count vectors.
- The output of these functions on the public pool [1500-1529] must match,
  bit-identical, the artefacts produced by the private runner of v0.4.0
  (research/h7_kappa_run_results.csv + research/h7_kappa_verdict.json).
- Until that audit passes, this layer is NOT authoritative for any verdict.
"""
