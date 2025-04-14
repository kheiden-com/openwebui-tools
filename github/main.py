"""
title: GitHub Project Search
author: kheiden-com
url: https://kheiden.com
date: 2025-04-14
version: 1.0.2
license: MIT
description: Allow model to access GitHub project items
"""

import requests
from pydantic import BaseModel, Field
import json
from datetime import datetime

class Tools:
    class Valves(BaseModel):
        github_token: str = Field(
            default="",
            description="GitHub Personal Access Token (needs read access to Projects)",
            json_schema_extra={"secret": True},
        )
        organization: str = Field(
            default="kheiden-com",
            description="The GitHub organization or user account to search in",
            json_schema_extra={"secret": False},
        )
        project_id: str = Field(
            default="2",
            description="Type: int, The GitHub Project id.",
            json_schema_extra={"secret": False},
        )
        org_or_user: str = Field(
            default="user",
            description="Select the location of the project to query, either 'organization' or 'user'",
            json_schema_extra={"secret": False},
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    async def search_recent_projects(
        self,
        query: str,
        __event_emitter__=None,
    ) -> str:
        """
        Search through GitHub projects for specific content.

        :param query: Search query string
        """
        try:
            if not self.valves.github_token:
                return "Error: GitHub token not configured. Please set up the GitHub token in tool settings."

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Searching projects...",
                            "done": False,
                            "hidden": False,
                        },
                    }
                )

            # Perform search
            url = "https://api.github.com/graphql"
            headers = {
                "Authorization": f"Bearer {self.valves.github_token}",
                "User-Agent": "Open-WebUI GitHub Tool (kheiden.com)",
            }
            query = """
query {
ORG_OR_USER(login: "ORGANIZATION") {projectV2(number: NUMBER){id}}
}
""".replace("ORGANIZATION", self.valves.organization)
            query = query.replace("ORG_OR_USER", self.valves.org_or_user.lower())
            query = query.replace("NUMBER", str(self.valves.project_id))
            output = requests.post(url, headers=headers, json={"query": query})
            node_id = output.json().get('data').get(self.valves.org_or_user.lower()).get("projectV2").get("id")
            query = """
query {
  node(id: "NODE_ID") {
    ... on ProjectV2 {
      items(first: 20) {
        nodes {
          id
          fieldValues(first: 8) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                text
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldDateValue {
                date
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldValue { # Add this catch-all fragment
                # This fragment intentionally selects nothing
              }
            }
          }
          content {
            ... on DraftIssue {
              title
              body
            }
            ... on Issue {
              title
              assignees(first: 10) {
                nodes {
                  login
                }
              }
            }
            ... on PullRequest {
              title
              assignees(first: 10) {
                nodes {
                  login
                }
              }
            }
          }
        }
      }
    }
  }
}
            """.replace("NODE_ID", node_id)
            output = requests.post(url, headers=headers, json={"query": query})
            nodes = output.json().get("data").get("node").get("items").get("nodes")
            item_limit = 20
            all_nodes = f"Top {item_limit} Github Project items:"
            for node in nodes:
                all_nodes += "\n"
                subnodes = node.get("fieldValues").get("nodes")
                for subnode in subnodes:
                    if subnode != {}:
                        all_nodes += json.dumps(subnode) + "\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Searching Complete.",
                            "done": True,
                            "hidden": True,
                        },
                    }
                )
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "citation",
                        "data": {
                            "document": [all_nodes],
                            "metadata": [
                                {
                                    "date_accessed": datetime.now().isoformat(),
                                    "source": "GitHub",
                                }
                            ],
                            "source": {
                                "name": "GitHub Project",
                                "url": f"https://github.com/orgs/{self.valves.organization}/projects/{self.valves.project_id}",
                            },
                        },
                    }
                )
            return all_nodes

        except Exception as e:
            return f"Error searching GitHub: {str(e)}"
