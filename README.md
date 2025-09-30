# ReplicationProject_MSR

## Project structure

```
ReplicationProject_MSR
│── requirements.txt
│── 3.1.1/
│   ├── activity/
│   ├── downloadable/
│   ├── final/
│   ├── iac_filter/
│   ├── pipeline.py
│   ├── github_api_manager.py
│   ├── 1_check_repos.py
│   ├── 2_filter_iac.py
│   ├── 3_filter_activity.py
│   └── 4_analyze_iac.py
|── 3.1.2/
|   ├── results/
|   ├── process.py
|   ├── github_commit_extraction.py
|   ├── github_repos_extraction.py
|   ├── tracker_issue_mining.py
|   ├── xcm_generator.py
│── data/
│   ├── IST_MIR.csv
│   ├── IST_MOZ.csv
│   ├── IST_OST.csv
│   └── IST_WIK.csv
│── RQ_1/
│   ├── results/
│   ├── distribution_property_values.py
│   ├── distribution_source_code_properties.py
│   ├── feature_importance_ranking.py
│   ├── median_values_defect_status.py
│   └── statistical_validation_analysis.py
└── .env
```

## Installation

After cloning the repository and creating a virtual environment, install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the root directory of the project, add your GitHub api keys and your Conduit api token (for Phabricator Wikimedia) as follows:

```
GITHUB_API_KEY_1=your_key_1
GITHUB_API_KEY_2=your_key_2
GITHUB_API_KEY_3=your_key_3
GITHUB_API_KEY_4=your_key_4
GITHUB_API_KEY_5=your_key_5
PHABRICATOR_TOKEN=your_phabricator_token
```
*Note: to Generate the Conduit API Token for calling the issue tracker Phabricator, create an account in [Phabricator](https://phabricator.wikimedia.org/conduit/login/) and look for the **Conduit API tokens** section in the settings.*
## Usage

Every command line instruction should be run from the root directory of the project. You can adjust the paths in the commands as needed.

### 3.1.1 Replication

To run the full pipeline, execute the following command:

```bash
python3 3.1.1/pipeline.py [GITHUB_ORG_URL]
```
with `[GITHUB_ORG_URL]` being the URL of the GitHub organization you want to analyze.
By default, the output files will be saved in the `3.1.1/downloadable/`, `3.1.1/iac_filter/`, `3.1.1/activity/`, and `3.1.1/final/` directories.

Alternatively, you can run each step of the pipeline separately:

1. Repository download check:
   ```bash
   python3 3.1.1/1_check_repos.py [GITHUB_ORG_URL] --out [OUTPUT_CSV_PATH]
   ```
    with `[GITHUB_ORG_URL]` being the URL of the GitHub organization you want to analyze, and `[OUTPUT_CSV_PATH]` being the path where you want to save the output CSV file.

2. IaC repository filtering:
   ```bash
   python3 3.1.1/2_filter_iac.py --in [INPUT_CSV] --out [OUTPUT_CSV]
    ```
    with `[INPUT_CSV]` being the path to the CSV file generated in step 1, and `[OUTPUT_CSV]` being the path where you want to save the filtered IaC repositories.

3. Active repository filtering:
    ```bash
    python3 3.1.1/3_filter_activity.py --in [INPUT_CSV] --out [OUTPUT_CSV]
    ```
    with `[INPUT_CSV]` being the path to the CSV file generated in step 2, and `[OUTPUT_CSV]` being the path where you want to save the filtered active repositories.

4. IaC analysis:
    ```bash
    python3 3.1.1/4_analyze_iac.py --in [INPUT_CSV] --out [OUTPUT_CSV] --org [ORG_NAME]
    ```
    with `[INPUT_CSV]` being the path to the CSV file generated in step 3, `[OUTPUT_CSV]` being the path where you want to save the final analysis results, and `[ORG_NAME]` being the name of the GitHub organization.

### 3.1.2 Replication
To run the full process, execute the following command:
```bash
python3 3.1.2/process.py
```

Alternatively, you can run manually the two steps of the process:

1. Extract the name of the repositories and files in CSV files:
```bash
python3 3.1.2/github_repos_extraction.py
```

2. Generate the Extended Commit Messages (XCM) for the extracted repositories:
```bash
python3 3.1.2/xcm_generator
```

### Research Question 1 Analysis

To replicate the analysis for Research Question 1, run the following commands:

1. Table 6: Distribution of Source Code Property values
   ```bash
   python3 RQ_1/distribution_source_code_properties.py
   ```

    In the terminal you will see the Table 6 printed out and a CSV file named `distribution_results.csv` will be created in the `RQ_1/results/` directory.

2. Fig 5: Distribution of property values for each dataset
    ```bash
    python3 RQ_1/distribution_property_values.py
    ```
    This will generate the plots for Fig 5 and save them in the `RQ_1/results/` directory under `distribution_property_values.png`.

3. Table 7: Median values of Source Code Properties grouped by defect status
    ```bash
    python3 RQ_1/median_values_defect_status.py
    ```

    In the terminal you will see the Table 7 printed out and a CSV file named `median_defect_status.csv` will be created in the `RQ_1/results/` directory.

4. Validation of identified source code properties
    ```bash
    python3 RQ_1/statistical_validation_analysis.py
    ```

    In the terminal you will see the statistical validation results printed out and a CSV file named `statistical_validation_results.csv` will be created in the `RQ_1/results/` directory.

5. Feature importance ranking using Random Forest
    ```bash
    python3 RQ_1/feature_importance_ranking.py
    ```

    In the terminal you will see the feature importance ranking printed out and a CSV file named `feature_importance_results.csv` will be created in the `RQ_1/results/` directory.