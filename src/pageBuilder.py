import sys
import os
from github import Github
from jinja2 import Environment, FileSystemLoader


class PageData:
    """This class keeps and prepares the data to be rendered in page"""

    def __init__(self, repos):
        self.repos = repos

    def get_repo(self, repoName):
        """Returns the first repo with the name 'repoName' or None if not found."""
        res = None
        for repo in self.repos:
            if repo.name == repoName:
                res = repo
                break
        return res

    def get_active_repo(self, repoName):
        """Returns the first not archived repo with the name 'repoName' or None if not found."""
        res = None
        for repo in self.repos:
            if not repo.archived:
                if repo.name == repoName:
                    res = repo
                    break
        return res

    def get_active_repos_nb(self, repoNameStart):
        """Returns all the not archived repos with the name starting with 'repoName' or None if not found."""
        res = []
        for repo in self.repos:
            if not repo.archived:
                if repo.name.startswith(repoNameStart):
                    res.append(repo)
        return res

    def get_repo_namelink_md(self, repo, two_lines=False):
        """Returns a markdown formatted string with the name and the description of the repo."""
        s = "[" + repo.name + "](" + repo.html_url + ")"
        if repo.description:
            if two_lines:
                s = s + "<br/>*" + repo.description + "*"
            else:
                s = s + " *" + repo.description + "*"
        return s

    def get_repo_info(self, repo):
        """Returns a string with the language, the number of stars and the number of forks."""
        s = repo.language
        if repo.stargazers_count > 0:
            if repo.stargazers_count == 1:
                s = s + ", one star"
            else:
                s = s + ", " + str(repo.stargazers_count) + " stars"
        if repo.forks_count > 0:
            if repo.forks_count == 1:
                s = s + ", one fork"
            else:
                s = s + ", " + str(repo.forks_count) + " forks"
        return s

    def create_output_data(self):
        self.esp_components = self.get_active_repos_nb("ESP32")
        return

    def render(self, templateName):
        fileLoader = FileSystemLoader(".")
        env = Environment(loader=fileLoader)
        template = env.get_template(templateName)
        return template.render(info=self)


if __name__ == "__main__":
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not defined")
        sys.exit(1)

    g = Github(token)
    repo_owner = os.getenv("REPOSITORY_OWNER")
    if repo_owner:
        user = g.get_user(repo_owner)
    else:
        user = g.get_user()
    print("Selected repository owner " + user.name)

    repos = user.get_repos()
    if repos:
        print("Number of repositories is " + str(repos.totalCount))

    page_data = PageData(repos)
    page_data.create_output_data()

    with open("README.md", "w") as out_file:
        out_file.write(page_data.render("src/README.md.j2"))
