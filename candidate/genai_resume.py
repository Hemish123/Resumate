import os
import base64
from openai import AzureOpenAI,OpenAI
import re
import json, os


def get_response(text, designation, skills_string, min_experience, max_experience, education):
    endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")

    # Initialize Azure OpenAI Service client with key-based authentication
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


def generate_interview_questions(text, designation, skills_string, min_experience, max_experience, education):
    """
    Generates tailored interview questions for a given job opening.
    """
    # endpoint = os.getenv("ENDPOINT_URL", "https://jivihireopenai.openai.azure.com/")
    client = OpenAI(api_key=os.environ['CHATGPT_API_KEY'])

    # Initialize Azure OpenAI Service client
    # client = AzureOpenAI(
    #     azure_endpoint=endpoint,
    #     api_key=os.environ['CHATGPT_API_KEY'],
    #     api_version="2024-05-01-preview",
    # )

    system_prompt = """
    You are an expert HR specialist.
    Your task is to generate a list of 5 varied and relevant interview questions for a candidate applying for the following job role.

    Make sure:
    - The questions are specific to the designation and skills.
    - They vary each time you are asked (do NOT always return the same questions).
    - Questions cover knowledge, experience, problem-solving, and cultural fit.

    IMPORTANT:
    Return ONLY a JSON array of strings.
    Do NOT include any explanation or extra text.
    Example:
    ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
    """

    user_prompt = (
        f"Job Designation: {designation}\n"
        f"Required Skills: {skills_string}\n"
        f"Minimum Experience: {min_experience} years\n"
        f"Maximum Experience: {max_experience} years\n"
        f"Required Education: {education}\n"
        f"Job Description:\n{text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    result_text = response.choices[0].message.content.strip()
    print("Raw GPT response:", repr(result_text))  # For debugging

    try:
        # Try to parse JSON directly
        return json.loads(result_text)
    except json.JSONDecodeError:
        # If GPT added extra text, extract JSON array using regex
        match = re.search(r"\[.*\]", result_text, re.DOTALL)
        if match:
            json_array = match.group(0)
            return json.loads(json_array)
        else:
            raise ValueError("Could not extract a JSON array from the GPT response.")