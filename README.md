  # Unlocking Behavioral Intelligence in Airline Loyalty Programs

  An end to end analysis of a airline's loyalty program (16,700 Canadian
  members, flight activity covering 2017-2018) predicting which members are likely to
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

  ## How churn is defined and why

  The dataset has a formal cancellation field but that's not the only kind of churn
  that matters. Someone can stay enrolled but simply stop flying. A member is
  labeled **churned** if either of the following is true:

  1. They formally cancelled.
  2. They used to fly but flew **zero times in the label window** .

  **Avoiding data leakage:** features are built only from the feature window (before
  the cutoff). Whether someone churned is checked only in the label window (after the
  cutoff.

  ## The churn model

  A single RandomForestClassifier with class_weight="balanced"
  since churn is rare (~5.6% of members). On the held-out test set: 91% accuracy,
  60% recall, 33% precision on the churned class. The precision is a
  trade-off here as roughly 2 in 3 flagged members won't
  actually churn, but since a false positive just costs a retention offer (not a real
  loss), erring toward catching more true churners (higher recall) is the right call
  for this business problem.


  ## Segmentation

  KMeans (K=5, chosen via the elbow method) over flight frequency, distance,
  redemption rate, recency, and CLV standardized first so no single feature
  dominates just because it's on a bigger scale. Segments are named from their
  actual behavior after clustering.

  Resulting segments: **Champions**, **Loyal Flyers**, **Occasional Travelers**, **Engaged** and
  **Dormant / Never Flew** with Dormant members showing by far the highest average
  churn risk (76%) and Champions the lowest (21%), which cross-validates the churn
  model's own findings.

  ## Retention playbook

  For every (segment, risk tier) combination, Retention_Playbook.ipynb assigns a
  specific action who receives it, what the offer is, when it triggers, and why.

  ## Known limitations

  - Members who enrolled after the feature-window cutoff are excluded from modeling
    (no fair history exists for them yet) worth stating explicitly if presenting
    this, since a real ops team would ask about brand-new members.
  - Missing salary values (all from the "College" education group) were filled with
    the overall population median, which likely over or under-states true salary
    for that group.
  - The "went silent" churn definition is one reasonable choice, not the only one
    worth testing a different window length against real business outcomes if this
    were deployed for real.

