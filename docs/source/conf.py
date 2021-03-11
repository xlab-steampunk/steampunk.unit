project = "NGINX Unit Ansible Collection"
copyright = "2020, XLAB Steampunk"
author = "XLAB Steampunk"

extensions = [
    "sphinx_rtd_theme",
]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_logo = "_static/logo.png"
html_context = {
    "display_github": True,
    "github_user": "xlab-steampunk",
    "github_repo": "steampunk.unit",
    "github_version": "master",
    "conf_py_path": "/docs/source/",
}
