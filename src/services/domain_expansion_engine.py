"""
Domain Expansion Engine - Cross-domain query enhancement system

Expands queries across multiple business and knowledge domains to provide
comprehensive coverage and context-aware query enhancement.

Features:
- 15+ business domain mappings
- Semantic domain detection
- Context-aware expansion algorithms  
- Domain-specific terminology enrichment
- Cross-domain relationship mapping

Designed for high-performance expansion with intelligent caching.
"""

import asyncio
import logging
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import re
import json

logger = logging.getLogger(__name__)

class BusinessDomain(Enum):
    """Comprehensive business domain classification"""
    MARKETING = "marketing"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    SALES = "sales"
    OPERATIONS = "operations"
    HUMAN_RESOURCES = "human_resources"
    LEGAL = "legal"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    REAL_ESTATE = "real_estate"
    CONSULTING = "consulting"
    MEDIA = "media"
    LOGISTICS = "logistics"
    AGRICULTURE = "agriculture"
    ENERGY = "energy"
    TOURISM = "tourism"
    GENERAL = "general"

@dataclass
class DomainContext:
    """Domain-specific context and terminology"""
    domain: BusinessDomain
    keywords: List[str]
    concepts: List[str]
    related_domains: List[BusinessDomain]
    terminology: Dict[str, str]
    weight: float = 1.0

@dataclass
class ExpandedQuery:
    """Single domain-expanded query"""
    original_query: str
    expanded_query: str
    domain: BusinessDomain
    expansion_type: str
    relevance_score: float
    added_terms: List[str]
    domain_context: Optional[DomainContext] = None

@dataclass
class ExpansionResult:
    """Complete domain expansion result"""
    original_query: str
    primary_domains: List[BusinessDomain]
    expanded_queries: List[ExpandedQuery]
    cross_domain_insights: List[str]
    processing_time: float
    confidence_score: float
    suggested_domains: List[Tuple[BusinessDomain, float]]

class DomainExpansionEngine:
    """
    Advanced domain expansion system for cross-domain query enhancement.
    
    Analyzes queries to identify relevant business domains and generates
    domain-specific expanded queries with context-aware terminology.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the domain expansion engine"""
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Domain mappings and relationships
        self.domain_contexts = self._initialize_domain_contexts()
        self.domain_relationships = self._initialize_domain_relationships()
        self.expansion_patterns = self._initialize_expansion_patterns()
        
        # Performance caching
        self.expansion_cache = {}
        self.domain_cache = {}
        
        # Metrics tracking
        self.metrics = {
            'total_expansions': 0,
            'cache_hit_rate': 0.0,
            'avg_processing_time': 0.0,
            'domain_accuracy': {},
            'expansion_effectiveness': {}
        }
        
        self.logger.info("Domain Expansion Engine initialized with 19 business domains")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for domain expansion"""
        return {
            'max_expanded_queries': 5,
            'min_relevance_score': 0.3,
            'enable_cross_domain_insights': True,
            'enable_caching': True,
            'cache_ttl_seconds': 3600,
            'expansion_depth': 2,
            'domain_weight_threshold': 0.1
        }
    
    def _initialize_domain_contexts(self) -> Dict[BusinessDomain, DomainContext]:
        """Initialize comprehensive domain contexts"""
        return {
            BusinessDomain.MARKETING: DomainContext(
                domain=BusinessDomain.MARKETING,
                keywords=['campaign', 'brand', 'advertising', 'promotion', 'customer', 'engagement', 'conversion'],
                concepts=['customer acquisition', 'brand awareness', 'content marketing', 'digital marketing', 'lead generation'],
                related_domains=[BusinessDomain.SALES, BusinessDomain.TECHNOLOGY, BusinessDomain.MEDIA],
                terminology={
                    'customers': 'target audience, prospects, leads',
                    'promote': 'advertise, market, publicize',
                    'strategy': 'campaign strategy, marketing plan, go-to-market strategy'
                }
            ),
            BusinessDomain.TECHNOLOGY: DomainContext(
                domain=BusinessDomain.TECHNOLOGY,
                keywords=['software', 'system', 'platform', 'integration', 'automation', 'digital', 'cloud'],
                concepts=['software development', 'system architecture', 'digital transformation', 'automation', 'cloud computing'],
                related_domains=[BusinessDomain.OPERATIONS, BusinessDomain.FINANCE, BusinessDomain.MARKETING],
                terminology={
                    'process': 'workflow, system process, automation',
                    'improve': 'optimize, enhance, upgrade',
                    'manage': 'administer, monitor, orchestrate'
                }
            ),
            BusinessDomain.FINANCE: DomainContext(
                domain=BusinessDomain.FINANCE,
                keywords=['budget', 'cost', 'revenue', 'profit', 'investment', 'financial', 'accounting'],
                concepts=['financial planning', 'cost management', 'investment analysis', 'budgeting', 'financial reporting'],
                related_domains=[BusinessDomain.OPERATIONS, BusinessDomain.SALES, BusinessDomain.LEGAL],
                terminology={
                    'money': 'capital, funds, investment',
                    'save': 'reduce costs, optimize expenses',
                    'track': 'monitor financials, analyze spending'
                }
            ),
            BusinessDomain.SALES: DomainContext(
                domain=BusinessDomain.SALES,
                keywords=['lead', 'prospect', 'deal', 'pipeline', 'conversion', 'closing', 'quota'],
                concepts=['lead qualification', 'sales funnel', 'deal closing', 'customer relationship', 'sales process'],
                related_domains=[BusinessDomain.MARKETING, BusinessDomain.FINANCE, BusinessDomain.OPERATIONS],
                terminology={
                    'customer': 'prospect, lead, client',
                    'sell': 'close deals, convert leads',
                    'target': 'prospect, qualify leads'
                }
            ),
            BusinessDomain.OPERATIONS: DomainContext(
                domain=BusinessDomain.OPERATIONS,
                keywords=['process', 'workflow', 'efficiency', 'productivity', 'quality', 'performance', 'delivery'],
                concepts=['process optimization', 'operational efficiency', 'quality management', 'supply chain', 'delivery'],
                related_domains=[BusinessDomain.TECHNOLOGY, BusinessDomain.FINANCE, BusinessDomain.HUMAN_RESOURCES],
                terminology={
                    'improve': 'optimize, streamline, enhance',
                    'manage': 'oversee, coordinate, execute',
                    'deliver': 'fulfill, complete, provide'
                }
            ),
            BusinessDomain.HUMAN_RESOURCES: DomainContext(
                domain=BusinessDomain.HUMAN_RESOURCES,
                keywords=['employee', 'talent', 'recruitment', 'training', 'performance', 'culture', 'benefits'],
                concepts=['talent management', 'employee development', 'performance management', 'organizational culture', 'compensation'],
                related_domains=[BusinessDomain.OPERATIONS, BusinessDomain.FINANCE, BusinessDomain.LEGAL],
                terminology={
                    'people': 'employees, talent, workforce',
                    'hire': 'recruit, onboard, acquire talent',
                    'develop': 'train, upskill, mentor'
                }
            ),
            BusinessDomain.LEGAL: DomainContext(
                domain=BusinessDomain.LEGAL,
                keywords=['compliance', 'contract', 'regulation', 'policy', 'risk', 'governance', 'audit'],
                concepts=['regulatory compliance', 'contract management', 'risk management', 'corporate governance', 'legal review'],
                related_domains=[BusinessDomain.FINANCE, BusinessDomain.HUMAN_RESOURCES, BusinessDomain.OPERATIONS],
                terminology={
                    'rules': 'regulations, policies, compliance requirements',
                    'manage': 'govern, oversee, ensure compliance',
                    'review': 'audit, assess, evaluate'
                }
            ),
            BusinessDomain.HEALTHCARE: DomainContext(
                domain=BusinessDomain.HEALTHCARE,
                keywords=['patient', 'medical', 'treatment', 'diagnosis', 'clinical', 'health', 'care'],
                concepts=['patient care', 'medical treatment', 'clinical diagnosis', 'healthcare delivery', 'medical records'],
                related_domains=[BusinessDomain.TECHNOLOGY, BusinessDomain.LEGAL, BusinessDomain.OPERATIONS],
                terminology={
                    'patient': 'client, individual, person receiving care',
                    'treat': 'provide care, administer treatment',
                    'track': 'monitor health, record medical data'
                }
            ),
            BusinessDomain.EDUCATION: DomainContext(
                domain=BusinessDomain.EDUCATION,
                keywords=['student', 'learning', 'curriculum', 'assessment', 'teaching', 'education', 'training'],
                concepts=['curriculum development', 'student assessment', 'educational technology', 'learning outcomes', 'instruction'],
                related_domains=[BusinessDomain.TECHNOLOGY, BusinessDomain.HUMAN_RESOURCES, BusinessDomain.OPERATIONS],
                terminology={
                    'learn': 'study, acquire knowledge, develop skills',
                    'teach': 'instruct, educate, train',
                    'assess': 'evaluate, test, measure progress'
                }
            ),
            BusinessDomain.RETAIL: DomainContext(
                domain=BusinessDomain.RETAIL,
                keywords=['product', 'inventory', 'store', 'customer', 'sales', 'merchandise', 'shopping'],
                concepts=['inventory management', 'customer experience', 'product merchandising', 'retail operations', 'point of sale'],
                related_domains=[BusinessDomain.MARKETING, BusinessDomain.SALES, BusinessDomain.LOGISTICS],
                terminology={
                    'sell': 'retail, merchandise, offer products',
                    'customer': 'shopper, buyer, consumer',
                    'stock': 'inventory, merchandise, products'
                }
            ),
            BusinessDomain.MANUFACTURING: DomainContext(
                domain=BusinessDomain.MANUFACTURING,
                keywords=['production', 'quality', 'supply', 'factory', 'equipment', 'materials', 'assembly'],
                concepts=['production planning', 'quality control', 'supply chain management', 'manufacturing processes', 'equipment maintenance'],
                related_domains=[BusinessDomain.OPERATIONS, BusinessDomain.LOGISTICS, BusinessDomain.TECHNOLOGY],
                terminology={
                    'make': 'manufacture, produce, fabricate',
                    'quality': 'quality control, quality assurance',
                    'supply': 'sourcing, procurement, supply chain'
                }
            ),
            BusinessDomain.REAL_ESTATE: DomainContext(
                domain=BusinessDomain.REAL_ESTATE,
                keywords=['property', 'lease', 'rental', 'market', 'location', 'investment', 'development'],
                concepts=['property management', 'real estate investment', 'property development', 'leasing', 'market analysis'],
                related_domains=[BusinessDomain.FINANCE, BusinessDomain.LEGAL, BusinessDomain.CONSULTING],
                terminology={
                    'property': 'real estate, premises, location',
                    'rent': 'lease, tenancy, occupancy',
                    'invest': 'property investment, real estate portfolio'
                }
            ),
            BusinessDomain.CONSULTING: DomainContext(
                domain=BusinessDomain.CONSULTING,
                keywords=['advisory', 'strategy', 'analysis', 'recommendation', 'expertise', 'solution', 'consulting'],
                concepts=['strategic consulting', 'business analysis', 'expert advisory', 'solution design', 'implementation support'],
                related_domains=[BusinessDomain.FINANCE, BusinessDomain.TECHNOLOGY, BusinessDomain.OPERATIONS],
                terminology={
                    'advice': 'consulting, advisory services, recommendations',
                    'analyze': 'assess, evaluate, review',
                    'solution': 'recommendation, strategy, approach'
                }
            ),
            BusinessDomain.MEDIA: DomainContext(
                domain=BusinessDomain.MEDIA,
                keywords=['content', 'publication', 'broadcast', 'digital', 'social', 'communication', 'audience'],
                concepts=['content creation', 'digital publishing', 'audience engagement', 'media distribution', 'communication strategy'],
                related_domains=[BusinessDomain.MARKETING, BusinessDomain.TECHNOLOGY, BusinessDomain.EDUCATION],
                terminology={
                    'content': 'media content, publication, material',
                    'audience': 'viewers, readers, consumers',
                    'publish': 'broadcast, distribute, share'
                }
            ),
            BusinessDomain.LOGISTICS: DomainContext(
                domain=BusinessDomain.LOGISTICS,
                keywords=['shipping', 'delivery', 'transport', 'warehouse', 'distribution', 'supply', 'logistics'],
                concepts=['supply chain logistics', 'transportation management', 'warehouse operations', 'distribution networks', 'delivery optimization'],
                related_domains=[BusinessDomain.OPERATIONS, BusinessDomain.MANUFACTURING, BusinessDomain.RETAIL],
                terminology={
                    'ship': 'transport, deliver, distribute',
                    'store': 'warehouse, inventory, stock',
                    'move': 'transport, transfer, deliver'
                }
            ),
            BusinessDomain.AGRICULTURE: DomainContext(
                domain=BusinessDomain.AGRICULTURE,
                keywords=['farming', 'crop', 'livestock', 'agricultural', 'harvest', 'soil', 'rural'],
                concepts=['crop management', 'livestock care', 'agricultural technology', 'sustainable farming', 'food production'],
                related_domains=[BusinessDomain.TECHNOLOGY, BusinessDomain.LOGISTICS, BusinessDomain.FINANCE],
                terminology={
                    'grow': 'cultivate, farm, produce crops',
                    'manage': 'agricultural management, farm operations',
                    'harvest': 'collect crops, agricultural yield'
                }
            ),
            BusinessDomain.ENERGY: DomainContext(
                domain=BusinessDomain.ENERGY,
                keywords=['power', 'electricity', 'renewable', 'grid', 'consumption', 'efficiency', 'utility'],
                concepts=['energy production', 'renewable energy', 'power distribution', 'energy efficiency', 'utility management'],
                related_domains=[BusinessDomain.TECHNOLOGY, BusinessDomain.OPERATIONS, BusinessDomain.LEGAL],
                terminology={
                    'power': 'energy, electricity, utility',
                    'efficient': 'energy-efficient, optimized consumption',
                    'generate': 'produce energy, power generation'
                }
            ),
            BusinessDomain.TOURISM: DomainContext(
                domain=BusinessDomain.TOURISM,
                keywords=['travel', 'hospitality', 'hotel', 'destination', 'tourist', 'vacation', 'booking'],
                concepts=['hospitality management', 'destination marketing', 'travel services', 'customer experience', 'tourism operations'],
                related_domains=[BusinessDomain.MARKETING, BusinessDomain.RETAIL, BusinessDomain.OPERATIONS],
                terminology={
                    'travel': 'tourism, hospitality, vacation',
                    'guest': 'tourist, traveler, visitor',
                    'service': 'hospitality service, customer care'
                }
            ),
            BusinessDomain.GENERAL: DomainContext(
                domain=BusinessDomain.GENERAL,
                keywords=['business', 'company', 'organization', 'management', 'strategy', 'operations', 'general'],
                concepts=['business strategy', 'organizational management', 'general operations', 'corporate governance', 'business development'],
                related_domains=[BusinessDomain.MARKETING, BusinessDomain.FINANCE, BusinessDomain.OPERATIONS],
                terminology={
                    'business': 'organization, company, enterprise',
                    'manage': 'oversee, administer, coordinate',
                    'strategy': 'plan, approach, methodology'
                }
            )
        }
    
    def _initialize_domain_relationships(self) -> Dict[BusinessDomain, Dict[BusinessDomain, float]]:
        """Initialize domain relationship strengths (0.0-1.0)"""
        return {
            BusinessDomain.MARKETING: {
                BusinessDomain.SALES: 0.9,
                BusinessDomain.TECHNOLOGY: 0.7,
                BusinessDomain.MEDIA: 0.8,
                BusinessDomain.RETAIL: 0.6
            },
            BusinessDomain.TECHNOLOGY: {
                BusinessDomain.OPERATIONS: 0.8,
                BusinessDomain.FINANCE: 0.6,
                BusinessDomain.MARKETING: 0.7,
                BusinessDomain.MANUFACTURING: 0.7
            },
            BusinessDomain.FINANCE: {
                BusinessDomain.OPERATIONS: 0.7,
                BusinessDomain.SALES: 0.8,
                BusinessDomain.LEGAL: 0.6,
                BusinessDomain.REAL_ESTATE: 0.7
            },
            BusinessDomain.SALES: {
                BusinessDomain.MARKETING: 0.9,
                BusinessDomain.FINANCE: 0.8,
                BusinessDomain.OPERATIONS: 0.6,
                BusinessDomain.RETAIL: 0.7
            },
            BusinessDomain.OPERATIONS: {
                BusinessDomain.TECHNOLOGY: 0.8,
                BusinessDomain.FINANCE: 0.7,
                BusinessDomain.HUMAN_RESOURCES: 0.6,
                BusinessDomain.MANUFACTURING: 0.8
            },
            BusinessDomain.HUMAN_RESOURCES: {
                BusinessDomain.OPERATIONS: 0.6,
                BusinessDomain.FINANCE: 0.5,
                BusinessDomain.LEGAL: 0.7,
                BusinessDomain.EDUCATION: 0.5
            },
            BusinessDomain.LEGAL: {
                BusinessDomain.FINANCE: 0.6,
                BusinessDomain.HUMAN_RESOURCES: 0.7,
                BusinessDomain.OPERATIONS: 0.5,
                BusinessDomain.HEALTHCARE: 0.6
            },
            BusinessDomain.HEALTHCARE: {
                BusinessDomain.TECHNOLOGY: 0.7,
                BusinessDomain.LEGAL: 0.6,
                BusinessDomain.OPERATIONS: 0.6,
                BusinessDomain.EDUCATION: 0.5
            }
        }
    
    def _initialize_expansion_patterns(self) -> Dict[str, List[str]]:
        """Initialize query expansion patterns"""
        return {
            'domain_specific_terms': [
                '{query} in {domain}',
                '{domain} approach to {query}',
                '{query} for {domain} industry',
                '{domain}-focused {query}'
            ],
            'cross_domain_insights': [
                '{query} across {domain1} and {domain2}',
                'How {domain1} and {domain2} handle {query}',
                '{query} integration between {domain1} and {domain2}'
            ],
            'terminology_expansion': [
                '{query} including {domain_terms}',
                '{query} with {domain_context}',
                '{expanded_query} in {domain} context'
            ]
        }
    
    async def expand_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> ExpansionResult:
        """
        Expand a query across relevant business domains
        
        Args:
            query: The original query to expand
            context: Optional context for expansion hints
            
        Returns:
            ExpansionResult with domain-expanded queries
        """
        start_time = time.time()
        
        try:
            if not query or not query.strip():
                return ExpansionResult(
                    original_query=query,
                    primary_domains=[],
                    expanded_queries=[],
                    cross_domain_insights=[],
                    processing_time=time.time() - start_time,
                    confidence_score=0.0,
                    suggested_domains=[]
                )
            
            query = query.strip()
            self.logger.debug(f"Expanding query: '{query[:50]}...'")
            
            # Check cache first
            cache_key = self._generate_cache_key(query, context)
            if self.config.get('enable_caching', True) and cache_key in self.expansion_cache:
                cached_result = self.expansion_cache[cache_key]
                cached_result.processing_time = time.time() - start_time
                self.metrics['cache_hit_rate'] = (self.metrics.get('cache_hit_rate', 0) * 0.9 + 0.1)
                return cached_result
            
            # Step 1: Identify primary domains
            primary_domains = await self._identify_primary_domains(query, context)
            
            # Step 2: Generate expanded queries for each domain
            expanded_queries = await self._generate_domain_expansions(query, primary_domains)
            
            # Step 3: Generate cross-domain insights
            cross_domain_insights = []
            if self.config.get('enable_cross_domain_insights', True):
                cross_domain_insights = await self._generate_cross_domain_insights(query, primary_domains)
            
            # Step 4: Calculate confidence and suggested domains
            confidence_score = await self._calculate_expansion_confidence(query, primary_domains, expanded_queries)
            suggested_domains = await self._suggest_additional_domains(query, primary_domains)
            
            # Create result
            processing_time = time.time() - start_time
            result = ExpansionResult(
                original_query=query,
                primary_domains=primary_domains,
                expanded_queries=expanded_queries,
                cross_domain_insights=cross_domain_insights,
                processing_time=processing_time,
                confidence_score=confidence_score,
                suggested_domains=suggested_domains
            )
            
            # Cache result
            if self.config.get('enable_caching', True):
                self.expansion_cache[cache_key] = result
            
            # Update metrics
            self.metrics['total_expansions'] += 1
            self.metrics['avg_processing_time'] = (
                (self.metrics.get('avg_processing_time', 0) * (self.metrics['total_expansions'] - 1) + processing_time) /
                self.metrics['total_expansions']
            )
            
            self.logger.info(f"Query expanded across {len(primary_domains)} domains in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Query expansion failed: {e}")
            return ExpansionResult(
                original_query=query,
                primary_domains=[],
                expanded_queries=[],
                cross_domain_insights=[f"Expansion error: {str(e)}"],
                processing_time=time.time() - start_time,
                confidence_score=0.0,
                suggested_domains=[]
            )
    
    async def _identify_primary_domains(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[BusinessDomain]:
        """Identify the most relevant domains for a query"""
        
        query_lower = query.lower()
        domain_scores = {}
        
        # Score each domain based on keyword matches
        for domain, domain_context in self.domain_contexts.items():
            score = 0.0
            
            # Keyword matching
            for keyword in domain_context.keywords:
                if keyword in query_lower:
                    score += 1.0
            
            # Concept matching
            for concept in domain_context.concepts:
                # Check if concept words appear in query
                concept_words = concept.split()
                matches = sum(1 for word in concept_words if word in query_lower)
                if matches > 0:
                    score += (matches / len(concept_words)) * 0.5
            
            # Terminology matching
            for term, expanded_terms in domain_context.terminology.items():
                if term in query_lower:
                    score += 0.3
                for expanded_term in expanded_terms.split(', '):
                    if expanded_term in query_lower:
                        score += 0.3
            
            if score > 0:
                domain_scores[domain] = score
        
        # Context boost
        if context and 'preferred_domains' in context:
            for domain_name in context['preferred_domains']:
                try:
                    domain = BusinessDomain(domain_name.lower())
                    if domain in domain_scores:
                        domain_scores[domain] += 1.0
                    else:
                        domain_scores[domain] = 0.5
                except ValueError:
                    continue
        
        # Sort and filter domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select top domains above threshold
        threshold = self.config.get('domain_weight_threshold', 0.1)
        primary_domains = []
        
        for domain, score in sorted_domains:
            if score >= threshold and len(primary_domains) < 5:  # Max 5 primary domains
                primary_domains.append(domain)
        
        # Ensure at least one domain (fallback to GENERAL)
        if not primary_domains:
            primary_domains.append(BusinessDomain.GENERAL)
        
        return primary_domains
    
    async def _generate_domain_expansions(
        self, 
        query: str, 
        domains: List[BusinessDomain]
    ) -> List[ExpandedQuery]:
        """Generate domain-specific expanded queries"""
        
        expanded_queries = []
        max_expansions = self.config.get('max_expanded_queries', 5)
        
        for domain in domains:
            if len(expanded_queries) >= max_expansions:
                break
            
            domain_context = self.domain_contexts.get(domain)
            if not domain_context:
                continue
            
            # Generate domain-specific expansions
            domain_expansions = []
            
            # Pattern 1: Add domain context
            domain_name = domain.value.replace('_', ' ')
            expanded_query = f"{query} in {domain_name}"
            domain_expansions.append({
                'query': expanded_query,
                'type': 'domain_context',
                'added_terms': [domain_name],
                'score': 0.8
            })
            
            # Pattern 2: Add domain terminology
            domain_terms = ', '.join(domain_context.keywords[:3])
            expanded_query = f"{query} considering {domain_terms}"
            domain_expansions.append({
                'query': expanded_query,
                'type': 'terminology_expansion',
                'added_terms': domain_context.keywords[:3],
                'score': 0.7
            })
            
            # Pattern 3: Industry-specific framing
            expanded_query = f"{domain_name} approach to {query}"
            domain_expansions.append({
                'query': expanded_query,
                'type': 'industry_framing',
                'added_terms': [f"{domain_name} approach"],
                'score': 0.6
            })
            
            # Select best expansion for this domain
            best_expansion = max(domain_expansions, key=lambda x: x['score'])
            
            expanded_queries.append(ExpandedQuery(
                original_query=query,
                expanded_query=best_expansion['query'],
                domain=domain,
                expansion_type=best_expansion['type'],
                relevance_score=best_expansion['score'],
                added_terms=best_expansion['added_terms'],
                domain_context=domain_context
            ))
        
        # Sort by relevance score
        expanded_queries.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return expanded_queries[:max_expansions]
    
    async def _generate_cross_domain_insights(
        self, 
        query: str, 
        domains: List[BusinessDomain]
    ) -> List[str]:
        """Generate insights from cross-domain relationships"""
        
        insights = []
        
        if len(domains) < 2:
            return insights
        
        # Generate pairwise insights
        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                if len(insights) >= 3:  # Limit insights
                    break
                
                # Check if domains have a relationship
                relationships = self.domain_relationships.get(domain1, {})
                if domain2 in relationships or domain1 in self.domain_relationships.get(domain2, {}):
                    domain1_name = domain1.value.replace('_', ' ')
                    domain2_name = domain2.value.replace('_', ' ')
                    
                    insight = f"Consider how {domain1_name} and {domain2_name} perspectives on '{query}' might complement each other"
                    insights.append(insight)
        
        return insights
    
    async def _calculate_expansion_confidence(
        self, 
        query: str, 
        domains: List[BusinessDomain], 
        expanded_queries: List[ExpandedQuery]
    ) -> float:
        """Calculate confidence score for the expansion"""
        
        if not domains or not expanded_queries:
            return 0.0
        
        # Base confidence from number of relevant domains found
        domain_confidence = min(len(domains) * 0.2, 1.0)
        
        # Average relevance score of expanded queries
        if expanded_queries:
            avg_relevance = sum(eq.relevance_score for eq in expanded_queries) / len(expanded_queries)
        else:
            avg_relevance = 0.0
        
        # Keyword density confidence
        total_keywords = sum(len(self.domain_contexts[domain].keywords) for domain in domains if domain in self.domain_contexts)
        keyword_confidence = min(total_keywords * 0.05, 0.5)
        
        # Combined confidence
        confidence = (domain_confidence * 0.4 + avg_relevance * 0.4 + keyword_confidence * 0.2)
        
        return min(confidence, 1.0)
    
    async def _suggest_additional_domains(
        self, 
        query: str, 
        primary_domains: List[BusinessDomain]
    ) -> List[Tuple[BusinessDomain, float]]:
        """Suggest additional relevant domains"""
        
        suggestions = []
        primary_domain_set = set(primary_domains)
        
        # Find related domains through relationships
        for domain in primary_domains:
            if domain in self.domain_relationships:
                for related_domain, strength in self.domain_relationships[domain].items():
                    if related_domain not in primary_domain_set and strength >= 0.5:
                        suggestions.append((related_domain, strength))
        
        # Remove duplicates and sort by strength
        unique_suggestions = {}
        for domain, strength in suggestions:
            if domain not in unique_suggestions or strength > unique_suggestions[domain]:
                unique_suggestions[domain] = strength
        
        sorted_suggestions = sorted(unique_suggestions.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_suggestions[:3]  # Top 3 suggestions
    
    def _generate_cache_key(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for query and context"""
        import hashlib
        key_data = f"{query}:{context or {}}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def batch_expand_queries(
        self, 
        queries: List[str], 
        context: Optional[Dict[str, Any]] = None
    ) -> List[ExpansionResult]:
        """
        Expand multiple queries in batch for high performance
        
        Args:
            queries: List of queries to expand
            context: Optional shared context for all queries
            
        Returns:
            List of ExpansionResult objects
        """
        if not queries:
            return []
        
        self.logger.info(f"Batch expanding {len(queries)} queries")
        
        try:
            # Process queries in parallel
            tasks = [self.expand_query(query, context) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch expansion failed for query {i}: {result}")
                    processed_results.append(ExpansionResult(
                        original_query=queries[i],
                        primary_domains=[],
                        expanded_queries=[],
                        cross_domain_insights=[f"Batch processing error: {str(result)}"],
                        processing_time=0.0,
                        confidence_score=0.0,
                        suggested_domains=[]
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch expansion failed: {e}")
            return [ExpansionResult(
                original_query=query,
                primary_domains=[],
                expanded_queries=[],
                cross_domain_insights=["Batch processing failed"],
                processing_time=0.0,
                confidence_score=0.0,
                suggested_domains=[]
            ) for query in queries]
    
    def get_domain_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed definitions of all supported domains"""
        definitions = {}
        
        for domain, context in self.domain_contexts.items():
            definitions[domain.value] = {
                'name': domain.value.replace('_', ' ').title(),
                'keywords': context.keywords,
                'concepts': context.concepts,
                'related_domains': [d.value for d in context.related_domains],
                'terminology': context.terminology
            }
        
        return definitions
    
    def get_expansion_metrics(self) -> Dict[str, Any]:
        """Get comprehensive expansion performance metrics"""
        return {
            'total_expansions': self.metrics['total_expansions'],
            'cache_hit_rate': self.metrics['cache_hit_rate'],
            'average_processing_time': self.metrics['avg_processing_time'],
            'supported_domains': len(self.domain_contexts),
            'domain_relationships': sum(len(rels) for rels in self.domain_relationships.values()),
            'configuration': self.config
        }
    
    def clear_cache(self):
        """Clear expansion cache"""
        self.expansion_cache.clear()
        self.domain_cache.clear()
        self.logger.info("Domain expansion cache cleared")

# Global instance factory
_domain_expansion_engine = None

async def get_domain_expansion_engine(config: Optional[Dict[str, Any]] = None) -> DomainExpansionEngine:
    """Get the global domain expansion engine instance"""
    global _domain_expansion_engine
    
    if _domain_expansion_engine is None:
        _domain_expansion_engine = DomainExpansionEngine(config)
    
    return _domain_expansion_engine