import requests
import shutil
import os
from datetime import datetime

# Get GitHub stats
username = "talfig"
token = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"token {token}"}
base_url = "https://api.github.com"

# Fetch repositories to calculate stars, forks, and commits
repos_url = f"{base_url}/users/{username}/repos"
repos_response = requests.get(repos_url, headers=headers)
repos = repos_response.json()

# Initialize counts
total_stars = 0
total_forks = 0
total_commits = 0
total_days = 0

# Calculate uptime in days
creation_dates = []

for repo in repos:
    total_stars += repo.get("stargazers_count", 0)
    total_forks += repo.get("forks_count", 0)

    # Collect creation dates for uptime calculation
    creation_dates.append(repo['created_at'])
    
    # Fetch all commits for each repository (with pagination)
    commits_url = f"{base_url}/repos/{username}/{repo['name']}/commits?author={username}"
    page = 1
    while True:
        paginated_commits_url = f"{commits_url}&page={page}&per_page=100"
        commits_response = requests.get(paginated_commits_url, headers=headers)
        commits = commits_response.json()

        if not commits or len(commits) == 0:
            break  # No more commits

        total_commits += len(commits)
        page += 1

# Calculate total uptime in days from the earliest repo creation date
if creation_dates:
    earliest_creation_date = min([datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") for date in creation_dates])
    total_days = (datetime.utcnow() - earliest_creation_date).days

# Fetch followers count
followers_url = f"{base_url}/users/{username}"
followers_response = requests.get(followers_url, headers=headers)
followers = followers_response.json().get("followers", 0)

# Fetch pull requests and issues count
pull_requests_url = f"{base_url}/search/issues?q=type:pr+author:{username}"
pull_requests_response = requests.get(pull_requests_url, headers=headers)
total_pull_requests = pull_requests_response.json().get("total_count", 0)

issues_url = f"{base_url}/search/issues?q=type:issue+author:{username}"
issues_response = requests.get(issues_url, headers=headers)
total_issues = issues_response.json().get("total_count", 0)

# Fetch gists count
gists_url = f"{base_url}/users/{username}/gists"
gists_response = requests.get(gists_url, headers=headers)
total_gists = len(gists_response.json())

# Store stats
stats = {
    "stars": total_stars,
    "forks": total_forks,
    "commits": total_commits,
    "followers": followers,
    "pull_requests": total_pull_requests,
    "issues": total_issues,
    "repos": len(repos),
    "gists": total_gists,
    "uptime": total_days
}

# Copy original file to new file with 'new_' prefix
original_file = "terminal_stats.svg"
new_file = "new_terminal_stats.svg"
shutil.copyfile(original_file, new_file)

# Update SVG content in the new file
with open(new_file, "r") as file:
    svg_content = file.read()

# Replace placeholders in SVG with actual stats
placeholder_mapping = {
    "stars": "[Stars]",
    "forks": "[Forks]",
    "commits": "[Commits]",
    "followers": "[Followers]",
    "pull_requests": "[Pull Requests]",
    "issues": "[Issues]",
    "repos": "[Repository]",
    "gists": "[Gists]",
    "uptime": "[uptime]"
}

for key, placeholder in placeholder_mapping.items():
    svg_content = svg_content.replace(placeholder, str(stats[key]))

# Write updated content to the new file
with open(new_file, "w") as file:
    file.write(svg_content)
