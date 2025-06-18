"""
Example usage of the updated Ellisphere agent for JSON extraction.
This demonstrates how to extract structured financial data from XML reports.
"""

import asyncio
import json
from helpers.ellisphere_helper import parse_year_to_json, get_year_line_ranges, extract_year_xml_content


async def main():
    """
    Main example function demonstrating different ways to use the JSON extraction.
    """
    print("=== Ellisphere JSON Extraction Example ===\n")
    
    # 1. First, let's see what years are available and their line ranges
    print("1. Analyzing available years in the XML file...")
    year_ranges = get_year_line_ranges()
    
    if year_ranges:
        print("Available years and their line ranges:")
        for year, (start, end) in year_ranges.items():
            print(f"  Year {year}: lines {start}-{end}")
    else:
        print("  No year data found or error reading file")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Extract JSON for the 2023 year (lines 3-1533 as specified)
    print("2. Extracting JSON for 2023 financial data (lines 3-1533)...")
    
    try:
        json_result = await parse_year_to_json(start_line=3, end_line=1533)
        
        if json_result:
            print("Successfully extracted JSON data!")
            print("First 500 characters of JSON result:")
            print(json_result[:500] + "..." if len(json_result) > 500 else json_result)
            
            # Try to parse as JSON to validate structure
            try:
                parsed_data = json.loads(json_result)
                print("\nJSON structure validation: SUCCESS ✓")
                
                # Show some key metrics if available
                if 'company_financial_report' in parsed_data:
                    report = parsed_data['company_financial_report']
                    print(f"Report Year: {report.get('report_year', 'N/A')}")
                    print(f"Privacy: {report.get('privacy', 'N/A')}")
                    print(f"Currency: {report.get('currency', 'N/A')}")
                    
                    if 'periods' in report and len(report['periods']) > 0:
                        period1 = report['periods'][0]
                        print(f"Period 1 End Date: {period1.get('end_date', 'N/A')}")
                        
                        # Show some financial metrics
                        if 'balance_sheet_assets' in period1:
                            assets = period1['balance_sheet_assets']
                            print(f"Total Assets: {assets.get('total_assets', 'N/A')}")
                        
                        if 'income_statement' in period1:
                            income = period1['income_statement']
                            print(f"Net Revenue: {income.get('net_revenue', 'N/A')}")
                            print(f"Net Income: {income.get('net_income', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"\nJSON structure validation: FAILED - {e}")
                print("Raw result (first 1000 chars):")
                print(json_result[:1000])
                
        else:
            print("Failed to extract JSON data")
            
    except Exception as e:
        print(f"Error during extraction: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Show how to extract raw XML content for inspection
    print("3. Extracting raw XML content for inspection...")
    
    xml_content = extract_year_xml_content(start_line=3, end_line=50)  # Just first 50 lines for demo
    if xml_content:
        print("Sample XML content (first 47 lines):")
        print(xml_content)
    else:
        print("Failed to extract XML content")


if __name__ == "__main__":
    print("Starting Ellisphere JSON extraction example...\n")
    asyncio.run(main())
    print("\nExample completed!") 