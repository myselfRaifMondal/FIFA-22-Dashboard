import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="FIFA 22 Match Analysis")

st.title("📊 FIFA 22 Match Analytics Dashboard")

# Load and cache the data
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")  # ← Change filename if needed
    df.columns = df.columns.str.strip()  # Clean weird spaces

    # Convert % strings to float
    def convert_percent(col):
        return col.str.replace('%', '', regex=False).astype(float)

    percent_cols = ['possession team1', 'possession team2']
    for col in percent_cols:
        if col in df.columns:
            try:
                df[col] = convert_percent(df[col])
            except Exception as e:
                st.warning(f"Could not convert column {col}: {e}")

    return df

df = load_data()

# Sidebar team filter
teams = sorted(set(df['team1'].dropna().unique()).union(set(df['team2'].dropna().unique())))
selected_team = st.sidebar.selectbox("🔍 Select a team to analyze", teams)

# Filter matches involving the selected team
team_df = df[(df['team1'] == selected_team) | (df['team2'] == selected_team)]

st.subheader(f"📁 Match Stats for: {selected_team}")
st.write(f"Total matches found: {team_df.shape[0]}")
st.dataframe(team_df.head(10), use_container_width=True)

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⚽ Avg Possession (%)", 
              round(team_df[['possession team1', 'possession team2']].mean().mean(), 2))
with col2:
    st.metric("🥅 Avg Goals", 
              round(team_df[['number of goals team1', 'number of goals team2']].mean().mean(), 2))
with col3:
    st.metric("🎯 Avg Attempts", 
              round(team_df[['total attempts team1', 'total attempts team2']].mean().mean(), 2))

# Charts section
st.subheader("📈 Possession vs Goals Trend")

fig, ax = plt.subplots(figsize=(10, 4))

team_df = team_df.sort_values(by='date')  # make sure it's chronological

# Determine if selected team is team1 or team2
team1_mask = team_df['team1'] == selected_team
team_possession = team_df['possession team1'].where(team1_mask, team_df['possession team2'])
team_goals = team_df['number of goals team1'].where(team1_mask, team_df['number of goals team2'])

ax.plot(team_df['date'], team_possession, label='Possession (%)', color='blue', marker='o')
ax.plot(team_df['date'], team_goals, label='Goals Scored', color='green', marker='x')
ax.set_xlabel("Date")
ax.set_ylabel("Values")
ax.set_title(f"📅 Match Trends for {selected_team}")
ax.legend()
plt.xticks(rotation=45)

st.pyplot(fig)

