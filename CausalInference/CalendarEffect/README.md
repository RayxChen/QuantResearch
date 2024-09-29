## Weekend/Weekday Effect on Sector Statistics

This project includes an analysis of the weekday effect on sector statistics, with a focus on the Banks sector. We examine how the Banks sector performs on different days of the week, compared to classic behavior financial theory. This analysis can reveal which days tend to be most profitable for bank stocks

![Sector Weekday Effect](./Banks/stats/sector_weekday_effect.jpg)

## Causal Study of the stats

The analysis further includes a causal study controlling the possible confounders @config.yaml, confirming the causality of the weekend effect (the bar effect in on next business day). 

![Weekday Effect](./Banks/causal_studies/weekday_effect/weekday_effect.jpg)


## Bulge Brackets

Goldman Sachs, JP Morgan especially GS have slightly different patterns on Monday possibly due to their investment banking business model. 

![Goldman Sachs](./Banks/stats/weekday_effect/GS_weekday_effect.jpg)

![JPMorgan Chase](./Banks/stats/weekday_effect/JPM_weekday_effect.jpg)


## What About Month?

While this time the possibly confounders are numerous, 
@config.yaml. We confirm the sector performs well in Apr, Jul, Oct, Nov, Dec but with different weights.

![Sector Month Effect](./Banks/stats/sector_month_effect.jpg)

![Month Effect](./Banks/causal_studies/month_effect/month_effect.jpg)