# app.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Cache data loading
@st.cache_data
def load_data():
    df = pd.read_csv('clean_anemia_prevalence.csv')
    return df

anemia_df = load_data()

# Set page config first
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Custom color palette
palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

# CSS to adjust spacing and fonts
st.markdown(
    """
    <style>
        .block-container { padding-top: 0rem; }
        h1 { font-size: 2.5rem !important; }
        h3 { font-size: 1.4rem !important; margin-top: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app
st.markdown("# Anaemia Prevalence Dashboard")

# Sidebar filters
with st.sidebar:
    st.header("Filters")

    # Reset button
    if st.button("🔄 Clear filters"):
        st.experimental_rerun()
    
    gender = st.multiselect(
        "Gender", 
        sorted(anemia_df['gender'].unique()),
        default=sorted(anemia_df['gender'].unique())
    )
    
    country = st.multiselect(
        "Country", 
        options=sorted(anemia_df['country'].unique()),
        default=[anemia_df['country'].unique()[0]]
    )
    
    dimension_df = anemia_df[
        (anemia_df['gender'].isin(gender)) & (anemia_df['country'].isin(country))
    ]

    dimension_options = sorted(dimension_df['dimension'].dropna().unique())

    dimension = st.selectbox(
        "Dimension", 
        dimension_options,
        index=0 if dimension_options else None
    )
    
    st.markdown("---")
    st.caption("📊 **Source:** WHO Global Health Observatory")
    st.caption("👨🏻‍💻 **Dashboard by Nader Abdul Salam**")

# Filter data for bar chart
filtered_df = anemia_df[
    (anemia_df['gender'].isin(gender)) & (anemia_df['country'].isin(country)) & (anemia_df['dimension'] == dimension)
]

# Bar chart: Gender comparison
chart_df = filtered_df[['country', 'gender', 'group', 'prevalence']]

bar_chart = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X('group:N', title='Group', axis=alt.Axis(labelAngle=-40)),
    xOffset='gender:N',
    y=alt.Y('prevalence:Q', title='Prevalence (%)'),
    color=alt.Color('gender:N', scale=alt.Scale(range=palette[:2])),
    tooltip=['country', 'gender', 'group', 'prevalence']
).properties(
    title=f"Gender Comparison - {dimension}"
)

# Trend chart
trend_df = anemia_df[
    (anemia_df['gender'].isin(gender)) & (anemia_df['country'].isin(country))
].groupby(['country', 'gender', 'dimension'])['prevalence'].mean().reset_index()

trend_chart = alt.Chart(trend_df).mark_line(point=True, strokeWidth=3).encode(
    x=alt.X('dimension:N', title='Dimension', sort=alt.EncodingSortField(field="dimension", order="ascending")),
    y=alt.Y('prevalence:Q', title='Prevalence (%)'),
    color=alt.Color('country:N', scale=alt.Scale(range=palette), title='Country'),
    strokeDash=alt.StrokeDash('gender:N', legend=None),
    tooltip=['country', 'gender', 'dimension', 'prevalence']
).properties(
    title=f"Trend across Dimensions"
)

# --- Top charts ---
col1, col2, col3 = st.columns([2,2,2])

with col1:
    st.altair_chart(bar_chart.properties(height=360), use_container_width=True)

with col2:
    st.altair_chart(trend_chart.properties(height=360), use_container_width=True)
    st.caption("**Legend:** Male = dashed line, Female = solid line")

# --- Total prevalence per country ---
total_df = anemia_df[
    (anemia_df['gender'].isin(gender)) & (anemia_df['country'].isin(country))
].groupby('country')['prevalence'].mean().reset_index()

total_chart = alt.Chart(total_df).mark_bar().encode(
    x=alt.X('country:N', title='Country'),
    y=alt.Y('prevalence:Q', title='Prevalence (%)'),
    color=alt.Color('country:N', scale=alt.Scale(range=palette), legend=None),
    tooltip=['country', 'prevalence']
).properties(
    title="Country Comparison"
)

with col3:
    st.altair_chart(total_chart, use_container_width=True)

# --- Average Anaemia Prevalence ---
summary_df = anemia_df[
    (anemia_df['gender'].isin(gender)) & (anemia_df['country'].isin(country))
].groupby('gender')['prevalence'].mean().reset_index()

# Dynamic country label
if len(country) == 1:
    country_label = f"in {country[0]}"
else:
    country_label = "in selected countries"

with col1:
    st.subheader(f"Average Anaemia Prevalence {country_label}")
    female_val = summary_df[summary_df['gender'] == 'Female']['prevalence'].values[0] if 'Female' in summary_df['gender'].values else None
    male_val = summary_df[summary_df['gender'] == 'Male']['prevalence'].values[0] if 'Male' in summary_df['gender'].values else None
    
    if female_val is not None:
        st.metric(label="Female", value=f"{female_val:.1f} %")
    if male_val is not None:
        st.metric(label="Male", value=f"{male_val:.1f} %")

# --- Top 5 countries globally ---
top5_df = anemia_df[
    (anemia_df['gender'].isin(gender))
].groupby('country')['prevalence'].mean().reset_index().sort_values(by='prevalence', ascending=False).head(5)

with col2:
    st.subheader("Top 5 Countries with Highest Anaemia Prevalence")
    st.dataframe(top5_df, use_container_width=True)

# --- Correlation chart ---
scatter_df = anemia_df[
    (anemia_df['dimension'] == dimension)
]

scatter_chart = alt.Chart(scatter_df).mark_circle(size=100).encode(
    x=alt.X('group:N', title=dimension),
    y=alt.Y('prevalence:Q', title='Anaemia Prevalence (%)'),
    color=alt.Color('gender:N', scale=alt.Scale(range=palette[:2])),
    tooltip=['country', 'gender', 'group', 'prevalence']
).properties(
    title=f"Correlation: {dimension} vs Anaemia Prevalence"
)

with col3:
    st.altair_chart(scatter_chart, use_container_width=True)

# --- Download button ---
st.markdown("---")
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='anaemia_filtered_data.csv',
    mime='text/csv'
)

# --- Global average ---
global_df = anemia_df.groupby('gender')['prevalence'].mean().reset_index()

with st.expander("🌍 Global Average Anaemia Prevalence"):
    col_g1, col_g2 = st.columns(2)
    g_female = global_df[global_df['gender'] == 'Female']['prevalence'].values[0] if 'Female' in global_df['gender'].values else None
    g_male = global_df[global_df['gender'] == 'Male']['prevalence'].values[0] if 'Male' in global_df['gender'].values else None
    
    with col_g1:
        if g_female is not None:
            st.metric(label="Global Female Prevalence", value=f"{g_female:.1f} %")
    with col_g2:
        if g_male is not None:
            st.metric(label="Global Male Prevalence", value=f"{g_male:.1f} %")

# --- Last updated timestamp ---
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"🕒 Last updated: {now}")
