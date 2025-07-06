"""
Improved Content Scraper Module with Enhanced Browser Simulation

This module provides reliable web content scraping using requests + BeautifulSoup
with robust error handling and anti-bot detection countermeasures.
"""

import os
import time
import logging
import random
import re
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse, urljoin, quote_plus
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import concurrent.futures
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserContentScraper:
    """
    A reliable content scraper with enhanced browser simulation and error handling.
    
    This class provides robust web scraping with anti-bot detection countermeasures.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize the content scraper.
        
        Args:
            headless: Kept for compatibility (not used in requests-based implementation)
        """
        self.headless = headless
        self.session = None
        self._lock = Lock()
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests
        self.failed_urls = set()  # Track failed URLs to avoid repeated attempts
        self._setup_session()
        
    def _setup_session(self):
        """Set up the requests session with enhanced browser simulation."""
        self.session = requests.Session()
        
        # Configure retry strategy for non-403 errors
        retry_strategy = Retry(
            total=2,  # Reduced retries for faster processing
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],  # Don't retry 403/429
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set comprehensive realistic headers
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        # Set shorter timeout to prevent hanging
        self.session.timeout = 10
    
    def _get_random_user_agent(self) -> str:
        """Get a random realistic user agent to avoid detection."""
        user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Chrome on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            # Firefox on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Safari on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        ]
        return random.choice(user_agents)
    
    def _rate_limit(self):
        """Rate limiting with random variation to appear more human-like."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Add random variation to delays (1.5-3 seconds)
        min_delay = self.min_request_interval + random.uniform(-0.5, 1.0)
        
        if time_since_last_request < min_delay:
            sleep_time = min_delay - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def __enter__(self):
        """Context manager entry point."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()
    
    def start_browser(self):
        """Compatibility method - no-op since we don't use a browser."""
        logger.info("Content scraper initialized (using requests + BeautifulSoup)")
    
    def close(self):
        """Close the session and clean up resources."""
        if self.session:
            self.session.close()
            self.session = None
        logger.info("Content scraper closed successfully")
    
    def scrape_content(self, url: str, retry_count: int = 0) -> Dict[str, Any]:
        """
        Scrape content from a web page with enhanced error handling.
        
        Args:
            url: URL of the web page to scrape
            retry_count: Current retry attempt (for internal use)
            
        Returns:
            Dictionary containing scraped content or error info
        """
        logger.info(f"Scraping content from URL: {url}")
        
        # Check if URL previously failed
        if url in self.failed_urls and retry_count == 0:
            logger.warning(f"Skipping previously failed URL: {url}")
            return self._get_error_result(url, "Previously failed - skipping to avoid repeated failures")
        
        # Rate limit to be polite
        self._rate_limit()
        
        try:
            # Refresh user agent for retry attempts
            if retry_count > 0:
                self.session.headers['User-Agent'] = self._get_random_user_agent()
                logger.info(f"Retry attempt {retry_count} with new User-Agent")
            
            # Make the request
            response = self.session.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract page title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Extract main content
            main_content = self._extract_main_content(soup)
            
            # Extract headings
            headings = self._extract_headings(soup)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Extract images
            images = self._extract_images(soup, url)
            
            # Calculate word count
            word_count = len(main_content.split())
            
            # Get domain
            domain = urlparse(url).netloc
            
            # Calculate content metrics
            content_metrics = self._calculate_content_metrics(main_content, headings, links["all"], images)
            
            # Compile results
            result = {
                "url": url,
                "title": title,
                "description": description,
                "meta_description": description,
                "main_content": main_content,
                "headings": headings,
                "links": links,
                "images": images,
                "word_count": word_count,
                "domain": domain,
                "content_metrics": content_metrics,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status_code": response.status_code,
                "retry_count": retry_count
            }
            
            logger.info(f"Successfully scraped content from URL: {url}")
            return result
            
        except requests.exceptions.HTTPError as e:
            return self._handle_http_error(url, e, retry_count)
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(url, e, retry_count)
        except Exception as e:
            logger.error(f"Unexpected error scraping URL {url}: {str(e)}")
            return self._get_error_result(url, f"Unexpected error: {str(e)}")
    
    def _handle_http_error(self, url: str, error: requests.exceptions.HTTPError, retry_count: int) -> Dict[str, Any]:
        """Handle HTTP errors with appropriate retry logic."""
        status_code = error.response.status_code if error.response else 0
        
        if status_code == 403:
            logger.warning(f"403 Forbidden for URL {url} - website blocking automated access")
            self.failed_urls.add(url)  # Mark as failed to avoid future attempts
            return self._get_error_result(url, f"403 Forbidden - Website blocks automated access", status_code)
        
        elif status_code == 429:
            if retry_count < 2:
                wait_time = (retry_count + 1) * 5  # 5, 10 seconds
                logger.warning(f"Rate limited for URL {url}, waiting {wait_time} seconds before retry")
                time.sleep(wait_time)
                return self.scrape_content(url, retry_count + 1)
            else:
                logger.error(f"Rate limit exceeded for URL {url} after {retry_count} retries")
                return self._get_error_result(url, f"Rate limit exceeded after {retry_count} retries", status_code)
        
        elif status_code in [404, 410]:
            logger.warning(f"Content not found for URL {url} (HTTP {status_code})")
            return self._get_error_result(url, f"Content not found (HTTP {status_code})", status_code)
        
        elif status_code >= 500 and retry_count < 1:
            logger.warning(f"Server error for URL {url} (HTTP {status_code}), retrying...")
            time.sleep(3)
            return self.scrape_content(url, retry_count + 1)
        
        else:
            logger.error(f"HTTP error for URL {url}: {status_code}")
            return self._get_error_result(url, f"HTTP {status_code} error", status_code)
    
    def _handle_request_error(self, url: str, error: requests.exceptions.RequestException, retry_count: int) -> Dict[str, Any]:
        """Handle request errors with retry logic."""
        error_msg = str(error)
        
        if "timeout" in error_msg.lower() and retry_count < 1:
            logger.warning(f"Timeout for URL {url}, retrying with longer timeout...")
            self.session.timeout = 25  # Increase timeout for retry
            time.sleep(2)
            return self.scrape_content(url, retry_count + 1)
        
        elif "connection" in error_msg.lower():
            logger.error(f"Connection error for URL {url}: {error_msg}")
            return self._get_error_result(url, f"Connection error: {error_msg}")
        
        else:
            logger.error(f"Request error for URL {url}: {error_msg}")
            return self._get_error_result(url, f"Request error: {error_msg}")
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        # Try to find main content area with various selectors
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '#content',
            '.main-content',
            '#main-content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.blog-content',
            '.page-content',
            '.single-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return content_elem.get_text(separator=' ', strip=True)
        
        # Fallback: try to find the largest text block
        all_divs = soup.find_all(['div', 'section', 'article'])
        if all_divs:
            # Find div with most text content
            largest_div = max(all_divs, key=lambda x: len(x.get_text(strip=True)))
            if len(largest_div.get_text(strip=True)) > 200:  # Minimum content threshold
                return largest_div.get_text(separator=' ', strip=True)
        
        # Final fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract headings from the page."""
        headings = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = heading.get_text(strip=True)
            if text and len(text) > 1:  # Filter out empty or single-character headings
                headings.append({
                    'level': heading.name,
                    'text': text
                })
        
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract links from the page."""
        links = []
        domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Skip empty hrefs, anchors, and javascript
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # Clean up the link text
            if not text:
                text = link.get('title', '') or link.get('aria-label', '') or ''
            
            if href:  # Only add if we have a valid URL
                links.append({
                    'text': text[:200],  # Limit text length
                    'url': href
                })
        
        # Categorize links
        internal_links = []
        external_links = []
        
        for link in links:
            if domain in urlparse(link['url']).netloc:
                internal_links.append(link)
            else:
                external_links.append(link)
        
        return {
            "internal": internal_links,
            "external": external_links,
            "all": links,
            "total": len(links)
        }
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from the page."""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')  # Handle lazy loading
            if not src:
                continue
            
            # Convert relative URLs to absolute
            if src.startswith('/'):
                src = urljoin(base_url, src)
            elif not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            alt = img.get('alt', '').strip()
            
            # Skip very small images (likely icons/tracking pixels)
            width = img.get('width', 0)
            height = img.get('height', 0)
            try:
                if width and height and (int(width) < 50 or int(height) < 50):
                    continue
            except (ValueError, TypeError):
                pass
            
            images.append({
                'alt': alt,
                'src': src
            })
        
        return images
    
    def _calculate_content_metrics(self, content: str, headings: List[Dict[str, str]], 
                                 links: List[Dict[str, str]], images: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate content metrics from scraped content."""
        # Count paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip() and len(p.strip()) > 10]
        paragraph_count = len(paragraphs)
        
        # Count sentences
        sentences = []
        for p in paragraphs:
            # Split on sentence endings
            sentence_parts = re.split(r'[.!?]+', p)
            sentences.extend([s.strip() for s in sentence_parts if s.strip() and len(s.strip()) > 5])
        sentence_count = len(sentences)
        
        # Calculate average lengths
        content_length = len(content)
        avg_paragraph_length = content_length / max(1, paragraph_count)
        avg_sentence_length = content_length / max(1, sentence_count)
        
        # Calculate readability score (Flesch Reading Ease approximation)
        words = content.split()
        word_count = len(words)
        
        if sentence_count > 0 and word_count > 0:
            avg_words_per_sentence = word_count / sentence_count
            avg_syllables_per_word = sum(self._count_syllables(word) for word in words[:100]) / min(100, word_count)
            readability_score = max(0, min(100, 
                206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
            ))
        else:
            readability_score = 50  # Default middle value
        
        # Calculate keyword density (top 10 words)
        word_freq = {}
        stop_words = {
            'the', 'and', 'a', 'to', 'of', 'in', 'is', 'that', 'it', 'with', 'for', 'as', 'on', 'by', 
            'this', 'be', 'are', 'an', 'or', 'at', 'from', 'they', 'we', 'you', 'have', 'has', 'had',
            'but', 'not', 'can', 'will', 'if', 'was', 'were', 'been', 'their', 'said', 'each', 'which'
        }
        
        for word in words:
            word = re.sub(r'[^\w]', '', word.lower())
            if word and word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 keywords by frequency
        keyword_density = {}
        for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
            keyword_density[word] = round(count / max(1, word_count), 4)
        
        return {
            "readability_score": round(readability_score, 2),
            "heading_count": len(headings),
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "image_count": len(images),
            "link_count": len(links),
            "avg_paragraph_length": round(avg_paragraph_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "keyword_density": keyword_density
        }
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for readability calculation."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _get_error_result(self, url: str, error_msg: str, status_code: int = 0) -> Dict[str, Any]:
        """Generate error result with consistent structure."""
        domain = urlparse(url).netloc
        return {
            "url": url,
            "error": error_msg,
            "status_code": status_code,
            "title": "",
            "description": "",
            "meta_description": "",
            "main_content": "",
            "headings": [],
            "links": {
                "internal": [],
                "external": [],
                "all": [],
                "total": 0
            },
            "images": [],
            "word_count": 0,
            "domain": domain,
            "content_metrics": {
                "readability_score": 0,
                "heading_count": 0,
                "paragraph_count": 0,
                "sentence_count": 0,
                "image_count": 0,
                "link_count": 0,
                "avg_paragraph_length": 0,
                "avg_sentence_length": 0,
                "keyword_density": {}
            },
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "failed": True
        }
