# import google.generativeai as genai
#
# genai.configure(api_key="AIzaSyCa1eUtc_8SzlQLo9NgstXMtYFD7A279yg")
#
# def get_gemini_response(text):
#     input_text = "you will be provided with unstructured data your task is to parse it into json format"
#     model=genai.GenerativeModel('gemini-1.5-flash')
#     # myfile = genai.upload_file(file)
#
#     response=model.generate_content([text, input_text])
#
#     return response.text



# text = get_gemini_response(input_text)
#
# print(text)


from openai import OpenAI
import json, os

def get_response(text, designation, skills_string, min_experience, max_experience, education):

    client = OpenAI(api_key="sk-proj-bGFqRLy2avrcM5Sa7UPuT3BlbkFJ5hK2bKLzO2PBvbg7yuTx")
    content = """Your task is to parse resume into json format with following keys:
    str(average_tenure(i.e. 2 years)), str(current_tenure(i.e. 2 years)), 
    skills(e.g.{'front-end': ['html', 'javascript']} grab all skills(no speaking languages) from resume and in which categories it falls),
    {projects_done({'project title' : {'description' : 'str(project description and skills in that project)', 'industry' : str(project in which industry)}})}, 
    skills_matching(dict with int(match)(0-100%)(match with respect to skills in jd) and str(reason_for_fit)),
    [personality_traits],str(behavioral_question(give one situation to know behavioural aspects)),
    [behavioral_assessment](top 5 questions for behavioral assessment),
     [interview_questions](top 5 questions from job description), 
    str(assignment) (technical assessment based on job description),
    [cocurricular_activities](only if any mentioned in resume i.e. [Sports, Leadership, Charity])
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={
            "type": "json_object"
        },
        messages=[{"role": "system", "content": content},
                  {"role": "user", "content": text + "for Job Description :" + designation +
                   "skills required : " + skills_string +
                    "min experience : " + min_experience +
                    "max experience : " + max_experience +
                    "required education : " + education}],
    )
    total_tokens = response.usage.total_tokens
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    print("total : ", total_tokens)
    print("prompt : ", prompt_tokens)
    print("complete : ", completion_tokens)
    return response.choices[0].message.content

# total_tokens = response.usage.total_tokens
# prompt_tokens = response.usage.prompt_tokens
# completion_tokens = response.usage.completion_tokens
# response = get_response(" ")
# print(response)
# print("total : ", total_tokens)
# print("prompt : ", prompt_tokens)
# print("complete : ", completion_tokens)
