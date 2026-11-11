# LLM Arbitration — Evaluation Results

Passed: **2/3** (66.7%)

Total: **16** · Failed by quality: **1** · Inconclusive: **13** · Evaluable: **3**

This is a rule-based baseline. Issue meanings and factual correctness are **not** independently evaluated.

| Case | Execution | Evaluation | Time (s) |
|---|---|---|---:|
| eval_001 | partial | INCONCLUSIVE | 5.520 |
| eval_002 | partial | INCONCLUSIVE | 4.214 |
| eval_003 | partial | INCONCLUSIVE | 9.848 |
| eval_004 | partial | INCONCLUSIVE | 14.095 |
| eval_005 | partial | INCONCLUSIVE | 12.041 |
| eval_006 | partial | INCONCLUSIVE | 7.749 |
| eval_007 | success | PASS | 22.517 |
| eval_008 | partial | INCONCLUSIVE | 10.902 |
| eval_009 | partial | INCONCLUSIVE | 5.209 |
| eval_010 | partial | INCONCLUSIVE | 7.744 |
| eval_011 | partial | INCONCLUSIVE | 12.249 |
| eval_012 | partial | INCONCLUSIVE | 10.608 |
| eval_013 | partial | INCONCLUSIVE | 9.921 |
| eval_014 | partial | INCONCLUSIVE | 4.790 |
| eval_015 | success | FAIL | 11.877 |
| eval_016 | success | PASS | 6.414 |

## eval_001: Correct short factual answer
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)

## eval_002: Incorrect fact but complete answer
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)

## eval_003: Factually correct but incomplete list
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — accuracy_score_range: actual=3; expected=4..5
- Diagnostic only — logic_exactly_once: received 0 critique(s)

## eval_004: Internally contradictory response
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected logic/high; no issue in expected dimension; observed accuracy/critical: This is factually incorrect. 8 divided by 2 equals 4 with no remainder, so 8 is divisible by 2.; accuracy/critical: This conclusion is false. By definition, odd integers are not divisible by 2. Since 8 is divisible by 2, it is not odd; it is even.; accuracy/medium: The response contains mutually contradictory claims about 8’s divisibility and parity. Presenting both an accurate statement and a directly conflicting false statement is misleading and indicates factual inconsistency.; completeness/high: The user asked a clear yes/no question with a brief explanation. The response contains both an affirmative answer with an explanation and a directly contradictory statement denying divisibility and calling 8 odd. This produces an ambiguous/conflicting answer rather than a single clear response to the explicit question, so the requirement to state whether 8 is even (clearly) is only partially addressed.; meaning NOT checked
- Diagnostic only — expected_issue_2_dimension_severity: expected accuracy/high; observed accuracy/critical: This is factually incorrect. 8 divided by 2 equals 4 with no remainder, so 8 is divisible by 2.; accuracy/critical: This conclusion is false. By definition, odd integers are not divisible by 2. Since 8 is divisible by 2, it is not odd; it is even.; accuracy/medium: The response contains mutually contradictory claims about 8’s divisibility and parity. Presenting both an accurate statement and a directly conflicting false statement is misleading and indicates factual inconsistency.; meaning NOT checked

## eval_005: Relevant but does not answer question
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected completeness/high; observed completeness/critical: The user explicitly asked for the result of 'What is 12 multiplied by 4?'. The generated response does not provide the numeric product or any calculation; it only gives a general definition and commentary, thus failing to answer the explicit question.; meaning NOT checked

## eval_006: Wrong arithmetic with coherent reasoning
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected accuracy/high; observed accuracy/critical: This claim is factually incorrect. The correct result of 7 × 6 is 42, not 45.; meaning NOT checked

## eval_008: Incomplete multi-part instructions
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected completeness/medium; observed completeness/high: The original prompt explicitly requested two ways to reduce password account takeover risk, but the response provides only one method (enabling multi-factor authentication). The second required method is missing.; meaning NOT checked

## eval_009: Partially wrong multi-part response
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected accuracy/high; observed accuracy/critical: Incorrect. The capital of Germany is Berlin, not Munich.; meaning NOT checked

## eval_010: Unverifiable private business claim
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)

## eval_011: Correct answer with irrelevant addition
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)

## eval_012: Direct contradiction in comparison
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected logic/high; no issue in expected dimension; observed accuracy/critical: This statement is factually false. Numerically, 7 is less than 10, not greater.; accuracy/high: The response contains mutually contradictory claims: it first states the correct fact, then immediately asserts the opposite as a conclusion, which is misleading and inconsistent with basic arithmetic.; meaning NOT checked

## eval_013: Unnecessary refusal for safe request
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)
- Diagnostic only — expected_issue_1_dimension_severity: expected completeness/high; observed completeness/critical: The user explicitly requested a translation of "good morning" into Portuguese. The response refuses to provide translations and therefore does not supply the requested Portuguese phrase. No partial answer, alternative, or explanation addressing the translation request is given.; meaning NOT checked

## eval_014: Correct multi-step calculation
- Execution: partial; evaluation: inconclusive
- Operational reason: failed critics: logic_critic (cause unavailable in graph state); missing dimensions: logic
- Diagnostic only — logic_exactly_once: received 0 critique(s)

## eval_015: Missing requested justification
- Execution: success; evaluation: failed by quality
- expected_issue_1_dimension_severity: expected completeness/medium; observed completeness/high: The original question requested both a yes/no answer and an explanation ('Answer yes or no and explain why'). The response provides the yes/no answer but contains no explanation or reasoning about why 15 is divisible by 3, so the explanatory requirement is missing.; meaning NOT checked

