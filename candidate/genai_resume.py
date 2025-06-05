import os
import base64
from openai import AzureOpenAI

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


