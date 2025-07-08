"""
Data Source Manager for handling different data source integrations.
Provides clean routing and content injection based on selected data sources.
"""
from typing import List


class DataSourceManager:
    """Manages data source integrations and content injection."""
    
    def __init__(self):
        """Initialize the data source manager."""
        self._data_sources = {
            "data-test": self._handle_test_data_source,
            "new-mexico-history": self._handle_new_mexico_history,
        }
    
    def get_data_source_content(self, data_source_ids: List[str]) -> str:
        """
        Get combined content from all selected data sources.
        
        Args:
            data_source_ids: List of data source IDs to process
            
        Returns:
            Combined content string from all data sources
        """
        if not data_source_ids:
            return ""
        
        content_parts = []
        
        for data_source_id in data_source_ids:
            if data_source_id in self._data_sources:
                content = self._data_sources[data_source_id]()
                if content:
                    content_parts.append(content)
        
        return "\n\n".join(content_parts) if content_parts else ""
    
    def is_data_source_available(self, data_source_id: str) -> bool:
        """Check if a data source is available."""
        return data_source_id in self._data_sources
    
    def get_available_data_sources(self) -> List[str]:
        """Get list of available data source IDs."""
        return list(self._data_sources.keys())
    
    def _handle_test_data_source(self) -> str:
        """Handle the test data source."""
        return (
            "TEST DATA SOURCE ACTIVE: This is a demonstration data source that provides "
            "sample test data. It contains simulated information for testing purposes "
            "and should not be used for production queries. The test data includes "
            "fictional user records, mock transactions, and placeholder content "
            "designed to validate data source integration functionality."
        )
    
    def _handle_new_mexico_history(self) -> str:
        """Handle the New Mexico history data source."""
        return (
            "NEW MEXICO HISTORICAL DATA SOURCE: You now have access to comprehensive "
            "historical information about New Mexico. This includes data about the state's "
            "rich cultural heritage spanning from ancient Pueblo civilizations through "
            "Spanish colonization (1598), Mexican territorial period (1821-1846), "
            "and U.S. statehood (1912). Key topics include: Native American tribes "
            "(Pueblo, Navajo, Apache), Spanish colonial missions, the Santa Fe Trail, "
            "territorial conflicts, mining history, nuclear research at Los Alamos, "
            "and the unique tri-cultural blend of Native American, Hispanic, and Anglo "
            "influences that define modern New Mexico. The state capital Santa Fe "
            "is one of the oldest continuously inhabited cities in the United States."
        )


# Global instance
data_source_manager = DataSourceManager()