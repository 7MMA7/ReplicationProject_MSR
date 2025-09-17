import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

data_folder = 'data'
csv_files = {
    'Mirantis': 'IST_MIR.csv',
    'Mozilla': 'IST_MOZ.csv',
    'Openstack': 'IST_OST.csv',
    'Wikimedia': 'IST_WIK.csv'
}

properties = ['Attribute', 'Command', 'Comment', 'Ensure', 'File', 'File_mode',
              'Hard_coded_string', 'Include', 'Lines_of_code', 'Require',
              'SSH_KEY', 'URL']

def calculate_feature_importance_cv(df, properties):
    if 'defect_status' not in df.columns:
        return {}
    
    X = df[properties].fillna(0)
    y = df['defect_status']
    
    if len(y.unique()) < 2:
        return {}
    
    if len(df) < 10:
        return {}
    
    rf = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1
    )
    
    rf.fit(X, y)
    importance_dict = {prop: score for prop, score in zip(properties, rf.feature_importances_)}
    
    return importance_dict

results = {}
for org, filename in csv_files.items():
    filepath = os.path.join(data_folder, filename)
    try:
        df = pd.read_csv(filepath)
        importance_scores = calculate_feature_importance_cv(df, properties)
        results[org] = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print("\n" + "="*105)
print("Table 9")
print("Ranked order of the 12 source code properties that show highest correlation according to feature \nimportance analysis")
print("="*105)

table9_data = []
max_rank = 12
for rank in range(1, max_rank + 1):
    row = {"Rank": rank}
    for org in csv_files.keys():
        if org in results and len(results[org]) >= rank:
            prop, score = results[org][rank-1]
            display_prop = prop.replace('_', ' ')
            if prop == 'Lines_of_code':
                display_prop = 'Lines of code'
            elif prop == 'Hard_coded_string':
                display_prop = 'Hard-coded string'
            elif prop == 'File_mode':
                display_prop = 'File mode'
            row[org] = f"{display_prop} ({score:.2f})"
        else:
            row[org] = "N/A"
    table9_data.append(row)

table9_df = pd.DataFrame(table9_data)
print(table9_df.to_string(index=False))

table9_df.to_csv("RQ_1/results/feature_importance_results.csv", index=False)
