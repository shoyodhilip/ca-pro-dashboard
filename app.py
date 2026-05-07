import streamlit as st
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- GOOGLE SHEETS SETUP ---------------- #

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

client = gspread.authorize(creds)

sheet = client.open("CA_FINAL_TRACKER")

# ---------------- SETTINGS ---------------- #

SUBJECTS = ["FR", "AFM", "Audit", "DT", "IDT"]

EXAM_DATE = datetime(2026, 11, 1)

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="CA Final Pro Dashboard",
    layout="wide"
)

# ---------------- MODERN UI ---------------- #

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3 {
    color: white;
}

div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1E1E2F, #252540);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #333;
    text-align: center;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}

div.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 3em;
    background: linear-gradient(90deg, #4CAF50, #2ECC71);
    color: white;
    border: none;
    font-size: 16px;
    font-weight: bold;
}

.stCheckbox {
    background-color: #1E1E2F;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    border: 1px solid #333;
}

section[data-testid="stSidebar"] {
    background-color: #161A28;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HOURS FIX ---------------- #

def convert_to_hours(duration):

    if duration is None:
        return 0

    try:

        if isinstance(duration, (int, float)):

            if pd.isna(duration):
                return 0

            return float(duration)

        if hasattr(duration, "hour"):
            return duration.hour + duration.minute / 60

        if hasattr(duration, "total_seconds"):
            return duration.total_seconds() / 3600

    except:
        return 0

    return 0

# ---------------- HEADER ---------------- #

st.title("🚀 CA Final Pro Dashboard")

st.markdown("---")

# ---------------- DASHBOARD CALCULATIONS ---------------- #

total_hours = 0
completed_hours = 0

subject_data = {}

for subject in SUBJECTS:

    ws = sheet.worksheet(subject)

    data = ws.get_all_records()

    df = pd.DataFrame(data)

    total = 0
    done = 0

    for index, row in df.iterrows():

        duration = row["Hours"]
        completed = row["Completed"]

        hrs = convert_to_hours(duration)

        total += hrs

        if completed:
            done += hrs

    subject_data[subject] = (done, total)

    total_hours += total
    completed_hours += done

# ---------------- COUNTDOWN ---------------- #

days_left = (EXAM_DATE.date() - date.today()).days

remaining_hours = max(total_hours - completed_hours, 0)

required_per_day = remaining_hours / days_left if days_left > 0 else 0

# ---------------- PRESSURE METER ---------------- #

if required_per_day < 4:
    pressure = "🟢 LOW"
elif required_per_day < 8:
    pressure = "🟡 MEDIUM"
else:
    pressure = "🔴 HIGH"

# ---------------- METRICS ---------------- #

col1, col2, col3, col4 = st.columns(4)

col1.metric("⏳ Days Left", days_left)
col2.metric("📚 Completed Hours", round(completed_hours, 1))
col3.metric("🔥 Required / Day", round(required_per_day, 1))
col4.metric("⚠️ Pressure", pressure)

# ---------------- OVERALL PROGRESS ---------------- #

overall_percent = (completed_hours / total_hours * 100) if total_hours else 0

st.subheader("📈 Overall Progress")

st.progress(overall_percent / 100)

st.write(f"### {overall_percent:.1f}% Completed")

# ---------------- SUBJECT SELECT ---------------- #

st.subheader("📘 Subject Tracker")

selected_subject = st.selectbox(
    "Choose Subject",
    ["Select"] + SUBJECTS,
    index=0
)

# ---------------- SUBJECT TASKS ---------------- #

if selected_subject != "Select":

    ws = sheet.worksheet(selected_subject)

    data = ws.get_all_records()

    df = pd.DataFrame(data)

    st.write(f"## 📖 {selected_subject}")

    for i, row in df.iterrows():

        day = row["Day"]
        part = row["Part"]
        topic = row["Topic"]
        duration = row["Hours"]
        completed = row["Completed"]

        hrs = convert_to_hours(duration)

        checkbox = st.checkbox(
            f"Day {day} | Part {part} | {topic} ({hrs:.1f} hrs)",
            value=bool(completed),
            key=f"{selected_subject}_{i}"
        )

        if checkbox != bool(completed):

            ws.update_cell(i + 2, 5, checkbox)

            if checkbox:
                ws.update_cell(i + 2, 6, str(date.today()))
            else:
                ws.update_cell(i + 2, 6, "")

            st.success("Progress Updated ✅")

            st.rerun()

# ---------------- SUBJECT PROGRESS ---------------- #

st.subheader("📊 Subject Progress")

for subject, values in subject_data.items():

    done, total = values

    percent = (done / total * 100) if total else 0

    st.write(f"### {subject}")

    st.progress(percent / 100)

    st.write(f"{done:.1f}/{total:.1f} hrs")

# ---------------- ADVANCED ANALYTICS ---------------- #

st.subheader("📈 Advanced Analytics")

if total_hours > 0:

    col1, col2 = st.columns(2)

    # PIE CHART
    with col1:

        labels = ["Completed", "Remaining"]

        sizes = [
            completed_hours,
            remaining_hours
        ]

        fig1, ax1 = plt.subplots()

        ax1.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%'
        )

        ax1.set_title("Overall Completion")

        st.pyplot(fig1)

    # BAR CHART
    with col2:

        subjects = list(subject_data.keys())

        percentages = []

        for s in subjects:

            done, total = subject_data[s]

            percent = (done / total * 100) if total else 0

            percentages.append(percent)

        fig2, ax2 = plt.subplots()

        ax2.bar(subjects, percentages)

        ax2.set_ylabel("Completion %")

        ax2.set_title("Subject Wise Progress")

        st.pyplot(fig2)

# ---------------- MOTIVATION ---------------- #

st.markdown("---")

if overall_percent < 25:
    st.warning("🚀 Start pushing harder. Consistency is key.")
elif overall_percent < 50:
    st.info("🔥 Good progress. Keep the momentum going.")
elif overall_percent < 75:
    st.success("💪 Excellent work. You're ahead of many students.")
else:
    st.balloons()
    st.success("🏆 You're very close to CA Final victory!")

# ---------------- FOOTER ---------------- #

st.markdown("---")

st.write("⚡ Built with Streamlit + Google Sheets Cloud Sync")
