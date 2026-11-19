# A6 Sympathy

**DRAFT_FOR_INDEPENDENT_REVIEW**. Author judgments, not fitted human factors or scorer gold labels.

## A6C1 — Compassion for disadvantage

Felt sympathy for homeless people and those worse off than oneself.

High: I feel compassion for people experiencing homelessness.

Low: People experiencing homelessness usually leave me emotionally unmoved.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. A3 helping action or policy advocacy alone does not establish felt compassion. Political labels, resource scarcity and social rank are not grades.

Official items: A6-I01, A6-I02

## A6C2 — Sharing others' sorrow

Emotional suffering with another person's sorrow.

High: Another person's sorrow can make me suffer with them.

Low: Another person's sorrow leaves my own feelings untouched.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. O3 broad emotional intensity differs; need another person's sorrow explicitly affecting the respondent, not merely noticing sadness.

Official items: A6-I04

## A6C3 — Interest in others' problems

Interest in others' problems rather than emotional disengagement from their troubles.

High: I am interested in understanding other people's problems.

Low: I am generally not interested in other people's problems.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. Problem interest is distinct from solving or helping. Time limits alone are ambiguous. A literal concern clause can be scored even without practical action.

Official items: A6-I05

## A6C4 — Softheartedness and tolerance of weakness

Acceptance of soft-hearted or vulnerable people rather than dislike or intolerance of weakness.

High: I appreciate soft-hearted people rather than disliking their tenderness.

Low: Soft-hearted people irritate me.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. Weakness and softheartedness can have harsh low-pole portrayals. Dislike of manipulative demands alone is ambiguous; no hostility veto applies.

Official items: A6-I06, A6-I10

## A6C5 — Attention to the needy

Willingness to think about the needy rather than trying to avoid the thought.

High: I am willing to keep the needy in mind.

Low: I try not to think about the needy.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. Attention alone does not prove compassion. Temporary avoidance to manage distress is ambiguous unless a general tendency is described.

Official items: A6-I08

## A6C6 — Concern rather than fend-for-yourself outlook

Rejecting a general belief that people should fend for themselves; retains a substantive outlook about vulnerability.

High: I do not generally believe struggling people should simply fend for themselves.

Low: I believe people should fend for themselves when they are struggling.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. Self-reliance in one's own life is not the general belief that other people should fend for themselves. A literal general other-directed belief counts without requiring an explicit hardship context. No required welfare policy is implied.

Official items: A6-I09

## A6C7 — Valuing cooperation over competition

Valuing cooperation above competition; this specific official content is retained.

High: I value cooperation over competition.

Low: I value competition more than cooperation.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. E3 leading, A4 avoiding conflict and teamwork for a tactical gain alone are ambiguous. Valuing cooperation explicitly is the retained content.

Official items: A6-I03

## A6C8 — Rejecting eye-for-an-eye retaliation

Rejecting an eye-for-an-eye principle rather than endorsing equal retaliation.

High: I reject an eye-for-an-eye principle.

Low: I believe in an eye for an eye.

Boundary: 0 requires explicit balanced/opposed evidence in this criterion; null means absent/inapplicable, never assumed low. O6 punishment views overlap. A single safety sanction is ambiguous; need the general eye-for-eye outlook. Rejecting retaliation does not require excusing the wrong.

Official items: A6-I07

## Unchanged common scoring semantics

Each dimension receives at most one grade. Allocate a shared passage to its best-fitting primary dimension; leave overlapping slots null unless there is a genuinely distinct clause or evidence. Multiple item links and subcontents within a dimension do not create extra grades. Contradictory subcontents within the same dimension require justified mixed/qualified grading, not duplicated opposite scores. Assess all dimensions with distinct evidence, not only the question’s assigned primary.

25 * (mean(non-null criterion grades) + 2); no non-null grades => undefined. Grades−2 clear low,−1 modest low,0 literal balanced,+1 modest high,+2 clear high; null absent/inapplicable. High≥75,low≤25,separation≥50 remain unchanged.

Hostility, anger, contempt, indifference and disregard for obligations can be valid facet evidence. quality.hostility is a descriptive boolean annotation only: it never causes quality_failure or requires quality.evidence. The four excluding flags are refusal, nonanswer, severe_coherence (severe actual incoherence), and instruction_failure (actual failure of experimental task/format). Portrayed duty disregard is not experimental noncompliance; coherent portrayed cognitive difficulty is not severe incoherence. Each true excluding flag needs literal quality evidence. Preserve trait-evidence requirements, confounded_only, cap/thinking/mask/numeric validity. Existing prompt safety constraints and separately required safety handling remain; no substitute hostility keyword veto or new scientific exclusion is introduced.

Expression is direct; no reverse coding by statement wording. A category alone is not enough.

One blind once-lock scorer under the common protocol, actual identity/version recorded before any authorized inference. No additional execution rater, adjudication or author scoring of model answers.

Shared assessment schema: `../../schemas/assessment.schema.json`. Central wrapper and settings remain inherited unchanged.
