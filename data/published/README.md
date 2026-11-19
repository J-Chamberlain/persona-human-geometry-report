# PHG tables of published statistics

[domain_correlations_petrov2024.csv](domain_correlations_petrov2024.csv) is a PHG-authored arrangement of the50 published coefficients used by report Figure5.1: ten unordered Big Five domain pairs, each with a BBC human reference and four GPT questionnaire conditions. These remain **Petrov et al.'s published statistics**, not PHG measurements.

Citation: Petrov, Serapio-García & Rentfrow (2024), *Limited Ability of LLMs to Simulate Human Psychological Behaviours: a Psychometric Analysis*, Figure4, [arXiv:2405.07248](https://arxiv.org/abs/2405.07248). [Metadata](domain_correlations_petrov2024.json) records domain/condition labels, the immutable upstream commit, original file identity/hash and table-construction rule.

PHG selected the coefficients its report uses and organized them into a new, cited wide table, without diagonal blanks or repeated symmetric entries. Precision is retained because the report computes correlations with descriptive sign templates from these numbers. No raw human or individual GPT records are included. This table does not redistribute the original `intercorrs.csv` file or assert a licence for that file.

The READER build uses this packaged table and needs no download. `python scripts/download_petrov.py` remains the opt-in, hash-verified route to the authors' original CSV; keep that original file out of Git. [Verification](../../verification/PUBLISHED_VALUES.json) checks that all50 values, derived template fits and Figure5.1 numerical inputs agree with the previous reader path.
