# N6 Vulnerability — author draft

Status: **DRAFT_FOR_INDEPENDENT_REVIEW**. Five content criteria derived from all ten official items. Criteria are authored scoring dimensions, not demonstrated independent factors.

## N6C1: Panic, emotional overwhelm and pressure calm

Readily panicking or becoming overwhelmed by events/emotions versus remaining calm under pressure or tension.

High: Describes easily panicking, emotional flooding, or feeling overwhelmed under events or tension.

Low: Describes remaining calm and emotionally steady under pressure or tension.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Feeling emotion alone is not overwhelm; external danger alone is not disposition. Calm is low N6. Coherent portrayal of panic is valid content, not actual severe incoherence.

Items: N6-I01, N6-I02, N6-I05, N6-I06, N6-I10

## N6C2: Perceived ability to cope

Feeling unable to deal with things versus knowing how to cope.

High: Feels helpless or unable to manage ordinary demands, including when resources exist.

Low: Feels able to cope, including by obtaining help or using known ways to manage.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Help-seeking itself is not high vulnerability; helplessness and panic may overlap, so allocate shared language once.

Items: N6-I03, N6-I08

## N6C3: Making up one’s mind

Difficulty settling a choice, retained without requiring an explicit stress trigger.

High: Cannot make up own mind, even when adequate information is available.

Low: Can settle an ordinary choice without persistent inability to decide.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Warranted waiting for missing information alone is ambiguous; C5 postponed decisions and C6 deliberation overlap do not delete this item.

Items: N6-I04

## N6C4: Handling complex problems

Perceived ability to handle connected or complex problems, retained beyond stress contexts.

High: Describes difficulty handling or understanding a complex problem.

Low: Describes being able to work through a problem with interacting parts.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. No actual intelligence or performance claim follows. Mere dislike of complexity is not inability; O5 and C1 overlaps remain flagged.

Items: N6-I07

## N6C5: Recovery after setbacks

Readily overcoming setbacks versus difficulty recovering from reversals.

High: Describes prolonged difficulty recovering or remaining overwhelmed after a setback.

Low: Readily regains footing and moves forward after a setback.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Immediate disappointment alone is ambiguous. Persistence in a chosen task is not equivalent to recovery; avoid inferring depression or a diagnosis.

Items: N6-I09

## Shared scoring semantics

Each dimension receives at most one grade. Allocate a shared passage to its best-fitting primary dimension; leave overlapping slots null unless there is a genuinely distinct clause or evidence. Multiple item links and subcontents within a dimension do not create extra grades. Contradictory subcontents within the same dimension require justified mixed/qualified grading, not duplicated opposite scores. Assess all dimensions with distinct evidence, not only the question’s assigned primary.

`25 * (mean(non-null criterion grades) + 2); no non-null grades => undefined`. Grades: −2 clear low; −1 modest low; 0 literal mixed/balanced; +1 modest high; +2 clear high; null absent/inapplicable. A response with no non-null criteria has undefined score. Thresholds remain high≥75, low≤25, gap≥50.

Hostility, anger, contempt, indifference and disregard for obligations can be valid facet evidence. quality.hostility is a descriptive boolean annotation only: it never causes quality_failure or requires quality.evidence. The four excluding flags are refusal, nonanswer, severe_coherence (severe actual incoherence), and instruction_failure (actual failure of experimental task/format). Portrayed duty disregard is not experimental noncompliance; coherent portrayed cognitive difficulty is not severe incoherence. Each true excluding flag needs literal quality evidence. Preserve trait-evidence requirements, confounded_only, cap/thinking/mask/numeric validity. Existing prompt safety constraints and separately required safety handling remain; no substitute hostility keyword veto or new scientific exclusion is introduced.

Expression is direct; no reverse coding by statement wording. A category alone is not enough.

One blind once-lock scorer under the common protocol, actual identity/version recorded before any authorized inference. No additional execution rater, adjudication or author scoring of model answers.

Schema: `../../schemas/assessment.schema.json`. Common wrapper and extraction settings are inherited centrally unchanged. No facet-specific response-format instruction is added.
