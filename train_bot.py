import json
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# 1. Load Data
try:
    with open('intents.json') as file:
        intents = json.load(file)
except FileNotFoundError:
    print("Error: intents.json not found. Make sure it's in the same folder!")
    exit()

patterns = []
tags = []

# 2. Organize Data
for intent in intents['intents']:
    for pattern in intent['patterns']:
        patterns.append(pattern)
        tags.append(intent['tag'])

# 3. Train Model (The "Fast" Way)
vectorizer = CountVectorizer()
clf = LogisticRegression(random_state=0, max_iter=1000)

x = vectorizer.fit_transform(patterns)
clf.fit(x, tags)

# 4. Save Everything
pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))
pickle.dump(clf, open('model.pkl', 'wb'))

print("SUCCESS! Fast Model trained. Now run app.py!")