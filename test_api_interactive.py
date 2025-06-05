#!/usr/bin/env python3
"""
MirrorCore Relationship Therapist - Interactive API Tester
This script provides an interactive menu to test various API endpoints.
"""

import requests
import json
import os
import sys
from datetime import datetime
import argparse
from colorama import init, Fore, Style, Back

# Initialize colorama for cross-platform colored terminal output
init()

# Base URL for API
BASE_URL = "http://127.0.0.1:8000"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    print(f"{Back.BLUE}{Fore.WHITE} MirrorCore Relationship Therapist - Interactive API Tester {Style.RESET_ALL}")
    print(f"{Fore.CYAN}==========================================================={Style.RESET_ALL}")
    print(f"Server URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Fore.CYAN}==========================================================={Style.RESET_ALL}\n")

def print_json(data):
    """Pretty print JSON data"""
    print(f"{Fore.GREEN}")
    print(json.dumps(data, indent=2))
    print(f"{Style.RESET_ALL}")

def make_request(endpoint, method="GET", data=None, params=None):
    """Make an HTTP request to the API"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"{Fore.YELLOW}Making {method} request to {url}{Style.RESET_ALL}")
    if data:
        print(f"{Fore.YELLOW}With data:{Style.RESET_ALL}")
        print_json(data)
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        # Check if the response is valid JSON
        try:
            response_data = response.json()
            print(f"{Fore.GREEN}Response (Status: {response.status_code}):{Style.RESET_ALL}")
            print_json(response_data)
        except:
            print(f"{Fore.GREEN}Response (Status: {response.status_code}):{Style.RESET_ALL}")
            print(response.text)
        
        return response
    
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}Error: Could not connect to the server at {url}")
        print(f"Make sure the server is running.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return None

def test_health():
    """Test the health check endpoint"""
    make_request("/api/health")

def test_analytics():
    """Test the analytics endpoint"""
    make_request("/api/analytics")

def test_user_stats():
    """Test the user stats endpoint"""
    make_request("/api/v1/user/stats")

def test_user_sessions():
    """Test the user sessions endpoint"""
    limit = input(f"{Fore.CYAN}Enter session limit (default: 5): {Style.RESET_ALL}") or "5"
    make_request(f"/api/v1/user/sessions?limit={limit}")

def test_recommendations():
    """Test the recommendations endpoint"""
    make_request("/api/recommendations")

def test_knowledge_base():
    """Test the knowledge base search endpoint"""
    query = input(f"{Fore.CYAN}Enter search query (default: communication): {Style.RESET_ALL}") or "communication"
    make_request(f"/api/v1/knowledge-base/search?q={query}")

def test_reports():
    """Test the reports endpoint"""
    make_request("/api/v1/reports")

def test_chat():
    """Test the chat endpoint"""
    message = input(f"{Fore.CYAN}Enter your message: {Style.RESET_ALL}") or "Hello, I need help with my relationship"
    
    data = {
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    
    make_request("/api/v1/chat", method="POST", data=data)

def test_chat_analyze():
    """Test the chat analysis endpoint"""
    print(f"{Fore.CYAN}Enter a sample conversation (at least 2 messages):{Style.RESET_ALL}")
    
    messages = []
    message_count = 1
    
    while True:
        if message_count % 2 == 1:
            role = "user"
        else:
            role = "assistant"
            
        content = input(f"{Fore.CYAN}Enter message #{message_count} ({role}): {Style.RESET_ALL}")
        
        if not content and message_count > 2:
            break
        elif not content:
            print(f"{Fore.YELLOW}Please enter at least 2 messages.{Style.RESET_ALL}")
            continue
            
        messages.append({
            "role": role,
            "content": content
        })
        
        message_count += 1
    
    data = {
        "messages": messages
    }
    
    make_request("/api/v1/chat/analyze", method="POST", data=data)

def test_settings():
    """Test the settings endpoints"""
    print(f"{Fore.CYAN}1. Get current settings")
    print(f"2. Update settings{Style.RESET_ALL}")
    
    choice = input(f"{Fore.CYAN}Enter your choice (1-2): {Style.RESET_ALL}")
    
    if choice == "1":
        make_request("/api/v1/settings")
    elif choice == "2":
        provider = input(f"{Fore.CYAN}Enter AI provider (default: openai): {Style.RESET_ALL}") or "openai"
        model = input(f"{Fore.CYAN}Enter model (default: gpt-4): {Style.RESET_ALL}") or "gpt-4"
        kb_format = input(f"{Fore.CYAN}Enter knowledge base format (default: default): {Style.RESET_ALL}") or "default"
        tier = input(f"{Fore.CYAN}Enter subscription tier (default: professional): {Style.RESET_ALL}") or "professional"
        
        data = {
            "ai_provider": {
                "provider": provider,
                "model": model,
                "api_key": "sk-xxxxxxxxxxxx"  # Masked for security
            },
            "knowledge_base_format": kb_format,
            "subscription_tier": tier,
            "extension_installed": True
        }
        
        make_request("/api/v1/settings", method="POST", data=data)
    else:
        print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")

def test_test_connection():
    """Test the connection test endpoint"""
    provider = input(f"{Fore.CYAN}Enter AI provider (default: openai): {Style.RESET_ALL}") or "openai"
    
    data = {
        "provider": provider,
        "api_key": "sk-xxxxxxxxxxxx",  # Masked for security
        "model": "gpt-4" if provider == "openai" else "claude-2"
    }
    
    make_request("/api/v1/test-connection", method="POST", data=data)

def test_file_upload():
    """Test the file upload endpoint"""
    platform = input(f"{Fore.CYAN}Enter platform (whatsapp, telegram, etc.): {Style.RESET_ALL}") or "whatsapp"
    
    # Sample conversation data
    data = {
        "platform": platform,
        "content": {
            "messages": [
                {"sender": "User1", "text": "We need to talk about our plans", "timestamp": "2025-06-01T10:15:00Z"},
                {"sender": "User2", "text": "I thought we already decided", "timestamp": "2025-06-01T10:16:30Z"},
                {"sender": "User1", "text": "You never actually listen to my input", "timestamp": "2025-06-01T10:17:45Z"},
                {"sender": "User2", "text": "That's not fair, I do listen", "timestamp": "2025-06-01T10:18:20Z"}
            ]
        }
    }
    
    make_request("/api/v1/upload/conversation", method="POST", data=data)

def test_feedback():
    """Test the feedback endpoint"""
    rating = input(f"{Fore.CYAN}Enter rating (1-5): {Style.RESET_ALL}") or "4.5"
    comment = input(f"{Fore.CYAN}Enter comment: {Style.RESET_ALL}") or "The relationship insights have been very helpful."
    category = input(f"{Fore.CYAN}Enter category (feature_request, bug, praise): {Style.RESET_ALL}") or "praise"
    
    data = {
        "rating": float(rating),
        "comment": comment,
        "category": category
    }
    
    make_request("/api/v1/feedback", method="POST", data=data)

def run_all_tests():
    """Run all API tests"""
    print(f"{Fore.MAGENTA}Running all API tests...{Style.RESET_ALL}")
    
    test_health()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    test_analytics()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    test_user_stats()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    test_user_sessions()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    test_recommendations()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    test_knowledge_base()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    test_reports()
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    # Sample chat message
    data = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, I need help improving communication in my relationship"
            }
        ]
    }
    
    make_request("/api/v1/chat", method="POST", data=data)
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    # Sample chat analysis
    data = {
        "messages": [
            {"role": "user", "content": "My partner never listens to me"},
            {"role": "assistant", "content": "That sounds frustrating. Could you share a specific example?"},
            {"role": "user", "content": "Yesterday I was talking about my day and they were just on their phone"},
            {"role": "assistant", "content": "I understand why that would feel dismissive. Have you shared how that made you feel?"}
        ]
    }
    
    make_request("/api/v1/chat/analyze", method="POST", data=data)
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    make_request("/api/v1/settings")
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    data = {
        "provider": "openai",
        "api_key": "sk-xxxxxxxxxxxx",
        "model": "gpt-4"
    }
    
    make_request("/api/v1/test-connection", method="POST", data=data)
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    # Sample file upload
    data = {
        "platform": "whatsapp",
        "content": {
            "messages": [
                {"sender": "User1", "text": "We need to talk about our plans", "timestamp": "2025-06-01T10:15:00Z"},
                {"sender": "User2", "text": "I thought we already decided", "timestamp": "2025-06-01T10:16:30Z"},
                {"sender": "User1", "text": "You never actually listen to my input", "timestamp": "2025-06-01T10:17:45Z"},
                {"sender": "User2", "text": "That's not fair, I do listen", "timestamp": "2025-06-01T10:18:20Z"}
            ]
        }
    }
    
    make_request("/api/v1/upload/conversation", method="POST", data=data)
    
    print(f"\n{Fore.GREEN}All tests completed!{Style.RESET_ALL}")

def show_menu():
    """Show the main menu"""
    clear_screen()
    print_header()
    
    print(f"{Fore.CYAN}Select an API to test:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1. Health Check{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. Analytics Dashboard Data{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3. User Statistics{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}4. User Sessions{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}5. AI Recommendations{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}6. Knowledge Base Search{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}7. Available Reports{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}8. Chat Message{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}9. Chat Analysis{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}10. Settings Management{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}11. Test AI Provider Connection{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}12. Upload Conversation{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}13. Submit Feedback{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}14. Run All Tests{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}0. Exit{Style.RESET_ALL}")
    
    choice = input(f"\n{Fore.CYAN}Enter your choice (0-14): {Style.RESET_ALL}")
    
    if choice == "1":
        test_health()
    elif choice == "2":
        test_analytics()
    elif choice == "3":
        test_user_stats()
    elif choice == "4":
        test_user_sessions()
    elif choice == "5":
        test_recommendations()
    elif choice == "6":
        test_knowledge_base()
    elif choice == "7":
        test_reports()
    elif choice == "8":
        test_chat()
    elif choice == "9":
        test_chat_analyze()
    elif choice == "10":
        test_settings()
    elif choice == "11":
        test_test_connection()
    elif choice == "12":
        test_file_upload()
    elif choice == "13":
        test_feedback()
    elif choice == "14":
        run_all_tests()
    elif choice == "0":
        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    show_menu()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MirrorCore Relationship Therapist - Interactive API Tester")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL for the API")
    
    args = parser.parse_args()
    
    global BASE_URL
    BASE_URL = args.url
    
    try:
        show_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()
