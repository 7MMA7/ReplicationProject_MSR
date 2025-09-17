import os
import sys
import csv
import subprocess
import tempfile
import shutil
import re
import argparse

def clone_repo(url, temp_dir):
    repo_name = url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(temp_dir, repo_name)
    try:
        subprocess.run(['git', 'clone', '--depth', '1', url, repo_path],
                       check=True, capture_output=True, text=True)
        return repo_path
    except subprocess.CalledProcessError:
        return None

def count_ssh_keys_simple(content):
    
    restrictive_patterns = [
        r'\.ssh/',
        r'\bssh_private_key\b',
        r'\bknown_hosts\b',
        r'ssh::known_host',
    ]
    
    found_elements = set()
    for pattern in restrictive_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            found_elements.add(match.lower().strip())
    
    return len(found_elements)


def analyze_puppet_file(file_path):
    metrics = {
        'require': 0, 'ensure': 0, 'include': 0, 'attribute': 0,
        'hard_coded_string': 0, 'comment': 0, 'command': 0,
        'file_mode': 0, 'ssh_key': 0, 'file': 0, 'url_count': 0, 'lines_of_code': 0
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        metrics['lines_of_code'] = len(content.splitlines())
        metrics['url_count'] = len(re.findall(r'https?://', content, re.IGNORECASE))
        metrics['require'] = len(re.findall(r'\brequire\b', content, re.IGNORECASE))
        metrics['ensure'] = len(re.findall(r'\bensure\b', content, re.IGNORECASE))
        metrics['include'] = len(re.findall(r'\binclude\s+[\w:]+', content, re.IGNORECASE))
        metrics['attribute'] = len(re.findall(r'\b\w+\s*=>', content))  # more general
        metrics['hard_coded_string'] = len(re.findall(r"'[^']+'|\"[^\"]+\"", content))
        metrics['comment'] = len(re.findall(r'#.*', content))
        metrics['command'] = len(re.findall(r'\bcmd\b', content, re.IGNORECASE))
        metrics['file'] = len(re.findall(r'\bfile\b', content, re.IGNORECASE))
        metrics['file_mode'] = len(re.findall(r'\bmode\s*=>\s*[\'"]?[0-7]+[\'"]?', content))
        metrics['ssh_key'] = len(re.findall(r'\bssh_authorized_key\b', content, re.IGNORECASE))

    except Exception as e:
        print(f"Error analyzing Puppet file {file_path}: {e}")

    return metrics


def calculate_defect_status(metrics):
    defect_indicators = 0
    if metrics['hard_coded_string'] > 10:
        defect_indicators += 1
    if metrics['command'] > 5:
        defect_indicators += 1
    if metrics['ssh_key'] > 0 and metrics['file_mode'] == 0:
        defect_indicators += 1
    if metrics['lines_of_code'] > 200:
        defect_indicators += 1
    if metrics['attribute'] > 50:
        defect_indicators += 1
    return 1 if defect_indicators >= 2 else 0


def analyze_repository(repo_path, org_name, repo_name):
    results = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            should_analyze = False
            if file.endswith('.pp'):
                should_analyze = True
                file_type = 'puppet'

            if should_analyze:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)

                metrics = analyze_puppet_file(file_path)
                defect_status = calculate_defect_status(metrics)

                result = {
                    'org': org_name.upper(),
                    'file_': repo_name + "/" + rel_path,
                    'URL': metrics['url_count'],
                    'File': metrics['file'],
                    'Lines_of_code': metrics['lines_of_code'],
                    'Require': metrics['require'],
                    'Ensure': metrics['ensure'],
                    'Include': metrics['include'],
                    'Attribute': metrics['attribute'],
                    'Hard_coded_string': metrics['hard_coded_string'],
                    'Comment': metrics['comment'],
                    'Command': metrics['command'],
                    'File_mode': metrics['file_mode'],
                    'SSH_KEY': metrics['ssh_key'],
                    'defect_status': defect_status
                }
                results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description='Analyze IaC defects in repositories')
    parser.add_argument('--in', dest="input", required=True, help='CSV file of active IaC repos')
    parser.add_argument('--out', dest="output", required=True, help="Output CSV file for results")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    all_results = []
    temp_dir = tempfile.mkdtemp()

    try:
        with open(args.input, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                repo_name = row['name']
                clone_url = row['clone_url']
                print(f"Analyzing repository: {repo_name}")

                repo_path = clone_repo(clone_url, temp_dir)
                if repo_path:
                    repo_results = analyze_repository(repo_path, args.org, repo_name)
                    all_results.extend(repo_results)
                    print(f"  → {len(repo_results)} IaC files analyzed")
                else:
                    print(f"  → Error cloning {repo_name}")

        fieldnames = ['org', 'file_', 'URL', 'File', 'Lines_of_code', 'Require', 'Ensure',
                      'Include', 'Attribute', 'Hard_coded_string', 'Comment', 'Command',
                      'File_mode', 'SSH_KEY', 'defect_status']

        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)

        print(f"Total files analyzed: {len(all_results)}")

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()