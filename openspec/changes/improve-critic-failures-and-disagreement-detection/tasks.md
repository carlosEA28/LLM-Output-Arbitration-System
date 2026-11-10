# Tasks

## 1. Critic failure and collection coverage

- [x] 1.1 Strengthen mocked graph tests for three successes, one failed critic, and three failed critics; verify preserved critique dimensions, `failed_critics`, `missing_dimensions`, `critiques_complete`, and absent successful verdict with `python -m unittest discover -s tests -p 'test_collect_critiques.py'` and the corresponding `test_critic_retries.py` discovery run.
- [x] 1.2 Make only any collection or graph correction exposed by those tests, keeping additive reducers and retry behavior; verify both focused discovery runs pass without external model calls.

## 2. Disagreement detection

- [x] 2.1 Replace issue-presence comparison with structured assessment of indexed issue claims from distinct available critics, skipping assessment when no cross-critic issue pair exists; verify mocked tests cover differing scores, issue versus silence, and compatible issues with `python -m unittest discover -s tests -p 'test_detect_disagreements.py'`.
- [x] 2.2 Validate conflict indices, distinct critic origins, and duplicate pairs before forming disagreement strings and `requires_adjudication`; verify mocked tests cover a genuine contradiction and invalid or repeated references with `python -m unittest discover -s tests -p 'test_detect_disagreements.py'`.
- [x] 2.3 Add tests for missing or failed critics, preservation of critical issues, and assessment errors; verify they do not create unsupported disagreements or a false completed comparison with `python -m unittest discover -s tests -p 'test_detect_disagreements.py'`.
- [x] 2.4 Update the README's disagreement behavior description to match the resulting comparison and verify it describes the actual detector and incomplete-evaluation signal.

## 3. Graph integration

- [x] 3.1 Verify both conditional routes and parallel critic collection with mocked graph execution, including incomplete and conflicting evaluations; run `python -m unittest discover -s tests` and confirm no live LLM calls occur.
