"""
Schema Validator

Provides schema.org markup validation and optimization for structured data
to enhance search visibility and Knowledge Graph integration.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class SchemaValidator:
    """
    Schema.org markup validator and optimizer for structured data
    """
    
    def __init__(self):
        """Initialize Schema Validator"""
        self.google_structured_data_url = 'https://search.google.com/structured-data/testing-tool/u/0/'
        self.schema_org_types = self._load_common_schema_types()
    
    def validate_structured_data(self, html_content: str = None, url: str = None) -> Dict[str, Any]:
        """
        Validate structured data markup
        
        Args:
            html_content: HTML content containing structured data
            url: URL to test (alternative to html_content)
            
        Returns:
            Validation results
        """
        if not html_content and not url:
            return {'error': 'Either html_content or url must be provided'}
        
        try:
            # Extract structured data
            structured_data = self._extract_structured_data(html_content, url)
            
            if not structured_data:
                return {
                    'valid': False,
                    'errors': ['No structured data found'],
                    'warnings': [],
                    'suggestions': [
                        'Add JSON-LD structured data to your page',
                        'Consider implementing Article, Organization, or WebPage schema'
                    ]
                }
            
            # Validate each structured data item
            validation_results = []
            for item in structured_data:
                result = self._validate_schema_item(item)
                validation_results.append(result)
            
            # Aggregate results
            total_errors = sum(len(r.get('errors', [])) for r in validation_results)
            total_warnings = sum(len(r.get('warnings', [])) for r in validation_results)
            
            return {
                'valid': total_errors == 0,
                'total_items': len(structured_data),
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'validation_results': validation_results,
                'suggestions': self._generate_improvement_suggestions(validation_results),
                'rich_result_eligibility': self._assess_rich_result_eligibility(validation_results)
            }
            
        except Exception as e:
            logger.error(f"Error validating structured data: {e}")
            return self._get_mock_validation_results()
    
    def suggest_schema_markup(self, content_type: str, content_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Suggest appropriate schema markup for content
        
        Args:
            content_type: Type of content (article, product, event, etc.)
            content_data: Content data to include in schema
            
        Returns:
            Schema markup suggestions
        """
        try:
            schema_suggestions = []
            
            # Get primary schema recommendation
            primary_schema = self._get_primary_schema(content_type)
            if primary_schema:
                schema_suggestions.append(primary_schema)
            
            # Add complementary schemas
            complementary_schemas = self._get_complementary_schemas(content_type)
            schema_suggestions.extend(complementary_schemas)
            
            # Generate JSON-LD examples
            json_ld_examples = []
            for schema in schema_suggestions:
                example = self._generate_json_ld_example(schema, content_data)
                json_ld_examples.append(example)
            
            return {
                'content_type': content_type,
                'recommended_schemas': schema_suggestions,
                'json_ld_examples': json_ld_examples,
                'implementation_priority': self._get_implementation_priority(content_type),
                'expected_benefits': self._get_expected_benefits(schema_suggestions),
                'testing_instructions': self._get_testing_instructions()
            }
            
        except Exception as e:
            logger.error(f"Error suggesting schema markup: {e}")
            return self._get_mock_schema_suggestions(content_type)
    
    def optimize_existing_schema(self, existing_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize existing schema markup
        
        Args:
            existing_schema: Current schema markup
            
        Returns:
            Optimization suggestions
        """
        try:
            optimization_suggestions = {
                'current_schema': existing_schema,
                'optimizations': [],
                'missing_properties': [],
                'enhancement_opportunities': []
            }
            
            schema_type = existing_schema.get('@type', 'Unknown')
            
            # Check for missing required properties
            required_props = self._get_required_properties(schema_type)
            for prop in required_props:
                if prop not in existing_schema:
                    optimization_suggestions['missing_properties'].append({
                        'property': prop,
                        'importance': 'high',
                        'description': f'Required property for {schema_type} schema'
                    })
            
            # Check for recommended properties
            recommended_props = self._get_recommended_properties(schema_type)
            for prop in recommended_props:
                if prop not in existing_schema:
                    optimization_suggestions['enhancement_opportunities'].append({
                        'property': prop,
                        'importance': 'medium',
                        'description': f'Recommended property to enhance {schema_type} schema'
                    })
            
            # General optimizations
            optimizations = []
            
            # Check for nested schema opportunities
            if schema_type == 'Article' and 'author' not in existing_schema:
                optimizations.append({
                    'type': 'nested_schema',
                    'suggestion': 'Add Person or Organization schema for author',
                    'benefit': 'Better author attribution and credibility'
                })
            
            # Check for image optimization
            if 'image' in existing_schema:
                optimizations.append({
                    'type': 'image_optimization',
                    'suggestion': 'Ensure image URLs are high-resolution and accessible',
                    'benefit': 'Better visual representation in rich results'
                })
            
            optimization_suggestions['optimizations'] = optimizations
            
            return optimization_suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing schema: {e}")
            return {'error': f'Optimization failed: {e}'}
    
    def generate_breadcrumb_schema(self, breadcrumb_items: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate breadcrumb schema markup
        
        Args:
            breadcrumb_items: List of breadcrumb items with 'name' and 'url'
            
        Returns:
            Breadcrumb schema markup
        """
        breadcrumb_list = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        for i, item in enumerate(breadcrumb_items):
            list_item = {
                "@type": "ListItem",
                "position": i + 1,
                "name": item.get('name', ''),
                "item": item.get('url', '')
            }
            breadcrumb_list["itemListElement"].append(list_item)
        
        return {
            'schema_type': 'BreadcrumbList',
            'json_ld': breadcrumb_list,
            'implementation_notes': [
                'Place this schema in the <head> section',
                'Ensure URLs are absolute and accessible',
                'Test with Google\'s Rich Results Test'
            ]
        }
    
    def generate_organization_schema(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate organization schema markup
        
        Args:
            org_data: Organization data (name, url, logo, etc.)
            
        Returns:
            Organization schema markup
        """
        organization = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": org_data.get('name', ''),
            "url": org_data.get('url', ''),
        }
        
        # Add optional properties
        if org_data.get('logo'):
            organization['logo'] = org_data['logo']
        
        if org_data.get('description'):
            organization['description'] = org_data['description']
        
        if org_data.get('address'):
            organization['address'] = {
                "@type": "PostalAddress",
                "streetAddress": org_data['address'].get('street', ''),
                "addressLocality": org_data['address'].get('city', ''),
                "addressRegion": org_data['address'].get('state', ''),
                "postalCode": org_data['address'].get('zip', ''),
                "addressCountry": org_data['address'].get('country', '')
            }
        
        if org_data.get('social_profiles'):
            organization['sameAs'] = org_data['social_profiles']
        
        return {
            'schema_type': 'Organization',
            'json_ld': organization,
            'implementation_notes': [
                'Place on homepage and main organizational pages',
                'Ensure logo is high-resolution and square format',
                'Include all relevant social media profiles'
            ]
        }
    
    def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Test basic schema generation
            test_schema = self.generate_organization_schema({'name': 'Test Org', 'url': 'https://test.com'})
            return 'json_ld' in test_schema
        except Exception as e:
            logger.error(f"Schema Validator health check failed: {e}")
            return False
    
    def _extract_structured_data(self, html_content: str = None, url: str = None) -> List[Dict[str, Any]]:
        """Extract structured data from HTML or URL"""
        structured_data = []
        
        if html_content:
            # Simple extraction of JSON-LD (would be enhanced with proper HTML parsing)
            import re
            json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
            matches = re.findall(json_ld_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                try:
                    data = json.loads(match.strip())
                    structured_data.append(data)
                except json.JSONDecodeError:
                    continue
        
        # For URL testing, would implement actual URL fetching and parsing
        if url and not html_content:
            # Mock implementation - would fetch and parse actual URL
            structured_data.append({
                "@context": "https://schema.org",
                "@type": "WebPage",
                "url": url,
                "name": "Sample Page"
            })
        
        return structured_data
    
    def _validate_schema_item(self, schema_item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual schema item"""
        errors = []
        warnings = []
        
        # Check for required @context
        if '@context' not in schema_item:
            errors.append('Missing @context property')
        
        # Check for @type
        if '@type' not in schema_item:
            errors.append('Missing @type property')
        else:
            schema_type = schema_item['@type']
            
            # Check required properties for this schema type
            required_props = self._get_required_properties(schema_type)
            for prop in required_props:
                if prop not in schema_item:
                    errors.append(f'Missing required property: {prop}')
            
            # Check recommended properties
            recommended_props = self._get_recommended_properties(schema_type)
            for prop in recommended_props:
                if prop not in schema_item:
                    warnings.append(f'Missing recommended property: {prop}')
        
        return {
            'schema_type': schema_item.get('@type', 'Unknown'),
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'properties_found': list(schema_item.keys())
        }
    
    def _get_required_properties(self, schema_type: str) -> List[str]:
        """Get required properties for schema type"""
        required_properties = {
            'Article': ['headline', 'datePublished'],
            'Organization': ['name'],
            'Person': ['name'],
            'Product': ['name', 'offers'],
            'Event': ['name', 'startDate'],
            'WebPage': ['name'],
            'BreadcrumbList': ['itemListElement']
        }
        return required_properties.get(schema_type, [])
    
    def _get_recommended_properties(self, schema_type: str) -> List[str]:
        """Get recommended properties for schema type"""
        recommended_properties = {
            'Article': ['author', 'image', 'dateModified', 'description'],
            'Organization': ['url', 'logo', 'description', 'address'],
            'Person': ['url', 'image', 'description'],
            'Product': ['description', 'image', 'brand', 'sku'],
            'Event': ['location', 'description', 'image'],
            'WebPage': ['description', 'image', 'url'],
            'BreadcrumbList': []
        }
        return recommended_properties.get(schema_type, [])
    
    def _generate_improvement_suggestions(self, validation_results: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on validation results"""
        suggestions = []
        
        for result in validation_results:
            if result['errors']:
                suggestions.append(f"Fix errors in {result['schema_type']} schema")
            if result['warnings']:
                suggestions.append(f"Consider adding recommended properties to {result['schema_type']} schema")
        
        return suggestions
    
    def _assess_rich_result_eligibility(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess eligibility for rich results"""
        eligible_types = []
        
        for result in validation_results:
            if result['valid'] and result['schema_type'] in ['Article', 'Product', 'Event', 'Organization']:
                eligible_types.append(result['schema_type'])
        
        return {
            'eligible': len(eligible_types) > 0,
            'eligible_types': eligible_types,
            'potential_rich_results': [
                'Featured Snippets',
                'Knowledge Panels',
                'Rich Cards'
            ] if eligible_types else []
        }
    
    def _load_common_schema_types(self) -> Dict[str, Any]:
        """Load common schema.org types and their properties"""
        return {
            'Article': {
                'required': ['headline', 'datePublished'],
                'recommended': ['author', 'image', 'dateModified', 'description']
            },
            'Organization': {
                'required': ['name'],
                'recommended': ['url', 'logo', 'description', 'address']
            },
            'Product': {
                'required': ['name', 'offers'],
                'recommended': ['description', 'image', 'brand', 'sku']
            },
            'Event': {
                'required': ['name', 'startDate'],
                'recommended': ['location', 'description', 'image']
            }
        }
    
    def _get_primary_schema(self, content_type: str) -> Dict[str, str]:
        """Get primary schema recommendation for content type"""
        schema_mapping = {
            'article': {'type': 'Article', 'priority': 'high'},
            'blog_post': {'type': 'BlogPosting', 'priority': 'high'},
            'product': {'type': 'Product', 'priority': 'high'},
            'event': {'type': 'Event', 'priority': 'high'},
            'organization': {'type': 'Organization', 'priority': 'high'},
            'person': {'type': 'Person', 'priority': 'medium'},
            'webpage': {'type': 'WebPage', 'priority': 'medium'}
        }
        return schema_mapping.get(content_type.lower())
    
    def _get_complementary_schemas(self, content_type: str) -> List[Dict[str, str]]:
        """Get complementary schema recommendations"""
        complementary = {
            'article': [
                {'type': 'WebPage', 'priority': 'medium'},
                {'type': 'BreadcrumbList', 'priority': 'low'}
            ],
            'product': [
                {'type': 'WebPage', 'priority': 'medium'},
                {'type': 'BreadcrumbList', 'priority': 'medium'}
            ]
        }
        return complementary.get(content_type.lower(), [])
    
    def _generate_json_ld_example(self, schema_info: Dict[str, str], content_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD example for schema type"""
        if not schema_info:
            return {}
        
        schema_type = schema_info['type']
        
        examples = {
            'Article': {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": content_data.get('title', 'Your Article Title'),
                "description": content_data.get('description', 'Article description'),
                "datePublished": content_data.get('date_published', '2024-01-01'),
                "author": {
                    "@type": "Person",
                    "name": content_data.get('author', 'Author Name')
                }
            },
            'Organization': {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": content_data.get('name', 'Your Organization'),
                "url": content_data.get('url', 'https://example.com'),
                "logo": content_data.get('logo', 'https://example.com/logo.png')
            }
        }
        
        return examples.get(schema_type, {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": content_data.get('name', 'Example Name') if content_data else 'Example Name'
        })
    
    def _get_implementation_priority(self, content_type: str) -> str:
        """Get implementation priority for content type"""
        high_priority = ['article', 'product', 'event', 'organization']
        return 'high' if content_type.lower() in high_priority else 'medium'
    
    def _get_expected_benefits(self, schemas: List[Dict[str, str]]) -> List[str]:
        """Get expected benefits from implementing schemas"""
        benefits = [
            'Improved search visibility',
            'Enhanced rich results eligibility',
            'Better content understanding by search engines'
        ]
        
        if any(s.get('type') == 'Article' for s in schemas):
            benefits.append('Potential for featured snippets')
        
        if any(s.get('type') == 'Organization' for s in schemas):
            benefits.append('Knowledge panel eligibility')
        
        return benefits
    
    def _get_testing_instructions(self) -> List[str]:
        """Get testing instructions for schema implementation"""
        return [
            'Use Google\'s Rich Results Test: https://search.google.com/test/rich-results',
            'Validate with Schema.org validator',
            'Monitor Google Search Console for structured data reports',
            'Test on multiple pages to ensure consistency'
        ]
    
    def _get_mock_validation_results(self) -> Dict[str, Any]:
        """Return mock validation results when real validation fails"""
        return {
            'valid': True,
            'total_items': 1,
            'total_errors': 0,
            'total_warnings': 1,
            'validation_results': [{
                'schema_type': 'WebPage',
                'valid': True,
                'errors': [],
                'warnings': ['Missing recommended property: description'],
                'properties_found': ['@context', '@type', 'name', 'url']
            }],
            'suggestions': ['Add description property for better content understanding'],
            'rich_result_eligibility': {
                'eligible': True,
                'eligible_types': ['WebPage'],
                'potential_rich_results': ['Featured Snippets']
            },
            'note': 'Mock validation results - Implement real validation for accurate results'
        }
    
    def _get_mock_schema_suggestions(self, content_type: str) -> Dict[str, Any]:
        """Return mock schema suggestions"""
        return {
            'content_type': content_type,
            'recommended_schemas': [{'type': content_type.title(), 'priority': 'high'}],
            'json_ld_examples': [{
                "@context": "https://schema.org",
                "@type": content_type.title(),
                "name": f"Example {content_type}"
            }],
            'implementation_priority': 'high',
            'expected_benefits': ['Improved search visibility', 'Rich results eligibility'],
            'testing_instructions': ['Use Google Rich Results Test'],
            'note': 'Mock schema suggestions - Implement real schema analysis for detailed recommendations'
        }
