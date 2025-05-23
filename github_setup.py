import os
import subprocess
import getpass
from pathlib import Path

def run_command(command, cwd=None):
    """Execute a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def setup_git_repo(repo_path, github_username, repo_name, github_token=None):
    """Set up a local Git repository and link it to GitHub."""
    # Change to the repository directory
    os.chdir(repo_path)
    print(f"Working in directory: {os.getcwd()}")
    
    # Initialize Git repository if not already done
    if not os.path.exists('.git'):
        print("Initializing new Git repository...")
        run_command("git init")
    
    # Set Git user configuration if not set
    print("Configuring Git user...")
    run_command("git config --local user.name \"" + github_username + "\"")
    
    # Get user email
    email = input("Enter your GitHub email: ").strip()
    run_command(f"git config --local user.email \"{email}\"")
    
    # Add all files and make initial commit
    print("Adding files to Git...")
    run_command("git add .")
    
    print("Making initial commit...")
    run_command("git commit -m \"Initial commit\"")
    
    # Create GitHub repository URL
    github_url = f"https://github.com/{github_username}/{repo_name}.git"
    
    # Check if remote exists, if not add it
    remotes = run_command("git remote -v")
    if "origin" not in remotes:
        print(f"Adding remote origin: {github_url}")
        run_command(f"git remote add origin {github_url}")
    else:
        print("Updating remote origin URL...")
        run_command(f"git remote set-url origin {github_url}")
    
    # Rename default branch to main
    run_command("git branch -M main")
    
    # Push to GitHub
    print("Pushing to GitHub...")
    if github_token:
        # If token is provided, use it for authentication
        auth_url = f"https://{github_username}:{github_token}@github.com/{github_username}/{repo_name}.git"
        run_command(f"git push -u {auth_url} main")
    else:
        # Otherwise, use SSH or prompt for credentials
        run_command("git push -u origin main")
    
    print("\n✅ Successfully set up Git and linked to GitHub!")
    print(f"You can access your repository at: https://github.com/{github_username}/{repo_name}")

def main():
    print("🚀 GitHub Repository Setup Tool")
    print("=" * 30)
    
    # Get repository path (default to current directory)
    repo_path = input(f"Enter the path to your project directory [default: {os.getcwd()}]: ").strip()
    repo_path = repo_path if repo_path else os.getcwd()
    
    # Validate path
    if not os.path.exists(repo_path):
        print(f"Error: Directory '{repo_path}' does not exist.")
        return
    
    # Get GitHub username
    github_username = input("Enter your GitHub username: ").strip()
    if not github_username:
        print("GitHub username is required!")
        return
    
    # Get repository name
    repo_name = input("Enter the name for your GitHub repository: ").strip()
    if not repo_name:
        print("Repository name is required!")
        return
    
    # Ask if user wants to use a GitHub token for authentication
    use_token = input("Do you want to use a GitHub Personal Access Token for authentication? (y/n): ").lower()
    token = None
    
    if use_token == 'y':
        token = getpass.getpass("Enter your GitHub Personal Access Token (input is hidden): ")
    
    print("\n🚀 Starting setup...")
    setup_git_repo(repo_path, github_username, repo_name, token)

if __name__ == "__main__":
    main()
