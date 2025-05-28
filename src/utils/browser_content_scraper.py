"""
Improved Content Scraper Module

This module provides reliable web content scraping using requests + BeautifulSoup.
This is a drop-in replacement for the Playwright-based scraper that fixes threading issues.
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
    A reliable content scraper using requests + BeautifulSoup.
    
    This class provides the same interface as the original Playwright-based scraper
    but with much better reliability and no threading issues.
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
        self._setup_session()
        
    def _setup_session(self):
        """Set up the requests session with proper configuration."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set realistic headers to avoid blocking
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set timeout
        self.session.timeout = 30
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent to avoid detection."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]
        return random.choice(user_agents)
    
    def _rate_limit(self):
        """Simple rate limiting to be polite to servers."""
        time.sleep(random.uniform(0.5, 1.5))
    
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
    
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a web page.
        
        Args:
            url: URL of the web page to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        logger.info(f"Scraping content from URL: {url}")
        
        try:
            # Rate limit to be polite
            self._rate_limit()
            
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
                "status_code": response.status_code
            }
            
            logger.info(f"Successfully scraped content from URL: {url}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Request error scraping content from URL {url}: {str(e)}")
            return self._get_error_result(url, str(e))
        except Exception as e:
            logger.error(f"Error scraping content from URL {url}: {str(e)}")
            return self._get_error_result(url, str(e))
    
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
    
    def _get_error_result(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Generate error result with consistent structure."""
        domain = urlparse(url).netloc
        return {
            "url": url,
            "error": error_msg,
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
                "image_count": 0,
                "link_count": 0,
                "avg_paragraph_length": 0,
                "avg_sentence_length": 0,
                "keyword_density": {}
            },
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def scrape_competitors(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape competitor content for a keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum number of competitors to scrape
            
        Returns:
            List of dictionaries containing competitor content
        """
        logger.info(f"Scraping competitors for keyword: {keyword}")
        
        try:
            # Get search results first
            search_results = self._get_search_results(keyword, limit)
            
            if not search_results:
                logger.warning(f"No search results found for keyword: {keyword}")
                return self._get_mock_competitors(keyword, limit)
            
            # Scrape content from each competitor
            competitors = []
            
            # Use ThreadPoolExecutor for concurrent scraping (but limit concurrency to be polite)
            max_workers = min(3, len(search_results))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit scraping tasks
                future_to_result = {
                    executor.submit(self._scrape_single_competitor, result): result 
                    for result in search_results
                }
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_result):
                    search_result = future_to_result[future]
                    try:
                        competitor_data = future.result()
                        if competitor_data:
                            competitors.append(competitor_data)
                    except Exception as e:
                        logger.error(f"Error scraping competitor {search_result.get('url', 'unknown')}: {str(e)}")
                        # Add error result
                        error_result = self._get_error_result(search_result.get('url', ''), str(e))
                        error_result.update({
                            'title': search_result.get('title', ''),
                            'snippet': search_result.get('snippet', '')
                        })
                        competitors.append(error_result)
            
            logger.info(f"Successfully scraped {len(competitors)} competitors for keyword: {keyword}")
            return competitors
            
        except Exception as e:
            logger.error(f"Error scraping competitors for keyword {keyword}: {str(e)}")
            return self._get_mock_competitors(keyword, limit)
    
    def _get_search_results(self, keyword: str, limit: int) -> List[Dict[str, str]]:
        """Get search results for a keyword."""
        try:
            # Use DuckDuckGo search (more reliable than Google for scraping)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(keyword)}"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            result_elements = soup.find_all('div', class_='result')
            
            for elem in result_elements[:limit]:
                title_elem = elem.find('a', class_='result__a')
                snippet_elem = elem.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    # Clean up URL (DuckDuckGo sometimes wraps URLs)
                    if url.startswith('/l/?uddg='):
                        # Extract actual URL from DuckDuckGo redirect
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                        if 'uddg' in parsed:
                            url = urllib.parse.unquote(parsed['uddg'][0])
                    
                    if url.startswith('http') and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting search results: {str(e)}")
            return []
    
    def _scrape_single_competitor(self, search_result: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Scrape a single competitor URL."""
        url = search_result.get('url', '')
        if not url:
            return None
        
        try:
            # Rate limit
            self._rate_limit()
            
            # Scrape the content
            content_data = self.scrape_content(url)
            
            # Add search result metadata
            content_data.update({
                'title': search_result.get('title', content_data.get('title', '')),
                'snippet': search_result.get('snippet', ''),
            })
            
            return content_data
            
        except Exception as e:
            logger.error(f"Error scraping competitor URL {url}: {str(e)}")
            return None
    
    def _get_mock_competitors(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate mock competitor data as fallback."""
        competitors = []
        
        # Common domains for fallback
        domains = [
            "example.com",
            "sample-site.org",
            "demo-content.net",
            "test-domain.com",
            "placeholder.info"
        ]
        
        for i in range(min(limit, len(domains))):
            domain = domains[i]
            title = f"{keyword.title()} - {domain.split('.')[0].title()}"
            snippet = f"Learn about {keyword} from {domain}. This is mock data due to scraping limitations."
            
            main_content = f"""
            {title}
            
            {snippet}
            
            This is mock content generated because the actual content scraping failed.
            In a real scenario, this would contain valuable information about {keyword}.
            
            Key Points about {keyword}:
            - Important concept in the field
            - Has various applications and use cases
            - Requires proper understanding and implementation
            
            For actual content, please refer to the original source.
            """
            
            content_data = {
                "title": title,
                "url": f"https://www.{domain}/{keyword.replace(' ', '-')}/",
                "snippet": snippet,
                "main_content": main_content,
                "word_count": len(main_content.split()),
                "headings": [
                    {"level": "h1", "text": title},
                    {"level": "h2", "text": f"About {keyword.title()}"}
                ],
                "links": {
                    "internal": [{"text": "Home", "url": f"https://www.{domain}/"}],
                    "external": [{"text": "External Link", "url": "https://www.google.com"}],
                    "all": [{"text": "Home", "url": f"https://www.{domain}/"}],
                    "total": 1
                },
                "images": [{"alt": "Sample Image", "src": f"https://www.{domain}/image.jpg"}],
                "meta_description": snippet,
                "description": snippet,
                "domain": domain,
                "content_metrics": {
                    "readability_score": 65.0,
                    "heading_count": 2,
                    "paragraph_count": 4,
                    "sentence_count": 8,
                    "image_count": 1,
                    "link_count": 1,
                    "avg_paragraph_length": 50.0,
                    "avg_sentence_length": 25.0,
                    "keyword_density": {keyword.replace(' ', ''): 0.1}
                },
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "is_mock": True
            }
            
            competitors.append(content_data)
        
        logger.info(f"Generated {len(competitors)} mock competitors for keyword: {keyword}")
        return competitors