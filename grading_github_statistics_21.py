"""
GitHub Statistics Script - Per User Weekly Summary

Shows for each user per week:
- Number of commits
- Lines added/deleted
- Number of PRs opened
- Project items created/moved

Usage:
python grading_github_statistics_21.py --repo . --all_refs --repo_full drew-csci/f25_opportunity --start_date 2025-08-25 --end_date 2025-12-12 --org_project_owner drew-csci --org_project_number 3 --user_project_owner alrudniy --user_project_number 7 --name_fix_file fix_github_names.xlsx 

"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


@dataclass
class WeeklyUserStats:
    """Statistics for a single user for a single week."""
    display_name: str
    github_username: str
    week_number: int
    week_start: str  # YYYY-MM-DD
    week_end: str    # YYYY-MM-DD
    commits: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    prs_opened: int = 0
    user_project_items_created: int = 0
    user_project_items_moved: int = 0
    org_project_items_created: int = 0
    org_project_items_moved: int = 0


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\n\nOutput:\n{e.output}") from e


def run_git(args: List[str], repo: str) -> str:
    return run_cmd(["git"] + args, cwd=repo)


def run_gh(args: List[str], repo: Optional[str] = None) -> str:
    return run_cmd(["gh"] + args, cwd=repo)


def extract_github_username(email: str) -> str:
    """Extract GitHub username from noreply email address."""
    email = (email or "").strip()
    if email.endswith("@users.noreply.github.com"):
        local = email.split("@", 1)[0]
        if "+" in local:
            return local.split("+", 1)[1]
        return local
    return ""


def parse_author_line(author_line: str) -> Tuple[str, str, str]:
    """
    Parse git author line like "John Doe <email@example.com>"
    Returns: (display_name, email, github_username)
    """
    s = author_line.strip()
    if "<" in s and ">" in s:
        name_part, email_part = s.rsplit("<", 1)
        display_name = name_part.strip()
        email = email_part.rstrip(">").strip()
        gh_user = extract_github_username(email)
        return display_name, email, gh_user
    return s, "", ""


def load_alias_map(path: str) -> Dict[str, Dict[str, str]]:
    """Load alias JSON for mapping git identities to canonical names/usernames."""
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError("alias_json must be a JSON object")
    normalized: Dict[str, Dict[str, str]] = {}
    for k, v in obj.items():
        if isinstance(v, str):
            normalized[k] = {"display_name": v, "github_username": ""}
        elif isinstance(v, dict):
            normalized[k] = {
                "display_name": v.get("display_name", ""),
                "github_username": v.get("github_username", ""),
            }
    return normalized


def load_name_fix_map(path: str) -> Dict[str, str]:
    """
    Load name fix mapping from Excel file.
    Maps original names (Name column) to fixed names (Name Fixed column).
    Returns: dict mapping name -> fixed_name (case-insensitive lookup)
    """
    if not path or not os.path.exists(path):
        return {}
    
    if not HAS_PANDAS:
        print("Warning: pandas not installed, cannot load name fix file")
        return {}
    
    try:
        df = pd.read_excel(path)
        name_map: Dict[str, str] = {}
        
        for _, row in df.iterrows():
            original_name = str(row.get('Name', '')).strip()
            fixed_name = str(row.get('Name Fixed', '')).strip()
            
            if original_name and fixed_name:
                # Store lowercase key for case-insensitive matching
                name_map[original_name.lower()] = fixed_name
        
        # Debug: show a few entries
        print(f"  Loaded {len(name_map)} name mappings")
        
        return name_map
    except Exception as e:
        print(f"Warning: Could not load name fix file: {e}")
        return {}


def apply_name_fix(name: str, name_fix_map: Dict[str, str]) -> str:
    """Apply name fix mapping to a name. Returns fixed name or original if not found."""
    if not name_fix_map:
        return name
    return name_fix_map.get(name.lower(), name)


def get_canonical_user(author_line: str, alias_map: Dict[str, Dict[str, str]]) -> Tuple[str, str]:
    """Get canonical display name and github username for an author line."""
    display_name, email, gh_user = parse_author_line(author_line)
    
    if author_line in alias_map:
        canon_name = alias_map[author_line].get("display_name") or display_name
        canon_gh = alias_map[author_line].get("github_username") or gh_user
    else:
        canon_name = display_name
        canon_gh = gh_user
    
    return canon_name, canon_gh


def get_weeks_between(start_date: str, end_date: str) -> List[Tuple[int, str, str]]:
    """
    Generate list of (week_number, week_start, week_end) tuples between two dates.
    Each week starts on Monday.
    Returns: List of (week_number, start_date_str, end_date_str)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    weeks = []
    week_num = 1
    
    # Find the Monday of the week containing start_date
    current = start - timedelta(days=start.weekday())
    
    while current <= end:
        week_start = current
        week_end = current + timedelta(days=6)
        
        # Clamp to actual date range
        actual_start = max(week_start, start)
        actual_end = min(week_end, end)
        
        weeks.append((
            week_num,
            actual_start.strftime("%Y-%m-%d"),
            actual_end.strftime("%Y-%m-%d")
        ))
        
        current += timedelta(days=7)
        week_num += 1
    
    return weeks


def count_commits_for_week(
    repo: str, 
    alias_map: Dict[str, Dict[str, str]], 
    week_start: str, 
    week_end: str,
    all_refs: bool = True,
    name_fix_map: Dict[str, str] = None
) -> Dict[str, Tuple[str, str, int, int, int]]:
    """
    Count commits and lines for a specific week.
    Returns: dict mapping fixed_name -> (fixed_name, github_username, commits, added, deleted)
    """
    if name_fix_map is None:
        name_fix_map = {}
    
    since = f"{week_start} 00:00:00"
    until = f"{week_end} 23:59:59"
    
    git_args = [
        "log", 
        "--numstat", 
        "--format=AUTHOR:%an <%ae>%nCOMMIT:%H",
        f"--since={since}",
        f"--until={until}"
    ]
    if all_refs:
        git_args.insert(1, "--all")
    
    try:
        log_out = run_git(git_args, repo)
    except RuntimeError:
        return {}
    
    # First pass: collect raw data by original name
    raw_data: Dict[str, Tuple[str, str, int, int, int]] = {}
    current_user_key: Optional[str] = None
    
    for line in log_out.splitlines():
        line = line.strip()
        
        if line.startswith("AUTHOR:"):
            author_line = line.replace("AUTHOR:", "", 1).strip()
            display_name, github_username = get_canonical_user(author_line, alias_map)
            current_user_key = display_name
            
            if current_user_key not in raw_data:
                raw_data[current_user_key] = (display_name, github_username, 0, 0, 0)
            continue
        
        if line.startswith("COMMIT:"):
            if current_user_key and current_user_key in raw_data:
                name, gh, commits, added, deleted = raw_data[current_user_key]
                raw_data[current_user_key] = (name, gh, commits + 1, added, deleted)
            continue
        
        # Parse numstat lines (added\tdeleted\tfilename)
        if "\t" in line and current_user_key:
            parts = line.split("\t")
            if len(parts) >= 2:
                add_s, del_s = parts[0], parts[1]
                if add_s != "-" and del_s != "-":
                    try:
                        name, gh, commits, added, deleted = raw_data[current_user_key]
                        raw_data[current_user_key] = (
                            name, gh, commits, 
                            added + int(add_s), 
                            deleted + int(del_s)
                        )
                    except ValueError:
                        pass
    
    # Second pass: apply name fix and merge users with same fixed name
    user_data: Dict[str, Tuple[str, str, int, int, int]] = {}
    
    for original_name, (display_name, github_username, commits, added, deleted) in raw_data.items():
        # Apply name fix - try display_name first, then github_username
        # Check if display_name is in the map (case-insensitive)
        if display_name.lower() in name_fix_map:
            fixed_name = name_fix_map[display_name.lower()]
            # Debug: print(f"DEBUG: '{display_name}' found in map -> '{fixed_name}'")
        elif github_username and github_username.lower() in name_fix_map:
            fixed_name = name_fix_map[github_username.lower()]
            # Debug: print(f"DEBUG: '{display_name}' not in map, but github '{github_username}' -> '{fixed_name}'")
        else:
            # Neither in map, use display_name as-is
            fixed_name = display_name
        
        # Merge with existing data for this fixed_name
        if fixed_name in user_data:
            existing_name, existing_gh, existing_commits, existing_added, existing_deleted = user_data[fixed_name]
            user_data[fixed_name] = (
                fixed_name,
                existing_gh or github_username,  # keep first non-empty github username
                existing_commits + commits,
                existing_added + added,
                existing_deleted + deleted
            )
        else:
            user_data[fixed_name] = (fixed_name, github_username, commits, added, deleted)
    
    return user_data


def count_prs_for_week(
    repo_full: str, 
    week_start: str, 
    week_end: str,
    name_fix_map: Dict[str, str] = None
) -> Dict[str, int]:
    """
    Count PRs opened during a specific week.
    Returns: dict mapping fixed_name -> pr_count
    """
    if name_fix_map is None:
        name_fix_map = {}
    
    try:
        out = run_gh([
            "pr", "list",
            "--repo", repo_full,
            "--limit", "2000",
            "--state", "all",
            "--search", f"created:{week_start}..{week_end}",
            "--json", "author,createdAt"
        ])
        prs = json.loads(out)
    except RuntimeError:
        return {}
    
    pr_counts: Dict[str, int] = defaultdict(int)
    
    for pr in prs:
        login = ((pr.get("author") or {}).get("login")) or ""
        if login:
            # Apply name fix to github login
            fixed_name = apply_name_fix(login, name_fix_map)
            pr_counts[fixed_name] += 1
    
    return dict(pr_counts)


def count_project_items_per_user(
    project_owner: str,
    project_number: int,
    is_org: bool = False,
    name_fix_map: Dict[str, str] = None
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Count project items created and moved by each user.
    Returns: (items_created_by, items_with_status) dicts mapping fixed_name -> count
    """
    if name_fix_map is None:
        name_fix_map = {}
    org_query = """
    query($login: String!, $number: Int!, $cursor: String) {
      organization(login: $login) {
        projectV2(number: $number) {
          id
          title
          items(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            totalCount
            nodes {
              id
              type
              creator { login }
              content {
                ... on Issue { author { login } }
                ... on PullRequest { author { login } }
                ... on DraftIssue { creator { login } }
              }
              fieldValues(first: 20) {
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
    
    user_query = """
    query($login: String!, $number: Int!, $cursor: String) {
      user(login: $login) {
        projectV2(number: $number) {
          id
          title
          items(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            totalCount
            nodes {
              id
              type
              creator { login }
              content {
                ... on Issue { author { login } }
                ... on PullRequest { author { login } }
                ... on DraftIssue { creator { login } }
              }
              fieldValues(first: 20) {
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
    
    items_created_by: Dict[str, int] = defaultdict(int)
    items_with_status: Dict[str, int] = defaultdict(int)
    
    query = org_query if is_org else user_query
    entity_type = "organization" if is_org else "user"
    
    cursor = None
    
    while True:
        gh_args = [
            "api", "graphql",
            "-f", f"query={query}",
            "-F", f"login={project_owner}",
            "-F", f"number={project_number}",
        ]
        if cursor:
            gh_args.extend(["-F", f"cursor={cursor}"])
        else:
            gh_args.extend(["-F", "cursor=null"])
        
        try:
            out = run_gh(gh_args)
        except RuntimeError:
            break
        
        payload = json.loads(out)
        
        if payload.get("errors"):
            break
        
        entity = (payload.get("data") or {}).get(entity_type) or {}
        project = entity.get("projectV2") or {}
        
        if not project:
            break
        
        items = project.get("items") or {}
        nodes = items.get("nodes") or []
        page = items.get("pageInfo") or {}
        has_next = page.get("hasNextPage")
        cursor = page.get("endCursor")
        
        for node in nodes:
            creator_login = None
            creator = node.get("creator") or {}
            creator_login = creator.get("login")
            
            if not creator_login:
                content = node.get("content") or {}
                author = content.get("author") or content.get("creator") or {}
                creator_login = author.get("login")
            
            if creator_login:
                # Apply name fix to creator login
                fixed_name = apply_name_fix(creator_login, name_fix_map)
                items_created_by[fixed_name] += 1
            
            field_values = (node.get("fieldValues") or {}).get("nodes") or []
            has_status = False
            for fv in field_values:
                if fv and fv.get("name"):
                    field = fv.get("field") or {}
                    field_name = field.get("name", "").lower()
                    if "status" in field_name:
                        has_status = True
                        break
            
            if has_status and creator_login:
                # Apply name fix to creator login
                fixed_name = apply_name_fix(creator_login, name_fix_map)
                items_with_status[fixed_name] += 1
        
        if not has_next:
            break
    
    return dict(items_created_by), dict(items_with_status)


def collect_weekly_stats(
    repo: str,
    alias_map: Dict[str, Dict[str, str]],
    weeks: List[Tuple[int, str, str]],
    repo_full: str = "",
    all_refs: bool = True,
    org_project_owner: str = "",
    org_project_number: int = 0,
    user_project_owner: str = "",
    user_project_number: int = 0,
    name_fix_map: Dict[str, str] = None
) -> Tuple[List[WeeklyUserStats], Dict[str, str], Dict[str, int], Dict[str, int], Dict[str, int], Dict[str, int]]:
    """
    Collect statistics for all users across all weeks.
    Returns: (list of WeeklyUserStats, dict of display_name -> github_username, project item dicts)
    """
    if name_fix_map is None:
        name_fix_map = {}
    
    all_stats: List[WeeklyUserStats] = []
    known_users: Dict[str, str] = {}  # display_name -> github_username
    
    # Get project items once (not per-week since API doesn't support date filtering)
    org_items_created: Dict[str, int] = {}
    org_items_moved: Dict[str, int] = {}
    user_items_created: Dict[str, int] = {}
    user_items_moved: Dict[str, int] = {}
    
    if org_project_owner and org_project_number:
        print(f"  Fetching organization project items ({org_project_owner} #{org_project_number})...")
        org_items_created, org_items_moved = count_project_items_per_user(
            org_project_owner, org_project_number, is_org=True, name_fix_map=name_fix_map
        )
        print(f"    Found {sum(org_items_created.values())} items created, {sum(org_items_moved.values())} with status")
        if org_items_created:
            print(f"    Users with org items: {list(org_items_created.keys())[:10]}...")
    
    if user_project_owner and user_project_number:
        print(f"  Fetching user project items ({user_project_owner} #{user_project_number})...")
        user_items_created, user_items_moved = count_project_items_per_user(
            user_project_owner, user_project_number, is_org=False, name_fix_map=name_fix_map
        )
        print(f"    Found {sum(user_items_created.values())} items created, {sum(user_items_moved.values())} with status")
        if user_items_created:
            print(f"    Users with user items: {list(user_items_created.keys())[:10]}...")
    
    for week_num, week_start, week_end in weeks:
        print(f"  Processing week {week_num}: {week_start} to {week_end}...")
        
        # Get commit data for this week (name fix applied inside)
        commit_data = count_commits_for_week(repo, alias_map, week_start, week_end, all_refs, name_fix_map)
        
        # Get PR data for this week (name fix applied inside)
        pr_data: Dict[str, int] = {}
        if repo_full:
            pr_data = count_prs_for_week(repo_full, week_start, week_end, name_fix_map)
        
        # Update known users
        for fixed_name, (_, github_username, _, _, _) in commit_data.items():
            if github_username:
                known_users[fixed_name] = github_username
        
        # Create stats for users with commits this week
        # Names are already fixed in commit_data and pr_data
        week_users: Dict[str, WeeklyUserStats] = {}
        
        # Make a copy of pr_data to track which PRs have been assigned
        remaining_prs = dict(pr_data)
        
        for fixed_name, (_, github_username, commits, added, deleted) in commit_data.items():
            gh = github_username or known_users.get(fixed_name, "")
            
            # Create or update stats for this user
            if fixed_name in week_users:
                existing = week_users[fixed_name]
                existing.commits += commits
                existing.lines_added += added
                existing.lines_deleted += deleted
                if not existing.github_username and gh:
                    existing.github_username = gh
            else:
                stats = WeeklyUserStats(
                    display_name=fixed_name,
                    github_username=gh,
                    week_number=week_num,
                    week_start=week_start,
                    week_end=week_end,
                    commits=commits,
                    lines_added=added,
                    lines_deleted=deleted,
                    prs_opened=0
                )
                week_users[fixed_name] = stats
            
            # Add PR count - check by fixed_name (PR data already has fixed names)
            if fixed_name in remaining_prs:
                week_users[fixed_name].prs_opened += remaining_prs.pop(fixed_name)
        
        # Add PR-only users (remaining in pr_data, already have fixed names)
        for fixed_name, pr_count in remaining_prs.items():
            if fixed_name in week_users:
                week_users[fixed_name].prs_opened += pr_count
            else:
                stats = WeeklyUserStats(
                    display_name=fixed_name,
                    github_username=fixed_name,  # Use fixed_name as github if we don't have it
                    week_number=week_num,
                    week_start=week_start,
                    week_end=week_end,
                    prs_opened=pr_count
                )
                week_users[fixed_name] = stats
                known_users[fixed_name] = fixed_name
        
        all_stats.extend(week_users.values())
    
    return all_stats, known_users, org_items_created, org_items_moved, user_items_created, user_items_moved


def generate_output_filename(base_name: str, extension: str = ".csv") -> str:
    """Generate output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"


def write_weekly_csv(
    path: str, 
    stats: List[WeeklyUserStats]
) -> None:
    """Write weekly statistics to CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "Week",
            "Week Start",
            "Week End",
            "Name",
            "GitHub",
            "Commits",
            "Added",
            "Deleted",
            "PRs"
        ])
        for s in stats:
            w.writerow([
                s.week_number,
                s.week_start,
                s.week_end,
                s.display_name,
                s.github_username,
                s.commits,
                s.lines_added,
                s.lines_deleted,
                s.prs_opened
            ])


def write_summary_csv(
    path: str, 
    stats: List[WeeklyUserStats], 
    weeks: List[Tuple[int, str, str]],
    known_users: Dict[str, str],
    org_items_created: Dict[str, int],
    org_items_moved: Dict[str, int],
    user_items_created: Dict[str, int],
    user_items_moved: Dict[str, int],
    name_fix_map: Dict[str, str] = None
) -> None:
    """Write a pivot-table style CSV with users as rows and weeks as columns."""
    if name_fix_map is None:
        name_fix_map = {}
    
    # Group stats by user (names are already fixed)
    user_weeks: Dict[str, Dict[int, WeeklyUserStats]] = defaultdict(dict)
    
    for s in stats:
        user_weeks[s.display_name][s.week_number] = s
    
    # Add users from project items who might not have commits
    # Project items already have fixed names applied
    all_project_users = set(org_items_created.keys()) | set(user_items_created.keys())
    for fixed_name in all_project_users:
        if fixed_name not in user_weeks:
            user_weeks[fixed_name] = {}
            known_users[fixed_name] = fixed_name
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        
        # Header row
        header = ["Name", "GitHub"]
        for week_num, week_start, week_end in weeks:
            header.extend([
                f"W{week_num} Commits",
                f"W{week_num} Added",
                f"W{week_num} Deleted",
                f"W{week_num} PRs"
            ])
        header.extend([
            "Total Commits", "Total Added", "Total Deleted", "Total PRs",
            "Usr Prj Items Crtd", "Usr Prj Items Mvd",
            "Org Prj Items Crtd", "Org Prj Items Mvd"
        ])
        w.writerow(header)
        
        # Sort users by total commits descending
        user_totals = {}
        for display_name in user_weeks:
            total_commits = sum(s.commits for s in user_weeks[display_name].values())
            user_totals[display_name] = total_commits
        
        sorted_users = sorted(user_weeks.keys(), key=lambda u: (-user_totals[u], u.lower()))
        
        # Data rows
        for display_name in sorted_users:
            github = known_users.get(display_name, "")
            row = [display_name, github]
            
            total_commits = 0
            total_added = 0
            total_deleted = 0
            total_prs = 0
            
            for week_num, week_start, week_end in weeks:
                if week_num in user_weeks[display_name]:
                    s = user_weeks[display_name][week_num]
                    row.extend([s.commits, s.lines_added, s.lines_deleted, s.prs_opened])
                    total_commits += s.commits
                    total_added += s.lines_added
                    total_deleted += s.lines_deleted
                    total_prs += s.prs_opened
                else:
                    row.extend([0, 0, 0, 0])
            
            # Get project items for this user (names already fixed at collection time)
            usr_created = user_items_created.get(display_name, 0)
            usr_moved = user_items_moved.get(display_name, 0)
            org_created = org_items_created.get(display_name, 0)
            org_moved = org_items_moved.get(display_name, 0)
            
            row.extend([
                total_commits, total_added, total_deleted, total_prs,
                usr_created, usr_moved, org_created, org_moved
            ])
            w.writerow(row)


def print_weekly_table(
    stats: List[WeeklyUserStats], 
    weeks: List[Tuple[int, str, str]],
    start_date: str,
    end_date: str
) -> None:
    """Print weekly statistics as a formatted table."""
    print(f"\n{'='*100}")
    print(f"GitHub Weekly Statistics Report: {start_date} to {end_date}")
    print(f"{'='*100}")
    
    # Group by week
    week_stats: Dict[int, List[WeeklyUserStats]] = defaultdict(list)
    for s in stats:
        week_stats[s.week_number].append(s)
    
    for week_num, week_start, week_end in weeks:
        print(f"\n{'─'*100}")
        print(f"Week {week_num}: {week_start} to {week_end}")
        print("─"*100)
        
        header = f"{'Name':30} {'GitHub':20} {'Commits':>8} {'Added':>8} {'Deleted':>8} {'PRs':>6}"
        print(header)
        print("-" * len(header))
        
        week_data = sorted(
            week_stats.get(week_num, []), 
            key=lambda s: (-s.commits, s.display_name.lower())
        )
        
        total_commits = 0
        total_added = 0
        total_deleted = 0
        total_prs = 0
        
        for s in week_data:
            if s.commits > 0 or s.prs_opened > 0:
                print(
                    f"{s.display_name[:30]:30} {s.github_username[:20]:20} "
                    f"{s.commits:>8} {s.lines_added:>8} {s.lines_deleted:>8} {s.prs_opened:>6}"
                )
                total_commits += s.commits
                total_added += s.lines_added
                total_deleted += s.lines_deleted
                total_prs += s.prs_opened
        
        if total_commits > 0 or total_prs > 0:
            print("-" * len(header))
            print(
                f"{'TOTAL':30} {'':20} "
                f"{total_commits:>8} {total_added:>8} {total_deleted:>8} {total_prs:>6}"
            )


def main() -> None:
    p = argparse.ArgumentParser(description="GitHub weekly statistics per user")
    
    p.add_argument("--repo", default=".", help="Path to local git repo")
    p.add_argument("--all_refs", action="store_true", help="Include all branches/tags for commit counting")
    p.add_argument("--alias_json", default="", help="Optional alias JSON for merging identities")
    p.add_argument("--name_fix_file", default="", help="Excel file with Name and Name Fixed columns for name mapping")
    
    p.add_argument("--repo_full", default="", help="GitHub repo as owner/repo (required for PR stats)")
    
    # Date range options
    p.add_argument("--start_date", required=True, help="Start date (YYYY-MM-DD)")
    p.add_argument("--end_date", required=True, help="End date (YYYY-MM-DD)")
    
    # Organization project options
    p.add_argument("--org_project_owner", default="", help="GitHub organization that owns the Project v2")
    p.add_argument("--org_project_number", type=int, default=0, help="Organization Project v2 number")
    
    # User project options
    p.add_argument("--user_project_owner", default="", help="GitHub user that owns the Project v2")
    p.add_argument("--user_project_number", type=int, default=0, help="User Project v2 number")
    
    p.add_argument("--out_csv", default="weekly_stats", help="Output CSV file base name (timestamp will be appended)")
    
    args = p.parse_args()
    
    repo_path = os.path.abspath(args.repo)
    
    # Generate output filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_weekly_csv = f"{args.out_csv}_detailed_{timestamp}.csv"
    out_summary_csv = f"{args.out_csv}_summary_{timestamp}.csv"
    
    print(f"Date range: {args.start_date} to {args.end_date}")
    print(f"Output files: {out_weekly_csv}, {out_summary_csv}")
    
    # Load alias map
    alias_map = load_alias_map(args.alias_json) if args.alias_json else {}
    
    # Load name fix map
    name_fix_map = load_name_fix_map(args.name_fix_file) if args.name_fix_file else {}
    if name_fix_map:
        print(f"Loaded {len(name_fix_map)} name mappings from {args.name_fix_file}")
    
    # Generate weeks
    weeks = get_weeks_between(args.start_date, args.end_date)
    print(f"Found {len(weeks)} weeks to analyze")
    
    # Collect statistics
    print("\nCollecting weekly statistics...")
    stats, known_users, org_items_created, org_items_moved, user_items_created, user_items_moved = collect_weekly_stats(
        repo_path,
        alias_map,
        weeks,
        repo_full=args.repo_full,
        all_refs=args.all_refs,
        org_project_owner=args.org_project_owner,
        org_project_number=args.org_project_number,
        user_project_owner=args.user_project_owner,
        user_project_number=args.user_project_number,
        name_fix_map=name_fix_map
    )
    
    # Output
    print_weekly_table(stats, weeks, args.start_date, args.end_date)
    
    # Write detailed CSV
    write_weekly_csv(out_weekly_csv, stats)
    print(f"\nWrote detailed stats to {out_weekly_csv}")
    
    # Write summary CSV
    write_summary_csv(out_summary_csv, stats, weeks, known_users, org_items_created, org_items_moved, user_items_created, user_items_moved, name_fix_map)
    print(f"Wrote summary stats to {out_summary_csv}")


if __name__ == "__main__":
    main()
