"""
Unit tests for the DataSourceManager service.
"""
import pytest
import sys

# Add the app directory to the Python path
sys.path.insert(0, '/app')

from app.services.data_source_manager import DataSourceManager, data_source_manager


class TestDataSourceManager:
    """Test the DataSourceManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = DataSourceManager()
    
    def test_manager_initialization(self):
        """Test that DataSourceManager initializes correctly."""
        assert self.manager is not None
        assert hasattr(self.manager, '_data_sources')
        assert isinstance(self.manager._data_sources, dict)
        
        # Should have our test data sources
        assert "data-test" in self.manager._data_sources
        assert "new-mexico-history" in self.manager._data_sources
    
    def test_get_available_data_sources(self):
        """Test getting list of available data sources."""
        sources = self.manager.get_available_data_sources()
        assert isinstance(sources, list)
        assert len(sources) == 2
        assert "data-test" in sources
        assert "new-mexico-history" in sources
    
    def test_is_data_source_available(self):
        """Test checking if data sources are available."""
        # Test existing sources
        assert self.manager.is_data_source_available("data-test") is True
        assert self.manager.is_data_source_available("new-mexico-history") is True
        
        # Test non-existing source
        assert self.manager.is_data_source_available("nonexistent") is False
        assert self.manager.is_data_source_available("") is False
    
    def test_get_data_source_content_single_source(self):
        """Test getting content from a single data source."""
        # Test data source
        test_content = self.manager.get_data_source_content(["data-test"])
        assert isinstance(test_content, str)
        assert len(test_content) > 0
        assert "TEST DATA SOURCE ACTIVE" in test_content
        assert "demonstration data source" in test_content
        assert "testing purposes" in test_content
        
        # New Mexico history source
        nm_content = self.manager.get_data_source_content(["new-mexico-history"])
        assert isinstance(nm_content, str)
        assert len(nm_content) > 0
        assert "NEW MEXICO HISTORICAL" in nm_content
        assert "Spanish colonization" in nm_content
        assert "Santa Fe" in nm_content
        assert "Los Alamos" in nm_content
    
    def test_get_data_source_content_multiple_sources(self):
        """Test getting content from multiple data sources."""
        content = self.manager.get_data_source_content(["data-test", "new-mexico-history"])
        assert isinstance(content, str)
        assert len(content) > 0
        
        # Should contain content from both sources
        assert "TEST DATA SOURCE ACTIVE" in content
        assert "NEW MEXICO HISTORICAL" in content
        
        # Should be separated properly (with double newlines)
        assert "\n\n" in content
    
    def test_get_data_source_content_empty_list(self):
        """Test getting content with empty data source list."""
        content = self.manager.get_data_source_content([])
        assert content == ""
    
    def test_get_data_source_content_unknown_source(self):
        """Test getting content from unknown data source."""
        content = self.manager.get_data_source_content(["unknown-source"])
        assert content == ""
        
        # Test mix of known and unknown
        content = self.manager.get_data_source_content(["unknown-source", "data-test", "another-unknown"])
        assert "TEST DATA SOURCE ACTIVE" in content
        assert len(content) > 0
    
    def test_get_data_source_content_order_preservation(self):
        """Test that data source content order is preserved."""
        content1 = self.manager.get_data_source_content(["data-test", "new-mexico-history"])
        content2 = self.manager.get_data_source_content(["new-mexico-history", "data-test"])
        
        # Content should be different due to different order
        assert content1 != content2
        
        # But both should contain both pieces of content
        assert "TEST DATA SOURCE ACTIVE" in content1
        assert "NEW MEXICO HISTORICAL" in content1
        assert "TEST DATA SOURCE ACTIVE" in content2
        assert "NEW MEXICO HISTORICAL" in content2
    
    def test_data_source_handlers_exist(self):
        """Test that individual data source handlers work correctly."""
        # Test data source handler
        test_content = self.manager._handle_test_data_source()
        assert isinstance(test_content, str)
        assert "TEST DATA SOURCE ACTIVE" in test_content
        assert "testing purposes" in test_content
        
        # New Mexico history handler
        nm_content = self.manager._handle_new_mexico_history()
        assert isinstance(nm_content, str)
        assert "NEW MEXICO HISTORICAL" in nm_content
        assert "1912" in nm_content  # Statehood year
        assert "Pueblo" in nm_content
    
    def test_global_instance(self):
        """Test that the global data_source_manager instance works."""
        assert data_source_manager is not None
        assert isinstance(data_source_manager, DataSourceManager)
        
        # Should have the same functionality as a new instance
        sources = data_source_manager.get_available_data_sources()
        assert "data-test" in sources
        assert "new-mexico-history" in sources
        
        content = data_source_manager.get_data_source_content(["data-test"])
        assert "TEST DATA SOURCE ACTIVE" in content


class TestDataSourceManagerEdgeCases:
    """Test edge cases and error conditions for DataSourceManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = DataSourceManager()
    
    def test_none_input(self):
        """Test handling of None input."""
        # get_data_source_content should handle None gracefully
        # Note: This might raise TypeError, which is acceptable behavior
        try:
            content = self.manager.get_data_source_content(None)
            # If it doesn't raise an error, it should return empty string
            assert content == ""
        except TypeError:
            # This is acceptable behavior for None input
            pass
    
    def test_duplicate_data_sources(self):
        """Test handling of duplicate data sources in the list."""
        content = self.manager.get_data_source_content(["data-test", "data-test"])
        
        # Should contain the test content
        assert "TEST DATA SOURCE ACTIVE" in content
        
        # Should handle duplicates gracefully (might appear twice or once, both are valid)
        assert len(content) > 0
    
    def test_case_sensitivity(self):
        """Test that data source IDs are case sensitive."""
        assert self.manager.is_data_source_available("data-test") is True
        assert self.manager.is_data_source_available("DATA-TEST") is False
        assert self.manager.is_data_source_available("Data-Test") is False
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in data source IDs."""
        assert self.manager.is_data_source_available(" data-test ") is False
        assert self.manager.is_data_source_available("data-test ") is False
        assert self.manager.is_data_source_available(" data-test") is False
    
    def test_content_consistency(self):
        """Test that content is consistent across multiple calls."""
        content1 = self.manager.get_data_source_content(["data-test"])
        content2 = self.manager.get_data_source_content(["data-test"])
        
        # Content should be identical
        assert content1 == content2
        
        # Same for New Mexico history
        nm_content1 = self.manager.get_data_source_content(["new-mexico-history"])
        nm_content2 = self.manager.get_data_source_content(["new-mexico-history"])
        assert nm_content1 == nm_content2


class TestDataSourceManagerIntegration:
    """Test DataSourceManager integration with other components."""
    
    def test_integration_with_system_prompt_engine(self):
        """Test that DataSourceManager works correctly with SystemPromptEngine."""
        from app.services.system_prompt_engine import system_prompt_engine
        
        # Generate system prompt with data sources
        prompt = system_prompt_engine.generate_system_prompt(
            selected_data_sources=["data-test", "new-mexico-history"]
        )
        
        # Should contain the data source content
        assert "TEST DATA SOURCE ACTIVE" in prompt
        assert "NEW MEXICO HISTORICAL" in prompt
        assert "ACTIVE DATA SOURCES:" in prompt
    
    def test_data_source_manager_extensibility(self):
        """Test that DataSourceManager can be extended with new sources."""
        # Create a test manager to verify extensibility pattern
        class TestExtendedManager(DataSourceManager):
            def __init__(self):
                super().__init__()
                self._data_sources["test-extension"] = self._handle_test_extension
            
            def _handle_test_extension(self):
                return "This is a test extension to the data source manager."
        
        extended_manager = TestExtendedManager()
        
        # Should have the original sources plus the new one
        sources = extended_manager.get_available_data_sources()
        assert "data-test" in sources
        assert "new-mexico-history" in sources
        assert "test-extension" in sources
        
        # Should be able to get content from the new source
        content = extended_manager.get_data_source_content(["test-extension"])
        assert "test extension" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__])