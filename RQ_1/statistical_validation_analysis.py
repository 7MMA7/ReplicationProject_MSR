import pandas as pd
import numpy as np
import os
from scipy import stats
from scipy.stats import mannwhitneyu, wilcoxon
import warnings
warnings.filterwarnings('ignore')

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

def cliff_delta_effect_size(x, y):
    if len(x) == 0 or len(y) == 0:
        return 0.0
    
    x = np.array(x)
    y = np.array(y)
    
    n1, n2 = len(x), len(y)
    
    x_expanded = x[:, np.newaxis]
    y_expanded = y[np.newaxis, :]
    
    greater = np.sum(x_expanded > y_expanded)
    less = np.sum(x_expanded < y_expanded)
    
    delta = (greater - less) / (n1 * n2)
    
    return abs(delta)

def normality_test(data, alpha=0.05):
    if len(data) < 3:
        return False
    
    try:
        _, p_value = stats.shapiro(data)
        return p_value > alpha
    except:
        return False

def statistical_validation_improved(df, properties):
    results = {}
    
    for prop in properties:
        if prop in df.columns and 'defect_status' in df.columns:
            defective = df[df['defect_status'] == 1][prop].dropna()
            non_defective = df[df['defect_status'] == 0][prop].dropna()
            
            if len(defective) > 2 and len(non_defective) > 2:
                try:
                    defective_normal = normality_test(defective)
                    non_defective_normal = normality_test(non_defective)
                    
                    statistic, p_value = mannwhitneyu(
                        defective, non_defective, 
                        alternative='two-sided',
                        use_continuity=True
                    )
                    
                    cliff_d = cliff_delta_effect_size(defective, non_defective)
                    
                    def get_descriptives(data):
                        return {
                            'mean': np.mean(data),
                            'median': np.median(data),
                            'std': np.std(data, ddof=1),
                            'min': np.min(data),
                            'max': np.max(data),
                            'q1': np.percentile(data, 25),
                            'q3': np.percentile(data, 75)
                        }
                    
                    defective_stats = get_descriptives(defective)
                    non_defective_stats = get_descriptives(non_defective)
                    
                    results[prop] = {
                        'p_value': p_value,
                        'cliff_delta': cliff_d,
                        'test_statistic': statistic,
                        'n_defective': len(defective),
                        'n_non_defective': len(non_defective),
                        'defective_normal': defective_normal,
                        'non_defective_normal': non_defective_normal,
                        'defective_stats': defective_stats,
                        'non_defective_stats': non_defective_stats
                    }
                    
                except Exception as e:
                    print(f"Error calculating statistics for {prop}: {e}")
                    results[prop] = create_empty_result()
            else:
                results[prop] = create_empty_result()
                results[prop]['n_defective'] = len(defective)
                results[prop]['n_non_defective'] = len(non_defective)
        else:
            results[prop] = create_empty_result()
    
    return results

def create_empty_result():
    return {
        'p_value': 1.0, 
        'cliff_delta': 0.0,
        'test_statistic': 0.0,
        'n_defective': 0, 
        'n_non_defective': 0,
        'defective_normal': False,
        'non_defective_normal': False,
        'defective_stats': {},
        'non_defective_stats': {}
    }

def interpret_cliff_delta(delta):
    abs_delta = abs(delta)
    if abs_delta < 0.147:
        return 'negligible'
    elif abs_delta < 0.33:
        return 'small'
    elif abs_delta < 0.474:
        return 'medium'
    else:
        return 'large'

def bonferroni_correction(p_values, alpha=0.05):
    return alpha / len(p_values)

def format_p_value(p_val):
    if p_val < 0.001:
        return "< 0.001"
    elif p_val < 0.01:
        return f"{p_val:.3f}"
    elif p_val < 0.05:
        return f"{p_val:.3f}"
    else:
        return f"{p_val:.3f}"

def format_property_name(prop):
    if prop == 'Lines_of_code':
        return 'Lines of code'
    elif prop == 'Hard_coded_string':
        return 'Hard-coded string'
    elif prop == 'File_mode':
        return 'File mode'
    else:
        return prop.replace('_', ' ')

results = {}
dataset_summaries = {}

for org, filename in csv_files.items():
    filepath = os.path.join(data_folder, filename)
    
    try:
        df = pd.read_csv(filepath)
        
        if 'defect_status' in df.columns:
            defect_counts = df['defect_status'].value_counts()
            non_defective = defect_counts.get(0, 0)
            defective = defect_counts.get(1, 0)

            dataset_summaries[org] = {
                'total': len(df),
                'defective': defective,
                'non_defective': non_defective,
                'defect_rate': defective/(defective+non_defective)*100
            }
        
        stats_results = statistical_validation_improved(df, properties)
        results[org] = stats_results
        
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        continue
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        continue

corrected_alpha = bonferroni_correction([0.05] * len(properties) * len(results))

print("\n" + "="*115)
print("Table 8")
print("Validation of identified source code properties")
print("="*115)

print(f"{'Property':<20}", end="")
for org in csv_files.keys():
    if org in results:
        print(f"{org:<20}", end="")
print()

print(f"{'':20}", end="")
for org in csv_files.keys():
    if org in results:
        print(f"{'p-value':<12}{'Cliff-δ':<10}", end="")
print()

all_significant = set(properties)
all_significant_corrected = set(properties)

for prop in properties:
    display_prop = format_property_name(prop)
    print(f"{display_prop:<20}", end="")
    
    is_significant_all = True
    is_significant_all_corrected = True
    
    for org in csv_files.keys():
        if org in results:
            p_val = results[org][prop]['p_value']
            if p_val >= 0.05:
                is_significant_all = False
            if p_val >= corrected_alpha:
                is_significant_all_corrected = False
    
    if not is_significant_all:
        all_significant.discard(prop)
    if not is_significant_all_corrected:
        all_significant_corrected.discard(prop)
    
    for org in csv_files.keys():
        if org in results and prop in results[org]:
            p_val = results[org][prop]['p_value']
            cliff_d = results[org][prop]['cliff_delta']
            
            p_str = format_p_value(p_val)
            cliff_str = f"{cliff_d:.2f}"

            print(f"{p_str:<12}{cliff_str:<10}", end="")
        else:
            print(f"{'1.000':<12}{'0.00':<10}{'N':<8}", end="")
    print()

if results:
    export_data = []
    for prop in properties:
        row = {'Property': prop}
        for org in csv_files.keys():
            if org in results and prop in results[org]:
                row[f'{org}_p_value'] = results[org][prop]['p_value']
                row[f'{org}_cliff_delta'] = results[org][prop]['cliff_delta']
                row[f'{org}_test_statistic'] = results[org][prop]['test_statistic']
                row[f'{org}_n_defective'] = results[org][prop]['n_defective']
                row[f'{org}_n_non_defective'] = results[org][prop]['n_non_defective']
            else:
                row[f'{org}_p_value'] = 1.0
                row[f'{org}_cliff_delta'] = 0.0
                row[f'{org}_test_statistic'] = 0.0
                row[f'{org}_n_defective'] = 0
                row[f'{org}_n_non_defective'] = 0
        export_data.append(row)
    
    export_df = pd.DataFrame(export_data)
    
    os.makedirs('RQ_1/results', exist_ok=True)
    export_df.to_csv('RQ_1/results/statistical_validation_results_improved.csv', index=False)