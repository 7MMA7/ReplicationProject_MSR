import pandas as pd
import os

data_folder = 'data'
csv_files = {
    'Mirantis': 'IST_MIR.csv',
    'Mozilla': 'IST_MOZ.csv', 
    'Openstack': 'IST_OST.csv',
    'Wikimedia': 'IST_WIK.csv'
}

properties = ['Attribute', 'Comment', 'Command', 'Ensure', 'File', 'File_mode',
              'Hard_coded_string', 'Include', 'Lines_of_code', 'Require', 
              'SSH_KEY', 'URL']

def calculate_median_by_defect_status(df, properties):
    results = {}
    
    for prop in properties:
        if prop in df.columns and 'defect_status' in df.columns:
            defective = df[df['defect_status'] == 1][prop]
            median_d = defective.median() if not defective.empty else 0.0
             
            non_defective = df[df['defect_status'] == 0][prop]
            median_nd = non_defective.median() if not non_defective.empty else 0.0
            
            results[prop] = {
                'D': median_d,
                'ND': median_nd
            }
        else:
            results[prop] = {'D': 0.0, 'ND': 0.0}
    
    return results

results = {}

for org, filename in csv_files.items():
    filepath = os.path.join(data_folder, filename)
    
    try:
        df = pd.read_csv(filepath)
        
        stats = calculate_median_by_defect_status(df, properties)
        results[org] = stats
        
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        continue
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        continue

print("\n" + "="*100)
print("Table 7")
print("Median values of 12 source code properties for both defective and non-defective scripts")
print("D = Defective, ND = Non-Defective")
print("="*100)

print(f"{'Property':<20}", end="")
for org in csv_files.keys():
    if org in results:
        print(f"{org:<15}", end="")
        print("   ", end="")
print()

print(f"{'':20}", end="")
for org in csv_files.keys():
    if org in results:
        print(f"{'D':<7}{'ND':<8}", end="")
        print("   ", end="")
print()

for prop in properties:
    if prop == 'Lines_of_code':
        display_prop = 'Lines of Code'
    elif prop == 'Hard_coded_string':
        display_prop = 'Hard-coded string'
    elif prop == 'File_mode':
        display_prop = 'File mode'
    else:
        display_prop = prop.replace('_', ' ')
    
    print(f"{display_prop:<20}", end="")
    
    for org in csv_files.keys():
        if org in results and prop in results[org]:
            d_val = results[org][prop]['D']
            nd_val = results[org][prop]['ND']
            print(f"{d_val:<7.1f}{nd_val:<8.1f}", end="")
        else:
            print(f"{'0.0':<7}{'0.0':<8}", end="")
        print("   ", end="")
    print()

if results:
    export_data = []
    for prop in properties:
        row = {'Property': prop}
        for org in csv_files.keys():
            if org in results and prop in results[org]:
                row[f'{org}_D'] = results[org][prop]['D']
                row[f'{org}_ND'] = results[org][prop]['ND']
            else:
                row[f'{org}_D'] = 0.0
                row[f'{org}_ND'] = 0.0
        export_data.append(row)
    
    export_df = pd.DataFrame(export_data)
    export_df.to_csv('RQ_1/results/median_defect_results.csv', index=False)