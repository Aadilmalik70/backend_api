# Sample Data for React Intern Assignment

## Sample 1: Content Structure Analysis

```json
{
  "contentId": "website-speed-optimization",
  "title": "How to Optimize Your Website Speed in 2025",
  "url": "https://example.com/blog/website-speed-optimization",
  "structureAnalysis": {
    "headingHierarchy": {
      "h1": 1,
      "h2": 3,
      "h3": 10,
      "h4": 0,
      "h5": 0,
      "h6": 0,
      "structure": [
        {
          "level": 1,
          "text": "How to Optimize Your Website Speed in 2025",
          "position": 0
        },
        {
          "level": 2,
          "text": "Why Website Speed Matters",
          "position": 2
        },
        {
          "level": 2,
          "text": "10 Proven Techniques to Optimize Website Speed",
          "position": 5
        },
        {
          "level": 3,
          "text": "1. Optimize Images and Media",
          "position": 6
        },
        {
          "level": 3,
          "text": "2. Implement Browser Caching",
          "position": 12
        },
        {
          "level": 3,
          "text": "3. Minify CSS, JavaScript, and HTML",
          "position": 19
        },
        {
          "level": 3,
          "text": "4. Use Content Delivery Networks (CDNs)",
          "position": 26
        },
        {
          "level": 3,
          "text": "5. Enable GZIP Compression",
          "position": 33
        },
        {
          "level": 3,
          "text": "6. Reduce Server Response Time",
          "position": 40
        },
        {
          "level": 3,
          "text": "7. Eliminate Render-Blocking Resources",
          "position": 47
        },
        {
          "level": 3,
          "text": "8. Optimize Web Fonts",
          "position": 54
        },
        {
          "level": 3,
          "text": "9. Implement HTTP/2 or HTTP/3",
          "position": 61
        },
        {
          "level": 3,
          "text": "10. Monitor and Optimize Core Web Vitals",
          "position": 68
        },
        {
          "level": 2,
          "text": "Conclusion",
          "position": 75
        },
        {
          "level": 2,
          "text": "Frequently Asked Questions",
          "position": 78
        },
        {
          "level": 3,
          "text": "What is a good page load time in 2025?",
          "position": 79
        },
        {
          "level": 3,
          "text": "Do mobile and desktop speeds need to be the same?",
          "position": 81
        },
        {
          "level": 3,
          "text": "How often should I check my website speed?",
          "position": 83
        }
      ]
    },
    "paragraphDistribution": {
      "total": 24,
      "averageLength": 42,
      "lengthDistribution": {
        "short": 8,
        "medium": 12,
        "long": 4
      }
    },
    "listElements": {
      "unorderedLists": 8,
      "orderedLists": 0,
      "totalListItems": 37,
      "averageItemsPerList": 4.6
    },
    "questionAnswerPatterns": {
      "total": 3,
      "patterns": [
        {
          "question": "What is a good page load time in 2025?",
          "answer": "In 2025, your website should load in under 2 seconds, with 1 second being the ideal target for optimal user experience and AI search visibility."
        },
        {
          "question": "Do mobile and desktop speeds need to be the same?",
          "answer": "While both should be fast, mobile optimization is even more critical as most users access content via mobile devices, and Google uses mobile-first indexing."
        },
        {
          "question": "How often should I check my website speed?",
          "answer": "Conduct a thorough speed audit at least once per month and after any significant website updates or changes."
        }
      ]
    },
    "codeBlocks": {
      "total": 2,
      "languages": ["html", "html"],
      "averageLength": 15
    }
  },
  "entityAnalysis": {
    "entities": [
      {
        "name": "Google",
        "type": "Organization",
        "mentions": 4,
        "confidence": 0.98
      },
      {
        "name": "PageSpeed Insights",
        "type": "Product",
        "mentions": 1,
        "confidence": 0.92
      },
      {
        "name": "Lighthouse",
        "type": "Product",
        "mentions": 2,
        "confidence": 0.94
      },
      {
        "name": "Core Web Vitals",
        "type": "Concept",
        "mentions": 2,
        "confidence": 0.96
      },
      {
        "name": "Largest Contentful Paint",
        "type": "Concept",
        "mentions": 1,
        "confidence": 0.91
      },
      {
        "name": "First Input Delay",
        "type": "Concept",
        "mentions": 1,
        "confidence": 0.90
      },
      {
        "name": "Cumulative Layout Shift",
        "type": "Concept",
        "mentions": 1,
        "confidence": 0.89
      },
      {
        "name": "GTmetrix",
        "type": "Product",
        "mentions": 1,
        "confidence": 0.88
      },
      {
        "name": "WebPageTest",
        "type": "Product",
        "mentions": 1,
        "confidence": 0.87
      }
    ],
    "entityDensity": 0.06,
    "entityRelationships": [
      {
        "source": "Google",
        "target": "Core Web Vitals",
        "relationship": "creator",
        "confidence": 0.95
      },
      {
        "source": "Core Web Vitals",
        "target": "Largest Contentful Paint",
        "relationship": "includes",
        "confidence": 0.97
      },
      {
        "source": "Core Web Vitals",
        "target": "First Input Delay",
        "relationship": "includes",
        "confidence": 0.97
      },
      {
        "source": "Core Web Vitals",
        "target": "Cumulative Layout Shift",
        "relationship": "includes",
        "confidence": 0.97
      }
    ]
  }
}
```

## Sample 2: AI Summary Score and Recommendations

```json
{
  "contentId": "website-speed-optimization",
  "title": "How to Optimize Your Website Speed in 2025",
  "url": "https://example.com/blog/website-speed-optimization",
  "aiSummaryScore": {
    "overall": 76,
    "subscores": {
      "structure": 82,
      "entities": 68,
      "directAnswers": 85,
      "factualAccuracy": 90,
      "comprehensiveness": 78,
      "freshness": 72
    },
    "summaryPotential": "High",
    "estimatedPosition": "Primary source"
  },
  "recommendations": [
    {
      "id": "rec-001",
      "category": "Structure",
      "priority": "High",
      "description": "Add a concise summary paragraph at the beginning of the article",
      "details": "Include a 2-3 sentence summary that directly answers 'how to optimize website speed' to increase chances of being featured in AI summaries",
      "estimatedScoreImprovement": 5,
      "implemented": false
    },
    {
      "id": "rec-002",
      "category": "Entities",
      "priority": "Medium",
      "description": "Add more specific entity references to speed testing tools",
      "details": "Include more specific mentions of tools like WebPageTest, GTmetrix with brief descriptions of each to strengthen entity relationships",
      "estimatedScoreImprovement": 3,
      "implemented": false
    },
    {
      "id": "rec-003",
      "category": "Structure",
      "priority": "Medium",
      "description": "Convert the '10 Proven Techniques' section to use ordered list elements",
      "details": "Change the current H3 headings to an ordered list to improve structure recognition by AI systems",
      "estimatedScoreImprovement": 2,
      "implemented": false
    },
    {
      "id": "rec-004",
      "category": "Direct Answers",
      "priority": "High",
      "description": "Add more question-answer pairs in FAQ section",
      "details": "Expand FAQ section with 3-5 more common questions about website speed optimization",
      "estimatedScoreImprovement": 4,
      "implemented": false
    },
    {
      "id": "rec-005",
      "category": "Entities",
      "priority": "Low",
      "description": "Add schema markup for HowTo content",
      "details": "Implement HowTo schema markup to explicitly define the step-by-step nature of the content",
      "estimatedScoreImprovement": 3,
      "implemented": false
    }
  ],
  "optimizedSections": [
    {
      "sectionId": "section-001",
      "heading": "10 Proven Techniques to Optimize Website Speed",
      "summaryScore": 88,
      "summaryPotential": "Very High",
      "reason": "Clear step-by-step structure with specific actionable advice"
    },
    {
      "sectionId": "section-002",
      "heading": "Frequently Asked Questions",
      "summaryScore": 85,
      "summaryPotential": "High",
      "reason": "Direct question-answer format ideal for AI summaries"
    },
    {
      "sectionId": "section-003",
      "heading": "Why Website Speed Matters",
      "summaryScore": 72,
      "summaryPotential": "Medium",
      "reason": "Good information but lacks specific data points"
    }
  ]
}
```

## Sample 3: Competitor Analysis in AI Summaries

```json
{
  "keyword": "how to optimize website speed",
  "dateAnalyzed": "2025-06-15T14:30:00Z",
  "aiSummaryPresent": true,
  "clientContentIncluded": false,
  "summaryAnalysis": {
    "length": 412,
    "sourcesCount": 4,
    "topSources": [
      {
        "domain": "moz.com",
        "title": "Website Speed Optimization: The Ultimate Guide",
        "url": "https://moz.com/learn/seo/website-speed-optimization",
        "contributionPercentage": 35,
        "keyFactorsIncluded": [
          "Image optimization techniques",
          "Server response time recommendations",
          "Core Web Vitals explanation"
        ]
      },
      {
        "domain": "web.dev",
        "title": "Fast load times: Optimize your website speed",
        "url": "https://web.dev/fast/",
        "contributionPercentage": 30,
        "keyFactorsIncluded": [
          "Code minification best practices",
          "Render-blocking resource elimination",
          "Performance measurement tools"
        ]
      },
      {
        "domain": "cloudflare.com",
        "title": "How to Speed Up Your Website in 2025",
        "url": "https://www.cloudflare.com/learning/performance/how-to-speed-up-website/",
        "contributionPercentage": 20,
        "keyFactorsIncluded": [
          "CDN implementation benefits",
          "HTTP/3 advantages",
          "Browser caching strategies"
        ]
      },
      {
        "domain": "wpbeginner.com",
        "title": "Ultimate Guide to Speed Up WordPress (Expert Tips)",
        "url": "https://www.wpbeginner.com/wordpress-performance-speed/",
        "contributionPercentage": 15,
        "keyFactorsIncluded": [
          "WordPress-specific optimization techniques",
          "Plugin management for speed",
          "Hosting recommendations"
        ]
      }
    ]
  },
  "competitorAnalysis": {
    "commonFeatures": [
      {
        "feature": "Clear step-by-step structure",
        "presentInPercent": 100,
        "importance": "Critical"
      },
      {
        "feature": "Specific tool recommendations",
        "presentInPercent": 75,
        "importance": "High"
      },
      {
        "feature": "Code examples",
        "presentInPercent": 50,
        "importance": "Medium"
      },
      {
        "feature": "Performance metrics with benchmarks",
        "presentInPercent": 75,
        "importance": "High"
      },
      {
        "feature": "Visual aids (charts, diagrams)",
        "presentInPercent": 25,
        "importance": "Medium"
      }
    ],
    "contentGaps": [
      {
        "gap": "AI search optimization for speed metrics",
        "opportunity": "High",
        "description": "None of the competitors discuss how website speed affects inclusion in AI search results"
      },
      {
        "gap": "Mobile-specific speed optimization",
        "opportunity": "Medium",
        "description": "Limited coverage of mobile-specific techniques beyond responsive design"
      },
      {
        "gap": "Speed optimization for different industries",
        "opportunity": "Medium",
        "description": "No competitor segments advice by industry type or website category"
      }
    ]
  },
  "improvementOpportunities": [
    {
      "id": "opp-001",
      "description": "Create content specifically addressing how website speed affects AI search inclusion",
      "difficulty": "Medium",
      "impactPotential": "Very High",
      "uniquenessScore": 9
    },
    {
      "id": "opp-002",
      "description": "Develop industry-specific speed optimization guides (e-commerce, media, SaaS)",
      "difficulty": "High",
      "impactPotential": "High",
      "uniquenessScore": 8
    },
    {
      "id": "opp-003",
      "description": "Include more visual aids like process diagrams and comparison charts",
      "difficulty": "Low",
      "impactPotential": "Medium",
      "uniquenessScore": 6
    },
    {
      "id": "opp-004",
      "description": "Add interactive elements like speed test tools or optimization checklist",
      "difficulty": "Medium",
      "impactPotential": "High",
      "uniquenessScore": 7
    }
  ]
}
```
