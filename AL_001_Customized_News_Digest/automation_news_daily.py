# Automation News Digest - Daily Email Script

import feedparser
import pandas as pd
from datetime import datetime
import time
import random
import re
import requests
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class RSSAutomationNewsDigest:
    def __init__(self, keywords=None, max_results=100, debug_mode=False):
        """
        Initialize the RSS-based Automation News Digest with keywords to filter news.
        
        Args:
            keywords (list): List of keywords to filter news. If None, default keywords will be used.
            max_results (int): Maximum number of results to return (default: 20)
            debug_mode (bool): Enable extra debug output
        """
        # Default keywords related to automation
        self.default_keywords = [
            # Primary focus - digital automation
            'workflow automation', 'process automation', 'digital automation',
            'robotic process automation', 'rpa', 'hyperautomation', 
            'no-code automation', 'low-code', 'business process automation',
            'intelligent automation', 'document automation', 'task automation',
            
            # Secondary focus - AI and tools
            'ai automation', 'digital twins', 'automation tools', 'agentic',
            'ai agent', 'automation platform', 'workflow management',
            
            # General terms that may still be relevant
            'automation', 'automate', 'automated', 'automating',
            
            # Work-related terms
            'productivity automation', 'office automation', 'email automation',
            'data automation', 'automation software', 'citizen developer'
        ]
        
        self.keywords = keywords if keywords else self.default_keywords
        self.max_results = max_results
        self.debug_mode = debug_mode
        
        # Digital and workflow automation-focused RSS feeds
        self.rss_feeds = [
            # General tech sites (kept from original)
            {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/'},
            {'name': 'TechCrunch Enterprise', 'url': 'https://techcrunch.com/enterprise/feed/'},
            {'name': 'VentureBeat', 'url': 'https://feeds.feedburner.com/venturebeat/SZYF'},
            {'name': 'Wired', 'url': 'https://www.wired.com/feed/rss'},
            {'name': 'MIT Technology Review', 'url': 'https://www.technologyreview.com/feed/'},
            
            # Digital workflow and RPA-specific sources
            {'name': 'UiPath Blog', 'url': 'https://www.uipath.com/blog/rss.xml'},
            {'name': 'AutomationEdge', 'url': 'https://automationedge.com/feed'},
            {'name': 'Digital Workforce', 'url': 'https://digitalworkforce.com/rpa-news/feed/'},
            {'name': 'Intelligent Automation Network', 'url': 'https://www.intelligentautomation.network/rss/all'},
            {'name': 'Process Excellence Network', 'url': 'https://www.processexcellencenetwork.com/rss/all'},
            {'name': 'The Enterprisers Project', 'url': 'https://enterprisersproject.com/taxonomy/term/8271/feed'},
            {'name': 'SSON Analytics RPA', 'url': 'https://www.sson-analytics.com/taxonomy/term/7066/feed'},
            {'name': 'Convedo Digital Transformation', 'url': 'https://convedo.com/blog/feed/'},
            {'name': 'Sisua Digital', 'url': 'https://sisuadigital.com/feed'},
            {'name': 'Roboyo', 'url': 'https://roboyo.global/insights/feed/'}
        ]
        
        self.news_items = []
    
    def _is_related_to_automation(self, title, description=""):
        """
        Check if the article title or description is related to automation based on keywords
        and ensure it's in English.
        
        Args:
            title (str): The article title
            description (str): The article description or summary
        
        Returns:
            bool: True if related to automation and in English, False otherwise
        """
        text_to_check = (title + " " + description).lower()
        
        # Print the title if in debug mode
        if self.debug_mode:
            print(f"Checking title: {title}")
        
        # Simple language detection - check for common English words
        english_markers = ['the', 'and', 'is', 'in', 'to', 'of', 'for', 'a', 'with', 'that']
        english_word_count = sum(1 for word in english_markers if f" {word} " in f" {text_to_check} ")
        
        # Consider it English if it contains at least 2 common English words
        is_english = english_word_count >= 2
        
        # Check if it's automation-related
        is_automation_related = any(keyword.lower() in text_to_check for keyword in self.keywords)
        
        if self.debug_mode and not is_english:
            print(f"  Skipping non-English content: {title}")
        
        return is_automation_related and is_english

    def fetch_feed(self, feed):
        """
        Fetch and parse an RSS feed.
        
        Args:
            feed (dict): Dictionary containing feed name and URL
            
        Returns:
            tuple: (list of relevant news items, number of entries checked)
        """
        feed_items = []
        entries_count = 0
        
        try:
            if self.debug_mode:
                print(f"\nFetching feed: {feed['name']} ({feed['url']})")
                
            # Parse the feed
            parsed_feed = feedparser.parse(feed['url'])
            
            # Track number of entries checked
            entries_count = len(parsed_feed.entries)
            
            if self.debug_mode:
                print(f"Found {entries_count} entries")
            
            # Process each entry
            for entry in parsed_feed.entries:
                title = entry.title
                
                # Get URL (link)
                url = entry.link if hasattr(entry, 'link') else ""
                
                # Get description (summary or content)
                description = ""
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                elif hasattr(entry, 'content') and len(entry.content) > 0:
                    description = entry.content[0].value
                
                # Get publication date
                pub_date = datetime.now().strftime('%Y-%m-%d')  # Default to today
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        pub_date = time.strftime('%Y-%m-%d', entry.published_parsed)
                    except:
                        pass
                elif hasattr(entry, 'pubDate'):
                    try:
                        # Try to parse the date string
                        parsed_date = pd.to_datetime(entry.pubDate)
                        pub_date = parsed_date.strftime('%Y-%m-%d')
                    except:
                        pass
                
                # Check if related to automation
                if title and url and self._is_related_to_automation(title, description):
                    # Clean up description (remove HTML tags)
                    clean_description = re.sub(r'<.*?>', '', description)
                    # Truncate to a reasonable length
                    truncated_description = clean_description[:200] + '...' if len(clean_description) > 200 else clean_description
                    
                    feed_items.append({
                        'title': title,
                        'url': url,
                        'description': truncated_description,
                        'source': feed['name'],
                        'date': pub_date
                    })
                    
                    if self.debug_mode:
                        print(f"  Added: {title}")
            
            if self.debug_mode:
                print(f"  Found {len(feed_items)} automation-related items in this feed")
                
            return feed_items, entries_count
            
        except Exception as e:
            if self.debug_mode:
                print(f"  Error fetching feed {feed['name']}: {str(e)}")
            raise e  # Re-raise the exception to be caught in fetch_news
    
    def fetch_news(self):
        """Fetch news from all RSS feeds and filter for automation-related content."""
        if self.debug_mode:
            print("Running in DEBUG MODE")
        
        total_feeds = len(self.rss_feeds)
        total_entries_checked = 0
        successful_feeds = 0
        failed_feeds = 0
        
        print(f"Starting to fetch news from {total_feeds} RSS feeds...")
        
        # Process each feed
        for feed_index, feed in enumerate(self.rss_feeds):
            print(f"Processing feed {feed_index+1}/{total_feeds}: {feed['name']}")
            try:
                feed_items, entries_count = self.fetch_feed(feed)
                total_entries_checked += entries_count
                
                if feed_items:
                    self.news_items.extend(feed_items)
                    print(f"✓ Successfully processed {feed['name']} - Found {len(feed_items)} relevant articles from {entries_count} entries")
                    successful_feeds += 1
                else:
                    print(f"✓ Processed {feed['name']} - No relevant articles found among {entries_count} entries")
                    successful_feeds += 1
                    
                # Be nice to servers
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"✗ Failed to process {feed['name']}: {str(e)}")
                failed_feeds += 1
        
        # Sort by date (newest first)
        self.news_items.sort(key=lambda x: x['date'], reverse=True)
        
        # Limit to max_results
        if len(self.news_items) > self.max_results:
            self.news_items = self.news_items[:self.max_results]
        
        print("\n=== SUMMARY ===")
        print(f"Total feeds processed: {total_feeds}")
        print(f"Successful feeds: {successful_feeds}")
        print(f"Failed feeds: {failed_feeds}")
        print(f"Total entries checked: {total_entries_checked}")
        print(f"Found {len(self.news_items)} automation-related news items (limited to {self.max_results}).")
        
        return self.news_items
    
    def filter_news(self, additional_keywords=None):
        """Further filter news based on additional keywords."""
        if not additional_keywords:
            return self.news_items
            
        filtered_items = []
        for item in self.news_items:
            text_to_check = (item['title'] + " " + item['description']).lower()
            if any(keyword.lower() in text_to_check for keyword in additional_keywords):
                filtered_items.append(item)
                
        # Limit to max_results
        filtered_items = filtered_items[:self.max_results]
        return filtered_items
    
    def get_dataframe(self):
        """Return news items as a pandas DataFrame."""
        return pd.DataFrame(self.news_items)
    
    def save_to_csv(self, filename=None):
        """
        Save news items to a CSV file with current date in the filename.
        Files are saved to 'automation_news_folder' in the working directory.
        
        Args:
            filename (str, optional): Base filename to use. If None, default naming will be used.
        """
        import os
        
        if not self.news_items:
            print("No news items to save.")
            return
        
        # Ensure folder exists
        folder_path = 'automation_news_folder'
        os.makedirs(folder_path, exist_ok=True)
        
        # Generate filename with current date if not provided
        if filename is None:
            today_date = datetime.now().strftime('%Y-%m-%d')
            filename = f'automation_news_{today_date}.csv'
        
        # Create full path including folder
        full_path = os.path.join(folder_path, filename)
        
        df = pd.DataFrame(self.news_items)
        df.to_csv(full_path, index=False)
        print(f"Saved {len(self.news_items)} news items to {full_path}")
    
        
    def generate_html(self):
        """Generate HTML content for display in Jupyter."""
        if not self.news_items:
            return "<p>No news items found.</p>"
            
        # Group by source
        sources = {}
        for item in self.news_items:
            source = item['source']
            if source not in sources:
                sources[source] = []
            sources[source].append(item)
            
        # Create HTML content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #333;">Automation News Digest</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """
        
        for source, items in sources.items():
            html_content += f"""
            <div style="margin-bottom: 30px;">
                <h2 style="color: #0066cc; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 10px;">{source}</h2>
                <ul style="list-style-type: none; padding: 0;">
            """
            
            for item in items:
                html_content += f"""
                <li style="margin-bottom: 15px;">
                    <a href="{item['url']}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">{item['title']}</a>
                    <div style="color: #333; margin: 5px 0;">{item['description']}</div>
                    <div style="color: #666; font-size: 0.8em;">{item['date']}</div>
                </li>
                """
                
            html_content += """
                </ul>
            </div>
            """
            
        html_content += """
        </div>
        """
        
        return html_content

    def save_to_html(self, filename=None):
        """
        Save news items to an HTML file with current date in the filename.
        Files are saved to 'automation_news_folder' in the working directory.
        
        Args:
            filename (str, optional): Base filename to use. If None, default naming will be used.
        """
        import os
        
        if not self.news_items:
            print("No news items to save.")
            return
        
        # Ensure folder exists
        folder_path = 'automation_news_folder'
        os.makedirs(folder_path, exist_ok=True)
        
        # Generate filename with current date if not provided
        if filename is None:
            today_date = datetime.now().strftime('%Y-%m-%d')
            filename = f'automation_news_{today_date}.html'
        
        # Create full path including folder
        full_path = os.path.join(folder_path, filename)
        
        html_content = self.generate_html()
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Saved HTML digest to {full_path}")

def get_claude_summary():
    """
    Uses Claude API to generate a summary of the automation news
    Requires a file named 'user_api_key.txt' with your Anthropic API key
    """
    # Check if API key file exists
    if not os.path.exists('user_api_key.txt'):
        print("Error: user_api_key.txt file not found. Please create this file with your Anthropic API key.")
        return None
        
    # Read API key
    with open('user_api_key.txt', 'r') as f:
        api_key = f.read().strip()
    
    # Generate the filename with today's date
    today_date = datetime.now().strftime('%Y-%m-%d')
    html_file = f'C:\\Users\\Masu_Dev\\Documents\\automation_library\\Project_001_Customized_News_Digest\\automation_news_folder\\automation_news_{today_date}.html'
        
    # Check if HTML file exists
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found. Please run the digest.save_to_html() cell first.")
        return None
        
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Prepare the prompt
    prompt = f"""
    Here is an HTML file containing today's automation news digest.
    Please provide a concise, straightforward summary of the key trends 
    and important developments in automation technology from this digest.
    Focus on the most significant news items, avoiding unnecessary words or fluff.
    Limit your response to 3-5 key points that someone interested in automation technology should know.
    Return in bullet list format and avoid naming the article.
    
    HTML Content:
    {html_content}
    """
    
    # Make API request to Claude
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result["content"][0]["text"]
            
            # Display the summary with date
            current_date = datetime.now().strftime('%B %d, %Y')
            print(f"🤖 CLAUDE'S AUTOMATION NEWS SUMMARY - {current_date}:\n")
            print("=" * 80)
            print(summary)
            print("=" * 80)
            
            return summary
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Details: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error making API request: {str(e)}")
        return None

def setup_email_config():
    """
    Set up the email configuration.
    For Gmail, you'll need to create an "App Password" in your Google Account settings
    if you have 2-factor authentication enabled.
    """
    # Email credentials and settings
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your.email@gmail.com',  # Replace with your Gmail address
        'password': '',  # You'll need to use an App Password if 2FA is enabled
        'recipient': 'your.email@gmail.com'  # Can be the same or different email
    }
    
    # Load config from file if it exists
    config_exists = os.path.exists('email_config.json')
    
    if config_exists:
        print("Email configuration file exists. Using existing configuration.")
        # Load existing config
        with open('email_config.json', 'r') as f:
            email_config = json.load(f)
    else:
        # Only prompt for password if config doesn't exist
        from getpass import getpass
        email_config['username'] = input("Enter your Gmail address: ")
        email_config['password'] = getpass("Enter your email password or app password: ")
        email_config['recipient'] = input("Enter recipient email address (can be the same): ")
        
        with open('email_config.json', 'w') as f:
            json.dump(email_config, f)
        print("Email configuration saved to email_config.json")
    
    return email_config

def send_news_digest_email(digest_obj, claude_summary=None):
    """
    Create and send a daily news digest email combining:
    1. Today's date
    2. Claude's AI summary (if available)
    3. The HTML digest from RSS feeds
    
    Args:
        digest_obj: The RSSAutomationNewsDigest object with fetched news
        claude_summary: Optional AI summary text
    """
    # Get email config
    email_config = setup_email_config()
    
    # Get today's date in a nice format
    today_date = datetime.now().strftime('%A, %B %d, %Y')
    
    # Create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Daily Automation News Digest - {today_date}'
    msg['From'] = email_config['username']
    msg['To'] = email_config['recipient']
    
    # Create the HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }}
            .summary {{ 
                background-color: #f5f5f5; 
                padding: 15px; 
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .digest {{ margin-top: 30px; }}
        </style>
    </head>
    <body>
        <h1>Daily Automation News Digest</h1>
        <h2>{today_date}</h2>
        
        <div class="summary">
            <h3>🤖 Today's AI Summary</h3>
    """
    
    # Add Claude summary if available
    if claude_summary:
        html_content += f"{claude_summary.replace('•', '<br>•').replace('*', '<br>*')}"
    else:
        html_content += "<p>AI summary not available for today.</p>"
    
    html_content += """
        </div>
        
        <div class="digest">
            <h3>Today's Automation News</h3>
    """
    
    # Add the HTML digest content
    digest_html = digest_obj.generate_html()
    # Remove the header part (we've already added our own)
    digest_html = digest_html.split('<h1 style="color: #333;">Automation News Digest</h1>', 1)[-1]
    # Remove the date line if present
    digest_html = re.sub(r'<p>Generated on .*?</p>', '', digest_html)
    
    html_content += digest_html
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Attach parts to email
    msg.attach(MIMEText(html_content, 'html'))
    
    # Send email
    try:
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['username'], email_config['password'])
        server.send_message(msg)
        server.quit()
        print(f"✅ Email successfully sent to {email_config['recipient']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def send_daily_digest():
    """
    Main function to run the entire news digest process and send the email.
    This is the function that would be scheduled to run daily.
    """
    print(f"Starting daily news digest process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Initialize digest with default settings
        digest = RSSAutomationNewsDigest(max_results=10, debug_mode=False)
        
        # 2. Fetch the news
        print("Fetching news...")
        digest.fetch_news()
        
        # 3. Save HTML and CSV outputs
        today_date = datetime.now().strftime('%Y-%m-%d')
        html_file = f'automation_news_{today_date}.html'
        csv_file = f'automation_news_{today_date}.csv'
        
        print("Saving digest files...")
        digest.save_to_html(html_file)
        digest.save_to_csv(csv_file)
        
        # 4. Generate Claude summary
        print("Generating AI summary...")
        claude_summary = get_claude_summary()
        
        if claude_summary:
            # Save summary to file
            with open('ai_summary.txt', 'w', encoding='utf-8') as f:
                f.write(claude_summary)
        
        # 5. Send email with digest and summary
        print("Sending email...")
        send_news_digest_email(digest, claude_summary)
        
        print("Daily digest process completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error in daily digest process: {str(e)}")
        # Still try to send email with whatever data we have
        try:
            if 'digest' in locals() and hasattr(digest, 'news_items') and digest.news_items:
                send_news_digest_email(digest, "Error generating AI summary.")
                print("Sent email with partial data.")
        except:
            print("Failed to send even partial data email.")
        return False

# This is the main entry point when the script is executed directly
if __name__ == "__main__":
    send_daily_digest()