import pandas as pd

def create_repos_and_files_names_csv():

    #loading datasets
    data_mir = pd.read_csv("data/IST_MIR.csv")
    data_moz = pd.read_csv("data/IST_MOZ.csv")
    data_ost = pd.read_csv("data/IST_OST.csv")
    data_wik = pd.read_csv("data/IST_WIK.csv")

    #creating empty dataframes for results
    repos_extract = pd.DataFrame(columns=["Mirantis", "mozilla", "openstack", "wikimedia"])
    files_extract = pd.DataFrame()

    #extracting mirantis repo names and files
    extract_repos_and_files_names_from_dataset(data_mir, "Mirantis", repos_extract, files_extract)
    #extracting mozilla repo names and files
    extract_repos_and_files_names_from_dataset(data_moz, "mozilla", repos_extract, files_extract)
    #extracting openstack repo names and files
    extract_repos_and_files_names_from_dataset(data_ost, "openstack", repos_extract, files_extract)
    #extracting wikimedia repo names and files
    extract_repos_and_files_names_from_dataset(data_wik, "wikimedia", repos_extract, files_extract)

    #creating resulting csv files
    repos_extract.to_csv("3.1.2/results/IaC_repos.csv", index=False)
    files_extract.to_csv("3.1.2/results/IaC_files.csv", index=False)

def extract_repos_and_files_names_from_dataset(data, org_name, repos_df, files_df):
    nb_repo = 0
    for index, file_path in enumerate(data["file_"]):
        #decomposing path to get repo name and file name
        path_elements = file_path.split("/")
        #repo_name in position 5
        repo_name = path_elements[5]
        #adding repo name to dataframe if not already present
        if repo_name not in repos_df[org_name].values:
            repos_df.loc[nb_repo, org_name] = repo_name
            #also adding a column in files_df dataframe for this repo
            files_df[f"{repo_name}"] = None
            nb_repo += 1
        #adding file name to files_df dataframe
        files_df.loc[files_df[f"{repo_name}"].count(), f"{repo_name}"] = path_elements[-1]

if __name__ == "__main__":
    create_repos_and_files_names_csv()