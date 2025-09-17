import pandas as pd
import numpy as np
import os

data_folder = 'data'
csv_files = {
    'Mirantis': 'IST_MIR.csv',
    'Mozilla': 'IST_MOZ.csv', 
    'Openstack': 'IST_OST.csv',
    'Wikimedia': 'IST_WIK.csv'
}

properties = ['URL', 'File', 'Require', 'Ensure', 'Include', 'Attribute', 
              'Hard_coded_string', 'Command', 'File_mode', 'SSH_KEY', 
              'Lines_of_code', 'Comment']

def calculate_distribution_stats(df, properties):
    stats = {}
    for prop in properties:
        if prop in df.columns:
            avg_val = df[prop].mean()
            max_val = df[prop].max()
            stats[prop] = (round(avg_val, 1), max_val)
        else:
            stats[prop] = (0.0, 0)
    return stats

results = {}

for org, filename in csv_files.items():
    filepath = os.path.join(data_folder, filename)
    
    try:
        df = pd.read_csv(filepath)
        
        stats = calculate_distribution_stats(df, properties)
        results[org] = stats
        
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        continue
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        continue

print("\n" + "="*80)
print("Table 6")
print("Distribution of source code property values")
print("="*80)

print(f"{'Property':<20}", end="")
for org in csv_files.keys():
    if org in results:
        print(f"{org:<20}", end="")
print()

for prop in properties:
    display_prop = prop.replace('_', ' ').replace('Hard coded string', 'Hard-coded string')
    print(f"{display_prop:<20}", end="")
    
    for org in csv_files.keys():
        if org in results and prop in results[org]:
            avg, max_val = results[org][prop]
            print(f"({avg}, {max_val})".ljust(20), end="")
        else:
            print("(0.0, 0)".ljust(20), end="")
    print()

if results:
    export_data = []
    for prop in properties:
        row = {'Property': prop.replace('_', ' ')}
        for org in csv_files.keys():
            if org in results and prop in results[org]:
                avg, max_val = results[org][prop]
                row[f'{org}_avg'] = avg
                row[f'{org}_max'] = max_val
            else:
                row[f'{org}_avg'] = 0.0
                row[f'{org}_max'] = 0
        export_data.append(row)
    
    export_df = pd.DataFrame(export_data)
    export_df.to_csv('RQ_1/results/distribution_results.csv', index=False)