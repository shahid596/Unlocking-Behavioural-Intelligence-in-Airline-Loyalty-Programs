# Unlocking Behavioral Intelligence in Airline Loyalty Programs

An end-to-end analysis for a mid-sized airline's loyalty program (~16,700 Canadian
members, flight activity covering 2017-2018): predict which members are likely to
churn, segment members by behavior + value (not just raw CLV), and turn both into
specific, actionable retention recommendations.

## Project structure

```
├── 1_Data_Understanding.ipynb        # initial exploration of the raw data
├── 2_Data_Cleaning_Final.ipynb       # cleaning, missing values, duplicates, outliers
├── Feature_Engineering.ipynb         # churn label, cutoff windows, feature list
├── Churn_Prediction_Model.ipynb      # Random Forest churn model
├── Customer_Segmentation.ipynb       # KMeans segmentation
├── Retention_Playbook.ipynb          # segment + risk -> specific action
├── app.py                            # Streamlit dashboard
│
├── Airline_Loyalty_Data_Dictionary.csv
├── Calendar.csv
├── customer_flight_activity_cleaned.csv     # output of notebook 2
├── customer_loyalty_history_cleaned.csv     # output of notebook 2
├── Final_dataset.csv                        # output of Feature_Engineering.ipynb
├── customer_churn_scored.csv                # output of Churn_Prediction_Model.ipynb
├── customer_segments.csv                    # output of Customer_Segmentation.ipynb
├── customer_action_list.csv                 # output of Retention_Playbook.ipynb
└── retention_playbook.csv                   # output of Retention_Playbook.ipynb
```

Each notebook reads the file the previous one saved, so **run them in the order
above** the first time. After that, any single notebook can be re-run on its own.

## How to run it

**Notebooks:** open each `.ipynb` in Jupyter or Google Colab and run all cells, in
the order listed above. Each one saves a CSV that the next one depends on.

**Dashboard:**
```
pip install streamlit pandas
python -m streamlit run app.py
```
(`python -m streamlit ...` avoids PATH issues on Windows where the plain `streamlit`
command sometimes isn't recognized.)

Two things the dashboard needs to actually work:
1. Run in Command Prompt / terminal from **inside this project folder** — use
   `cd /d "path\to\this\folder"` on Windows if the folder is on a different drive
   than your terminal opened on.
2. `customer_action_list.csv` and `retention_playbook.csv` must be sitting in the
   **same folder** as `app.py` — it reads them by filename only, not a full path.

## How churn is defined (and why)

The dataset has a formal cancellation field, but that's not the only kind of churn
that matters — someone can stay enrolled but simply stop flying. A member is
labeled **churned** if either is true:

1. They formally cancelled, **or**
2. They used to fly, but flew **zero times in the label window** ("went silent")

**Avoiding data leakage:** features are built only from the feature window (before
the cutoff). Whether someone churned is checked only in the label window (after the
cutoff). `Feature_Engineering.ipynb` includes an explicit correlation-based check to
confirm no leaky column (like `Cancellation Year`) snuck into the feature list.

## The churn model

A single `RandomForestClassifier` (scikit-learn) with `class_weight="balanced"`,
since churn is rare (~5.6% of members). On the held-out test set: ~91% accuracy,
~60% recall, ~33% precision on the churned class. The precision is the honest
trade-off worth flagging in the report — roughly 2 in 3 flagged members won't
actually churn, but since a false positive just costs a retention offer (not a real
loss), erring toward catching more true churners (higher recall) is the right call
for this business problem.

Top predictors: recency (months since last flight), months active, and tenure —
all intuitive and easy to defend to a CFO/CMO.

## Segmentation

`KMeans` (K=5, chosen via the elbow method) over flight frequency, distance,
redemption rate, recency, and CLV — standardized first so no single feature
dominates just because it's on a bigger scale. Segments are named from their
actual behavior after clustering, not a fixed label per cluster number (KMeans can
hand out different numbers to the same "shape" of segment on different runs).

Resulting segments: **Champions**, **Loyal Flyers**, **Occasional Travelers**, and
**Dormant / Never Flew** — with Dormant members showing by far the highest average
churn risk (~76%) and Champions the lowest (~21%), which cross-validates the churn
model's own findings.

## Retention playbook

For every (segment, risk tier) combination, `Retention_Playbook.ipynb` assigns a
specific action — who receives it, what the offer is, when it triggers, and why —
rather than a generic "offer bonus points" recommendation. See
`retention_playbook.csv` for the full table, and `customer_action_list.csv` for the
per-member version the dashboard reads from.

Estimated revenue at risk (CLV x churn probability, summed across all members):
**~$30M**, with **~$6.2M** of CLV sitting in the High Risk tier alone.

## Known limitations

- Members who enrolled after the feature-window cutoff are excluded from modeling
  (no fair history exists for them yet) — worth stating explicitly if presenting
  this, since a real ops team would ask about brand-new members.
- Missing salary values (all from the "College" education group) were filled with
  the overall population median, which likely over- or under-states true salary
  for that group.
- The "went silent" churn definition is one reasonable choice, not the only one —
  worth testing a different window length against real business outcomes if this
  were deployed for real.

