"""
iac_defect_prediction.py
Reproduit PCA + apprentissages + évaluation 10x10 décrits en 3.5.1-3.5.3 du papier.
Entrée attendue : CSV avec colonnes pour chaque propriété (counts) et une colonne 'label'
où label == 1 indique script "defectif" et 0 "neutre".
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

import argparse
import math
from collections import defaultdict

def load_data(csv_path, label_col='label'):
    df = pd.read_csv(csv_path)

    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in CSV")

    # Conserver uniquement les colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if label_col not in numeric_cols:
        numeric_cols.append(label_col)

    df = df[numeric_cols]

    X = df.drop(columns=[label_col]).values
    y = df[label_col].values
    feature_names = [c for c in df.columns if c != label_col]

    print(f"[INFO] Données chargées : {len(df)} échantillons, {len(feature_names)} features numériques.")
    return X, y, feature_names


def preprocess_log_and_scale(X):
    # log-transform counts: log(x+1)
    X_log = np.log1p(X)
    # standardize for PCA and learners
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)
    return X_scaled, scaler

def apply_pca(X_scaled, variance_threshold=0.95):
    pca = PCA(n_components=variance_threshold, svd_solver='full')
    X_pca = pca.fit_transform(X_scaled)
    # nombre de composants retenus
    n_components = X_pca.shape[1]
    explained = np.sum(pca.explained_variance_ratio_)
    return X_pca, pca, n_components, explained

def build_learners(random_state=42):
    learners = {
        'CART': DecisionTreeClassifier(random_state=random_state),
        'KNN': KNeighborsClassifier(),
        'LR': LogisticRegression(max_iter=2000, random_state=random_state),
        'NB': GaussianNB(),
        'RF': RandomForestClassifier(n_estimators=100, random_state=random_state)
    }
    return learners

def evaluate_10x10(X, y, learners, repeats=10, n_splits=10, seed_base=0):
    # stockage des scores (liste de valeurs par learner)
    results = {name: defaultdict(list) for name in learners.keys()}

    for rep in range(repeats):
        rk = seed_base + rep
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=rk)
        for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            for name, clf in learners.items():
                # entraînement
                clf.fit(X_train, y_train)
                y_pred = clf.predict(X_test)
                # probas pour AUC ; si pas disponible handle gracefully
                try:
                    if hasattr(clf, "predict_proba"):
                        y_proba = clf.predict_proba(X_test)[:, 1]
                    elif hasattr(clf, "decision_function"):
                        # some classifiers expose decision_function
                        y_proba = clf.decision_function(X_test)
                    else:
                        y_proba = None
                except Exception:
                    y_proba = None

                # métriques
                prec = precision_score(y_test, y_pred, zero_division=0)
                rec = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)

                # AUC: si y_test contient une seule classe, roc_auc_score échoue -> nan
                if y_proba is not None and len(np.unique(y_test)) > 1:
                    try:
                        auc = roc_auc_score(y_test, y_proba)
                    except Exception:
                        auc = float('nan')
                else:
                    auc = float('nan')

                # append
                results[name]['precision'].append(prec)
                results[name]['recall'].append(rec)
                results[name]['f1'].append(f1)
                results[name]['auc'].append(auc)

    # calculer la médiane sur les (repeats * n_splits) valeurs pour chaque metric
    summary = {}
    for name, metrics in results.items():
        summary[name] = {
            'precision_median': float(np.nanmedian(metrics['precision'])),
            'recall_median': float(np.nanmedian(metrics['recall'])),
            'f1_median': float(np.nanmedian(metrics['f1'])),
            'auc_median': float(np.nanmedian(metrics['auc']))
        }
    return summary, results

def print_summary(summary):
    print("\n=== Résumé des performances (médianes sur 10x10 CV) ===")
    print("{:10s} {:>9s} {:>9s} {:>9s} {:>9s}".format("Learner", "Precision", "Recall", "F1", "AUC"))
    for name, m in summary.items():
        print("{:10s} {:9.3f} {:9.3f} {:9.3f} {:9.3f}".format(
            name, m['precision_median'], m['recall_median'], m['f1_median'], 
            math.nan if math.isnan(m['auc_median']) else m['auc_median']
        ))

def main(csv_path, label_col='label', variance_threshold=0.95, repeats=10):
    X_raw, y, feature_names = load_data(csv_path, label_col=label_col)
    X_scaled, scaler = preprocess_log_and_scale(X_raw)
    X_pca, pca, n_components, explained = apply_pca(X_scaled, variance_threshold=variance_threshold)

    print(f"PCA: retenu {n_components} composants expliquant {explained*100:.2f}% de la variance")

    learners = build_learners(random_state=42)
    summary, _ = evaluate_10x10(X_pca, y, learners, repeats=repeats, n_splits=10, seed_base=0)
    print_summary(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce sections 3.5.1-3.5.3")
    parser.add_argument("csv", help="Chemin vers le CSV des propriétés (colonnes: propriétés..., label)")
    parser.add_argument("--label", default="label", help="Nom de la colonne label (default='label')")
    parser.add_argument("--variance", type=float, default=0.95, help="Variance expliquée cible pour PCA (default=0.95)")
    parser.add_argument("--repeats", type=int, default=10, help="Nombre de répétitions pour 10x10 CV (default=10)")
    args = parser.parse_args()
    main(args.csv, label_col=args.label, variance_threshold=args.variance, repeats=args.repeats)
