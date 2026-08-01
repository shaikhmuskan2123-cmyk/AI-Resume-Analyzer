import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analyzer import analyze_resume

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

html,body,[class*="css"]{
    font-family:Segoe UI;
}

.main{
    background:#f5f7fb;
}

.block-container{
    padding-top:4rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;
}
.title{
    font-size:40px;
    font-weight:700;
    color:#0b5394;
}

.subtitle{
    color:gray;
    font-size:18px;
    margin-bottom:20px;
}

.metric-card{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 0px 8px rgba(0,0,0,.15);
}

.rank1{
    background:#e6ffe6;
    padding:10px;
    border-radius:10px;
}

.rank2{
    background:#fff7d6;
    padding:10px;
    border-radius:10px;
}

.rank3{
    background:#f8f8f8;
    padding:10px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    "<div class='title'>🤖 AI Resume Analyzer & ATS System</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Analyze multiple resumes against one Job Description</div>",
    unsafe_allow_html=True
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Settings")

minimum_score = st.sidebar.slider(
    "Minimum ATS Score",
    0,
    100,
    0
)

show_charts = st.sidebar.checkbox(
    "Show Charts",
    True
)

show_table = st.sidebar.checkbox(
    "Show Ranking Table",
    True
)

search_name = st.sidebar.text_input(
    "Search Candidate"
)

# -----------------------------
# FILE UPLOADS
# -----------------------------
st.header("Upload Files")

col1,col2 = st.columns(2)

with col1:

    jd = st.file_uploader(
        "Upload Job Description",
        type=["pdf","docx"]
    )

with col2:

    resumes = st.file_uploader(
        "Upload Resumes",
        type=["pdf","docx"],
        accept_multiple_files=True
    )

# -----------------------------
# WAIT FOR FILES
# -----------------------------
if jd is None:

    st.info("Upload a Job Description to begin.")
    st.stop()

if resumes is None or len(resumes)==0:

    st.info("Upload one or more resumes.")
    st.stop()

# -----------------------------
# READ JD TEXT
# -----------------------------
from analyzer import extract_text

jd_text = extract_text(jd)

# -----------------------------
# ANALYZE ALL RESUMES
# -----------------------------
results = []

progress = st.progress(0)

status = st.empty()

total = len(resumes)

for i,resume in enumerate(resumes):

    status.text(f"Analyzing {resume.name}")

    data = analyze_resume(resume,jd_text)

    data["Resume File"] = resume.name

    results.append(data)

    progress.progress((i+1)/total)

status.success("Analysis Completed")

progress.empty()

# -----------------------------
# DATAFRAME
# -----------------------------
df = pd.DataFrame(results)

df = df.sort_values(
    by="ATS Score",
    ascending=False
).reset_index(drop=True)

df.insert(0,"Rank",range(1,len(df)+1))

# -----------------------------
# FILTER
# -----------------------------
df = df[df["ATS Score"]>=minimum_score]

if search_name!="":

    df = df[
        df["Candidate"]
        .str.lower()
        .str.contains(search_name.lower(),na=False)
    ]

if len(df)==0:

    st.warning("No resumes match current filters.")
    st.stop()

# -----------------------------
# TOP METRICS
# -----------------------------
highest = df["ATS Score"].max()

average = round(df["ATS Score"].mean(),2)

total_candidates = len(df)

matched = len(df[df["ATS Score"]>=70])

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric(
        "Candidates",
        total_candidates
    )

with c2:
    st.metric(
        "Highest Score",
        highest
    )

with c3:
    st.metric(
        "Average Score",
        average
    )

with c4:
    st.metric(
        "Qualified",
        matched
    )

st.divider()

# -----------------------------
# TOP 3
# -----------------------------
st.subheader("🏆 Top Candidates")

top = df.head(3)

cols = st.columns(3)

for i,row in top.iterrows():

    with cols[i]:

        if row["Rank"]==1:
            css="rank1"

        elif row["Rank"]==2:
            css="rank2"

        else:
            css="rank3"

        st.markdown(
            f"""
            <div class="{css}">
            <h3>{row['Candidate']}</h3>
            <b>ATS Score:</b> {row['ATS Score']}<br>
            <b>Experience:</b> {row['Experience']} Years<br>
            <b>Email:</b> {row['Email']}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ==========================================================
# RANKING TABLE
# ==========================================================

if show_table:

    st.subheader("📋 Resume Ranking")

    display_df = df[
        [
            "Rank",
            "Candidate",
            "ATS Score",
            "Semantic Score",
            "Skill Score",
            "Experience",
            "Education",
            "Email"
        ]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================================
# DOWNLOAD CSV
# ==========================================================

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Ranking CSV",
    data=csv,
    file_name="resume_ranking.csv",
    mime="text/csv"
)

st.divider()

# ==========================================================
# CHARTS
# ==========================================================

if show_charts:

    st.subheader("📊 Resume Analytics")

    col1,col2=st.columns(2)

    with col1:

        fig=px.bar(
            df,
            x="Candidate",
            y="ATS Score",
            color="ATS Score",
            text="ATS Score",
            title="ATS Score Comparison"
        )

        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig2=px.bar(
            df,
            x="Candidate",
            y="Semantic Score",
            color="Semantic Score",
            text="Semantic Score",
            title="Semantic Similarity"
        )

        fig2.update_layout(height=450)

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    col3,col4=st.columns(2)

    with col3:

        fig3=px.scatter(
            df,
            x="Experience",
            y="ATS Score",
            size="Semantic Score",
            color="ATS Score",
            hover_name="Candidate",
            title="Experience vs ATS"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    with col4:

        avg_skill=df["Skill Score"].mean()
        avg_semantic=df["Semantic Score"].mean()
        avg_ats=df["ATS Score"].mean()

        radar=go.Figure()

        radar.add_trace(go.Scatterpolar(
            r=[
                avg_skill,
                avg_semantic,
                avg_ats
            ],
            theta=[
                "Skill Match",
                "Semantic",
                "ATS"
            ],
            fill="toself",
            name="Average"
        ))

        radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0,100]
                )
            ),
            showlegend=False,
            title="Overall Performance"
        )

        st.plotly_chart(
            radar,
            use_container_width=True
        )

st.divider()

# ==========================================================
# DETAILED CANDIDATE VIEW
# ==========================================================

st.subheader("👤 Candidate Details")

candidate=st.selectbox(

    "Select Candidate",

    df["Candidate"]

)

row=df[df["Candidate"]==candidate].iloc[0]

left,right=st.columns([2,1])

with left:

    st.markdown("### Resume Information")

    st.write("**Name:**",row["Candidate"])

    st.write("**Email:**",row["Email"])

    st.write("**Phone:**",row["Phone"])

    st.write("**Experience:**",row["Experience"],"Years")

    st.write("**Education:**",row["Education"])

    st.write("**GitHub:**",row["GitHub"])

    st.write("**LinkedIn:**",row["LinkedIn"])

with right:

    st.metric(
        "ATS Score",
        row["ATS Score"]
    )

    st.metric(
        "Semantic",
        row["Semantic Score"]
    )

    st.metric(
        "Skill Match",
        row["Skill Score"]
    )

st.divider()

# ==========================================================
# SKILLS
# ==========================================================

colA,colB=st.columns(2)

with colA:

    st.subheader("✅ Candidate Skills")

    skills=row["Skills"]

    if skills!="":

        for s in skills.split(","):

            st.success(s.strip())

with colB:

    st.subheader("❌ Missing Skills")

    miss=row["Missing Skills"]

    if miss!="":

        for s in miss.split(","):

            st.error(s.strip())

        if miss.strip()=="":
            st.success("No Missing Skills")

st.divider()

# ==========================================================
# ATS FEEDBACK
# ==========================================================

st.subheader("📝 ATS Feedback")

feedback=[]

if row["ATS Score"]>=90:

    feedback.append("Excellent resume.")

elif row["ATS Score"]>=75:

    feedback.append("Very good resume.")

elif row["ATS Score"]>=60:

    feedback.append("Good resume but needs improvements.")

else:

    feedback.append("Resume requires significant improvement.")

if row["GitHub"]=="Not Found":

    feedback.append("Add GitHub profile.")

if row["LinkedIn"]=="Not Found":

    feedback.append("Add LinkedIn profile.")

if row["Experience"]==0:

    feedback.append("Mention internships or experience.")

missing=row["Missing Skills"]

if missing!="":

    feedback.append(
        "Include missing skills: "+missing
    )

for item in feedback:

    st.write("•",item)

st.divider()

# ==========================================================
# SKILL FREQUENCY ANALYSIS
# ==========================================================

st.subheader("📌 Skill Frequency")

skill_dict = {}

for skills in df["Skills"]:

    if pd.isna(skills):
        continue

    for skill in skills.split(","):

        skill = skill.strip()

        if skill == "":
            continue

        skill_dict[skill] = skill_dict.get(skill,0)+1

if len(skill_dict)>0:

    skill_df = pd.DataFrame({

        "Skill":skill_dict.keys(),

        "Count":skill_dict.values()

    })

    skill_df = skill_df.sort_values(

        "Count",

        ascending=False

    ).head(15)

    fig = px.bar(

        skill_df,

        x="Skill",

        y="Count",

        color="Count",

        text="Count",

        title="Top Skills"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

st.divider()

# ==========================================================
# EXPERIENCE DISTRIBUTION
# ==========================================================

st.subheader("💼 Experience Distribution")

fig = px.histogram(

    df,

    x="Experience",

    nbins=10,

    title="Years of Experience"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ==========================================================
# ATS GAUGE
# ==========================================================

st.subheader("🎯 Selected Candidate ATS")

gauge = go.Figure(

    go.Indicator(

        mode="gauge+number",

        value=row["ATS Score"],

        title={"text":"ATS Score"},

        gauge={

            "axis":{"range":[0,100]},

            "bar":{"color":"green"},

            "steps":[

                {"range":[0,50],"color":"#ffb3b3"},

                {"range":[50,75],"color":"#fff0b3"},

                {"range":[75,100],"color":"#b3ffb3"}

            ]

        }

    )

)

st.plotly_chart(

    gauge,

    use_container_width=True

)

st.divider()

# ==========================================================
# CANDIDATE COMPARISON
# ==========================================================

st.subheader("📊 Compare Candidates")

compare = st.multiselect(

    "Select Candidates",

    df["Candidate"]

)

if len(compare)>=2:

    compare_df = df[

        df["Candidate"].isin(compare)

    ]

    fig = px.bar(

        compare_df,

        x="Candidate",

        y=[

            "ATS Score",

            "Semantic Score",

            "Skill Score"

        ],

        barmode="group",

        title="Candidate Comparison"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

st.divider()

# ==========================================================
# BEST CANDIDATE
# ==========================================================

best = df.iloc[0]

st.success(

f"""

🏆 Best Candidate

Name : {best['Candidate']}

ATS Score : {best['ATS Score']}

Experience : {best['Experience']} Years

Email : {best['Email']}

"""

)

st.divider()

# ==========================================================
# SUMMARY
# ==========================================================

st.subheader("📈 Summary")

col1,col2,col3 = st.columns(3)

with col1:

    st.info(

        f"Average ATS Score : {round(df['ATS Score'].mean(),2)}"

    )

with col2:

    st.info(

        f"Highest ATS Score : {df['ATS Score'].max()}"

    )

with col3:

    st.info(

        f"Candidates : {len(df)}"

    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(

"""

---

### 🤖 AI Resume Analyzer

Developed using

- Python

- Streamlit

- spaCy

- Scikit-Learn

- Plotly

- Pandas

Features

✅ Resume Ranking

✅ ATS Score

✅ Semantic Matching

✅ Skill Analysis

✅ Candidate Comparison

✅ Charts

✅ CSV Export

"""

)