from transformers import pipeline
#1. Initialise sentiment-analysis pipeline
classifier = pipeline("sentiment-analysis")
sentences = [
    "The client was very satisfied with the delivery.",
    "The project is significantly over budget and behind schedule.",
    "The new regulatory framework presents both risks and oppotunities.",
    #2. Add one sentence
    "The clients do not want to visit on Tuesday."
]

def getSentiment(classifier, text):
  result=classifier(text)
  return result[0]

#3. Run classifier on all sentences and print
for s in sentences:
    result = getSentiment(classifier, s)
    label = result['label']
    score = result['score']
    print(f'"{s[:50]}..." -> {label} {score:.4f})')

import mlflow, mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
mlflow.set_tracking_uri("sqlite:///quiz.db")
mlflow.set_experiment("quiz-experiment")

X, y = load_iris(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)
MAX_DEPTH=5
N_ESTIMATORS=100

with mlflow.start_run(run_name="quize-run"):
  #a. log parameters
  mlflow.log_param("max_depth", MAX_DEPTH)
  mlflow.log_param("n_estimators", N_ESTIMATORS)

  model = RandomForestClassifier(max_depth=MAX_DEPTH, n_estimators=N_ESTIMATORS, random_state=42)
  model.fit(X_tr, y_tr)
  preds = model.predict(X_te)

  #b. Log metrics
  mlflow.log_metric("accuracy", accuracy_score(y_te, preds))
  mlflow.log_metric("f1", f1_score(y_te, preds, average="macro"))

  #c. Log and register the model
  mlflow.sklearn.log_model(model, "random-forest-model", registered_model_name="random-forest-model")

  #d. Set a tag
  mlflow.set_tag("team", "random_forest_model")