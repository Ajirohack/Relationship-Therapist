#!/usr/bin/env python3
"""
MirrorCore Relationship Therapist - WebSocket Test Client
This script connects to the WebSocket endpoint and displays real-time analytics updates.
"""

import asyncio
import json
import websockets
import argparse
import sys
import signal
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init()

# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    print(f"\n{Fore.YELLOW}WebSocket connection terminated by user.{Style.RESET_ALL}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def connect_to_websocket(url, duration=60):
    """Connect to a WebSocket server and display received messages"""
    try:
        print(f"{Fore.CYAN}Connecting to WebSocket at {url}...{Style.RESET_ALL}")
        
        async with websockets.connect(url) as websocket:
            print(f"{Fore.GREEN}Connection established! Waiting for data...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Press Ctrl+C to disconnect{Style.RESET_ALL}")
            
            start_time = datetime.now()
            end_time = start_time + (datetime.now() - start_time) + asyncio.timedelta(seconds=duration)
            
            update_count = 0
            
            while datetime.now() < end_time:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    update_count += 1
                    
                    # Parse and print the received JSON data
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"\n{Fore.CYAN}======== Update #{update_count} at {timestamp} ========{Style.RESET_ALL}")
                    
                    # Print sentiment analysis
                    print(f"{Fore.MAGENTA}Sentiment Analysis:{Style.RESET_ALL}")
                    sentiment = data.get('sentiment_analysis', {})
                    print(f"  Positive: {sentiment.get('positive', 'N/A')}%")
                    print(f"  Neutral:  {sentiment.get('neutral', 'N/A')}%")
                    print(f"  Negative: {sentiment.get('negative', 'N/A')}%")
                    
                    # Print communication patterns
                    print(f"\n{Fore.MAGENTA}Communication Patterns:{Style.RESET_ALL}")
                    patterns = data.get('communication_patterns', {})
                    for key, value in patterns.items():
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                    
                    # Print relationship health
                    print(f"\n{Fore.MAGENTA}Relationship Health:{Style.RESET_ALL}")
                    health = data.get('relationship_health', {})
                    print(f"  Overall Score: {health.get('overall_score', 'N/A')}")
                    print(f"  Trend: {health.get('trend', 'N/A')}")
                    
                    # Print real-time metrics
                    print(f"\n{Fore.MAGENTA}Real-time Metrics:{Style.RESET_ALL}")
                    metrics = data.get('real_time_metrics', {})
                    for key, value in metrics.items():
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                    
                except asyncio.TimeoutError:
                    print(f"{Fore.YELLOW}Waiting for data...{Style.RESET_ALL}")
                    
            print(f"\n{Fore.GREEN}WebSocket test completed after {duration} seconds.{Style.RESET_ALL}")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"{Fore.RED}Connection closed: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='WebSocket Client for MirrorCore Analytics')
    parser.add_argument('--url', default='ws://127.0.0.1:8000/ws/analytics', 
                        help='WebSocket server URL (default: ws://127.0.0.1:8000/ws/analytics)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds to run the WebSocket client (default: 60)')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}MirrorCore Relationship Therapist - WebSocket Test Client{Style.RESET_ALL}")
    print(f"{Fore.CYAN}====================================================={Style.RESET_ALL}")
    
    try:
        asyncio.run(connect_to_websocket(args.url, args.duration))
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}WebSocket connection terminated by user.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
