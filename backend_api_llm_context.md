# LLM Context: SERP Strategist Backend API

## 1. Project Overview

This project (`backend_api`) serves as the backend API for the **SERP Strategist** application. SERP Strategist is an AI-powered tool designed to help users create SEO-optimized content blueprints to improve search engine rankings.

The backend is built using **Python** and the **Flask** web framework.

## 2. Core Purpose & Functionality

The primary purpose of this API is to receive requests (likely keywords or URLs) from the SERP Strategist frontend, perform complex analysis and AI-driven processing, and return structured data, primarily detailed content blueprints.

Key functionalities implemented include:

*   **Content Blueprint Generation:** Creating detailed outlines for content based on SEO analysis.
*   **Competitor Analysis:** Analyzing top-ranking competitor content.
*   **Keyword Processing & Research:** Analyzing keywords, potentially using external APIs.
*   **SERP Feature Optimization:** Providing recommendations for targeting specific SERP features.
*   **Content Performance Prediction:** Estimating the potential success of content (likely based on internal models or heuristics).
*   **Export & Integration:** Capabilities to export generated data.

## 3. Architecture & Key Modules

*   **Framework:** Flask (`Flask==3.1.0`)
*   **Entry Points:** `main.py` / `main_real.py` likely initialize and run the Flask app using `app.py` / `app_real.py`.
*   **Routing:** API endpoints are defined in `src/routes/api.py`.
*   **Core Logic Modules:** Located in `src/`, including modules like:
    *   `content_analyzer_enhanced.py` / `content_analyzer_enhanced_real.py`
    *   `keyword_processor_enhanced.py` / `keyword_processor_enhanced_real.py`
    *   `insight_generator_enhanced.py`
    *   `serp_feature_optimizer.py` / `serp_feature_optimizer_real.py`
    *   `competitor_analysis_real.py`
    *   `content_performance_predictor.py`
    *   `export_integration.py`
    *   (Note the presence of `_real.py` versions, suggesting a shift or parallel implementation using live data integrations vs. older/mock versions).
*   **Utilities:** A comprehensive `src/utils/` directory contains helper modules for specific tasks:
    *   External API clients (`serpapi_client.py`, `keyword_planner_api.py`, `google_nlp_client.py`, `gemini_nlp_client.py`)
    *   Web scraping/browser automation (`browser_content_scraper.py` - likely using Playwright/Selenium)
    *   Data analysis & validation (`backlink_analyzer.py`, `content_performance_analyzer.py`, `search_intent_analyzer.py`, `data_validation.py`, `prediction_validator.py`)
*   **Database:** Uses SQLAlchemy (`SQLAlchemy==2.0.40`) and PyMySQL (`PyMySQL==1.1.1`), suggesting interaction with a MySQL database, likely for storing user data, results, or configuration.
*   **Data:** Includes static mock data (`src/static/mock_data.json`) for testing or development.

## 4. Key Dependencies & Integrations

*   **Web Framework:** Flask, Flask-CORS
*   **Database:** SQLAlchemy, PyMySQL
*   **External APIs:**
    *   Google Ads API (`google-ads`)
    *   SerpAPI (`google-search-results`)
    *   Google NLP / Google Generative AI (Gemini) (`google-generativeai`, `langchain-google-genai`)
*   **Web Scraping/Automation:** Playwright, Selenium, BeautifulSoup4
*   **NLP/ML:** NLTK, Scikit-learn, Sentence-Transformers, Textstat
*   **General:** Requests, Pandas, Numpy

## 5. Development & Testing

*   The project includes a `venv` for dependency management.
*   Extensive testing scripts are present (`test_*.py`, `validate_integrations.py`, `run_tests.sh`), indicating a focus on testing, especially for the "real" data integrations.
*   Environment variables are likely managed via `.env` files (`python-dotenv`).

## 6. Summary for LLM

This is a Flask-based backend API for an AI SEO content strategy tool (SERP Strategist). It takes user inputs (keywords/topics), performs analysis using internal logic and external APIs (Google Ads, SerpAPI, Google AI/Gemini), potentially interacts with a MySQL database, and returns structured content blueprints. Key features involve competitor analysis, keyword research, and blueprint generation. It utilizes web scraping and various NLP/ML libraries. The codebase includes both mock-data-based modules and newer `_real.py` modules integrating live external APIs.
