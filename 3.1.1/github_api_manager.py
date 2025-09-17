import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class GitHubAPIManager:
    def __init__(self):
        self.api_keys = [
            os.getenv('GITHUB_API_KEY_1'),
            os.getenv('GITHUB_API_KEY_2'),
            os.getenv('GITHUB_API_KEY_3'),
            os.getenv('GITHUB_API_KEY_4'),
            os.getenv('GITHUB_API_KEY_5')
        ]
        self.api_keys = [key for key in self.api_keys if key]
        self.current_key_index = 0
        
    def _get_headers(self):
        return {
            'Authorization': f'token {self.api_keys[self.current_key_index]}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def _rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Rotation vers clé {self.current_key_index + 1}")
    
    def make_request(self, url, params=None, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self._get_headers(), params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    if 'rate limit' in response.text.lower():
                        print(f"Rate limit atteinte pour clé {self.current_key_index + 1}")
                        self._rotate_key()
                        time.sleep(1)
                        continue
                elif response.status_code == 401:
                    print(f"Clé invalide {self.current_key_index + 1}")
                    self._rotate_key()
                    continue
                else:
                    print(f"Erreur HTTP {response.status_code}: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"Erreur requête: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
        
        return None

github_api = GitHubAPIManager()