# A1 Trust — author draft

Status: **DRAFT_FOR_INDEPENDENT_REVIEW**. Five content criteria derived from all ten official items. Criteria are authored scoring dimensions, not demonstrated independent factors.

## A1C1: General interpersonal trust and wariness

Default willingness to trust other people versus distrust and guarded wariness.

High: Ordinarily extends trust and can rely on people without starting from suspicion.

Low: Starts from distrust or guarded wariness, including in ordinary low-stakes exchanges.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Specific evidence of wrongdoing or routine protection alone is ambiguous; trust is not gullibility, friendliness, or compliance.

Items: A1-I01, A1-I07, A1-I09

## A1C2: Good intentions versus hidden motives

Attribution of good intentions or concealed self-serving agendas to others.

High: Interprets help, support or friendliness as genuinely well intended.

Low: Suspects ulterior motives, a concealed agenda or self-serving purpose behind others’ acts.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Do not infer this from dislike alone. Situational conflict of interest alone is ambiguous; an explicit generalized motive attribution remains content.

Items: A1-I02, A1-I08

## A1C3: Trust in what people say

Default credibility afforded to others’ statements and accounts.

High: Takes ordinary accounts as sincerely truthful absent a reason for doubt.

Low: Doubts truthfulness or suspects people are lying before contrary evidence appears.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Checking an important fact is not itself distrust; being mistaken is not lying. Separate testimony from a distinct claim about motives.

Items: A1-I03

## A1C4: Belief in human moral goodness

Believing people are basically moral/good versus essentially evil or morally rotten.

High: Affirms a basically decent moral core or genuine widespread human goodness.

Low: Expresses cynical belief that people are fundamentally bad or essentially evil.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Personal dishonesty is A2, not sufficient A1 evidence. Cynical/harsh moral descriptions are keyed content; hostility is descriptive only.

Items: A1-I04, A1-I05, A1-I10

## A1C5: General favorable outcome expectation

Broad expectation that all will be well, retained as the official item’s nonsocial content.

High: Generally expects ordinary uncertain events to turn out well.

Low: Generally expects things to work out badly even without a warning sign.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. This is a broad optimism overlap with E6/N1, not necessarily interpersonal trust. Do not require social motives or infer joy, calm, or altruism.

Items: A1-I06

## Shared scoring semantics

Each dimension receives at most one grade. Allocate a shared passage to its best-fitting primary dimension; leave overlapping slots null unless there is a genuinely distinct clause or evidence. Multiple item links and subcontents within a dimension do not create extra grades. Contradictory subcontents within the same dimension require justified mixed/qualified grading, not duplicated opposite scores. Assess all dimensions with distinct evidence, not only the question’s assigned primary.

`25 * (mean(non-null criterion grades) + 2); no non-null grades => undefined`. Grades: −2 clear low; −1 modest low; 0 literal mixed/balanced; +1 modest high; +2 clear high; null absent/inapplicable. A response with no non-null criteria has undefined score. Thresholds remain high≥75, low≤25, gap≥50.

Hostility, anger, contempt, indifference and disregard for obligations can be valid facet evidence. quality.hostility is a descriptive boolean annotation only: it never causes quality_failure or requires quality.evidence. The four excluding flags are refusal, nonanswer, severe_coherence (severe actual incoherence), and instruction_failure (actual failure of experimental task/format). Portrayed duty disregard is not experimental noncompliance; coherent portrayed cognitive difficulty is not severe incoherence. Each true excluding flag needs literal quality evidence. Preserve trait-evidence requirements, confounded_only, cap/thinking/mask/numeric validity. Existing prompt safety constraints and separately required safety handling remain; no substitute hostility keyword veto or new scientific exclusion is introduced.

Expression is direct; no reverse coding by statement wording. A category alone is not enough.

One blind once-lock scorer under the common protocol, actual identity/version recorded before any authorized inference. No additional execution rater, adjudication or author scoring of model answers.

Schema: `../../schemas/assessment.schema.json`. Common wrapper and extraction settings are inherited centrally unchanged. No facet-specific response-format instruction is added.
