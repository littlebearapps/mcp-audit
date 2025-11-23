#!/usr/bin/env python3
"""
Codex Session Format Investigation Script
Searches Codex session files to find where token usage data is stored
"""

import os
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    BOLD = '\033[1m'
    NC = '\033[0m'

class CodexInvestigator:
    def __init__(self):
        self.codex_home = Path.home() / ".codex"
        self.sessions_dir = self.codex_home / "sessions"

        # Statistics
        self.entry_types = Counter()
        self.fields_by_type = defaultdict(set)
        self.token_related_entries = []
        self.sample_entries = defaultdict(list)

    def investigate(self):
        """Main investigation routine"""
        print(f"{Colors.CYAN}=== Codex Session Format Investigation ==={Colors.NC}\n")

        # Find recent session files
        print(f"{Colors.YELLOW}Step 1: Finding recent session files...{Colors.NC}")
        recent_files = self.find_recent_files(limit=5)

        if not recent_files:
            print(f"{Colors.RED}No session files found in {self.sessions_dir}{Colors.NC}")
            return

        print(f"{Colors.GREEN}Found {len(recent_files)} recent files{Colors.NC}")
        for f in recent_files:
            print(f"  - {f.name} ({f.stat().st_size} bytes)")
        print()

        # Analyze files
        print(f"{Colors.YELLOW}Step 2: Analyzing session file structure...{Colors.NC}")
        for file_path in recent_files:
            self.analyze_file(file_path)

        # Report findings
        print(f"\n{Colors.CYAN}=== Investigation Results ==={Colors.NC}\n")
        self.report_findings()

    def find_recent_files(self, limit=5):
        """Find most recent session files"""
        all_files = []

        if not self.sessions_dir.exists():
            return all_files

        # Walk through year/month/day structure
        for year_dir in sorted(self.sessions_dir.iterdir(), reverse=True):
            if not year_dir.is_dir():
                continue

            for month_dir in sorted(year_dir.iterdir(), reverse=True):
                if not month_dir.is_dir():
                    continue

                for day_dir in sorted(month_dir.iterdir(), reverse=True):
                    if not day_dir.is_dir():
                        continue

                    # Get all .jsonl files in this day
                    for file_path in sorted(day_dir.glob("*.jsonl"),
                                          key=lambda x: x.stat().st_mtime,
                                          reverse=True):
                        if file_path.stat().st_size > 0:
                            all_files.append(file_path)
                            if len(all_files) >= limit:
                                return all_files

        return all_files

    def analyze_file(self, file_path):
        """Analyze a single session file"""
        print(f"  Analyzing: {file_path.name}")

        line_count = 0
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                line_count += 1
                try:
                    data = json.loads(line)
                    self.analyze_entry(data, file_path.name, line_num)
                except json.JSONDecodeError as e:
                    print(f"    {Colors.RED}JSON error at line {line_num}: {e}{Colors.NC}")

        print(f"    Processed {line_count} entries")

    def analyze_entry(self, data, filename, line_num):
        """Analyze a single JSONL entry"""
        # Track entry type
        entry_type = data.get('type', 'unknown')
        self.entry_types[entry_type] += 1

        # Track all fields for this type
        self.track_fields(data, entry_type)

        # Look for token-related data
        self.search_for_tokens(data, filename, line_num, entry_type)

        # Store sample entries (max 2 per type)
        if len(self.sample_entries[entry_type]) < 2:
            self.sample_entries[entry_type].append({
                'file': filename,
                'line': line_num,
                'data': data
            })

    def track_fields(self, data, entry_type, prefix=''):
        """Recursively track all fields in the data"""
        for key, value in data.items():
            field_path = f"{prefix}.{key}" if prefix else key
            self.fields_by_type[entry_type].add(field_path)

            # Recursively track nested objects (but not too deep)
            if isinstance(value, dict) and prefix.count('.') < 2:
                self.track_fields(value, entry_type, field_path)

    def search_for_tokens(self, data, filename, line_num, entry_type):
        """Search for token/usage data anywhere in the entry"""
        # Convert to JSON string for searching
        data_str = json.dumps(data).lower()

        # Keywords that might indicate token usage
        token_keywords = [
            'token', 'usage', 'prompt_tokens', 'completion_tokens',
            'total_tokens', 'input_tokens', 'output_tokens',
            'cache_creation', 'cache_read'
        ]

        for keyword in token_keywords:
            if keyword in data_str:
                self.token_related_entries.append({
                    'file': filename,
                    'line': line_num,
                    'type': entry_type,
                    'keyword': keyword,
                    'data': data
                })
                break  # Only record once per entry

    def report_findings(self):
        """Generate investigation report"""
        # Entry type distribution
        print(f"{Colors.BOLD}Entry Types Found:{Colors.NC}")
        for entry_type, count in self.entry_types.most_common():
            print(f"  {entry_type:<30} {count:>6} entries")
        print()

        # Fields by type
        print(f"{Colors.BOLD}Fields by Entry Type:{Colors.NC}")
        for entry_type in sorted(self.entry_types.keys()):
            print(f"\n  {Colors.CYAN}{entry_type}:{Colors.NC}")
            fields = sorted(self.fields_by_type[entry_type])
            for field in fields[:15]:  # Show first 15 fields
                print(f"    - {field}")
            if len(fields) > 15:
                print(f"    ... and {len(fields) - 15} more fields")
        print()

        # Token-related entries
        print(f"{Colors.BOLD}Token-Related Entries:{Colors.NC}")
        if self.token_related_entries:
            print(f"{Colors.GREEN}Found {len(self.token_related_entries)} entries with token-related keywords{Colors.NC}\n")

            # Group by type and keyword
            by_type = defaultdict(lambda: defaultdict(int))
            for entry in self.token_related_entries:
                by_type[entry['type']][entry['keyword']] += 1

            for entry_type, keywords in sorted(by_type.items()):
                print(f"  {Colors.CYAN}{entry_type}:{Colors.NC}")
                for keyword, count in sorted(keywords.items()):
                    print(f"    {keyword}: {count} entries")

            # Show sample token-related entry
            print(f"\n{Colors.YELLOW}Sample Token-Related Entry:{Colors.NC}")
            sample = self.token_related_entries[0]
            print(f"  Type: {sample['type']}")
            print(f"  File: {sample['file']}")
            print(f"  Line: {sample['line']}")
            print(f"  Keyword: {sample['keyword']}")
            print(f"\n{Colors.YELLOW}Full Entry:{Colors.NC}")
            print(json.dumps(sample['data'], indent=2)[:1500])  # First 1500 chars
            if len(json.dumps(sample['data'])) > 1500:
                print(f"\n  ... (truncated, {len(json.dumps(sample['data']))} total chars)")
        else:
            print(f"{Colors.RED}No entries with token-related keywords found!{Colors.NC}")
            print(f"{Colors.YELLOW}This suggests tokens might be calculated by ccusage, not stored directly.{Colors.NC}")
        print()

        # Sample entries
        print(f"{Colors.BOLD}Sample Entries by Type:{Colors.NC}")
        for entry_type in ['session_meta', 'turn_context', 'response_item'][:3]:
            if entry_type in self.sample_entries:
                samples = self.sample_entries[entry_type]
                print(f"\n  {Colors.CYAN}{entry_type} (showing 1 sample):{Colors.NC}")
                sample = samples[0]
                print(f"    File: {sample['file']}, Line: {sample['line']}")
                print(f"    Keys: {', '.join(sample['data'].keys())}")
                if 'payload' in sample['data']:
                    print(f"    Payload keys: {', '.join(sample['data']['payload'].keys())}")
        print()

        # Recommendations
        print(f"{Colors.CYAN}=== Recommendations ==={Colors.NC}\n")
        if self.token_related_entries:
            print(f"{Colors.GREEN}✓{Colors.NC} Token data found! Can build live tracker.")
            print(f"  Next step: Extract token values from {self.token_related_entries[0]['type']} entries")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.NC} No direct token data found in session files.")
            print(f"  Possible reasons:")
            print(f"    1. Tokens are calculated by ccusage from message content")
            print(f"    2. Tokens are stored in a different location")
            print(f"    3. Need to look at different/newer session files")
            print(f"  Next step: Check how ccusage/codex calculates tokens")

if __name__ == "__main__":
    investigator = CodexInvestigator()
    investigator.investigate()
