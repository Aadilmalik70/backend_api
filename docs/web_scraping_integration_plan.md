# Web Scraping Integration Plan for SERP Strategist

## Executive Summary

This document outlines a comprehensive plan to upgrade the current web scraping implementation in the SERP Strategist backend_api project. The goal is to create a more robust, scalable, and compliant scraping architecture suitable for SaaS-level competitor analysis. The plan addresses the current limitations of the requests+BeautifulSoup approach and proposes a phased implementation of modern scraping technologies.

## Current Implementation Analysis

The current implementation (`browser_content_scraper.py`) uses:
- Requests + BeautifulSoup for HTML parsing
- Basic anti-bot measures (rotating user agents, rate limiting)
- Retry mechanisms with backoff
- Fallback to mock data when scraping fails
- Limited handling of JavaScript-rendered content

**Key Limitations:**
1. Cannot handle JavaScript-heavy websites effectively
2. Limited ability to bypass sophisticated anti-bot systems
3. No distributed scraping capabilities for scale
4. Potential compliance issues with Terms of Service and GDPR
5. Lacks robust proxy management for high-volume scraping

## Recommended Architecture

We recommend a hybrid approach that combines:

1. **Managed Scraping API** as the primary method
2. **Headless Browser Fallback** for JavaScript-heavy sites
3. **Proxy Rotation System** for reliability and scale
4. **Compliance Framework** for legal and ethical scraping

### Architecture Diagram

```
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                 │     │                   │     │                   │
│  Scraping       │     │  Proxy            │     │  Compliance       │
│  Orchestrator   ├────►│  Management       ├────►│  Filter           │
│                 │     │                   │     │                   │
└────────┬────────┘     └───────────────────┘     └─────────┬─────────┘
         │                                                  │
         ▼                                                  ▼
┌─────────────────┐                               ┌─────────────────────┐
│                 │                               │                     │
│  Managed API    │                               │  Data Processing    │
│  Client         │                               │  & Storage          │
│  (Primary)      │                               │                     │
│                 │                               └─────────────────────┘
└────────┬────────┘                                         ▲
         │                                                  │
         ▼                                                  │
┌─────────────────┐                               ┌─────────────────────┐
│                 │                               │                     │
│  Headless       ├───────────────────────────────►  Error Handling     │
│  Browser        │                               │  & Retry Logic      │
│  (Fallback)     │                               │                     │
│                 │                               └─────────────────────┘
└─────────────────┘
```

## Phased Implementation Plan

### Phase 1: Managed API Integration (Weeks 1-2)

1. **Select and integrate a managed scraping API**
   - Recommended: ScraperAPI or similar service
   - Create a new class `ManagedScraperClient` in `/src/utils/`
   - Implement configuration in `.env` for API keys

2. **Create adapter layer**
   - Develop `ScraperFactory` class to maintain the same interface
   - Ensure backward compatibility with existing code
   - Implement feature detection for when to use API vs. fallback

```python
# Example implementation structure
class ScraperFactory:
    @staticmethod
    def get_scraper(scrape_type="default"):
        if scrape_type == "api" or os.getenv("USE_MANAGED_API", "True").lower() == "true":
            return ManagedScraperClient()
        else:
            return BrowserContentScraper()  # Existing implementation
```

3. **Update error handling and retry logic**
   - Implement more sophisticated retry mechanisms
   - Add detailed logging for debugging and monitoring

### Phase 2: Headless Browser Integration (Weeks 3-4)

1. **Implement headless browser solution**
   - Use Playwright (recommended) or Puppeteer
   - Create `HeadlessBrowserScraper` class
   - Configure for JavaScript rendering and interaction

2. **Enhance the ScraperFactory**
   - Add logic to route to headless browser for JavaScript-heavy sites
   - Implement content type detection

```python
# Enhanced ScraperFactory
class ScraperFactory:
    @staticmethod
    def get_scraper(url=None, scrape_type=None):
        if scrape_type == "api" or (scrape_type is None and os.getenv("USE_MANAGED_API", "True").lower() == "true"):
            return ManagedScraperClient()
        elif scrape_type == "headless" or ScraperFactory._requires_javascript(url):
            return HeadlessBrowserScraper()
        else:
            return BrowserContentScraper()
            
    @staticmethod
    def _requires_javascript(url):
        # Logic to determine if site requires JavaScript
        # Could use a predefined list or heuristics
        pass
```

3. **Implement browser fingerprinting protection**
   - Configure browser to avoid detection
   - Randomize browser fingerprints

### Phase 3: Proxy Management & Scaling (Weeks 5-6)

1. **Implement proxy rotation system**
   - Create `ProxyManager` class
   - Integrate with proxy providers (if not using managed API)
   - Implement IP rotation strategies

2. **Add distributed scraping capabilities**
   - Implement job queue for large scraping tasks
   - Add asynchronous processing with `asyncio`
   - Create rate limiting per domain

3. **Optimize for performance**
   - Implement caching layer
   - Add request deduplication
   - Configure concurrent scraping limits

### Phase 4: Compliance Framework (Weeks 7-8)

1. **Implement robots.txt parser and respector**
   - Create `RobotsParser` class
   - Integrate with scraping workflow

2. **Add GDPR compliance filters**
   - Implement PII detection and filtering
   - Create data anonymization functions

3. **Develop ethical scraping policies**
   - Implement rate limiting based on site size
   - Add courtesy headers identifying your scraper
   - Create Terms of Service analyzer

## Code Modifications

### 1. Update `browser_content_scraper.py`

```python
"""
Enhanced Content Scraper Module

This module provides a factory pattern for selecting the appropriate scraping method
based on the target website and configuration.
"""

import os
from typing import Dict, Any, List, Optional, Union

from .managed_scraper_client import ManagedScraperClient
from .headless_browser_scraper import HeadlessBrowserScraper
from .legacy_content_scraper import LegacyContentScraper  # Renamed from BrowserContentScraper
from .proxy_manager import ProxyManager
from .compliance_filter import ComplianceFilter

class ScraperFactory:
    @staticmethod
    def get_scraper(url=None, scrape_type=None):
        """
        Factory method to get the appropriate scraper based on URL and configuration.
        
        Args:
            url: Target URL to scrape
            scrape_type: Force a specific scraper type
            
        Returns:
            A scraper instance with a consistent interface
        """
        # Check if we should use the managed API
        use_api = scrape_type == "api" or (
            scrape_type is None and 
            os.getenv("USE_MANAGED_API", "True").lower() == "true"
        )
        
        # Check if site requires JavaScript
        requires_js = scrape_type == "headless" or (
            url and ScraperFactory._requires_javascript(url)
        )
        
        # Select the appropriate scraper
        if use_api:
            return ManagedScraperClient()
        elif requires_js:
            return HeadlessBrowserScraper()
        else:
            return LegacyContentScraper()
    
    @staticmethod
    def _requires_javascript(url):
        """Determine if a site requires JavaScript for proper rendering."""
        # Implementation could use a predefined list or heuristics
        js_heavy_domains = [
            "twitter.com", "x.com", "instagram.com", 
            "facebook.com", "linkedin.com", "airbnb.com",
            "booking.com", "react", "angular", "vue"
        ]
        
        return any(domain in url.lower() for domain in js_heavy_domains)


class ContentScraper:
    """
    Main scraper interface that delegates to the appropriate implementation
    while adding compliance and proxy management.
    """
    
    def __init__(self, use_proxies=True, enforce_compliance=True):
        """
        Initialize the content scraper with optional proxy and compliance support.
        
        Args:
            use_proxies: Whether to use proxy rotation
            enforce_compliance: Whether to enforce compliance filters
        """
        self.use_proxies = use_proxies
        self.enforce_compliance = enforce_compliance
        self.proxy_manager = ProxyManager() if use_proxies else None
        self.compliance_filter = ComplianceFilter() if enforce_compliance else None
    
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a web page using the appropriate scraper.
        
        Args:
            url: URL of the web page to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        # Get the appropriate scraper
        scraper = ScraperFactory.get_scraper(url)
        
        # Apply proxy if needed
        if self.use_proxies and self.proxy_manager:
            proxy = self.proxy_manager.get_proxy(url)
            scraper.set_proxy(proxy)
        
        # Perform the scraping
        result = scraper.scrape_content(url)
        
        # Apply compliance filtering if needed
        if self.enforce_compliance and self.compliance_filter:
            result = self.compliance_filter.filter_content(result, url)
        
        return result
```

### 2. Create `managed_scraper_client.py`

```python
"""
Managed Scraper Client Module

This module provides integration with managed scraping APIs like ScraperAPI.
"""

import os
import time
import logging
import requests
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManagedScraperClient:
    """
    Client for managed scraping APIs that handle proxies, CAPTCHAs, and JavaScript rendering.
    """
    
    def __init__(self):
        """Initialize the managed scraper client."""
        self.api_key = os.getenv("SCRAPER_API_KEY")
        if not self.api_key:
            logger.warning("No SCRAPER_API_KEY found in environment variables")
        
        self.base_url = os.getenv("SCRAPER_API_URL", "https://api.scraperapi.com")
        self.session = requests.Session()
    
    def set_proxy(self, proxy):
        """Method for compatibility with the scraper interface."""
        # Not needed as the managed API handles proxies
        pass
    
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a web page using the managed API.
        
        Args:
            url: URL of the web page to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        logger.info(f"Scraping content from URL via managed API: {url}")
        
        try:
            # Prepare the API request
            params = {
                "api_key": self.api_key,
                "url": url,
                "render_js": "true",  # Enable JavaScript rendering
                "keep_headers": "true"  # Maintain headers for better site compatibility
            }
            
            # Make the request
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Process the response
            return self._process_response(response, url)
            
        except requests.RequestException as e:
            logger.error(f"API request error scraping content from URL {url}: {str(e)}")
            return self._get_error_result(url, str(e))
        except Exception as e:
            logger.error(f"Error scraping content from URL {url}: {str(e)}")
            return self._get_error_result(url, str(e))
    
    def _process_response(self, response, url):
        """Process the API response and extract content."""
        # Implementation would be similar to the existing BrowserContentScraper
        # but adapted for the managed API response format
        
        # For now, we'll use a simplified version
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract basic information
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ""
        
        # Get main content (simplified)
        body = soup.find('body')
        main_content = body.get_text(separator=' ', strip=True) if body else ""
        
        return {
            "url": url,
            "title": title,
            "description": description,
            "meta_description": description,
            "main_content": main_content,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status_code": response.status_code
        }
    
    def _get_error_result(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Generate error result with consistent structure."""
        return {
            "url": url,
            "error": error_msg,
            "title": "",
            "description": "",
            "meta_description": "",
            "main_content": "",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
```

### 3. Create `headless_browser_scraper.py`

```python
"""
Headless Browser Scraper Module

This module provides web scraping capabilities using a headless browser
for JavaScript-heavy websites.
"""

import os
import time
import logging
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeadlessBrowserScraper:
    """
    A scraper that uses Playwright for headless browser automation.
    """
    
    def __init__(self):
        """Initialize the headless browser scraper."""
        self.proxy = None
        self.browser_type = os.getenv("HEADLESS_BROWSER_TYPE", "chromium")
        self.user_agent = self._get_random_user_agent()
    
    def set_proxy(self, proxy):
        """Set proxy for browser requests."""
        self.proxy = proxy
    
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a web page using a headless browser.
        
        Args:
            url: URL of the web page to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        logger.info(f"Scraping content from URL via headless browser: {url}")
        
        try:
            # Run the async scraping function
            return asyncio.run(self._async_scrape_content(url))
            
        except Exception as e:
            logger.error(f"Error scraping content from URL {url}: {str(e)}")
            return self._get_error_result(url, str(e))
    
    async def _async_scrape_content(self, url: str) -> Dict[str, Any]:
        """Asynchronous implementation of content scraping."""
        async with async_playwright() as p:
            # Select browser type
            if self.browser_type == "firefox":
                browser_engine = p.firefox
            elif self.browser_type == "webkit":
                browser_engine = p.webkit
            else:
                browser_engine = p.chromium
            
            # Configure browser options
            browser_kwargs = {
                "headless": True
            }
            
            # Add proxy if specified
            if self.proxy:
                browser_kwargs["proxy"] = {
                    "server": f"http://{self.proxy['host']}:{self.proxy['port']}",
                }
                if self.proxy.get('username') and self.proxy.get('password'):
                    browser_kwargs["proxy"]["username"] = self.proxy['username']
                    browser_kwargs["proxy"]["password"] = self.proxy['password']
            
            # Launch browser
            browser = await browser_engine.launch(**browser_kwargs)
            
            try:
                # Create a new context with custom user agent
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    viewport={"width": 1920, "height": 1080}
                )
                
                # Create a new page
                page = await context.new_page()
                
                # Navigate to the URL with timeout
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait for content to load
                await page.wait_for_load_state("networkidle")
                
                # Extract page content
                result = await self._extract_page_content(page, url)
                
                return result
                
            finally:
                await browser.close()
    
    async def _extract_page_content(self, page, url):
        """Extract content from the loaded page."""
        # Extract title
        title = await page.title()
        
        # Extract meta description
        description = await page.evaluate("""
            () => {
                const metaDesc = document.querySelector('meta[name="description"]') || 
                                document.querySelector('meta[property="og:description"]');
                return metaDesc ? metaDesc.getAttribute('content') : '';
            }
        """)
        
        # Extract main content
        main_content = await page.evaluate("""
            () => {
                // Try to find main content area with various selectors
                const contentSelectors = [
                    'main', 'article', '[role="main"]', '.content', '#content',
                    '.main-content', '#main-content', '.post-content', '.entry-content',
                    '.article-content', '.blog-content', '.page-content', '.single-content'
                ];
                
                for (const selector of contentSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return element.innerText;
                    }
                }
                
                // Fallback to body content
                return document.body.innerText;
            }
        """)
        
        # Extract headings
        headings = await page.evaluate("""
            () => {
                const headings = [];
                document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
                    const text = heading.innerText.trim();
                    if (text && text.length > 1) {
                        headings.push({
                            level: heading.tagName.toLowerCase(),
                            text: text
                        });
                    }
                });
                return headings;
            }
        """)
        
        # Compile results
        return {
            "url": url,
            "title": title,
            "description": description,
            "meta_description": description,
            "main_content": main_content,
            "headings": headings,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent to avoid detection."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]
        import random
        return random.choice(user_agents)
    
    def _get_error_result(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Generate error result with consistent structure."""
        return {
            "url": url,
            "error": error_msg,
            "title": "",
            "description": "",
            "meta_description": "",
            "main_content": "",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
```

## Required Dependencies

Add the following to `requirements.txt`:

```
# Existing dependencies
requests>=2.28.0
beautifulsoup4>=4.11.0
urllib3>=1.26.0

# New dependencies
playwright>=1.30.0  # For headless browser
asyncio>=3.4.3      # For async operations
aiohttp>=3.8.1      # For async HTTP
scraperapi-sdk>=0.2.2  # For ScraperAPI integration (if chosen)
```

## Implementation Timeline

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 1 | Select managed API, create client class | `managed_scraper_client.py` |
| 2 | Create adapter layer, update error handling | `scraper_factory.py` |
| 3 | Implement headless browser solution | `headless_browser_scraper.py` |
| 4 | Enhance factory with content detection | Updated `scraper_factory.py` |
| 5 | Implement proxy rotation system | `proxy_manager.py` |
| 6 | Add distributed scraping capabilities | `scraping_queue.py` |
| 7 | Implement robots.txt parser | `robots_parser.py` |
| 8 | Add GDPR compliance filters | `compliance_filter.py` |

## Cost Considerations

1. **Managed API Costs**
   - ScraperAPI: Starting at $49/month for 100,000 API calls
   - Consider volume-based pricing for production

2. **Proxy Service Costs** (if not using managed API)
   - Residential proxies: $100-300/month depending on volume
   - Datacenter proxies: $50-100/month

3. **Development Costs**
   - Estimated 160-200 hours of development time

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | High | Implement request throttling, caching |
| Legal compliance issues | High | Use compliance filters, respect robots.txt |
| Increased costs | Medium | Monitor usage, implement caching |
| Breaking changes in target sites | Medium | Regular testing, monitoring |
| Performance bottlenecks | Medium | Profiling, optimization |

## Conclusion

This implementation plan provides a clear roadmap for upgrading the web scraping capabilities of the SERP Strategist backend_api. By adopting a hybrid approach with managed APIs, headless browsers, and robust compliance measures, the system will be able to handle SaaS-scale competitor analysis while maintaining reliability and legal compliance.

The phased approach allows for incremental improvements while maintaining backward compatibility, ensuring that existing functionality continues to work throughout the upgrade process.
