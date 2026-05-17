import os, base64, json, requests

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = 'lxztry/interview-coder'
BRANCH = 'master'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_sha(path):
    url = f'https://api.github.com/repos/{REPO}/contents/{path}?ref={BRANCH}'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()['sha']
    return None

def push_file(path, content):
    data = {
        'message': f'Add {path}',
        'content': base64.b64encode(content.encode('utf-8')).decode(),
        'branch': BRANCH
    }
    sha = get_sha(path)
    if sha:
        data['sha'] = sha
    
    url = f'https://api.github.com/repos/{REPO}/contents/{path}'
    r = requests.put(url, headers=headers, json=data)
    if r.status_code in (200, 201):
        print(f'OK: {path}')
    else:
        print(f'FAIL: {path} - {r.status_code} - {r.text}')

# Walk directory
root = r'D:\code\aipkgame\interview-coder'
for dirpath, dirnames, filenames in os.walk(root):
    # Skip .git
    dirnames[:] = [d for d in dirnames if d != '.git']
    
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        relpath = os.path.relpath(filepath, root).replace('\\', '/')
        
        # Skip .git folder
        if '.git/' in relpath or relpath.startswith('.git'):
            continue
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        push_file(relpath, content)

print('Done!')