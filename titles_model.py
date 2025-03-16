import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression 
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

model = None
def get_title_model():
    global model
    if (model != None):
        return model
    # Sample labeled dataset
    data = [
        ("CEO", 1), ("Founder | CEO", 1), ("Chief Technology Officer", 1), ("Chief Financial Officer", 1), ("CFO", 1), ("CTO", 1), ("Chief Executive Officer", 1), ("Founder", 1), ("CxO", 1), ("Founder", 1), ("Co-Founder", 1),
        ("VP", 2),("Director", 2), ("Senior Vice President", 2), ("Vice President", 2), ("Director of Marketing", 2), ("Managing Director", 2), ("SVP", 2), ("EVP", 2), ("Executive Vice President", 2), ("Senior President", 2), ("Senior VP", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior President", 2), ("Executive Vice President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2), ("Vice President", 2), ("President", 2), ("Senior VP", 2), ("Senior President", 2), ("Senior Vice President", 2), ("Executive Vice President", 2),
        ("Head of Engneering", 3), ("Head of Sales", 3), ("Delivery Head", 3), ("Head of Marketing", 3), ("Head of HR", 3), ("Head of Finance", 3), ("Head of Operations", 3), ("Head of Product", 3), ("Head of IT", 3), ("Head of Customer Service", 3), ("Head of Support", 3),
        ("principal Consultant", 4), ("principal Engineer", 4), ("principal Architect", 4), ("Delivery Manager", 4), ("Data Manager", 4), ("Engineering Manager", 4), ("Sales Manager", 4), ("Marketing Manager", 4), ("HR Manager", 4), ("Finance Manager", 4), ("Operations Manager", 4), ("Product Manager", 4), ("Customer Service Manager", 4), ("Support Manager", 4),
        ("Product Lead", 5), ("Team Supervisor", 5), ("Engineering Lead", 5), ("Lead Engineer", 5), ("Lead Analyst", 5), ("Lead Consultant", 5), ("QA Lead", 5), ("Sales Lead", 5), ("Marketing Lead", 5), ("HR Lead", 5), ("Finance Lead", 5), ("Operations Lead", 5), ("Product Lead", 5), ("Customer Service Lead", 5), ("Support Lead", 5), ("Specialist", 5),
        ("Executive", 5), ("Sales Executive", 5), ("Marketing Executive", 5), ("HR Executive", 5), ("Finance Executive", 5), ("Operations Executive", 5), ("Product Executive", 5), ("Customer Service Executive", 5), ("Support Executive", 5),
        ("Analyst", 6), ("Business Consultant", 6), ("Marketing Associate", 6), ("Sales Associate", 6), ("Software Engineer", 6), ("Engineer", 6), ("Consultant", 6), ("Business Analyst", 6), ("Marketing Analyst", 6), ("Sales Analyst", 6), ("Software Analyst", 6), ("Business Consultant", 6), ("Marketing Consultant", 6), ("Sales Consultant", 6), ("Software Consultant", 6), ("Business Associate", 6), ("Marketing Associate", 6), ("Sales Associate", 6), ("Software Associate", 6), ("Business Engineer", 6), ("Marketing Engineer", 6), ("Sales Engineer", 6), ("Software Engineer", 6), ("Business Analyst", 6), ("Marketing Analyst", 6), ("Sales Analyst", 6), ("Software Analyst", 6), ("Business Consultant", 6), ("Marketing Consultant", 6), ("Sales Consultant", 6), ("Software Consultant", 6), ("Business Associate", 6), ("Marketing Associate", 6), ("Sales Associate", 6), ("Software Associate", 6), ("Business Engineer", 6), ("Marketing Engineer", 6), ("Sales Engineer", 6), ("Software Engineer", 6), ("Business Analyst", 6), ("Marketing Analyst", 6), ("Sales Analyst", 6), ("Software Analyst", 6), ("Business Consultant", 6), ("Marketing Consultant", 6), ("Sales Consultant", 6), ("Software Consultant", 6), ("Business Associate", 6), ("Marketing Associate", 6), ("Sales Associate", 6), ("Software Associate", 6), ("Business Engineer", 6), ("Marketing Engineer", 6), ("Sales Engineer", 6), ("Software Engineer", 6), ("Business Analyst", 6), ("Marketing Analyst", 6), ("Sales Analyst", 6), ("Software Analyst", 6), ("Business Consultant", 6), ("Marketing Consultant", 6), ("Sales Consultant", 6), ("Software Consultant", 6), ("Business Associate", 6), ("Marketing Associate", 6), ("Sales Associate", 6), ("Software Associate", 6), ("Business Engineer", 6), ("Marketing Engineer", 6), ("Sales Engineer", 6), ("Software Engineer", 6), ("Business Analyst", 6), ("Marketing Analyst", 6), ("Sales Analyst", 6), ("Software Analyst", 6), ("Business Consultant", 6), ("Marketing Consultant", 6),
        ("Software Engineer", 7), ("Intern", 7), ("Trainee Developer", 7), ("Junior Developer", 7), ("Intern", 7), ("Junior", 7), ("Developer", 7)
    ]

    df = pd.DataFrame(data, columns=["designation", "rank"])

    vectorizer = TfidfVectorizer(ngram_range=(1,2))

    X_train, X_test, y_train, y_test = train_test_split(df["designation"], df["rank"], test_size=0.2, random_state=42)

    model = Pipeline([
        ("tfidf", vectorizer),
        ("classifier", 
         LogisticRegression(max_iter=500, random_state=42)) 
         # RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    # Train model
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    # Predict rank for a new designation
    new_designations = ["Delivery Manager at Overture Partners", "Chief Technology Officer", "Senior Software Engineer", "Managing Director", "Intern"]
    predicted_ranks = model.predict(new_designations)

    for d, r in zip(new_designations, predicted_ranks):
        print(f"Designation: {d}, Predicted Rank: {r}")

    return model

if __name__ == "__main__":
    get_title_model()
