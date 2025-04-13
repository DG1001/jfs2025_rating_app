#!/usr/bin/env python3
"""
Export detailed ratings CSV with one column per user showing their ratings.
"""
import json
import csv
import os
from datetime import datetime
from pathlib import Path

def load_json_file(filepath):
    """Load JSON data from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def export_detailed_ratings():
    """Export detailed ratings to CSV with per-user columns."""
    # Get paths relative to script location
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    # Load all required data
    talks = load_json_file(data_dir / 'talks.json')
    ratings = load_json_file(data_dir / 'ratings.json')
    users = load_json_file(data_dir / 'users.json')
    
    if not all([talks, ratings, users]):
        print("Error: Missing required data files")
        return
    
    # Prepare output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = data_dir / f'ratings_detailed_{timestamp}.csv'
    
    # Create CSV writer
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        header = ['Talk ID', 'Title']
        header.extend(users[user_id]['name'] for user_id in users)
        writer.writerow(header)
        
        # Write data rows
        for talk_id, talk in talks.items():
            row = [talk_id, talk.get('title', '')]
            
            # Add ratings from each user
            for user_id in users:
                if user_id in ratings and talk_id in ratings[user_id]:
                    row.append(ratings[user_id][talk_id])
                else:
                    row.append('')  # Empty if no rating
            
            writer.writerow(row)
    
    print(f"Successfully exported detailed ratings to {output_file}")

if __name__ == '__main__':
    export_detailed_ratings()
