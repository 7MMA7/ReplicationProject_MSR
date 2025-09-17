import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

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

datasets = {}
for org, filename in csv_files.items():
    filepath = os.path.join(data_folder, filename)
    try:
        df = pd.read_csv(filepath)
        datasets[org] = df
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        continue

if not datasets:
    print("No datasets found!")
    exit()

plt.style.use('default')
sns.set_palette("Set1")

fig, axes = plt.subplots(3, 4, figsize=(16, 12))
fig.suptitle('Fig. 5. Distribution of property values for each dataset', 
             fontsize=16, fontweight='bold', y=0.98)

axes = axes.flatten()

for idx, prop in enumerate(properties):
    ax = axes[idx]
    plot_data = []
    org_labels = []
    
    for org in ['Mirantis', 'Mozilla', 'Openstack', 'Wikimedia']:
        if org in datasets and prop in datasets[org].columns:
            values = datasets[org][prop].dropna()
            plot_data.append(values)
            org_labels.append(org)
        else:
            plot_data.append([0])
            org_labels.append(org)
    
    box_plot = ax.boxplot(plot_data, vert=False, tick_labels=org_labels, patch_artist=True)
    
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
    for patch, color in zip(box_plot['boxes'], colors[:len(plot_data)]):
        patch.set_facecolor(color)
    
    title = prop.replace('_', ' ').replace('Hard coded string', 'Hard-coded string')
    ax.set_title(title, fontsize=10, fontweight='bold')
    
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    
    for i, data in enumerate(plot_data):
        if len(data) > 0:
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = [x for x in data if x < lower_bound or x > upper_bound]
            if outliers:
                y_pos = [i + 1 + np.random.uniform(-0.1, 0.1) for _ in outliers]
                ax.scatter(outliers, y_pos, c='red', s=20, alpha=0.6)

for idx in range(len(properties), len(axes)):
    fig.delaxes(axes[idx])

plt.tight_layout()
plt.subplots_adjust(top=0.92, hspace=0.4, wspace=0.3)

plt.savefig('RQ_1/results/distribution_property_values.png', dpi=300, bbox_inches='tight')