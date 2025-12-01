# backend/model_train.py
import re
import joblib
import numpy as np
from pathlib import Path
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import FunctionTransformer
from sklearn.utils import shuffle

# small feature extractor
date_re = re.compile(r"\b(?:\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))", flags=re.I)
time_re = re.compile(r"\b(?:[01]?\d|2[0-3])[:.][0-5]\d|\b\d{1,2}\s?(?:am|pm)\b", flags=re.I)

class TextStats(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        out = []
        for s in X:
            s = s or ""
            out.append([
                len(s.split()),
                len(s),
                int(bool(date_re.search(s))),
                int(bool(time_re.search(s))),
                int(any(k in s.lower() for k in ("venue","online","meet")))
            ])
        return np.array(out, dtype=float)

# vectorizers
word_tfidf = TfidfVectorizer(analyzer="word", ngram_range=(1,2), max_features=20000, min_df=2)
char_tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,6), max_features=5000)

from scipy import sparse
class CombinedVectorizer(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        self.w = word_tfidf.fit(X)
        self.c = char_tfidf.fit(X)
        return self
    def transform(self, X):
        wv = self.w.transform(X)
        cv = self.c.transform(X)
        return sparse.hstack([wv, cv]).tocsr()

def build_pipeline():
    features = FeatureUnion([
        ("tfidf", CombinedVectorizer()),
        ("stats", TextStats())
    ], transformer_weights={"tfidf": 1.0, "stats": 1.0})

    clf = LogisticRegression(solver="saga", max_iter=2000, class_weight="balanced", n_jobs=-1)
    pipe = Pipeline([("features", features), ("clf", clf)])
    return pipe

def train_and_save(X, y, save_path: str = "backend/model.joblib"):
    pipe = build_pipeline()
    # quick grid for C
    params = {"clf__C":[0.1,1.0,3.0]}
    gs = GridSearchCV(pipe, params, cv=5, scoring="f1_macro", n_jobs=-1)
    Xs, ys = shuffle(X, y, random_state=42)
    gs.fit(Xs, ys)
    joblib.dump(gs.best_estimator_, save_path)
    return gs.best_score_, save_path

if __name__ == "__main__":
    # placeholder quick training demo: save empty pipeline if no data provided
    p = build_pipeline()
    joblib.dump(p, Path(__file__).parent / "model.joblib")
