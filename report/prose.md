# Report prose

<!-- One entry per section or result. Write plain text under each ### slot.
     Empty slots are left out of the report and listed in EDITORIAL_TRACKER.md.
     lead: the text above a figure. how_to_read: the caption under it.
     shows / limitation: the evidence panel. body: running text (blank line between blocks; "- " lists; "#### " subheads).
     Iteration 49: first full writing pass after the Nov 9 layout freeze. Every number here is pinned by a check
     in Appendix D; do not add a number without adding its check. -->

## summary
<!-- Introduction (iteration 50; replaces the Summary of findings) -->
### body
Large language models raise two complementary challenges for AI safety: our ability to predict AI, and AI's ability to predict us. Both turn on how a model represents human character, and either answer matters.

The first challenge is that models can take on characters their developers never intended. Anthropic found that a model which learned to cheat on its training tasks went on to show broader misaligned behaviour (MacDiarmid et al., 2025), and the Hugging Face incident is a real-world case of such behaviour emerging.

The second challenge is that models are becoming instruments for predicting people. Agents built from interviews reproduce real individuals' survey answers 85% as accurately as those individuals reproduce their own two weeks later (Park et al., 2024), and a model fine-tuned on human choices predicts behaviour in psychological experiments better than established cognitive models (Binz et al., 2025).

Both challenges come down to how a model represents the characters it plays. Prediction studies like these work from what models say; interpretability can look at the representation itself. Chen et al. (2025) showed that a character trait can be read from a model's internal activity as a direction, and that pushing the model along that direction changes how it behaves. Lu et al. (2026) took this approach to scale, extracting directions for 275 character archetypes and 240 descriptive traits from three open models: Qwen 3 32B, Gemma 2 27B and Llama 3.3 70B. A single direction, running from the default Assistant toward theatrical roles, captures much of how characters differ, and conversations can carry a model along it. In one of their case studies, Llama drifted from the Assistant during an emotionally vulnerable conversation and encouraged a user's allusions to self-harm; capping drift along the axis roughly halved harmful responses. But one axis cannot tell an angel from a demon: the two sit at similar distances from the Assistant, yet the demon gives harmful responses more often. Telling characters apart takes the structure of their traits.

This report maps that structure and asks two questions. Is it shared, so that separately trained models arrange personality traits in the same way? And is it human, so that the arrangement matches how traits go together in people? Where models depart from each other or from people, the characters they play may combine traits in ways no one would anticipate; where they agree with people, they come closer to a working model of human psychology, with uses and risks of its own. We find some of each. The three models arrange traits in largely the same way, and they share one consistent departure from people: Neuroticism and Extraversion, which run in opposite directions in people, run together in every model. In Qwen, for example, friendliness and anger, which in people go modestly in opposite directions, go together: the friendlier a character, the angrier it tends to be.

Sections 1 and 2 describe each model's structure and compare the three models. Sections 3 and 4 compare them with people: first through trait words matched to a large personality survey, then through personality facets that we extracted from Qwen's internal activity ourselves, using questions written for each facet of a standard personality questionnaire. Qwen is our reference model throughout, because it is the model in which we ran these extractions; Section 2 shows how closely the other two agree with it. Throughout, the comparison is between patterns: which traits go together, in the models and in people. A shared pattern would not by itself show that models and people arrive at it in the same way.

Frontier models can be studied only from the outside, since their internal activity is not available. Petrov, Serapio-García and Rentfrow (2024) had GPT-3.5 and GPT-4 answer a Big Five questionnaire while playing personas and published how the five domains correlated in those answers. As far as is publicly known, their models are much larger than the three we study, and they were measured through their answers rather than their internal activity. Section 5 compares the two sets of results and considers which of these differences, scale or measurement, better explains them.



## section.1
<!-- 1 The persona landscape -->
### lead
We begin inside each model, before comparing models with each other or with people: what the main axes of each model's persona space separate, which characters personify them, and where the 240 traits sit on them.




## 1.1
<!-- What the main activation axes separate -->
### lead
Each model's activation axes come from a principal component analysis of its 275 character vectors, ordered by how much of the variation among characters they carry: in Qwen 32%, 16% and 9% for the first three (Appendix G.3). Each axis can be read from the traits that rise and fall along it. Qwen's PC1 runs from dramatic, poetic, romantic characters (poet, leviathan) to factual, analytical, methodical ones (auditor, examiner): factual correlates +.95 with it and dramatic −.97. PC2 runs from introverted, ritualistic characters to experiential, practical ones (introverted −.95), and PC3 from benevolent, nurturing characters to callous, cynical ones (callous +.94). Some traits sit between axes: conscientious rises toward the lower right of the map (+.69 with PC1, −.70 with PC2).

### how_to_read
To explore: use the menus to change the model, the vertical axis and the trait that colours the characters. With PC3 on the vertical axis, angel and demon move to opposite edges. Each dot is one of the 275 characters; its position summarizes the model's internal activity while playing that character. Colour shows each character's score on the trait chosen in the menu (red high, blue low), and the note above the plot gives that trait's correlation with PC1 to PC3. The menu offers the trait at each end of PC1 and of the chosen vertical axis, plus the one lying most evenly between them; for Qwen's PC1 these are factual and dramatic, chosen as the clearest words among the most strongly correlated traits. The first table below lists, for each model's first three axes, the most strongly correlated traits and the most extreme characters at each end.

### shows

### limitation




## chars
<!-- 1 Characters that personify the axes (body text) -->
### body
A few characters sit almost purely on one axis and personify it. On PC1, poet sits at the dramatic end, just behind leviathan, and secretary at the factual end: one says things as no one has said them, the other passes information on as plainly as possible. The Assistant itself sits toward the factual end. PC2 separates two factual characters, theorist and pragmatist, into thinking and doing; furthest toward experience are teenager, adolescent and toddler. PC3 runs from care to coldness: mediator leans benevolent and robot callous. So do angel and demon. They sit close together with PC2 on the vertical axis, then move to opposite edges with PC3, the distinction Lu et al. found a single Assistant Axis could not capture.



## tmap
<!-- 1.2 Where the 240 traits sit on each model's main activation axes -->
### lead
Figure 1.1 places the characters on the activation axes; Figure 1.2 places the 240 traits on the same axes. In every model the traits crowd toward the outer circle: PC1 and PC2 together explain at least half of 180 of Qwen's 240 traits, 187 of Gemma's and 188 of Llama's, and adding PC3 raises the count to 228, 212 and 213. The 240 trait words describe far fewer distinct directions than their number suggests. Opposites sit on opposite sides: in Qwen, transparent and factual anchor one end of PC1 and narrative the other, and with PC3 on the vertical axis callous and vindictive sit at the top while benevolent, supportive and forgiving sit at the bottom. Llama's PC2 runs from impulsive to calm. This compression describes how each model organizes these characters, not human personality, which Section 3 turns to.

### how_to_read
To explore: switch the vertical axis to PC3, or the model to Gemma or Llama, and hover over any dot to see its trait. Each dot is one trait word, placed by how strongly its scores across the 275 characters rise with PC1 (left to right) and with the axis chosen in the menu (bottom to top). Because the axes are uncorrelated, no trait can lie outside the outer circle, and the closer a trait lies to it, the more fully the two axes describe it; inside the dashed circle (light dots) they explain less than half of a trait. Traits close together near the outer circle rise and fall together, and traits on opposite sides run against each other; two traits close together near the centre need not be related. Hover for any trait. Axis signs are arbitrary for each model. Each model's axes are its own; Section 2 compares them.

### shows

### limitation




## 1.2
<!-- 1.3 Exploring the persona landscape (Persona Landscape Explorer) -->
### lead
Figure 1.3 joins the two views: pick any two characters on the map and compare their scores on all 240 traits.

### how_to_read
To explore: pick any two characters from the A and B lists, or tap them on the map, and the bars show the traits on which they differ most. Try angel and demon: close on the first axis, far apart on the third. The axis tags come from the table under Figure 1.1. Trait scores are readings of the model's internal activity, shown in standard deviations from the average character; they are not questionnaire answers.

### shows

### limitation


## section.2
<!-- 2 The three models arrange traits in largely the same way -->
### lead
Before comparing the models with people, we ask whether the three models arrange traits alike. In broad outline they do. The simplest test takes every pair of traits, measures how strongly the two go together across the 275 characters, and asks whether the models agree. Across the 28,680 pairs among the 240 traits, the three models' trait correlations agree at r = .73 to .87 (Figure 2.1). Section 3 applies the same test to people. The models also score each trait across the characters in nearly the same way (median r .88 to .94; Appendix G.2), their main activation axes correspond (Figure 2.2), and five directions they share sit on each model's leading axes (Figure 2.3). Agreement is strongest for this broad structure; specific trait groupings differ between models (Appendix H).


## 2.1
<!-- Main activation axes compared between models -->
### lead
Gemma's first two activation axes line up with Qwen's (PC1 r = .95, PC2 r = .92). Llama's do not line up one to one: Qwen's PC1 correlates +.68 with Llama's PC1 and −.68 with Llama's PC2. The planes the first two axes span nearly coincide, though (canonical correlations .97 and .90), so Llama's first two axes are rotated relative to Qwen's within a shared plane.

### how_to_read
To explore: switch between Gemma and Llama. Gemma's strongest cells run down the diagonal, one axis matching one axis; Llama's first two axes each split between Qwen's first two. Each cell is the correlation, across the 275 characters, between one of Qwen's axes and one of the other model's. Signs are arbitrary: a strong negative value means the same axis pointing the other way.

### shows

### limitation




## 2.2
<!-- Character scores compared between models, per trait -->
### lead
For each trait, the 275 character scores agree between models: median r = .88 (Qwen–Llama), .94 (Qwen–Gemma) and .92 (Llama–Gemma). Only two traits change sign, both between Qwen and Llama (avoidant and generalist).

### how_to_read
Each dot is one trait: how closely two models agree in scoring the 275 characters on it. Black line: median. The vertical spread is only for visibility.

### shows

### limitation




## 2.3
<!-- Shared directions D1-D5 (internal C1-C5) and each model's activation axes -->
### lead
A joint analysis of the three models' trait scores finds five directions they share, D1 to D5; their readings are in the key above the figure. These shared directions sit on each model's leading activation axes. That is expected in part, since both come from the same activations; what it shows is that the structure the three models share is the structure each model is organized around. In Qwen, D1, D2 and D3 are essentially PC1, PC2 and PC3 (r = .94, .98 and .92 in size), and Gemma is close behind (.90, .90, .78). In Llama, D1 and D2 each split across PC1 and PC2, the rotation seen in Figure 2.2; together PC1 and PC2 account for about 90% of the variance of each. D4 and D5 are weaker and spread over the later axes in every model. With the models' shared structure in hand, Section 3 asks whether people share it too.

### how_to_read
To explore: change Model to compare Gemma and Llama, and switch Show to Contributing traits to see the three strongest traits at each end of each direction; they sit on the same axis as the direction. Each cell is the correlation, across the 275 characters, between the model's score on a shared direction (rows) and its position on an activation axis (columns). Signs are arbitrary.

### shows

### limitation




## section.sapa
<!-- 3 Do people arrange the traits the same way? (SAPA bridge) -->
### lead
To compare the models with people we need a shared description of personality. We use the Big Five: Neuroticism, Extraversion, Openness, Agreeableness and Conscientiousness. Forty-two of the 240 trait words correspond directly to a Big Five facet (anxious to Neuroticism, gregarious to Extraversion, and so on). We measure the same 42 traits in people through SAPA, a large online personality survey (23,679 respondents in the release we use). SAPA draws on a very large pool of items covering many personality scales, which is what makes it useful here: almost any trait word can be matched to items that ask about it. That lets us compare all three models with people using the trait scores already released for every model, with no new measurement. The mapping was fixed before any geometry was examined, and it holds up: in people, 90% of the 42 traits correlate most strongly with the survey's scale for the Big Five domain they were assigned to. Anxious, for example, tracks the survey's Neuroticism scale more closely than any other (table under Figure 3.1). The more precise comparison in Section 4 needs the questionnaire's facets measured afresh inside the model, which so far we have done only for Qwen.


## 1.3
<!-- 3.1 People and the three models through the Big Five -->
### lead
Overall, the models' pattern across trait pairs agrees with people's only modestly (r .39 to .58), while the models agree with each other at .73 to .87 on the same measure (Figure 2.1). Each model is much closer to the other models than to people. The clearest difference concerns Neuroticism and Extraversion. In people they are separate, even slightly opposed (average trait-pair r −.21). In all three models they go together (Qwen +.53, Gemma +.39, Llama +.11).

The grouping comes from the models' strongest shared direction, D1 (Section 2). In all three models, Neuroticism, Extraversion and Openness sit toward its charged end, and Agreeableness and Conscientiousness toward its factual, moderate end. When each shared direction is compared with the factors found in people, D1 has no single human counterpart, while D3, care against bluntness, does; the others cannot yet be judged with the traits we can bridge. The models' clearest departure from people therefore lies along their main shared direction.

### how_to_read
To explore: use Rows and Columns to pick which sources to compare (people or a model), and Show to switch between domains and the 42 traits. Red means two traits rise together, blue that one rises as the other falls.

### shows

### limitation
In people, each pair of traits is correlated across survey respondents; in the models, across the 275 characters the model was asked to play, each scored on every trait. Each human trait also rests on only a few survey items, so this comparison is coarse. It also depends on how well trait words written for another purpose match the survey's items. Section 4 removes that step by measuring the questionnaire's own facets directly in Qwen.


## section.3
<!-- 4 Measuring the Big Five facets directly inside Qwen -->
### lead
Section 3 compared trait words with a survey that was not designed around them. Here we use the questionnaire's own facets. The IPIP-NEO is a public-domain version of the most widely used Big Five questionnaire: 30 facets, each measured by ten items written for it. In Johnson's IPIP-NEO data every respondent answered all 300 items, so every facet correlation uses all respondents (here 30,000 people), where SAPA's rest on a few hundred each. Lu et al.'s 240 traits were not built for these facets: only 42 of them correspond to one, and none is defined the way the questionnaire defines it. So we extracted each facet's direction in Qwen ourselves. Twenty-six of the 30 could be measured reliably.


## s3.1
<!-- 4 How each facet was extracted (body text) -->
### body
Lu et al.'s method and ours both measure a trait by contrast, and both are built on **pairs**. A pair is one question answered twice by the model: once under an instruction to express the trait strongly (the high pole) and once under an instruction to express it weakly or not at all (the low pole). The difference in the model's internal activity between the two answers is one estimate of the trait's direction, and averaging over many pairs gives the direction itself.

We kept the essentials of Lu et al.'s method for trait vectors: the same model, the same way of forming pairs, the same judged standard for accepting a pair, and the same way of measuring the direction. We changed two things. The instructions, questions and judging criteria for each facet were written from the questionnaire itself, rather than generated from a trait's name. And instead of a fixed bank of 2,400 responses per pole, we stopped each facet as soon as its direction had converged. Across both formats, a facet needed 87 responses per pole on average, about 27 times fewer than Lu et al. This convergence rule is our own addition; [Appendix A.14](#method-extraction) describes it in full.

Each facet was extracted twice, from scenario questions and from survey-style statements, and kept only if both converged; 26 of 30 did. The main text uses the scenario questions (survey-style results are in Appendix F).


## H
<!-- 4.1 Trait pairs: Qwen links some traits as people do, and reverses others -->
### lead
Across the 325 pairs among the 26 facets, Qwen's pattern partly resembles people's: pattern agreement r = .44, with the same direction in 67% of pairs. Qwen also links facets about twice as strongly (trend slope 2.0). Thirteen pairs reverse the human direction in both prompt formats, and nine of them pair a Neuroticism facet with an Extraversion facet.

### how_to_read
Each dot is one facet pair: how strongly the two facets go together across about 30,000 people (left to right) and across Qwen's 275 characters (bottom to top). Dots on the dashed diagonal would mean Qwen links the pair exactly as people do. The table lists the 13 reversed pairs.

### shows

### limitation
Pairs share facets, so the 325 correlations are not independent of each other; the reversal screen requires both prompt formats to agree (Appendix A.2).


## 4.2
<!-- 4.2 Correlation matrices and domain averages -->
### lead
Arranged by domain, most reversals fall in one block. In people, Neuroticism and Extraversion facets run against each other (block average −.27); in Qwen they run together (+.51), the grouping the trait words showed in Section 3. It is not produced by unusual characters such as the leviathan: among the 130 ordinary roles alone (occupations such as judge and librarian), the block is +.56. Section 5 considers why this matters.

### how_to_read
Each square shows how strongly two facets go together (red together, blue opposite, darker stronger). The menu switches between people, Qwen and their difference, and to domain averages. Black outlines mark the 13 reversed pairs from Figure 4.1; each appears twice because the matrix is symmetric. In the difference view a coloured cell can mean a reversal or a stronger link in the same direction; tap a cell to see both values.

### shows

### limitation


## 4.4
<!-- 4 Closing notes after Figure 4.2 (body text) -->
### body
Outside this block, the clearest misfits are Liberalism and Activity Level, which sit loosely in their own domains in both people and Qwen (Appendix E.2). And as measured, Qwen's facet relationships predict real people's scores weakly: average R² .05, or .25 after a single rescaling, against .58 for a benchmark built from people's own correlations (Appendix E.6). The comparison above does not depend on prediction.


## discussion.0
<!-- 5 Discussion opening, before Figure 5.1 (body text) -->
### body
The three models agree with one another more than any of them agrees with people. They organize Lu et al.'s 240 traits in largely the same way (Section 2), yet relationships that hold among people are often reversed inside them. The clearest case is Neuroticism and Extraversion. In people the two run slightly apart in both our sources: −.21 among the SAPA trait words and −.27 among the IPIP-NEO facets. In the models they run together: in Qwen by two separate routes, the trait words (+.53) and the directly measured facets (+.51), in Gemma more weakly (+.39) and in Llama faintly (+.11). Nine of the 13 facet pairs Qwen reverses fall in this block. The discrepancy is reproducible across models and methods. What our data cannot tell us is what produces it, and for that we turn to outside evidence.


## discussion
<!-- 5 Discussion after Figure 5.1 (body text) -->
### body
#### Other evidence points the other way

Two lines of work find models closer to people. As Figure 5.1 shows, GPT-3.5 and GPT-4 keep the human direction when they answer a personality questionnaire in character. And Geng et al. (2026) found that trait directions extracted from a smaller Qwen model closely match the structure of human impressions of fictional characters. Neither measures what we measure. Questionnaire answers describe what a model says; our readings describe its internal activity. And impressions of characters capture how people perceive personality, which need not match how traits go together in real people's descriptions of themselves. Taken together, the results suggest the models may mirror how personality is talked about and perceived more closely than how it is organized in people.

#### What could explain the difference

Three explanations remain open, and our data cannot yet separate them.

The first is measurement: the reversal may belong to how we read the models, not to what they represent. Response style is one candidate. The Friendliness–Anger pair, an instance of the block, survives the removal of any single character but reverses when formality is held constant (Appendix H). The persona set is another: it is a landscape of authored archetypes, not a population, although the grouping holds among the 130 ordinary roles alone.

The second is capacity. Llama, the largest of the three, is the least dominated by a single activation axis (17% of the variation on its first axis, against 24% in Gemma and 32% in Qwen; Appendix G.3) and the least different from people. Larger models may resolve personality into more independent directions, so that traits bundled in a smaller model can vary separately. But size alone does not order the three: Gemma is smaller than Qwen yet less concentrated, and size is confounded with architecture and training.

The third is training. Lu et al. (2026) found nearly the same Assistant Axis, the leading direction of their persona space, in pretrained and post-trained versions of the same models, which suggests that much of this structure is set during pretraining, with post-training mainly shaping which parts of it a model expresses. Whether post-training also changes the wider geometry, and by how much, is unknown.

#### Why it matters

If traits are coupled inside a model, moving one may move others. In Qwen, Friendliness and Anger rise together across characters (+.71) where in people they run apart (−.28). If such coupling held in a far more capable model, a persona pushed toward warmth or excitement might carry hostility with it, much as narrow training on reward hacking spread to broad misalignment (MacDiarmid et al., 2025). We have not shown this: our evidence is a correlation across characters, not the effect of moving a model, and activation-derived traits are not shown to govern behaviour the way dispositions do in people. But the structural difference is consistent enough that it should be tested by intervention, not assumed away.

#### The next step

Each explanation makes a prediction that a larger model can test. If capacity drives the bundling, a substantially larger model should show more independent trait directions and closer agreement with people. If pretraining sets the structure, pretrained and post-trained versions of the same model should share it. And if the reversal belongs to measurement rather than representation, the same model's questionnaire answers and internal readings should disagree. The methods in this report (the persona and facet measurements, and the convergence rule that makes facet extraction about 27 times cheaper than a fixed bank) can be applied unchanged. The most informative extension is therefore to repeat this analysis on a substantially larger open-weight model and, where internal access allows, on frontier systems (Section 8).


## 6.1
<!-- 5.1 Big Five domain correlations: people, model answers, model activations -->
### lead
How strongly the five domains go together depends on where they are measured. Petrov, Serapio-García and Rentfrow (2024) had GPT-3.5 and GPT-4 answer a 44-item Big Five questionnaire (the BFI) while playing personas, and compared them with people from the BBC Big Personality Test, a large online survey run with the BBC in the UK. In those people, as in ours, Neuroticism and Extraversion run in opposite directions (−.33 in the BBC sample, −.44 from our 26 IPIP-NEO facets). The GPT answers keep that human direction (−.27 to −.47). In the activations of all three models we studied, the two domains go together (Qwen +.73 from facets and +.91 from trait words; Gemma +.84; Llama +.59). The same split holds for Extraversion with Agreeableness and with Conscientiousness: positive in people and in every GPT condition except one (GPT-3.5 with demographic personas, Extraversion with Agreeableness −.03), negative in every activation source.

### how_to_read
Each row is one pair of Big Five domains; each marker is the correlation between the two domain scores in one source. Diamonds are people, squares GPT answers, circles and triangles model activations; the shaded top row is Neuroticism with Extraversion. The menu switches the GPT answers between generic and demographic personas, or shows the three activation models together. The second table below scores each source against two sign patterns: valence (desirable traits together, Neuroticism opposite) and intensity (Neuroticism, Extraversion and Openness together, Agreeableness and Conscientiousness opposite). People and GPT answers match valence (.76 to .95); activations match intensity (.75 to .98) and valence at most .31.

### limitation
The sources share little beyond the five domain names. The GPT values are published aggregates from another study: different models, the 44-item BFI, 150 generic or 1,000 demographic personas, and answers rather than activations. Our human IPIP-NEO and Qwen facet values are composites of 26 facets; our trait-word values use 42 mapped traits. The two sign patterns were defined after seeing these numbers and are descriptive, not a test.


## limitations
<!-- 6 Limitations -->
### body
- **An authored landscape, not a population.** The 275 characters are archetypes written for another study and weighted equally.
- **One model measured directly.** Direct facets exist for Qwen only, and for 26 of the 30 facets (no Assertiveness, Depression, Dutifulness or Immoderation).
- **Inherited vectors.** The exact checkpoint and response masks behind the released vectors are not fully documented.
- **Response style.** Conditioning on style removes much of each trait's variance and is not a correction, but holding formality constant reverses the Friendliness–Anger link (Appendix H), so style may carry part of the Neuroticism–Extraversion block.
- **Human data.** Self-report from self-selected internet samples; the evaluation respondents were reused across exploratory analyses.
- **Correlational geometry.** The findings describe how representations are arranged; behavioural validation is limited.


## related
<!-- 7 Related work -->
### body
This work inherits its personas, traits and vectors from Lu et al. (2026) and its extraction approach from Chen et al. (2025). Questionnaire studies have administered the IPIP-NEO and BFI to language models playing simulated personas (Serapio-García et al., 2023; Petrov, Serapio-García and Rentfrow, 2024); the latter's published GPT values enter Figure 5.1. Activation studies have found Big Five directions in open models and steered along them (for example arXiv:2512.17639 for Llama 3.3 70B and arXiv:2602.15847 for 8B models), but have not compared how the domains relate to each other with people. Geng et al. (2026) compare implicit personality representations in humans and models. Anthropic's studies of emotion concepts (2026) and of the persona selection model (2026) bear on how models represent and select the characters they play.

#### References

- Anthropic (2026). Emotion concepts and their function in a large language model. [transformer-circuits.pub](https://www.transformer-circuits.pub/2026/emotions/index.html)
- Anthropic (2026). The persona selection model. [anthropic.com](https://www.anthropic.com/research/persona-selection-model)
- Cammarata, N. (2026). Neural networks are already clean. Goodfire. [already-clean.goodfire.com](https://already-clean.goodfire.com/)
- Carver, C. S., and Harmon-Jones, E. (2009). Anger is an approach-related affect: Evidence and implications. Psychological Bulletin, 135(2), 183–204. [doi:10.1037/a0013965](https://doi.org/10.1037/a0013965)
- Chen, R., Arditi, A., Sleight, H., Evans, O., and Lindsey, J. (2025). Persona vectors: Monitoring and controlling character traits in language models. [arXiv:2507.21509](https://arxiv.org/abs/2507.21509)
- DeYoung, C. G. (2006). Higher-order factors of the Big Five in a multi-informant sample. Journal of Personality and Social Psychology, 91(6), 1138–1151.
- Digman, J. M. (1997). Higher-order factors of the Big Five. Journal of Personality and Social Psychology, 73(6), 1246–1256.
- Geng, Y., Abend, O., Hovy, E., and Frermann, L. (2026). Implicit personality representations in humans and LLMs. [arXiv:2609.12704](https://arxiv.org/abs/2609.12704)
- Johnson, J. A. IPIP-NEO-300 item-level responses. Open Science Framework.
- Binz, M., et al. (2025). A foundation model to predict and capture human cognition. Nature.
- Lench, H. C., Reed, N., George, T., Kaiser, K., and North, S. (2023). Anger has benefits for attaining goals. Journal of Personality and Social Psychology.
- Lu, C., Gallagher, J., Michala, J., Fish, K., and Lindsey, J. (2026). The Assistant Axis: Situating and stabilizing the default persona of language models. Proceedings of ICML 2026, PMLR 306. [arXiv:2601.10387](https://arxiv.org/abs/2601.10387)
- MacDiarmid, M., et al. (2025). Natural emergent misalignment from reward hacking in production RL. Anthropic.
- OpenAI (2026). OpenAI–Hugging Face incident technical report. [cdn.openai.com](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf)
- Park, J. S., et al. (2024). Generative agent simulations of 1,000 people. [arXiv:2411.10109](https://arxiv.org/abs/2411.10109)
- Petrov, N. B., Serapio-García, G., and Rentfrow, J. (2024). Limited ability of LLMs to simulate human psychological behaviours: A psychometric analysis. [arXiv:2405.07248](https://arxiv.org/abs/2405.07248)
- Serapio-García, G., et al. (2023). Personality traits in large language models. [arXiv:2307.00184](https://arxiv.org/abs/2307.00184)



## open
<!-- 8 Open questions and next steps -->
### body
- **Separate the measurement from the model.** Have Qwen, Gemma and Llama answer the IPIP-NEO in character for the same 275 personas. If the answers show Neuroticism and Extraversion running apart while the activations show them together, the reversal belongs to the representation (Section 5).
- **Test the valence-versus-intensity hypothesis directly.** Does a desirability direction exist in the persona activations, and is it separate from the intensity direction D1?
- **Scale and concentration.** Repeat the analysis in a larger open model, and in base and instruction-tuned versions of the same model, to see whether persona space spreads over more axes and bundles traits less.
- **Measure the facets directly in Gemma and Llama,** and recover the four missing facets, especially Assertiveness.
- **Frontier models.** Compute the five-domain matrix from released persona scores (Serapio-García et al., 2023, including GPT-4o; de Winter et al., 2024, GPT-4 with 2,000 personas), and if warranted administer the IPIP-NEO to the 275 personas.
- **Other human anchors.** Compare the models' structure with people's ratings of the same characters, with observer ratings and with behaviour-based measures, and build personas from real human profiles.
- **Behaviour.** Test whether steering one trait moves its bundled partners, and use Anger measures that capture constructive or assertive anger.


## about
<!-- About this work -->
### body
Josiah Chamberlain. Analysis and code were developed with AI assistants (Claude, Claude Code, GPT and Codex) under the author's direction. Contact and citation details to follow.


## section.E
<!-- Appendix E: Technical explorations -->
### lead
Technical results behind the main text: how well each facet fits its domain (E.2), facet-specific rescaling (E.3), each model's own trait factors (E.4), where Qwen's facets sit in its geometry (E.5) and prediction of real people's scores (E.6). E.1 keeps an earlier experiment.


## E.1
<!-- Appendix E: calibration slider (earlier nine-facet experiment) -->
### lead

### how_to_read

### shows

### limitation


## E.2
<!-- Appendix E: how well each facet fits its domain -->
### lead
Facets that sit loosely in their own domain are harder to predict from the other facets, for people and for Qwen alike: across the 26 facets, fit and prediction R² have rank correlations of .84 in people and .66 in Qwen. This partly explains Figure E.6.

### how_to_read
Each row is one facet, placed by how strongly it goes together, on average, with the other facets in its domain. Facets far to the left sit loosely in their domain.

### shows

### limitation


## E.4
<!-- Appendix E: each model's own trait factors -->
### lead
A factor analysis of each model's 240 trait scores groups the traits into a few broad factors: five in Qwen, six in Llama and Gemma. They give the same picture as the shared directions and the activation axes in a different rotation: Qwen's F1 (calm vs edgy) is D1 read from the other end (r = −.89), and Qwen's factors explain 83% of each facet on average, against 82% for D1 to D5. No factor matches a single axis, but PC1 to PC6 explain 83% to 99% of each Qwen factor; Qwen's F1, for example, combines PC1 (+.75), PC2 (−.50) and PC3 (−.42).

### how_to_read
Each cell is the correlation, across the 275 characters, between one of the model's own factors (rows) and an activation axis (columns); the menu switches models, and hovering shows how much of a factor PC1 to PC6 explain together. The key names Qwen's factors by the traits at each end; Gemma's and Llama's are fitted separately, so their numbers do not correspond to Qwen's. Signs are arbitrary.

### shows

### limitation
The factors are allowed to correlate (Qwen's F2 and F5 correlate −.49), and Gemma and Llama have six factors to Qwen's five, so rows do not correspond across models; Appendix G.4 matches them.


## 3.2
<!-- E.5 Where the facets sit in Qwen's geometry -->
### lead
Qwen's 26 facet readouts sit almost entirely within the directions from Sections 1 and 2: on average the five shared directions explain 82% of each facet's variation across the 275 characters and Qwen's first five activation axes 78% (Qwen's own factors 83%; Appendix E.4). One direction does most of the work. All four Neuroticism facets (r = +.80 to +.92) and Excitement-Seeking (+.91) sit at the charged end of D1, while Self-Discipline, Self-Efficacy, Cautiousness and Cooperation (−.86 to −.90) sit at the moderate end; the same split runs along Qwen's PC1. The caring direction D3 carries Sympathy (+.86) and Altruism (+.74). Most of each facet's direction nevertheless lies outside the first few activation axes: the first three components, refitted at block 48, hold a median 14% (at most 32%) of a facet's final direction. Facet scores follow those axes closely because the characters differ mostly along them.

### how_to_read
Each cell is the correlation, across the 275 characters, between Qwen's score on a facet (scenario prompts) and its score on a direction. The menu switches between the shared directions (default) and Qwen's activation axes; each axis column names the shared direction it matches best (Figure 2.3). Hover to see how much of a facet the five directions explain together. Signs are arbitrary.

### shows

### limitation
Facet scores and directions come from the same persona vectors, so high shares are expected in part. Whether people's facets line up the same way is the subject of Section 4.


## 4.3
<!-- E.6 Predicting real people's scores (held-out R² per facet) -->
### lead
As measured, Qwen's facet relationships predict real people's facet scores weakly: average R² .05, against .58 for a benchmark built from people's own correlations. Qwen's links are stronger than people's, and shrinking its predictions by one common factor (0.53 for scenario prompts, fitted on separate respondents) raises the average to .25. Rescaling does not change which facets Qwen links or reverses.

### how_to_read
Qwen, calibrated: predictions shrunk toward the average by one factor per prompt format. Bars: 95% uncertainty from how Qwen's facet directions were extracted (a different draw of questions). Uncertainty from the 10,000 test respondents is smaller; values are in the tables below.

### shows

### limitation


## G.1
<!-- Appendix G: trait-pair correlations (Figure G.1) -->
### lead
No model links its traits much more strongly than another: the trend slopes between model pairs run from 0.94 to 1.04.

### how_to_read
To explore: switch between the three model pairs. Each point in the shading is one pair of traits, placed by its correlation in each of the two models; pairs near the diagonal are linked equally strongly in both. These are the trait words, not the questionnaire facets, which were measured in Qwen only.

### shows

### limitation


## G.2
<!-- Appendix G: persona scores (pointer to Figure 2.2) -->
### lead

### how_to_read

### shows

### limitation


## G.3
<!-- Appendix G: main activation axes (pointer to Figure 2.1) -->
### lead

### how_to_read

### shows

### limitation


## elbow
<!-- G.3a How much of the variation among characters the activation axes carry -->
### lead
The three models spread the variation among their 275 characters differently. In Qwen the first axis dominates: it carries 31.6% of the variation, nearly twice the second (16.2%), and the first three together carry 56%. Gemma has the same shape, softer (23.5% on its first axis, 42% on the first three). Llama has almost no elbow at the top: its first two axes are nearly tied (17.2% and 14.2%), its first three carry 38%, and its first axis is the least stable when the characters are resampled. Section 5 discusses what this concentration might mean.

### how_to_read
Each line is one model. The chart opens on the cumulative view: each point is the share of the variation carried by PC1 through that axis together. The menu switches to each axis's own share (the elbow view), where a steep drop after the first point means one axis dominates. The table gives each axis's stability when the characters are resampled (5th-percentile bootstrap cosine; PC1 .98 for Qwen, .97 for Gemma, .76 for Llama).

### shows

### limitation
The shares describe this particular set of 275 authored characters; a different set would give different shares.


## G.3b
<!-- Appendix G: PC1 scatter -->
### lead

### how_to_read
Each dot is one of the 275 characters; the menu switches between Gemma (default) and Llama.

### shows

### limitation


## G.4
<!-- Appendix G: factor matching -->
### lead
AA17 fitted five or six factors per model from the 240 traits. Matching each factor to its best counterpart gives congruences of .61 to .92 in size for Qwen–Llama, .73 to .93 for Qwen–Gemma and .52 to .91 for Llama–Gemma. The strongest match is Qwen F3 with Llama F2 and (oppositely signed) Gemma F6. Figure H.7 shows two worked examples; there, Qwen F1 is compared with Gemma F3, the runner-up (.77) to its matched Gemma F1 (.79).

### how_to_read
Tucker congruence between factor loading patterns over the 240 traits. Outlined cells are the matched pairs. Factor signs are arbitrary.

### shows

### limitation
Only the strongest broad match survives the sensitivity checks of the matching study (PHG-CM01); other correspondences depend on the representation and indicators used.


## G.5
<!-- Appendix G: shared directions D1-D5 -->
### lead
A joint analysis of the three models' trait scores found five directions shared by all three (D1 to D5). A follow-up compared them with factors fitted to the SAPA data: D3 is independently supported, D2 is a partial human analogue, D1 is a combination of human factors, and D4 and D5 cannot yet be tested because the human bridge does not cover them adequately. As the project's research record cautions: Do not infer common semantic factors from alignment alone.

### how_to_read

### shows

### limitation
The human comparison runs through a limited set of bridged traits, so a missing human match for D4 or D5 is not evidence that none exists.


## G.6
<!-- Appendix G: beyond personas -->
### lead
A separate October 9 study compared local semantic geometry in Llama-3.1-8B and Gemma-2-2B on 640 texts per model: the two models' relational structure agreed with Spearman rho = .839 across held-out contexts. These are different, smaller models and different data from the persona bank, so this is context for the persona comparisons, not a fourth model pair.

### how_to_read

### shows

### limitation
That study established relational agreement only; it did not identify matching regions or a shared subspace across the two models.


## G.7
<!-- Appendix G: not yet compared -->
### lead
Direct facets exist only for Qwen. The trait-word bridge (Section 3) compares all three models with people, but coarsely; whether Gemma and Llama would relate to people's facet structure as Qwen does is untested.

### how_to_read

### shows

### limitation
Without direct Gemma and Llama facet measurements, any statement about their agreement with people rests on trait-word proxies.


## section.5
<!-- Appendix H: Case study: Friendliness and Anger -->
### lead
Friendliness (an Extraversion facet) and Anger (a Neuroticism facet) correlate −.28 in people and +.71 in Qwen (scenario prompts; +.61 survey-style). This appendix tests that one pair from the Neuroticism–Extraversion block against five explanations, as a worked example of how fragile a single pair can be.


## 5a
<!-- H.1 Unusual personas? (influence) -->
### lead
Not unusual characters. Removing any single character leaves the correlation between .70 and .72 (scenario prompts; the most influential character is zealot), and no single removal changes the sign of any of the 13 reversals. Among the 130 ordinary roles alone the pair is +.83.

### how_to_read

### shows

### limitation


## 5b
<!-- H.2 Response style? (Friendliness vs Anger by Formal) -->
### lead
Partly response style. Holding the Formal style readout constant reverses the link (−.24), as does holding five styles constant (−.23). Conditioning removes much of each facet's variance, though (a median 48% for Formal and 75% for the five styles), so this shows that style and the pair are entangled, not that style explains it.

### how_to_read

### shows

### limitation


## 5c
<!-- H.3 Where in the geometry? (C/T/F projected vs residual) -->
### lead
Inside the shared geometry. Splitting each of the 13 reversed correlations into the part carried by a five-dimensional subspace and the remainder, Qwen's own factors (F) carry 88% to 99.5% of the absolute contribution: the reversals live in the main directions, not in a residual.

### how_to_read

### shows

### limitation


## 5d.1
<!-- Questionnaire wording: Friendliness and Anger items -->
### lead
Not particular human items. In 117,259 respondents, all ten Anger items correlate negatively with Friendliness.

### how_to_read

### shows

### limitation


## 5d.2
<!-- H.4 Anger items vs Friendliness and Assertiveness -->
### lead
Each Anger item against Friendliness and against Assertiveness: the Friendliness correlations are all negative, while the Assertiveness correlations are small and mixed.

### how_to_read

### shows

### limitation


## 5d.3
<!-- H.5 Friendliness by Anger level -->
### lead
Friendliness falls steadily as Anger rises: mean Friendliness is 3.70, 3.48 and 3.19 in the low, moderate and high Anger bands, with no turn at high Anger.

### how_to_read

### shows

### limitation


## 5e.1
<!-- H.6 Other models: historical relationships -->
### lead
Partly specific to Qwen. The closest trait-word proxies show Qwen's pattern only in part: Negative Avoidant with Hostile is positive in Qwen (+.58) but negative in Llama (−.71) and Gemma, while Nurturing with Hostile is negative in all three.

### how_to_read

### shows

### limitation


## 5e.2
<!-- PHG-CM01 focal relationships -->
### lead
In the focal relationships of the matching study, Charismatic with Hostile is positive in Qwen (+.74) and Gemma (+.51) but negative in Llama (−.53).

### how_to_read

### shows

### limitation


## 5e.3
<!-- H.7 Trait–factor patterns, Qwen F1 vs Llama F1 / Gemma F3 -->
### lead
At the level of whole factors, Qwen's F1 matches Llama's F1 (congruence .73) and Gemma's F3 (.77) only in part; the red dots are the traits that disagree most.

### how_to_read

### shows

### limitation


## method.extraction
<!-- Appendix A.14 Facet extraction and the convergence rule (body text) -->
### body
**Pairs.** Lu et al.'s method and ours both measure a trait by contrast, and both are built on pairs. A pair is one question answered twice by the model: once under an instruction to express the trait strongly (the high pole) and once under an instruction to express it weakly or not at all (the low pole). The difference in the model's internal activity between the two answers is one estimate of the trait's direction, and averaging over many pairs gives the direction itself.

**Lu et al.'s method.** Following Chen et al. (2025), a language model wrote, from each trait's name and a short description, five pairs of instructions and 40 questions; within each pair, one instruction encouraged the trait and the other suppressed it. A judge scored every answer from 0 to 100, and a pair qualified when the two answers differed by at least 50 points. They generated a fixed bank of 2,400 responses per pole for every trait and required at least 10 qualifying pairs (Lu et al. 2026, Appendix C.1).

**What we kept:**

- the same model, Qwen 3 32B;
- the same way of forming pairs: each question answered under a high and a low instruction;
- the same acceptance standard: an AI judge scores each answer from 0 to 100, and a pair is accepted only if the two answers differ by at least 50 points (we also required the high answer to score at least 75 and the low at most 25);
- the same method of measuring the direction: the average activity of the high answers minus the low.

**What we changed: the materials.** For each facet we studied its ten questionnaire items, its scoring key and the published descriptions of the construct, and from them wrote three things:

- a high and a low instruction, each a short portrait of a person at that end of the facet;
- a bank of 64 scenario questions, short realistic situations that ask what the person would do;
- a scoring rubric for the judge, a few criteria grouped from the content of the ten items.

The questions are our own, drafted with AI assistants and reviewed facet by facet; the questionnaire supplies only its items, which the questions cover without paraphrasing. The judge, a separate model, scored each answer against the rubric without knowing whether it came from the high or the low instruction. A second bank of 64 survey-style statements per facet was prepared the same way.

**What we changed: the convergence rule.** Rather than generate a fixed bank, we raised the minimum to 16 accepted pairs, compared with Lu et al.'s 10, and ended extraction as soon as the direction had converged. We worked through the questions in batches and recalculated the direction at checkpoints of 8, 12, 16, 24, 32, 48 and 64 accepted pairs. A facet stopped at the first checkpoint where:

- it had at least 16 accepted pairs;
- the direction was stable under resampling (below);
- the direction had barely changed since the previous checkpoint (cosine similarity at least .98, where 1 means identical; for example, 24 pairs compared with 16).

The resampling test asks whether the direction depends on which particular questions happened to be accepted. At a checkpoint with 24 accepted pairs, we draw 24 of them at random, allowing repeats and keeping each question's high and low answers together, and average them. Repeating this 1,000 times shows how much the direction would shift with a different set of questions. The test passes when 95% of these redrawn directions point almost the same way as the actual one (cosine at least .95). No new answers are generated; this is computation on the pairs already accepted.

**Why these thresholds.** They are practical choices, fixed before any facet was measured, not derived as statistical optima. They were tested first on Lu et al.'s own traits: applied to Flippant, Pensive and Accessible, the rule converged and recovered Lu et al.'s released directions almost exactly (cosines .980, .966 and .969). The 95% figure describes the resampled directions; it is not a confidence statement about the psychological construct. The rule shows that a direction is stable, not that it is valid. Validity is what the comparison with people in Section 4 tests.

**Results.** Every facet kept stopped after 16 to 48 accepted pairs; none reached the last checkpoint of 64.

[[TABLE:stops]]

Each facet generated 32 or 64 question pairs per format, including pairs the judge rejected and accepted pairs beyond the stopping point. Across the 26 facets kept, that is 2,272 question pairs (1,024 scenario, 1,248 survey-style), or 4,544 model responses. Of these pairs, 361 were rejected, 447 were accepted after the stopping point and left out, and 1,464 form the final directions. No response was generated twice.

[[TABLE:efficiency]]

Counting the four facets that did not converge (each used 64 question pairs in both formats), the full extraction generated 5,568 responses, against 124,800 for 26 traits at Lu et al.'s published rate: about 22 times fewer. These are counts of generated responses, not costs, and the two procedures also differ in how questions are built and judged and in the layer read.

A facet was kept only if both formats converged. Depression, Dutifulness and Assertiveness converged in one format but not the other, and Immoderation in neither, leaving 26 of 30. The two formats agree closely: characters' facet scores correlate .94 between them (median). Unlike Lu et al.'s released trait vectors, used in Sections 1 to 3, which average all of the model's layers, these directions are read at a single layer (block 48).

**Notes on Lu et al.'s counts.** Lu et al. describe the 10 qualifying pairs as "system prompt pairs", but generated only five instruction pairs per trait, so we read them as qualifying response pairs. Their published 2,400 responses per pole does not reconcile with their released materials (five instructions × 240 shared questions gives 1,200 per pole); the comparisons above use the published figure. At 1,200, every ratio halves (about 14 times fewer on average).

**Sources.** Lu et al. (2026), Appendix C.1, p. 29; the project's frozen Direct-30 extraction protocol (judging, rubric, thresholds); the September 24 calibration (codex/adaptive-trait-hifwb-extraction-20260924 @ 2524afc, calibration_report.md); the convergence audit (codex/facet-convergence-geometry-20261106 @ 598857c), with per-facet question counts reconciled against the Direct-12, Direct-18 and Direct-30 A and B execution records.
