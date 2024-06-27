import spacy
from sklearn.metrics.pairwise import cosine_similarity
import json

roles = ['Java Developer', 'Testing', 'DevOps Engineer', 'Python Developer', 'Web Designing', 'HR',
         'Hadoop', 'Blockchain', 'ETL Developer', 'Operations Manager', 'Data Science', 'Sales',
         'Mechanical Engineer', 'Arts', 'Database', 'Electrical Engineering', 'Health and fitness',
         'PMO', 'Business Analyst', 'DotNet Developer', 'Automation Testing',
         'Network Security Engineer', 'SAP Developer', 'Civil Engineer', 'Advocate']

nlp = spacy.load('en_core_web_lg')
# cosine_similarity = lambda vec1, vec2 : 1 - spatial.distance.cosine(vec1,vec2)
# computed_similarities = []
for s in nlp.vocab.vectors:
    _ = nlp.vocab[s]

item_vectors = [nlp(role).vector for role in roles]

# Calculate cosine similarity between each pair of items
similarity_matrix = cosine_similarity(item_vectors)

# Print similarity matrix
# print("Similarity Matrix:", similarity_matrix)

# Convert similarity matrix to a dictionary
similarity_dict = {}
for i, item in enumerate(roles):
    similarity_dict[item] = {}
    for j, other_item in enumerate(roles):
        if i != j:
            similarity_dict[item][other_item] = float(similarity_matrix[i][j])
            similarity_dict[item] = dict(sorted(similarity_dict[item].items(), key=lambda x: x[1], reverse=True))

# Save the similarity dictionary to a JSON file
with open('similarity_matrix.json', 'w') as json_file:
    json.dump(similarity_dict, json_file, indent=4)


# for i, item in enumerate(roles):
#     similarities = similarity_matrix[i]
#     similar_items = [(roles[j], round(similarity, 2)) for j, similarity in enumerate(similarities) if ((j != i) and (similarity>0.5))]
#     similar_items.sort(key=lambda x: x[1], reverse=True)
    # print(f"{item}: {similar_items}")

