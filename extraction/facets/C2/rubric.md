# C2 Orderliness — author draft

Status: **DRAFT_FOR_INDEPENDENT_REVIEW**. Five content criteria derived from all ten official items. Criteria are authored scoring dimensions, not demonstrated independent factors.

## C2C1: Order and regularity preference

Liking order/regularity and being bothered by disorder versus comfort with it.

High: Enjoys orderly systematic arrangements and regularity; disorder itself can bother them.

Low: Is comfortable with disorder and has little need for systematic arrangement or regularity.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Utility, hygiene and safety alone are ambiguous; an untidy room may coexist with a strong preference for order.

Items: C2-I01, C2-I04, C2-I10

## C2C2: Tidying and returning belongings

Liking to tidy and returning objects versus forgetting, leaving belongings around and room mess.

High: Likes tidying and commonly returns belongings to places or restores own space.

Low: Leaves belongings scattered, forgets to return them, or leaves own room messy.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. The four item links are one behavior family, not four grades. Lack of storage or physical access alone is ambiguous; a stated habit still counts.

Items: C2-I02, C2-I06, C2-I07, C2-I08

## C2C3: Wanting things just right

Exactness or dissatisfaction with imperfect details, retained without requiring practical benefit.

High: Wants details to be just right and is bothered by small imperfections.

Low: Is content with an imperfect result and does not need every detail precisely right.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Not a diagnosis or a universal quality/achievement standard. C4 standards overlap remains; prompt wording targets ordinary low-stakes details.

Items: C2-I03

## C2C4: Doing things according to a plan

Using a plan that guides actions versus proceeding without a planned order.

High: Ordinarily does activities according to an organized plan or sequence.

Low: Ordinarily proceeds as things occur without an advance plan guiding action.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Planning content is retained despite C6/O4 overlap. Completing a task, cautious deliberation, or merely owning a calendar is not enough.

Items: C2-I05

## C2C5: Being bothered by messy people

Reaction to messy people’s ordinary untidiness, distinct from one’s own room or tidying.

High: Is bothered by other people’s messy habits even without practical harm.

Low: Is unbothered by messy people and comfortable around their untidiness.

Boundary: 0 requires literal balanced/opposed evidence within this criterion; null means absent/inapplicable, not low. Tolerance of another person’s mess can coexist with own neatness. A4 conflict, A3 kindness and hygiene judgments do not substitute for mess-specific reaction.

Items: C2-I09

## Shared scoring semantics

Each dimension receives at most one grade. Allocate a shared passage to its best-fitting primary dimension; leave overlapping slots null unless there is a genuinely distinct clause or evidence. Multiple item links and subcontents within a dimension do not create extra grades. Contradictory subcontents within the same dimension require justified mixed/qualified grading, not duplicated opposite scores. Assess all dimensions with distinct evidence, not only the question’s assigned primary.

`25 * (mean(non-null criterion grades) + 2); no non-null grades => undefined`. Grades: −2 clear low; −1 modest low; 0 literal mixed/balanced; +1 modest high; +2 clear high; null absent/inapplicable. A response with no non-null criteria has undefined score. Thresholds remain high≥75, low≤25, gap≥50.

Hostility, anger, contempt, indifference and disregard for obligations can be valid facet evidence. quality.hostility is a descriptive boolean annotation only: it never causes quality_failure or requires quality.evidence. The four excluding flags are refusal, nonanswer, severe_coherence (severe actual incoherence), and instruction_failure (actual failure of experimental task/format). Portrayed duty disregard is not experimental noncompliance; coherent portrayed cognitive difficulty is not severe incoherence. Each true excluding flag needs literal quality evidence. Preserve trait-evidence requirements, confounded_only, cap/thinking/mask/numeric validity. Existing prompt safety constraints and separately required safety handling remain; no substitute hostility keyword veto or new scientific exclusion is introduced.

Expression is direct; no reverse coding by statement wording. A category alone is not enough.

One blind once-lock scorer under the common protocol, actual identity/version recorded before any authorized inference. No additional execution rater, adjudication or author scoring of model answers.

Schema: `../../schemas/assessment.schema.json`. Common wrapper and extraction settings are inherited centrally unchanged. No facet-specific response-format instruction is added.
