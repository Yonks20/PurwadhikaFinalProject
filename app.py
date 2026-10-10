from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Term Deposit Campaign Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).with_name("bank-additional-full.csv")
OVERALL_RATE = 11.27
MONTH_ORDER = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root { --navy: #102a43; --teal: #177e89; --gold: #d7a528; --mist: #f5f8fa; }
            .stApp { background: #f7f9fb; }
            [data-testid="stSidebar"] { background: #102a43; }
            [data-testid="stSidebar"] * { color: #f7f9fb; }
            [data-testid="stSidebar"] [data-baseweb="select"] > div {
                background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.18);
            }
            [data-testid="stSidebar"] [data-baseweb="tag"] { background: #177e89; }
            [data-testid="stSidebar"] [data-testid="stExpander"] {
                border: 1px solid rgba(255,255,255,.17); border-radius: 12px; background: rgba(255,255,255,.04);
            }
            .bank-hero {
                background: linear-gradient(115deg, #102a43 0%, #173f5f 66%, #177e89 100%);
                color: white; padding: 1.7rem 2rem; border-radius: 18px; margin: .25rem 0 1.25rem;
                box-shadow: 0 10px 24px rgba(16,42,67,.16);
            }
            .bank-kicker { color: #f4d06f; font-weight: 700; font-size: .78rem; letter-spacing: .11em; text-transform: uppercase; }
            .bank-hero h1 { color: white; margin: .25rem 0 .45rem; font-size: 2.05rem; }
            .bank-hero p { color: #dce8ee; margin: 0; max-width: 850px; }
            [data-testid="stMetric"] { background: white; border: 1px solid #e4ebf0; border-radius: 14px; padding: .85rem 1rem; }
            [data-testid="stMetricLabel"] { color: #527080; font-size: .82rem; }
            [data-testid="stMetricValue"] { color: #102a43; }
            button[kind="secondary"] { border-radius: 9px; border-color: #d7a528; color: #8a6612; }
            .filter-note { color: #b9c9d6; font-size: .82rem; margin: .35rem 0 .75rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """Load the campaign-level bank marketing dataset."""
    data = pd.read_csv(path, sep=";")
    data["subscribed"] = data["y"].eq("yes")
    return data


def subscription_by(data: pd.DataFrame, column: str) -> pd.DataFrame:
    summary = (
        data.groupby(column, dropna=False, observed=False)["subscribed"]
        .agg(Observations="size", Subscriptions="sum", Subscription_Rate="mean")
        .reset_index()
    )
    summary["Subscription Rate (%)"] = summary.pop("Subscription_Rate") * 100
    return summary.sort_values("Subscription Rate (%)", ascending=False)


def clean_chart(fig):
    """Keep Plotly visuals consistent regardless of the browser theme."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_color="#102a43",
        legend_title_text="",
        xaxis=dict(gridcolor="#e8eef2", zerolinecolor="#e8eef2"),
        yaxis=dict(gridcolor="#e8eef2", zerolinecolor="#e8eef2"),
    )
    return fig


def reset_filters() -> None:
    """Clear filter state before Streamlit renders the widgets again."""
    for key in ("month_filter", "contact_filter", "job_filter"):
        st.session_state[key] = []


def rate_bar(data: pd.DataFrame, category: str, title: str, height: int = 390):
    summary = subscription_by(data, category).sort_values("Subscription Rate (%)")
    fig = px.bar(
        summary,
        x="Subscription Rate (%)",
        y=category,
        orientation="h",
        color="Subscription Rate (%)",
        color_continuous_scale="Teal",
        hover_data={"Observations": ":,", "Subscriptions": ":,"},
        title=title,
        text="Subscription Rate (%)",
    )
    fig.add_vline(
        x=OVERALL_RATE,
        line_dash="dash",
        line_color="#e76f51",
        annotation_text=f"Overall rate: {OVERALL_RATE:.2f}%",
        annotation_position="top right",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=height,
        coloraxis_showscale=False,
        margin=dict(l=10, r=25, t=60, b=10),
        xaxis_title="Subscription Rate (%)",
        yaxis_title=None,
    )
    return clean_chart(fig)


def main() -> None:
    inject_styles()

    if not DATA_PATH.exists():
        st.error(f"Dataset tidak ditemukan: `{DATA_PATH.name}`")
        st.stop()

    df = load_data(DATA_PATH)

    st.sidebar.markdown("## Campaign filters")
    st.sidebar.markdown("<p class='filter-note'>Optional — leave empty to include all campaign records.</p>", unsafe_allow_html=True)
    month_options = [month for month in MONTH_ORDER if month in df["month"].unique()]
    with st.sidebar.expander("Refine campaign data", expanded=True):
        selected_months = st.multiselect(
            "Month", month_options, placeholder="All months", key="month_filter"
        )
        selected_contacts = st.multiselect(
            "Contact channel", sorted(df["contact"].unique()), placeholder="All channels", key="contact_filter"
        )
        selected_jobs = st.multiselect(
            "Job", sorted(df["job"].unique()), placeholder="All jobs", key="job_filter"
        )
        st.button("Reset filters", use_container_width=True, on_click=reset_filters)

    selected_months = selected_months or month_options
    selected_contacts = selected_contacts or list(df["contact"].unique())
    selected_jobs = selected_jobs or list(df["job"].unique())

    filtered = df.loc[
        df["month"].isin(selected_months)
        & df["contact"].isin(selected_contacts)
        & df["job"].isin(selected_jobs)
    ].copy()

    if filtered.empty:
        st.warning("Tidak ada observasi untuk kombinasi filter ini. Ubah filter di sidebar.")
        st.stop()

    st.markdown(
        """
        <section class="bank-hero">
            <div class="bank-kicker">Campaign intelligence · term deposit</div>
            <h1>Know where to focus the next call.</h1>
            <p>Explore historical campaign patterns, identify stronger segments, and use validated model evidence to support outreach prioritization.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    total_contacts = len(filtered)
    total_subscriptions = int(filtered["subscribed"].sum())
    subscription_rate = filtered["subscribed"].mean() * 100
    median_contacts = filtered["campaign"].median()

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("Campaign contacts", f"{total_contacts:,}")
    kpi_2.metric("Subscriptions", f"{total_subscriptions:,}")
    kpi_3.metric("Subscription rate", f"{subscription_rate:.2f}%", f"{subscription_rate - OVERALL_RATE:+.2f} pp vs overall")
    kpi_4.metric("Median contacts / campaign", f"{median_contacts:.0f}")

    overview_tab, campaign_tab, segment_tab, model_tab, data_tab = st.tabs(
        ["Overview", "Campaign performance", "Customer segments", "Model result", "Data explorer"]
    )

    with overview_tab:
        left, right = st.columns([0.85, 1.15])
        with left:
            target_counts = (
                filtered["y"].value_counts().rename_axis("Subscription").reset_index(name="Contacts")
            )
            target_counts["Subscription"] = target_counts["Subscription"].map(
                {"yes": "Subscribed", "no": "Not subscribed"}
            )
            fig = px.pie(
                target_counts,
                names="Subscription",
                values="Contacts",
                hole=0.62,
                color="Subscription",
                color_discrete_map={"Subscribed": "#2a9d8f", "Not subscribed": "#d9e2e8"},
                title="Campaign outcome mix",
            )
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(height=390, margin=dict(l=10, r=10, t=60, b=10))
            st.plotly_chart(clean_chart(fig), width="stretch")
        with right:
            month_order = ["mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
            month_summary = subscription_by(filtered, "month")
            month_summary["month"] = pd.Categorical(month_summary["month"], categories=month_order, ordered=True)
            month_summary = month_summary.sort_values("month")
            fig = px.line(
                month_summary,
                x="month",
                y="Subscription Rate (%)",
                markers=True,
                title="Historical subscription rate by campaign month",
                hover_data={"Observations": ":,", "Subscriptions": ":,"},
            )
            fig.add_hline(y=OVERALL_RATE, line_dash="dash", line_color="#e76f51")
            fig.update_traces(line_color="#264653", marker_color="#2a9d8f")
            fig.update_layout(height=390, margin=dict(l=10, r=10, t=60, b=10), yaxis_title="Subscription Rate (%)")
            st.plotly_chart(clean_chart(fig), width="stretch")

        st.info(
            "Interpretasi: visual ini menunjukkan association pada data historis, bukan bukti bahwa "
            "channel atau bulan tertentu secara langsung menyebabkan subscription."
        )

    with campaign_tab:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(rate_bar(filtered, "contact", "Subscription rate by contact channel"), width="stretch")
        with right:
            st.plotly_chart(rate_bar(filtered, "poutcome", "Subscription rate by previous campaign outcome"), width="stretch")

        campaign_bins = [0, 1, 2, 3, 5, 10, float("inf")]
        campaign_labels = ["1", "2", "3", "4-5", "6-10", ">10"]
        campaign_group = filtered.copy()
        campaign_group["Current campaign contacts"] = pd.cut(
            campaign_group["campaign"], bins=campaign_bins, labels=campaign_labels
        )
        fig = rate_bar(
            campaign_group,
            "Current campaign contacts",
            "Subscription rate by current campaign intensity",
            height=430,
        )
        st.plotly_chart(fig, width="stretch")

    with segment_tab:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(rate_bar(filtered, "job", "Subscription rate by job", height=500), width="stretch")
        with right:
            age_group = filtered.copy()
            age_group["Age group"] = pd.cut(
                age_group["age"],
                bins=[0, 29, 39, 49, 59, 69, 120],
                labels=["≤29", "30-39", "40-49", "50-59", "60-69", "70+"],
            )
            st.plotly_chart(rate_bar(age_group, "Age group", "Subscription rate by age group", height=500), width="stretch")

    with model_tab:
        st.subheader("Validated model evidence from the notebook")
        st.caption(
            "The dashboard reports notebook-validated results. It does not retrain or score clients because no deployed model artifact is included."
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Selected model", "Gradient Boosting + ROS")
        m2.metric("5-fold CV AP", "0.4634")
        m3.metric("Untouched test AP", "0.4810")

        model_results = pd.DataFrame(
            {
                "Threshold": [0.50, 0.60],
                "Precision": [0.3811, 0.4381],
                "Recall": [0.6595, 0.6142],
                "F1-score": [0.4830, 0.5114],
                "Targeted clients": [1606, 1301],
            }
        )
        left, right = st.columns([1.1, 0.9])
        with left:
            metric_chart = model_results.melt(
                id_vars="Threshold", value_vars=["Precision", "Recall", "F1-score"],
                var_name="Metric", value_name="Score"
            )
            fig = px.line(metric_chart, x="Threshold", y="Score", color="Metric", markers=True,
                          title="Test-set threshold scenarios")
            fig.update_layout(yaxis_range=[0, 1], height=360, margin=dict(l=10, r=10, t=60, b=10))
            st.plotly_chart(clean_chart(fig), width="stretch")
        with right:
            st.dataframe(model_results, hide_index=True, width="stretch", column_config={
                "Precision": st.column_config.NumberColumn(format="%.3f"),
                "Recall": st.column_config.NumberColumn(format="%.3f"),
                "F1-score": st.column_config.NumberColumn(format="%.3f"),
                "Targeted clients": st.column_config.NumberColumn(format="%,d"),
            })

        st.warning(
            "`duration` is excluded from production-oriented scoring: it becomes known after a call completes and would leak outcome information. "
            "Thresholds are operating scenarios, not financially optimized recommendations."
        )

    with data_tab:
        st.subheader("Filtered campaign records")
        visible_columns = [col for col in filtered.columns if col not in ["subscribed"]]
        st.dataframe(filtered[visible_columns], width="stretch", height=460)
        csv = filtered[visible_columns].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download filtered data as CSV",
            data=csv,
            file_name="bank_campaign_filtered.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
