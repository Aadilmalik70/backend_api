# Developer Prompt: Implement Enhanced Web Scraping Architecture

**Project:** SERP Strategist Backend API

**Context:**

We need to upgrade the existing web scraping functionality within the `backend_api` project to support SaaS-level competitor analysis. The current implementation (`src/utils/browser_content_scraper.py`) using `requests` + `BeautifulSoup` has limitations in handling JavaScript-heavy sites, bypassing advanced anti-bot measures, scaling, and ensuring compliance.

A detailed integration plan has been developed to address these issues. Please refer to the attached document: `/home/ubuntu/web_scraping_integration_plan.md` for the full technical specification, architecture, and phased approach.

**Objective:**

Implement the enhanced web scraping architecture as outlined in the integration plan. The goal is to create a robust, scalable, reliable, and compliant scraping system capable of handling diverse websites for competitor analysis.

**Key Requirements:**

1.  **Follow the Integration Plan:** Strictly adhere to the architecture, phased implementation, code structure, and recommendations detailed in `/home/ubuntu/web_scraping_integration_plan.md`.
2.  **Phased Implementation:** Implement the changes according to the 4 phases outlined in the plan:
    *   Phase 1: Managed API Integration
    *   Phase 2: Headless Browser Integration (Playwright recommended)
    *   Phase 3: Proxy Management & Scaling
    *   Phase 4: Compliance Framework (robots.txt, GDPR)
3.  **Backward Compatibility:** Ensure the new implementation maintains the existing interface expected by other modules. Use the `ScraperFactory` pattern as suggested in the plan to manage different scraping strategies.
4.  **Code Structure:** Create the new modules (`ManagedScraperClient`, `HeadlessBrowserScraper`, `ProxyManager`, `ComplianceFilter`, etc.) within the `/src/utils/` directory as specified.
5.  **Configuration:** Use environment variables (`.env`) for API keys, configurations, and feature flags (e.g., `USE_MANAGED_API`).
6.  **Dependencies:** Add the required dependencies (Playwright, asyncio, etc.) to `requirements.txt`.
7.  **Error Handling & Logging:** Implement robust error handling, retry logic, and detailed logging for each scraping method and component.
8.  **Testing:** Develop unit and integration tests for the new components and the overall scraping workflow.
9.  **Documentation:** Add necessary code comments and update any relevant internal documentation.

**Primary Tasks (Refer to plan for details):**

*   Refactor the existing `browser_content_scraper.py` (potentially renaming it to `legacy_content_scraper.py`).
*   Implement the `ScraperFactory` class.
*   Implement `ManagedScraperClient` (integrating with a service like ScraperAPI).
*   Implement `HeadlessBrowserScraper` using Playwright.
*   Implement `ProxyManager` (if not relying solely on a managed API).
*   Implement `ComplianceFilter` (robots.txt parsing, PII filtering).
*   Update calling modules to use the new `ContentScraper` interface or `ScraperFactory`.
*   Configure environment variables and update `requirements.txt`.

**Expected Outcome:**

A significantly improved web scraping module that:
*   Can successfully scrape both static and dynamic (JavaScript-rendered) websites.
*   Effectively handles common anti-bot measures.
*   Is scalable for handling a higher volume of scraping tasks.
*   Adheres to legal and ethical scraping practices (robots.txt, GDPR).
*   Provides reliable data for the SERP Strategist competitor analysis features.

Please review the attached integration plan thoroughly before starting implementation. Coordinate if any deviations from the plan seem necessary.
