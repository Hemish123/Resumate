import joblib

def ResumeScreening(text):
    category_mapping = ['Data Science', 'HR', 'Advocate', 'Arts', 'Web Designing',
       'Mechanical Engineer', 'Sales', 'Health and fitness', 'Civil Engineer',
       'Java Developer', 'Business Analyst', 'SAP Developer',
       'Automation Testing', 'Electrical Engineering', 'Operations Manager',
       'Python Developer', 'DevOps Engineer', 'Network Security Engineer',
       'PMO', 'Database', 'Hadoop', 'ETL Developer', 'DotNet Developer',
       'Blockchain', 'Testing']
    field_mapping = ['IT', 'Non-IT']


    model = "screening/resume_screening/resume_screening1.sav"
    loaded_model = joblib.load(model)
    # result = loaded_model.predict([text])
    prediction = loaded_model.predict([text])[0]
    predicted_field = field_mapping[int(prediction[0])]
    predicted_category = category_mapping[int(prediction[1])]
    result = {'field': predicted_field, 'category': predicted_category}
    return result


