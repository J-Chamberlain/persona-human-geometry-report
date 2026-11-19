# External published aggregates

Files here come from outside this repository. Each is an aggregate table (no individual records), used unchanged and
cited in the report. The SHA-256 below is checked when the notebook runs.

| File | Source | Commit | SHA-256 |
|---|---|---|---|
| `petrov2024_intercorrs.csv` | Petrov, Serapio-García & Rentfrow (2024), *Limited Ability of LLMs to Simulate Human Psychological Behaviours: a Psychometric Analysis*, arXiv:2405.07248. Repository https://github.com/nikbpetrov/LLMs-Simulate-Humans, file `data/data_for_R/intercorrs.csv` (the values plotted in the paper's Figure 4). | `85c3c2f78d5371cf16b71b8b94006d379b4c24fd` | `aa55c342bd2ee55ba111927e3f31a71ec8f702a692da4b5ec4cb46db97224e0c` |

Contents: Big Five (BFI-44) domain-score intercorrelations for BBC human data (Rentfrow et al. 2015; N = 123,828 after
cleaning) and for GPT-3.5 (gpt-3.5-turbo-1106) and GPT-4 (gpt-4-1106-preview) answering as 150 generic (PersonaChat)
or 1,000 "silicon" (BBC demographic) personas, temperature 0.
