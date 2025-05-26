"""
Export and Integration Manager

This module provides functionality for exporting analysis results in various formats
and integrating with external systems.
"""

import os
import logging
import json
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExportIntegration:
    """
    Export and integration manager.
    
    This class provides methods for exporting analysis results in various formats
    and integrating with external systems.
    """
    
    def __init__(self, export_dir: Optional[str] = None):
        """
        Initialize the export and integration manager.
        
        Args:
            export_dir: Directory to save exported files (defaults to /tmp/exports)
        """
        self.export_dir = export_dir or "/tmp/exports"
        
        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_data(self, data: Dict[str, Any], format: str = "pdf") -> str:
        """
        Export data in the specified format.
        
        Args:
            data: Data to export
            format: Export format (pdf, csv, json)
            
        Returns:
            Path to exported file
        """
        logger.info(f"Exporting data in {format} format")
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"export_{timestamp}.{format}"
        filepath = os.path.join(self.export_dir, filename)
        
        # Export based on format
        if format.lower() == "pdf":
            return self._export_as_pdf(data, filepath)
        elif format.lower() == "csv":
            return self._export_as_csv(data, filepath)
        elif format.lower() == "json":
            return self._export_as_json(data, filepath)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_as_pdf(self, data: Dict[str, Any], filepath: str) -> str:
        """
        Export data as PDF.
        
        Args:
            data: Data to export
            filepath: Path to save PDF file
            
        Returns:
            Path to exported PDF file
        """
        try:
            # In a real implementation, this would use a PDF generation library
            # For now, we'll create a simple text file with .pdf extension
            with open(filepath, "w") as f:
                f.write("PDF EXPORT\n\n")
                f.write(json.dumps(data, indent=2))
            
            logger.info(f"Exported data as PDF to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting as PDF: {str(e)}")
            raise
    
    def _export_as_csv(self, data: Dict[str, Any], filepath: str) -> str:
        """
        Export data as CSV.
        
        Args:
            data: Data to export
            filepath: Path to save CSV file
            
        Returns:
            Path to exported CSV file
        """
        try:
            # In a real implementation, this would use a CSV generation library
            # For now, we'll create a simple CSV-like text file
            with open(filepath, "w") as f:
                f.write("key,value\n")
                self._write_dict_as_csv(data, f)
            
            logger.info(f"Exported data as CSV to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting as CSV: {str(e)}")
            raise
    
    def _write_dict_as_csv(self, data: Dict[str, Any], file, prefix: str = ""):
        """
        Write dictionary as CSV rows.
        
        Args:
            data: Dictionary to write
            file: File object to write to
            prefix: Prefix for nested keys
        """
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._write_dict_as_csv(value, file, full_key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._write_dict_as_csv(item, file, f"{full_key}[{i}]")
                    else:
                        # Fix: Avoid using backslash in f-string expression
                        escaped_item = str(item).replace('"', '""')
                        file.write(f'{full_key}[{i}],"{escaped_item}"\n')
            else:
                # Fix: Avoid using backslash in f-string expression
                escaped_value = str(value).replace('"', '""')
                file.write(f'{full_key},"{escaped_value}"\n')
    
    def _export_as_json(self, data: Dict[str, Any], filepath: str) -> str:
        """
        Export data as JSON.
        
        Args:
            data: Data to export
            filepath: Path to save JSON file
            
        Returns:
            Path to exported JSON file
        """
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported data as JSON to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting as JSON: {str(e)}")
            raise
    
    def get_export_formats(self) -> list:
        """
        Get available export formats.
        
        Returns:
            List of available export formats
        """
        return [
            {
                "id": "pdf",
                "name": "PDF Document",
                "description": "Export as a professionally formatted PDF document",
                "extension": "PDF"
            },
            {
                "id": "docx",
                "name": "Word Document",
                "description": "Export as an editable Microsoft Word document",
                "extension": "DOCX"
            },
            {
                "id": "html",
                "name": "HTML Document",
                "description": "Export as an HTML document ready for web publishing",
                "extension": "HTML"
            },
            {
                "id": "md",
                "name": "Markdown",
                "description": "Export as a Markdown file for easy editing",
                "extension": "MD"
            },
            {
                "id": "csv",
                "name": "CSV Spreadsheet",
                "description": "Export data as a CSV spreadsheet",
                "extension": "CSV"
            },
            {
                "id": "json",
                "name": "JSON Data",
                "description": "Export raw data in JSON format",
                "extension": "JSON"
            }
        ]
    
    def get_cms_platforms(self) -> list:
        """
        Get available CMS platforms for integration.
        
        Returns:
            List of available CMS platforms
        """
        return [
            {
                "id": "wordpress",
                "name": "WordPress",
                "description": "Publish directly to your WordPress site",
                "icon": "wordpress-icon.svg"
            },
            {
                "id": "webflow",
                "name": "Webflow",
                "description": "Export to your Webflow CMS",
                "icon": "webflow-icon.svg"
            },
            {
                "id": "contentful",
                "name": "Contentful",
                "description": "Publish to your Contentful workspace",
                "icon": "contentful-icon.svg"
            },
            {
                "id": "shopify",
                "name": "Shopify",
                "description": "Export to your Shopify blog",
                "icon": "shopify-icon.svg"
            },
            {
                "id": "hubspot",
                "name": "HubSpot",
                "description": "Publish to your HubSpot CMS",
                "icon": "hubspot-icon.svg"
            }
        ]
    
    def integrate_with_cms(self, data: Dict[str, Any], cms_type: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Integrate data with a content management system.
        
        Args:
            data: Data to integrate
            cms_type: CMS type (wordpress, drupal, etc.)
            credentials: CMS credentials
            
        Returns:
            Integration result
        """
        logger.info(f"Integrating data with {cms_type}")
        
        # In a real implementation, this would use CMS-specific APIs
        # For now, we'll return a mock result
        return {
            "status": "success",
            "cms_type": cms_type,
            "integration_id": f"int_{int(time.time())}",
            "url": f"https://example.com/{cms_type}/content/{int(time.time())}"
        }
