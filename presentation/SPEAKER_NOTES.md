# Speaker notes

Talking points, not a script. Each slide: what to say, one number to remember, one caution, and a transition.

## 1. Title

**What to say:** Introduce yourself and the project in one sentence: I looked at five seasons of Transfermarkt data to see which player characteristics move together with a player's market value.

**Transition:** "Let me start with the question and why it is worth asking."

## 2. Question and motivation

**What to say:** Read the research question. Then explain why it matters: values range from tens of thousands to hundreds of millions of euros, and players who produce similar numbers can be valued very differently. My goal is descriptive: which characteristics move with value, not predicting a 'true price'. Point at the dark box: market value is Transfermarkt's estimate, not a transfer fee. Mention who cares: fans and journalists quote these values, analysts and recruiters use them as a reference, players and agents are affected by them.

**Number to remember:** Market value is an estimate, not a fee.

**Caution:** Do not call it the player's 'price' or 'worth' as a fact.

**Transition:** "To answer this I needed player-level data across several seasons."

## 3. Data

**What to say:** Source is David Caribou's public transfermarkt-datasets, which is scraped from Transfermarkt and released under CC0. Walk through the four numbers: 32,046 player-seasons, 13,511 different players, 14 domestic European leagues, five seasons from 2020/21 to 2024/25. Explain the unit: one row is one player in one season, so a player who played all five seasons appears five times. List the main variables quickly; do not read every one.

**Number to remember:** 32,046 player-seasons

**Caution:** Rows are not independent people: the same player can appear up to five times.

**Transition:** "The raw data did not come in this shape, so here is how I built it."

## 4. Data preparation

**What to say:** The raw data is match-level: about 1.9 million appearance rows. Follow the arrows: join each appearance to its game to get season and league, add up minutes, goals and assists per player per season, attach age and position, then attach the valuation at the end of that season. Then the three rules. 450 minutes: per-90 rates explode for players who barely played, one goal in one minute is 90 goals per 90, so rates are only used above five full matches; low-minute players stay in the data for everything else. July 31: Transfermarkt updates values a few times a year, mostly in June, so I take the latest value on or before July 31 after the season. 365 days: if that value is more than a year old, the row is excluded. In total 920 rows (2.8%) were excluded.

**Number to remember:** 920 excluded of 32,966 (2.8%)

**Caution:** These thresholds are practical choices, not the only correct ones.

**Transition:** "With the dataset built, the first question everyone asks is about age."

## 5. Age

**What to say:** Look at the lines: value rises through the early twenties, stays high from about 22 to 28, then falls after 30. The bar chart shows the age groups: under 21 is €0.8M, 21-23 €1.8M, 24-26 is the highest at €2.0M, 27-29 €1.8M, 30 and over €0.75M. Then the key point: the Spearman correlation between age and value is -0.03, basically zero, but age obviously matters. A correlation measures a steady up or down trend; here value goes up and then down, so it cancels out. This is why plotting the data matters. Mention the y-axis is log-scaled because values are so skewed.

**Number to remember:** 24-26 has the highest median (€2.0M); Spearman -0.03

**Caution:** Do not say 'younger players are worth more'. Under 21 is low. Also these are different players at different ages, not one player ageing.

**Transition:** "Age applies to everyone. Performance is where position matters."

## 6. Position and performance

**What to say:** Goals and assists mean different things for different jobs. For attackers with at least 450 minutes, goals per 90 has a Spearman correlation of 0.37 with value; for midfielders 0.23; for defenders 0.18. The scatter shows attackers: lots of spread, but the median line rises steadily. The caution: this does not say goals are how you judge a defender. The dataset has no tackles, interceptions or saves, so defenders and goalkeepers are under-described.

**Number to remember:** Goals/90 vs value: 0.37 attackers, 0.23 midfielders, 0.18 defenders

**Caution:** Moderate correlation: plenty of high scorers with modest values and the reverse.

**Transition:** "Position and performance differ within leagues, but the biggest gaps are between leagues."

## 7. League context

**What to say:** This is the most striking chart. The Premier League median is €13M. The other big leagues: Bundesliga and Serie A €4M, Ligue 1 €3.5M, LaLiga €3M. Every other league is €1M or less, down to €350K in Ukraine. Pooled, the top-five median is €4.5M against €600K for the other nine. About 35% of the variation in log value lies between leagues, compared with about 1% between positions. But this is context, not cause: leagues differ in money, clubs, player quality and media exposure. I cannot say playing in England makes a player worth more.

**Number to remember:** Premier League €13M; top-five €4.5M vs others €600K; ~35% between leagues

**Caution:** Never say 'the league causes higher value'. 35% is a share of variation between groups, not a percentage influence.

**Transition:** "Coming back to attackers: what happens if we look at age and output together?"

## 8. Age x performance

**What to say:** Here I split attackers with at least 450 minutes into three age bands and into high or lower output, where high output means the top quarter of goals plus assists per 90. Young high-output attackers have the highest median, €10M, then prime-age high-output €8M, then experienced high-output €3.5M. Lower-output groups sit around €1-2.3M. At the same output, younger is valued higher. I checked it is not just a league effect: the same ordering holds inside the top-five leagues (€31M vs €25M) and outside them (€5M vs €4.5M).

**Number to remember:** Young high output €10M vs prime €8M vs experienced €3.5M

**Caution:** Descriptive only. A plausible explanation is resale value and future potential, but the data cannot test that.

**Transition:** "My professor suggested checking whether players fall into natural groups, so I tried clustering."

## 9. Clustering

**What to say:** K-means puts players with similar numbers into the same group. I used 6,095 attacker-seasons with at least 450 minutes and four inputs: age, minutes, goals per 90, assists per 90, scaled so each counts equally. Market value and league were not inputs, so value can be compared afterwards and the method cannot produce 'league clusters'. I tried k from 2 to 6. The silhouette score, which measures how well separated the groups are, was only about 0.21 to 0.22 at every k, which is weak. I kept k = 4 because the groups are readable: regular starters (€8M), creative attackers (€5M), younger lower-output (€1.5M), older with fewer minutes (€1M). The honest conclusion: attacker profiles form a continuum, and K-means sliced it into four readable but overlapping groups.

**Number to remember:** Silhouette ~0.21 at every k

**Caution:** Do not say K-means found the true types of attacker, or league groups.

**Transition:** "Putting it together, here is what I can and cannot conclude."

## 10. Conclusions

**What to say:** Go across the six cards in order and keep each to one sentence. End by repeating that all of these are associations.

**Number to remember:** Use one number per card: €2.0M peak at 24-26, 0.51, 0.37, €13M, €10M, 0.21.

**Caution:** None of these is causal.

**Transition:** "And here is what the project cannot show."

## 11. Limitations

**What to say:** Pick three or four limitations rather than reading all eight: values are estimates; no causal claims because age, minutes, league and club overlap; no defensive or goalkeeper statistics and no injury data; the thresholds are my choices. Then thank the audience and invite questions.

**Transition:** "Thank you, happy to take questions."

## Backup deck: title slide

**What to say:** Separate file (DATA400_market_value_backup_slides.pptx). Open it only when a question needs one of these slides.

## Backup A: cleaning

**What to say:** Exact exclusion counts in the order the rules were applied: 9 missing position, 5 missing birth date, 490 no valuation, 416 stale valuation. 23,328 rows (72.8%) have at least 450 minutes.

**Number to remember:** 920 excluded

## Backup B: K-means details

**What to say:** Silhouette and inertia for k = 2-6, cluster sizes and medians, stability. Stability means repeated runs give nearly the same groups (adjusted Rand index minimum 0.92, median 0.97); that is not the same as the groups being well separated.

**Number to remember:** Silhouette 0.207 at k = 4

**Caution:** Stable is not the same as well separated.

## Backup C: segments

**What to say:** Rule-based segments: high scorers (goals/90 at least 0.40), creative (assists/90 at least 0.23), then age bands. I define these, so call them segments, not clusters.

**Number to remember:** High scorers €6M, creative €4M

## Backup D: league medians

**What to say:** All 14 league medians, highest to lowest.

**Number to remember:** Lowest top-five (€3M) is 3x the highest other league (€1M)

## Backup E: playing time

**What to say:** Spearman 0.51 between minutes and value. Explain the two-way direction: clubs play players they value, and playing raises value.

**Number to remember:** 0.51

**Caution:** Do not say more minutes cause higher value.
