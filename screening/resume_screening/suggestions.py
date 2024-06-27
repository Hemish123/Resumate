import json
file = '/home/nikita/projects/JMS_ATS/parser/resume_screening/similarity_matrix.json'
def GiveSuggestion(category):
    with open(file) as f:
        similarity_matrix = json.load(f)

    similar_roles = []
    # print(similarity_matrix['Java Developer'])
    similarities = similarity_matrix[category]
    for role, similarity in similarities.items():
        if similarity>0.5:
            similar_roles += [role]
    if len(similar_roles)>5:
        return similar_roles[:5]
    return similar_roles

# similar_roles = GiveSuggestion('HR')
# print(similar_roles)



