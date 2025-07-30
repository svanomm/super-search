#!/usr/bin/env python3
"""
Command line version of the GUI to test the BM25 integration functionality.
This demonstrates the search integration without requiring GUI dependencies.
"""

import os
import sys
import json

# Add current directory to path for imports
sys.path.append('.')

class MockSearchApp:
    def __init__(self):
        self.bm25_index_path = 'index_bm25'
        self.search_results = []
        
    def mock_query_bm25(self, query, index_path, num_results=3):
        """Mock version that simulates the real query_bm25 function"""
        print(f"[MOCK] Searching for: '{query}' in index: '{index_path}'")
        print(f"[MOCK] Requested {num_results} results")
        
        # Simulate different types of results based on query
        if "machine learning" in query.lower():
            return {
                'text': [
                    "Machine learning algorithms are designed to improve automatically through experience. They build mathematical models based on training data to make predictions or decisions without being explicitly programmed to do so.",
                    "Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers to progressively extract higher-level features from raw input data.",
                    "Supervised learning is a machine learning approach where the model is trained on labeled data, meaning the desired output is known for each training example."
                ],
                'id': [42, 73, 156]
            }
        elif "economics" in query.lower():
            return {
                'text': [
                    "Economics is the social science that studies how societies allocate scarce resources among competing uses. It examines production, distribution, and consumption of goods and services.",
                    "Microeconomics focuses on individual agents such as households and firms, analyzing their decision-making processes and interactions in markets.",
                    "Macroeconomics studies the economy as a whole, examining aggregate indicators like GDP, unemployment rates, and inflation."
                ],
                'id': [201, 202, 203]
            }
        elif "empty" in query.lower():
            return {'text': [], 'id': []}
        else:
            return {
                'text': [
                    f"This is a sample document chunk that contains relevant information about '{query}' and related topics.",
                    f"Another relevant result for '{query}' showing how the search algorithm identifies matching content."
                ],
                'id': [301, 302]
            }
    
    def format_search_results(self, results):
        """Format search results for display"""
        formatted_results = []
        
        if results['text'] and len(results['text']) > 0:
            print(f"\nFound {len(results['text'])} results:")
            print("-" * 80)
            
            for i, (text, chunk_id) in enumerate(zip(results['text'], results['id'])):
                # Clean up text for display
                clean_text = ' '.join(text.split())
                # Truncate for display
                display_text = clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
                
                formatted_result = f"[{i+1}] Chunk {chunk_id}: {display_text}"
                formatted_results.append(formatted_result)
                
                print(f"Result {i+1}:")
                print(f"  Chunk ID: {chunk_id}")
                print(f"  Text: {display_text}")
                print()
        else:
            print("No results found for your query.")
            formatted_results = ["No results found for your query."]
        
        return formatted_results
    
    def search(self, query):
        """Perform search operation - this is the core integration logic"""
        if not query.strip():
            print("Error: Please enter a search query.")
            return False
        
        if not os.path.exists(self.bm25_index_path):
            print(f"Error: No BM25 index found at '{self.bm25_index_path}'. Please build an index first.")
            return False
        
        try:
            print(f"Searching for: '{query}'")
            
            # This is where the real query_bm25 would be called
            # results = query_bm25(query=query, index_path=self.bm25_index_path, num_results=10)
            results = self.mock_query_bm25(query=query, index_path=self.bm25_index_path, num_results=10)
            
            # Format and store results
            self.search_results = self.format_search_results(results)
            
            return True
            
        except Exception as e:
            print(f"Error performing search: {str(e)}")
            self.search_results = [f"Error: {str(e)}"]
            return False
    
    def clear_search(self):
        """Clear search results"""
        self.search_results = []
        print("Search results cleared.")
    
    def show_help(self):
        """Show available commands"""
        print("\nAvailable commands:")
        print("  search <query>  - Search for documents containing the query")
        print("  clear          - Clear search results")
        print("  results        - Show last search results")
        print("  help           - Show this help message")
        print("  exit           - Exit the application")
        print()
    
    def show_results(self):
        """Display current search results"""
        if self.search_results:
            print("\nCurrent search results:")
            print("-" * 80)
            for result in self.search_results:
                print(result)
        else:
            print("No search results to display.")
    
    def run(self):
        """Main application loop"""
        print("BM25 Search Integration Test")
        print("=" * 40)
        print("This demonstrates the query_bm25() integration in the GUI's search tab.")
        print("Note: Using mock data since actual dependencies are not installed.")
        print()
        self.show_help()
        
        while True:
            try:
                user_input = input("\nEnter command: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'clear':
                    self.clear_search()
                
                elif user_input.lower() == 'results':
                    self.show_results()
                
                elif user_input.lower().startswith('search '):
                    query = user_input[7:]  # Remove 'search ' prefix
                    self.search(query)
                
                else:
                    print(f"Unknown command: '{user_input}'. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def test_integration_scenarios():
    """Test various integration scenarios"""
    print("Testing Integration Scenarios")
    print("=" * 40)
    
    app = MockSearchApp()
    
    # Test 1: Normal search
    print("\nTest 1: Normal search query")
    app.search("machine learning")
    
    # Test 2: Empty query
    print("\nTest 2: Empty query")
    app.search("")
    
    # Test 3: Query with no results
    print("\nTest 3: Query with no results")
    app.search("empty results")
    
    # Test 4: Economics query
    print("\nTest 4: Economics query")
    app.search("economics and markets")
    
    print("\n" + "=" * 40)
    print("Integration testing completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_integration_scenarios()
    else:
        app = MockSearchApp()
        app.run()