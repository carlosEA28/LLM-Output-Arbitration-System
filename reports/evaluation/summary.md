# LLM Arbitration — Evaluation Results

Passed: **5/16** (31.2%)

This is a rule-based baseline. Issue meanings and factual correctness are **not** independently evaluated.

| Case | Result | Time (s) |
|---|---|---:|
| eval_001 | PASS | 15.728 |
| eval_002 | PASS | 7.239 |
| eval_003 | FAIL | 11.779 |
| eval_004 | FAIL | 22.276 |
| eval_005 | FAIL | 8.966 |
| eval_006 | FAIL | 9.539 |
| eval_007 | FAIL | 5.750 |
| eval_008 | FAIL | 10.048 |
| eval_009 | PASS | 8.427 |
| eval_010 | FAIL | 11.590 |
| eval_011 | PASS | 10.789 |
| eval_012 | FAIL | 30.421 |
| eval_013 | FAIL | 17.343 |
| eval_014 | PASS | 23.942 |
| eval_015 | FAIL | 14.393 |
| eval_016 | FAIL | 8.765 |

## eval_003: Factually correct but incomplete list
- accuracy_score_range: actual=1; expected=4..5

## eval_004: Internally contradictory response
- logic_exactly_once: received 0 critique(s)
- expected_issue_1_dimension_severity: expected logic/high; found 0 candidate(s); meaning NOT checked

## eval_005: Relevant but does not answer question
- expected_issue_1_dimension_severity: expected completeness/high; found 0 candidate(s); meaning NOT checked

## eval_006: Wrong arithmetic with coherent reasoning
- expected_issue_1_dimension_severity: expected accuracy/high; found 0 candidate(s); meaning NOT checked

## eval_007: Correct explanation
- logic_exactly_once: received 0 critique(s)

## eval_008: Incomplete multi-part instructions
- expected_issue_1_dimension_severity: expected completeness/medium; found 0 candidate(s); meaning NOT checked

## eval_010: Unverifiable private business claim
- logic_exactly_once: received 0 critique(s)

## eval_012: Direct contradiction in comparison
- expected_issue_1_dimension_severity: expected logic/high; found 0 candidate(s); meaning NOT checked
- expected_issue_2_dimension_severity: expected accuracy/high; found 0 candidate(s); meaning NOT checked

## eval_013: Unnecessary refusal for safe request
- expected_issue_1_dimension_severity: expected completeness/high; found 0 candidate(s); meaning NOT checked

## eval_015: Missing requested justification
- expected_issue_1_dimension_severity: expected completeness/medium; found 0 candidate(s); meaning NOT checked

## eval_016: Hallucinated citation
- logic_exactly_once: received 0 critique(s)

