from git import Repo

repo_url = input("Enter GitHub Repository URL: ")

Repo.clone_from(repo_url, "repositories/repo")

print("Repository cloned successfully!")