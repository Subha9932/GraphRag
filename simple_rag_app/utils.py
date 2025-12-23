import os
import shutil
import subprocess
import urllib.request
import zipfile
import io
from pathlib import Path

def get_git_command():
    """Attempts to find the git executable."""
    git_path = shutil.which("git")
    if git_path: return git_path
    
    # Common Windows paths fallback
    common_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Users\202317\AppData\Local\Programs\Git\cmd\git.exe",
    ]
    for p in common_paths:
        if os.path.exists(p): return p
    return None

def download_zip_repo(repo_url: str, target_dir: str, branch: str = "main"):
    """Downloads repo as zip if git is not available."""
    print(f"Git not found. Attempting ZIP download for {repo_url}...")
    
    # Clean URL
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
        
    # Construct ZIP URL
    # Try different branch names if the default fails
    dataset_branches = [branch, "master", "dev"]
    if branch not in dataset_branches:
        dataset_branches.insert(0, branch)
        
    # Add User-Agent headers to avoid 403/404 from some servers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Add Authentication for Private Repos
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("Using GITHUB_TOKEN for authentication.")
        headers['Authorization'] = f"token {token}"

    for current_branch in dataset_branches:
        zip_url = f"{repo_url}/archive/refs/heads/{current_branch}.zip"
        print(f"Trying to download {zip_url}...")
        
        try:
            req = urllib.request.Request(zip_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                    z.extractall(target_dir)
                    
            print(f"Successfully downloaded token from {current_branch}")
            
            # The zip usually extracts to a folder like "repo-main".
            # We need to find that folder and set it as the content root.
            extracted_roots = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
            if extracted_roots:
               # Find the one that was just created? Or just the first one?
               # Usually there is only one unless multiple downloads happened.
               # Let's verify it matches the pattern
               possible_root = os.path.join(target_dir, f"{repo_url.split('/')[-1]}-{current_branch}")
               
               # Robust search: return the directory that contains files
               for root_name in extracted_roots:
                   return os.path.join(target_dir, root_name)
                
            return target_dir
            
        except urllib.error.HTTPError as e:
            print(f"Failed to download {current_branch}: {e}")
            continue
        except Exception as e:
            print(f"Error downloading {current_branch}: {e}")
            continue

    raise Exception(f"Failed to download ZIP from {repo_url} after trying branches: {dataset_branches}")

def clone_repo(repo_url: str, target_dir: str):
    """
    Clones a GitHub repository to a target directory.
    Fallback to ZIP download if git is missing.
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)
    else:
        os.makedirs(target_dir, exist_ok=True) # Ensure dir exists for zip method
    
    clean_url = repo_url.strip()
    subpath = ""
    branch = "main" # Default guess
    
    if "github.com" in clean_url and "/tree/" in clean_url:
        parts = clean_url.split("/tree/")
        base_repo_url = parts[0]
        remainder = parts[1]
        clean_url = base_repo_url
        
        split_remainder = remainder.split("/", 1)
        branch = split_remainder[0] # Capture branch!
        if len(split_remainder) > 1:
            subpath = split_remainder[1]
    
    git_cmd = get_git_command()
    
    # Try git clone
    if git_cmd:
        try:
            subprocess.run([git_cmd, "clone", clean_url, target_dir], check=True, capture_output=True)
            # Git clone puts it IN target_dir if target_dir is empty? 
            # Actually `git clone url target_dir` puts contents IN target_dir.
            # So return target_dir/subpath
            return str(Path(target_dir) / subpath) if subpath else target_dir
        except (FileNotFoundError, Exception) as e:
            print(f"Git failed ({e}), using ZIP fallback.")
    else:
        print("Git command not found in system or common paths. Using ZIP fallback.")

    # Fallback to ZIP
    extracted_root = download_zip_repo(clean_url, target_dir, branch)
    
    # If we have a subpath, we need to append it to the extracted root
    full_path = Path(extracted_root) / subpath if subpath else Path(extracted_root)
    return str(full_path)

def process_files(source_dir: str, dest_dir: str):
    """
    Walks through the source directory, reads code files, and copies them 
    as text files to the destination directory.
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)

    # Clear destination directory first
    if dest_path.exists():
        for file in dest_path.glob("*"):
            if file.is_file():
                file.unlink()
    else:
        dest_path.mkdir(parents=True, exist_ok=True)

    # Optimized Filtering
    ignore_dirs = {
        '.git', '.idea', '.vscode', '__pycache__', 'node_modules', 
        'dist', 'build', 'coverage', 'venv', 'env', 'bin', 'obj', 
        'target', 'out', 'assets', 'images', 'media', 'test', 'tests'
    }
    
    # Strict Code Only - Removed JSON/YAML to avoid data bloating
    allowed_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', 
        '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rs', 
        '.php', '.rb', '.kt', '.swift','.cls'
    }

    file_count = 0
    max_file_size = 100 * 1024 # 100KB limit per file

    for root, dirs, files in os.walk(source_path):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
        for file in files:
            file_path = Path(root) / file
            
            # Check Extension
            if file_path.suffix.lower() not in allowed_extensions:
                continue

            # Check File Size to avoid bloating context
            try:
                if file_path.stat().st_size > max_file_size:
                    print(f"Skipping large file: {file_path.name}")
                    continue
                    
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Create flat filename: src/utils/helper.js -> src_utils_helper.js.txt
                relative_path = file_path.relative_to(source_path)
                safe_name = str(relative_path).replace(os.sep, '_') + ".txt"
                
                with open(dest_path / safe_name, 'w', encoding='utf-8') as f:
                    # Context Injection for GraphRAG
                    lang = file_path.suffix[1:] # py, js, etc
                    header = f"START FILE: {relative_path.as_posix()}\nLANGUAGE: {lang}\n-----------------------------------\n"
                    f.write(header + content)
                    
                file_count += 1
            except Exception as e:
                print(f"Skipping file {file_path}: {e}")

    return file_count

