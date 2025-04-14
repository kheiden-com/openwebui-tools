# Github Project Search

This tool for OpenWebUI allows the user to retrieve GitHub project data directly within their chat context.

Specifically, this tool uses the GitHub GraphQL API to retrieve the top 20 items in a given project and returns them as a citation.

## Setup

First, add the code as a new tool to your OpenWebUI instance. You can copy the code from this repository or use the following link:

https://openwebui.com/t/kheidencom/github_project_search

### PAT Creation

To integrate with a project that exists within an organization, follow these steps:

Next, create a personal token with read access to projects and add it as a secret to your OpenWebUI instance. You can do this by navigating to your GitHub profile > click Settings >click Developer settings > under Personal access tokens, select Fine-grained tokens and click "Generate new token". Select the appropriate resource owner and ensure that the "Projects" organization permission is set to "Read"

To integrate with a project that exists outside of an organization (such as a personal account), follow these steps:

create a personal token with read access to projects and add it as a secret to your OpenWebUI instance. You can do this by navigating to your GitHub profile > click Settings >click Developer settings > under Personal access tokens, select "Tokens (classic)" then "Generate new token (classic)". Make sure to provision "read:project" access, as seen in the image below:

![read:project access](image.png)

Configure the valves in OpenWebUI for the tool. Make sure to set either "user" or "organization" for the "org_or_user" field.

