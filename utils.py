#!/usr/bin/env python3
"""
Utilities for working with transcription results
"""

import json
import csv
from typing import Dict, List, Any
import argparse


def json_to_csv(json_file: str, csv_file: str):
    """
    Convert JSON result to CSV format
    
    Args:
        json_file: Path to JSON file
        csv_file: Path to output CSV file
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Headers
        writer.writerow(['Number', 'Start (sec)', 'End (sec)', 'Duration (sec)', 'Sentence', 'Language'])
        
        # Data
        for i, sentence in enumerate(data['sentences'], 1):
            writer.writerow([
                i,
                sentence['start_time'],
                sentence['end_time'],
                sentence['duration'],
                sentence['sentence'],
                sentence['language']
            ])
    
    print(f"CSV file saved: {csv_file}")


def json_to_srt(json_file: str, srt_file: str):
    """
    Convert JSON result to SRT format for subtitles
    
    Args:
        json_file: Path to JSON file
        srt_file: Path to output SRT file
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(srt_file, 'w', encoding='utf-8') as f:
        for i, sentence in enumerate(data['sentences'], 1):
            start_time = format_time_srt(sentence['start_time'])
            end_time = format_time_srt(sentence['end_time'])
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{sentence['sentence']}\n\n")
    
    print(f"SRT file saved: {srt_file}")


def format_time_srt(seconds: float) -> str:
    """
    Format time in SRT format (HH:MM:SS,mmm)
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def get_statistics(json_file: str):
    """
    Output transcription statistics
    
    Args:
        json_file: Path to JSON file
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== Transcription Statistics ===")
    print(f"File: {data['file_path']}")
    print(f"Language: {data['detected_language']} (probability: {data['language_probability']})")
    print(f"Total duration: {data['duration']:.2f} seconds ({data['duration']/60:.1f} minutes)")
    print(f"Number of sentences: {data['sentence_count']}")
    print(f"Number of words: {data['word_count']}")
    print(f"Speech rate: {data['word_count']/(data['duration']/60):.1f} words/minute")
    print()
    
    # Sentence duration statistics
    if data['sentences']:
        durations = [s['duration'] for s in data['sentences']]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print("=== Sentence Statistics ===")
        print(f"Average sentence duration: {avg_duration:.2f} seconds")
        print(f"Minimum duration: {min_duration:.2f} seconds")
        print(f"Maximum duration: {max_duration:.2f} seconds")
        print()
        
        # Longest sentences
        sorted_sentences = sorted(data['sentences'], key=lambda x: x['duration'], reverse=True)
        print("=== Top 5 Longest Sentences ===")
        for i, sentence in enumerate(sorted_sentences[:5], 1):
            print(f"{i}. [{sentence['duration']:.2f}s] {sentence['sentence'][:100]}...")


def search_in_transcript(json_file: str, query: str):
    """
    Search in transcription text
    
    Args:
        json_file: Path to JSON file
        query: Search query
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    query_lower = query.lower()
    matches = []
    
    for i, sentence in enumerate(data['sentences'], 1):
        if query_lower in sentence['sentence'].lower():
            matches.append((i, sentence))
    
    if matches:
        print(f"Found {len(matches)} matches for '{query}':")
        print()
        for i, (sentence_num, sentence) in enumerate(matches, 1):
            print(f"{i}. Sentence {sentence_num} [{sentence['start_time']:.2f}s - {sentence['end_time']:.2f}s]:")
            print(f"   {sentence['sentence']}")
            print()
    else:
        print(f"No matches found for '{query}'.")


def main():
    """Main function for command line"""
    parser = argparse.ArgumentParser(description='Utilities for working with transcription results')
    parser.add_argument('json_file', help='Path to JSON file with results')
    parser.add_argument('--csv', help='Convert to CSV')
    parser.add_argument('--srt', help='Convert to SRT')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--search', help='Search in text')
    
    args = parser.parse_args()
    
    if not args.csv and not args.srt and not args.stats and not args.search:
        print("Select at least one option: --csv, --srt, --stats or --search")
        return
    
    try:
        if args.csv:
            json_to_csv(args.json_file, args.csv)
        
        if args.srt:
            json_to_srt(args.json_file, args.srt)
        
        if args.stats:
            get_statistics(args.json_file)
        
        if args.search:
            search_in_transcript(args.json_file, args.search)
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
