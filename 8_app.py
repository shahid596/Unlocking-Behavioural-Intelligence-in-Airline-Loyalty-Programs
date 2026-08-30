

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Loyalty Retention Dashboard", layout="wide")

#Load Data

@st.cache_data
def load_data():
    customers = pd.read_csv("Outputs/customer_action_list.csv")
    playbook = pd.read_csv("Outputs/retention_playbook.csv")
    return customers, playbook

customers, playbook = load_data()

st.title("Loyalty Program Retention Dashboard")
st.caption("A first-time user should be able to see who needs attention and what to do about it, right away.")

col1, col2, col3, col4 = st.columns(4)

total_members = len(customers)
high_risk_count = (customers["churn_risk_tier"] == "High Risk").sum()
revenue_at_risk = (customers["CLV"] * customers["churn_risk_score"]).sum()
high_risk_clv = customers.loc[customers["churn_risk_tier"] == "High Risk", "CLV"].sum()

col1.metric("Total Members", f"{total_members:,}")
col2.metric("High Risk Members", f"{high_risk_count:,}")
col3.metric("Est. Revenue at Risk", f"${revenue_at_risk:,.0f}")
col4.metric("CLV in High Risk Tier", f"${high_risk_clv:,.0f}")

st.divider()


st.subheader("Find members who need attention")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_segments = st.multiselect(
        "Segment",
        options=sorted(customers["segment_name"].unique()),
        default=list(customers["segment_name"].unique()),
    )
with filter_col2:
    selected_risk = st.multiselect(
        "Risk tier",
        options=["High Risk", "Medium Risk", "Low Risk"],
        default=["High Risk", "Medium Risk"],
    )

filtered = customers[
    customers["segment_name"].isin(selected_segments)
    & customers["churn_risk_tier"].isin(selected_risk)
].sort_values("CLV", ascending=False)

st.write(f"**{len(filtered):,} members match your filters** (sorted by CLV, highest first)")

st.dataframe(
    filtered[[
        "Loyalty Number", "segment_name", "churn_risk_tier", "churn_risk_score",
        "CLV", "Months Since Last Flight", "recommended_action",
    ]].rename(columns={
        "segment_name": "Segment",
        "churn_risk_tier": "Risk Tier",
        "churn_risk_score": "Risk Score",
        "recommended_action": "Recommended Action",
    }),
    use_container_width=True,
    height=350,
)

st.download_button(
    "Download this list as CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_members.csv",
    mime="text/csv",
)

st.divider()
# The playbook

st.subheader("Retention Playbook: what to do for each group")
st.dataframe(playbook, use_container_width=True, height=400)

st.divider()

#segment overview

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Members by segment")
    st.bar_chart(customers["segment_name"].value_counts())

with chart_col2:
    st.subheader("Average churn risk by segment")
    avg_risk_by_segment = customers.groupby("segment_name")["churn_risk_score"].mean().sort_values(ascending=False)
    st.bar_chart(avg_risk_by_segment)
