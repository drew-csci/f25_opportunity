"""
python debug_github_api.py --repo . --all_refs --repo_full drew-csci/your-repo --project_owner drew-csci --project_number 3 --project_org
"""

import subprocess
import json
import sys

def run_gh(args):
    try:
        result = subprocess.check_output(["gh"] + args, stderr=subprocess.STDOUT, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.output}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_project.py <owner> <project_number>")
        print("Example: python debug_project.py alrudniy 3")
        sys.exit(1)
    
    owner = sys.argv[1]
    number = int(sys.argv[2])
    
    print(f"Testing project: owner={owner}, number={number}")
    print("=" * 60)
    
    # Test 1: Check gh auth status
    print("\n1. Checking gh auth status...")
    out = run_gh(["auth", "status"])
    if out:
        print(out)
    
    # Test 2: Try simple user project query
    print("\n2. Testing USER project query...")
    user_query = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
          title
          items(first: 10) {
            totalCount
            nodes {
              id
              creator { login }
            }
          }
        }
      }
    }
    """
    
    out = run_gh([
        "api", "graphql",
        "-F", f"login={owner}",
        "-F", f"number={number}",
        "-f", f"query={user_query}"
    ])
    
    if out:
        print("Raw response:")
        print(out)
        data = json.loads(out)
        print("\nParsed:")
        print(json.dumps(data, indent=2))
        
        # Check if we got data
        user = data.get("data", {}).get("user", {})
        project = user.get("projectV2", {})
        if project:
            print(f"\n✓ Found project: {project.get('title')}")
            items = project.get("items", {})
            print(f"✓ Total items: {items.get('totalCount', 0)}")
            nodes = items.get("nodes", [])
            for i, node in enumerate(nodes):
                creator = (node.get("creator") or {}).get("login", "NO CREATOR")
                print(f"  Item {i+1}: creator={creator}")
    
    # Test 3: Try organization project query
    print("\n3. Testing ORGANIZATION project query...")
    org_query = """
    query($login: String!, $number: Int!) {
      organization(login: $login) {
        projectV2(number: $number) {
          id
          title
          items(first: 10) {
            totalCount
            nodes {
              id
              creator { login }
            }
          }
        }
      }
    }
    """
    
    out = run_gh([
        "api", "graphql",
        "-F", f"login={owner}",
        "-F", f"number={number}",
        "-f", f"query={org_query}"
    ])
    
    if out:
        print("Raw response:")
        print(out)
        data = json.loads(out)
        
        org = data.get("data", {}).get("organization", {})
        project = org.get("projectV2", {})
        if project:
            print(f"\n✓ Found org project: {project.get('title')}")
            items = project.get("items", {})
            print(f"✓ Total items: {items.get('totalCount', 0)}")
    
    # Test 4: List all projects for the user
    print("\n4. Listing all projects for user...")
    list_query = """
    query($login: String!) {
      user(login: $login) {
        projectsV2(first: 20) {
          nodes {
            number
            title
            items { totalCount }
          }
        }
      }
    }
    """
    
    out = run_gh([
        "api", "graphql",
        "-F", f"login={owner}",
        "-f", f"query={list_query}"
    ])
    
    if out:
        data = json.loads(out)
        projects = data.get("data", {}).get("user", {}).get("projectsV2", {}).get("nodes", [])
        if projects:
            print("Available projects:")
            for p in projects:
                print(f"  #{p.get('number')}: {p.get('title')} ({p.get('items', {}).get('totalCount', 0)} items)")
        else:
            print("No projects found for this user")
    
    # Test 5: Check detailed item with content
    print("\n5. Testing detailed item query with content...")
    detail_query = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          items(first: 5) {
            nodes {
              id
              type
              creator { login }
              content {
                ... on Issue {
                  title
                  author { login }
                }
                ... on PullRequest {
                  title
                  author { login }
                }
                ... on DraftIssue {
                  title
                  creator { login }
                }
              }
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    
    out = run_gh([
        "api", "graphql",
        "-F", f"login={owner}",
        "-F", f"number={number}",
        "-f", f"query={detail_query}"
    ])
    
    if out:
        data = json.loads(out)
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()