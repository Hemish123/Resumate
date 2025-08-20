import os
import base64
from openai import AzureOpenAI,OpenAI
import re
import json, os


def get_response(text, designation, skills_string, min_experience, max_experience, education):
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )
    # client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])
    content = """Your task is to parse resume into json format with following keys:
    str(average_tenure(i.e. 2 years)), str(current_tenure(i.e. 2 years)), 
    skills(e.g.{'front-end': ['html', 'javascript']} grab all skills(no speaking languages) from resume and in which categories it falls),
    {projects_done({'project title' : {'description' : 'str(project description and skills in that project)', 'industry' : str(project in which industry)}})}, 
    skills_matching(dict with int(match)(0-100%)(match with respect to skills in jd) and str(reason_for_fit)),
    [personality_traits],str(behavioral_question(give one situation to know behavioural aspects)),
    [behavioral_assessment](top 5 questions for behavioral assessment),
     [interview_questions](top 5 questions from job description), 
    str(assignment) (technical assessment based on job description),
    [certifications](mentioned in resume),
    [achievements]
    """



    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={
            "type": "json_object"
        },
        messages=[{"role": "system", "content": content},
                  {"role": "user", "content": f"{text} for Job Description : {designation} "
                                              f"skills required : {skills_string} "
                                              f"min experience : {min_experience} "
                                              f" max experience : {max_experience} "
                                              f"required education : {education}"}]
    )

    # total_tokens = response.usage.total_tokens
    # prompt_tokens = response.usage.prompt_tokens
    # completion_tokens = response.usage.completion_tokens
    # # response = get_response(" ")
    # # print(response)
    # print("total : ", total_tokens)
    # print("prompt : ", prompt_tokens)
    # print("complete : ", completion_tokens)


    return response.choices[0].message.content



def transcribe_audio(audio_file_path):
    """
    Convert audio file to text using OpenAI's Whisper model
    """
    # client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",  # Using Whisper model
                file=audio_file
            )
        return transcription.text
    except Exception as e:
        print(f"Error in audio transcription: {e}")
        return None

# def generate_next_question(job_opening, candidate, resume_analysis, previous_answers):
#     """
#     Generates the next interview question:
#     - First question: "Tell me about yourself."
#     - Then, cover each skill, experience, education.
#     - Adapt to previous answers.
#     """
#     client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])

#     system_prompt = """
# You are an expert HR interviewer.
# Generate ONE interview question at a time.
# Rules:
# - If there are no previous answers, return: "Tell me about yourself."
# - Ensure every skill from the required skills is covered (one question per skill minimum).
# - Also cover experience, education, and cultural fit.
# - Adapt each question based on previous answers (e.g., ask follow-up questions).
# Return ONLY the question text (no JSON).
#     """

#     prior_qas = "\n".join(
#         f"Q: {qa['question']}\nA: {qa['answer']}"
#         for qa in previous_answers
#     ) if previous_answers else ""

#     skills = job_opening.requiredskills
#     resume_text = json.dumps(resume_analysis.response_text, indent=2) if resume_analysis else ""

#     user_prompt = f"""
# Job Designation: {job_opening.designation}
# Required Skills: {skills}
# Minimum Experience: {job_opening.min_experience}
# Maximum Experience: {job_opening.max_experience}
# Education: {job_opening.education}
# Job Description:
# {job_opening.jd_content}

# Candidate:
# Name: {candidate.name}
# Education: {candidate.education}
# Experience: {candidate.experience}
# Resume Analysis:
# {resume_text}

# Previous Q&A:
# {prior_qas}

# Generate the next interview question.
# """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ]
#     )

#     return response.choices[0].message.content.strip()

def generate_next_question(job_opening, candidate, resume_analysis, previous_answers):
    """
    Generates the next interview question:
    1. Intro question.
    2. Follow-up on intro.
    3. For each skill (up to 5), question + follow-up.
    """
    import os
    from openai import OpenAI
    import json
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )
    # client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])

    # Question number
    question_number = len(previous_answers) + 1

    # Try extracting skills from resume_analysis
    candidate_skills = []
    if resume_analysis and resume_analysis.response_text:
        skills_data = resume_analysis.response_text
        if isinstance(skills_data, dict) and "skills" in skills_data:
            candidate_skills = [s.strip() for s in skills_data["skills"] if s.strip()]

    # Fallback to job opening if resume has no skills
    if not candidate_skills:
        candidate_skills = [s.strip() for s in job_opening.requiredskills.split(",") if s.strip()]

    # Cap at top 5
    top_skills = candidate_skills[:5]

    # How many total questions?
    total_questions = 2 + len(top_skills) * 2

    # Safety fallback if no skills
    if not top_skills:
        total_questions = 2

    # If all questions are done
    if question_number > total_questions:
        return "Thank you. The interview questions are complete."

    # Prior Q&A text
    prior_qas = "\n".join(
        f"Q: {qa['question']}\nA: {qa['answer']}"
        for qa in previous_answers
    ) if previous_answers else ""

    system_prompt = """
You are an expert HR interviewer.
Follow this exact question sequence:
1. If no previous answers, always ask: "Tell me about yourself."
2. If only one answer, ask a follow-up question about their background.
3. For each skill (up to 5):
   - Ask one question about the skill.
   - Ask one follow-up question based on their answer.
Return ONLY the question text.
"""

    # 1️⃣ Intro
    if question_number == 1:
        return "Tell me about yourself."

    # 2️⃣ Follow-up
    if question_number == 2:
        last_answer = previous_answers[-1]["answer"]
        user_prompt = f"""
The candidate just answered "Tell me about yourself." Their answer:
\"\"\"
{last_answer}
\"\"\"
Generate a follow-up question to explore their background further.
"""
    # 3️⃣ Skill questions
    else:
        # Compute which skill and whether it's first or follow-up question
        skill_question_index = question_number - 3
        skill_idx = skill_question_index // 2
        is_followup = (skill_question_index % 2 == 1)

        if skill_idx >= len(top_skills):
            return "Thank you. We have completed the skill-based questions."

        current_skill = top_skills[skill_idx]

        if not is_followup:
            # First question about the skill
            user_prompt = f"""
Ask the candidate an interview question to assess their experience and proficiency in the skill "{current_skill}".
"""
        else:
            # Follow-up question
            last_answer = previous_answers[-1]["answer"]
            user_prompt = f"""
The candidate just answered a question about the skill "{current_skill}":
\"\"\"
{last_answer}
\"\"\"
Generate a follow-up question to explore their expertise in "{current_skill}" further.
"""

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()



# client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])

def evaluate_answer(question: str, answer: str, required_skills: list) -> dict:
    """
    Sends the interview question and candidate answer to GPT,
    requesting:
      - question_score (0–100)
      - skill_scores dict (skill name -> score)
      - technical_skills_score (0–100)

    Always returns a dict with consistent keys and cleaned values.
    """
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )
    # Convert the required skills list to comma-separated string for the prompt
    skills_list = ", ".join(required_skills)

    # System prompt to instruct GPT
    system = (
        "You are a technical interviewer. Respond ONLY with valid JSON.\n"
        "Format must be:\n"
        "{\n"
        '  "question_score": (integer between 0 and 100),\n'
        '  "technical_skills_score": (integer between 0 and 100),\n'
        '  "skill_scores": {\n'
        '     "Python": 85,\n'
        '     "Django": 90,\n'
        '     ... (one entry per required skill)\n'
        "  }\n"
        "}\n"
        "⚠️ skill_scores must be a dictionary with skill names as keys — not a list or characters.\n"
        "⚠️ Do not split skill names into letters."
    )

    # User prompt with the actual question, answer, and skills to assess
    user = f"""
Question:
{question}

Candidate Answer:
{answer}

Please score each of these skills: {skills_list}.
Also provide an overall "technical_skills_score" based on depth and clarity of technical knowledge.
"""

    # Call GPT
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0
    )

    # Extract the raw text response
    text = resp.choices[0].message.content.strip()

    try:
        parsed = json.loads(text)

        # Initialize clean result with defaults
        result = {
            "question_score": 0,
            "skill_scores": {},
            "technical_skills_score": 0
        }

        # Get question_score safely
        if isinstance(parsed.get("question_score"), (int, float)):
            result["question_score"] = parsed["question_score"]

        # Get technical_skills_score safely
        if isinstance(parsed.get("technical_skills_score"), (int, float)):
            result["technical_skills_score"] = parsed["technical_skills_score"]

        # Clean skill_scores
        raw_skills = parsed.get("skill_scores", {})
        clean_skills = {}
        if isinstance(raw_skills, dict):
            for k, v in raw_skills.items():
                # Force key to string, strip whitespace, skip if empty
                k_str = str(k).strip()
                if k_str:
                    # Force value to number, or 0
                    score = float(v) if isinstance(v, (int, float)) else 0
                    clean_skills[k_str] = score

        # If GPT returned nothing, default to all 0s
        if not clean_skills:
            clean_skills = {skill: 0 for skill in required_skills}

        result["skill_scores"] = clean_skills

        return result

    except json.JSONDecodeError:
        # Fallback if GPT did not return JSON
        print("💥 GPT JSON parse error:\n", text)
        return {
            "question_score": 0,
            "skill_scores": {skill: 0 for skill in required_skills},
            "technical_skills_score": 0
        }

# def generate_interview_summary(candidate_name: str, questions: list, required_skills: list) -> str:
#     """
#     Generate a summary of the interview overall performance.
#     """
#     # Build a detailed string with Q&A and scores
#     qna_text = ""
#     for q in questions:
#         qna_text += f"""
# Q: {q['question']}
# A: {q['answer']}
# Score: {q['score']}%
# Technical Skills: {q['technical_skills_score']}%
# """

#         if q["skills"]:
#             skills_str = ", ".join([f"{s}: {v}%" for s, v in q["skills"].items()])
#             qna_text += f"Skill Scores: {skills_str}\n"

#     skills_list = ", ".join(required_skills)

#     system = (
#         "You are a senior interviewer and hiring manager. "
#         "Based on the interview transcript, write a short professional summary assessing the candidate's performance, "
#         "strengths, weaknesses, and fit for the role. Keep it concise (max 200 words)."
#     )

#     user = f"""
# Candidate: {candidate_name}

# Interview Summary Data:
# {qna_text}

# Skills evaluated: {skills_list}

# Please write the interview summary:
# """

#     resp = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system},
#             {"role": "user", "content": user}
#         ],
#         temperature=0.3
#     )

#     return resp.choices[0].message.content.strip()

def generate_interview_summary(candidate_name: str, questions: list, required_skills: list) -> str:
    """
    Generate a 5-bullet summary of the interview covering all aspects: performance, skills, and fit.
    """
    qna_text = ""
    for q in questions:
        qna_text += f"""
Q: {q['question']}
A: {q['answer']}
Score: {q['score']}%
Technical Skills: {q['technical_skills_score']}%
"""
        if q["skills"]:
            skills_str = ", ".join([f"{s}: {v}%" for s, v in q["skills"].items()])
            qna_text += f"Skill Scores: {skills_str}\n"

    skills_list = ", ".join(required_skills)

    # ✅ GPT prompt for 5 bullet points
    system = (
        "You are a senior interviewer. Based on the provided interview data, generate a summary in exactly 5 bullet points. "
        "Cover the candidate's performance, strengths, weaknesses, technical and soft skills, and overall recommendation. "
        "Be concise, avoid repetition, and use professional tone."
    )

    user = f"""
Candidate: {candidate_name}

Interview Summary Data:
{qna_text}

Skills evaluated: {skills_list}

Write 5 bullet points summarizing the interview:
"""
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.3
    )

    return resp.choices[0].message.content.strip()


def generate_questions_from_skills(skills):
    if not skills:
        return []

    # client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )
    user_prompt = f"""Generate 5 interview questions based on these skills: {', '.join(skills)}.
    Return a JSON list: {{ "questions": ["q1", "q2", ...] }}"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful technical recruiter."},
                {"role": "user", "content": user_prompt}
            ]
        )
        data = json.loads(resp.choices[0].message.content)
        return data.get("questions", [])[:5]
    except Exception as e:
        print(f"Error generating resume-based questions: {e}")
        return []

def generate_combined_questions_for_skills(designation, skill_levels, n=5):
    print("generating..")
    """
    Generate exactly `n` interview questions for multiple skills combined.
    skill_levels: [{'skill': 'Python', 'level': 'fresher'}, ...]
    """
    # client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # # # Initialize Azure OpenAI Service client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ['CHATGPT_API_KEY'],
        api_version="2024-05-01-preview",
    )

    # ✅ Create descriptive list for prompt
    skills_desc = ", ".join([f"{s['skill']} ({s['level']} level)" for s in skill_levels])

    user_prompt = (
        f"Generate exactly {n} interview questions for a \"{designation}\" role. "
        f"The questions should cover the following skills and their levels: {skills_desc}. "
        "Distribute questions fairly across skills. Return a JSON list: { \"questions\": [\"q1\", \"q2\", ...] }"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert interviewer."},
                {"role": "user", "content": user_prompt}
            ]
        )
        data = json.loads(resp.choices[0].message.content)
        return data.get("questions", [])[:n]
    except Exception as e:
        print("Error generating combined questions:", e)
        return []
