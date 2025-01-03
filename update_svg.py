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
    creation_dates.append(repo['created_at'])

    # Set the initial URL for commits with the author filter
    commits_url = f"{base_url}/repos/{username}/{repo['name']}/commits?author={username}&per_page=100"
    page = 1

    # Fetch commits with pagination
    while True:
        paginated_commits_url = f"{commits_url}&page={page}"
        commits_response = requests.get(paginated_commits_url, headers=headers)

        # Check for successful response
        if commits_response.status_code != 200:
            print(f"Error fetching commits for {repo['name']}: {commits_response.status_code}")
            break
        
        commits = commits_response.json()
        
        # If the response is an error message, log and exit loop
        if isinstance(commits, dict) and commits.get("message"):
            print(f"API Error: {commits.get('message')}")
            break

        # If there are no more commits, stop paginating
        if not commits:
            break

        # Count only commits authored by the user
        for commit in commits:
            if commit.get("author") and commit["author"]["login"] == username:
                total_commits += 1

        # Move to the next page
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

def fetch_gists_count():
    gists_url = f"{base_url}/users/{username}/gists"
    page = 1
    per_page = 100  # Max allowed per page
    total_gists = 0

    while True:
        response = requests.get(gists_url, headers=headers, params={'page': page, 'per_page': per_page})
        
        if response.status_code != 200:
            print(f"Error fetching gists, status code: {response.status_code}")
            break

        gists = response.json()
        if not gists:
            # No more gists to fetch
            break

        total_gists += len(gists)
        page += 1  # Move to next page

    return total_gists

# Fetch and print total gists count
total_gists = fetch_gists_count()

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
    "repos": "[Repositories]",
    "gists": "[Gists]",
    "uptime": "[uptime]"
}

for key, placeholder in placeholder_mapping.items():
    svg_content = svg_content.replace(placeholder, str(stats[key]))

# Write updated content to the new file
with open(new_file, "w") as file:
    file.write(svg_content)
