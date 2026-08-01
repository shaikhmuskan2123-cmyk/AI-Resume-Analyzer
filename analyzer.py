import re
import math
import pandas as pd
import numpy as np
import spacy

from PyPDF2 import PdfReader
from docx import Document

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

# ===========================
# MASTER SKILLS DATABASE
# ===========================

SKILLS = [

# Programming
"python","java","c","c++","c#","r","go","rust","php",

# Web
"html","css","javascript","typescript","react","angular","vue",
"node","express","flask","django",

# Database
"sql","mysql","postgresql","oracle","mongodb","firebase",

# AI
"machine learning","deep learning","nlp","tensorflow",
"keras","opencv","pytorch","scikit-learn",

# Cloud
"aws","azure","gcp","docker","kubernetes",

# Tools
"git","github","linux","jenkins","jira",

# Data
"power bi","tableau","excel","pandas","numpy"

]

# ===========================
# PDF / DOCX TEXT EXTRACTION
# ===========================

def extract_text(file):

    text = ""

    if file.name.endswith(".pdf"):

        reader = PdfReader(file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text

    elif file.name.endswith(".docx"):

        doc = Document(file)

        for para in doc.paragraphs:

            text += para.text + "\n"

    return text

# ===========================
# EMAIL EXTRACTION
# ===========================

def extract_email(text):

    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

    emails = re.findall(pattern,text)

    return emails[0] if emails else "Not Found"

# ===========================
# PHONE EXTRACTION
# ===========================

def extract_phone(text):

    pattern = r'(\+?\d[\d\s\-]{8,15}\d)'

    phones = re.findall(pattern,text)

    return phones[0] if phones else "Not Found"

# ===========================
# NAME EXTRACTION
# ===========================

def extract_name(text):

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_=="PERSON":

            return ent.text

    return "Unknown"

# ===========================
# GITHUB
# ===========================

def extract_github(text):

    match = re.search(r'github\.com/[A-Za-z0-9_-]+',text)

    if match:

        return match.group()

    return "Not Found"

# ===========================
# LINKEDIN
# ===========================

def extract_linkedin(text):

    match = re.search(r'linkedin\.com/in/[A-Za-z0-9_-]+',text)

    if match:

        return match.group()

    return "Not Found"

# ===========================
# EXPERIENCE
# ===========================

def extract_experience(text):

    text=text.lower()

    pattern=r'(\d+)\+?\s*(year|years)'

    match=re.findall(pattern,text)

    if match:

        years=[int(i[0]) for i in match]

        return max(years)

    return 0

# ===========================
# EDUCATION
# ===========================

def extract_education(text):

    degrees=[]

    education_words=[

        "b.e",
        "b.tech",
        "m.tech",
        "bca",
        "mca",
        "b.sc",
        "m.sc",
        "phd",
        "diploma"

    ]

    txt=text.lower()

    for degree in education_words:

        if degree in txt:

            degrees.append(degree.upper())

    return degrees

# ===========================
# SKILLS
# ===========================

def extract_skills(text):

    text=text.lower()

    found=[]

    for skill in SKILLS:

        if skill in text:

            found.append(skill)

    return sorted(list(set(found)))

# ===========================
# COSINE SIMILARITY
# ===========================

def semantic_similarity(resume,jd):

    tfidf=TfidfVectorizer(stop_words="english")

    matrix=tfidf.fit_transform([resume,jd])

    score=cosine_similarity(matrix[0],matrix[1])[0][0]

    return round(score*100,2)

# ===========================
# SKILL SCORE
# ===========================

def skill_score(resume_skills,jd_skills):

    if len(jd_skills)==0:

        return 0

    matched=len(set(resume_skills)&set(jd_skills))

    return round((matched/len(jd_skills))*100,2)

# ===========================
# ATS SCORE
# ===========================

def ats_score(text,jd):

    score=0

    if extract_email(text)!="Not Found":

        score+=10

    if extract_phone(text)!="Not Found":

        score+=10

    if extract_linkedin(text)!="Not Found":

        score+=10

    if extract_github(text)!="Not Found":

        score+=10

    skills=extract_skills(text)

    jdskills=extract_skills(jd)

    score+=skill_score(skills,jdskills)*0.4

    score+=semantic_similarity(text,jd)*0.3

    experience=extract_experience(text)

    score+=min(experience*2,20)

    return min(round(score,2),100)

# ===========================
# MISSING SKILLS
# ===========================

def missing_skills(resume,jd):

    r=set(extract_skills(resume))

    j=set(extract_skills(jd))

    return sorted(list(j-r))

# ===========================
# RESUME ANALYSIS
# ===========================

def analyze_resume(file,jd_text):

    text=extract_text(file)

    return {

        "Candidate":extract_name(text),

        "Email":extract_email(text),

        "Phone":extract_phone(text),

        "GitHub":extract_github(text),

        "LinkedIn":extract_linkedin(text),

        "Experience":extract_experience(text),

        "Education":", ".join(extract_education(text)),

        "Skills":", ".join(extract_skills(text)),

        "ATS Score":ats_score(text,jd_text),

        "Semantic Score":semantic_similarity(text,jd_text),

        "Skill Score":skill_score(
            extract_skills(text),
            extract_skills(jd_text)
        ),

        "Missing Skills":", ".join(
            missing_skills(text,jd_text)
        )

    }