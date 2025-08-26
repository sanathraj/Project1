"""
Example Usage of LangGraph Organizational Agent System
"""

import os
from langraph_org_agent import LangGraphOrgAgent

def main():
    """Demonstrate the LangGraph organizational agent system"""
    
    # Make sure to set your OpenAI API key
    # You can do this by:
    # 1. Setting OPENAI_API_KEY environment variable
    # 2. Creating a .env file with OPENAI_API_KEY=your_key
    # 3. Passing it directly to LangGraphOrgAgent(openai_api_key="your_key")
    
    try:
        # Initialize the agent system
        print("Initializing LangGraph Organizational Agent System...")
        org_agent = LangGraphOrgAgent()
        
        # Display available capabilities
        print("\n=== Available Agent Capabilities ===")
        capabilities = org_agent.get_agent_capabilities()
        for agent_type, capability in capabilities.items():
            print(f"🤖 {agent_type.replace('_', ' ').title()}: {capability}")
        
        # Interactive query processing
        print("\n=== Interactive Query Processing ===")
        print("Enter employee queries to see how they're analyzed and routed.")
        print("Type 'quit' to exit.\n")
        
        while True:
            query = input("Employee Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
            
            print("\nProcessing query...")
            print("-" * 50)
            
            # Process the query
            result = org_agent.process_employee_query(query)
            
            # Display results
            analysis = result['analysis']
            print(f"📝 Original Query: {result['query']}")
            print(f"🏷️  Category: {analysis['category']}")
            print(f"⚡ Urgency Level: {analysis['urgency']}/5")
            print(f"🎯 Intent: {analysis['intent']}")
            print(f"📋 Key Entities: {', '.join(analysis['entities'])}")
            print(f"👤 Assigned Agent: {result['assigned_agent'].replace('_', ' ').title()}")
            print(f"✅ Requires Approval: {'Yes' if analysis['requires_approval'] else 'No'}")
            print(f"\n💬 Response:\n{result['response']}")
            print("\n" + "="*60 + "\n")
        
        print("Thank you for using the LangGraph Organizational Agent System!")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("2. Set it as an environment variable: export OPENAI_API_KEY='your-key-here'")
        print("3. Or create a .env file with: OPENAI_API_KEY=your-key-here")
        print("4. Or pass it directly: LangGraphOrgAgent(openai_api_key='your-key')")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("Please check your configuration and try again.")

def demo_with_sample_queries():
    """Run a demo with predefined sample queries"""
    
    try:
        org_agent = LangGraphOrgAgent()
        
        # Sample queries covering different categories
        sample_queries = [
            {
                "query": "I haven't received my paycheck this month. What should I do?",
                "expected_category": "payroll"
            },
            {
                "query": "What is our company policy on remote work?",
                "expected_category": "hr_policies"
            },
            {
                "query": "How do I enroll in the health insurance plan?",
                "expected_category": "benefits"
            },
            {
                "query": "My laptop is not connecting to the company VPN",
                "expected_category": "it_support"
            },
            {
                "query": "I want to request time off for next week",
                "expected_category": "benefits"
            },
            {
                "query": "Can you help me understand my 401k options?",
                "expected_category": "benefits"
            },
            {
                "query": "I need access to the new software system",
                "expected_category": "it_support"
            },
            {
                "query": "When is my performance review scheduled?",
                "expected_category": "performance"
            }
        ]
        
        print("🚀 Running Demo with Sample Queries")
        print("="*50)
        
        for i, sample in enumerate(sample_queries, 1):
            query = sample["query"]
            expected = sample["expected_category"]
            
            print(f"\n📋 Sample Query {i}: {query}")
            print("-" * 40)
            
            result = org_agent.process_employee_query(query)
            analysis = result['analysis']
            
            # Check if categorization matches expectation
            category_match = "✅" if analysis['category'] == expected else "⚠️"
            
            print(f"{category_match} Category: {analysis['category']} (Expected: {expected})")
            print(f"⚡ Urgency: {analysis['urgency']}/5")
            print(f"🎯 Intent: {analysis['intent']}")
            print(f"👤 Agent: {result['assigned_agent'].replace('_', ' ').title()}")
            print(f"💬 Response Preview: {result['response'][:100]}...")
            
        print(f"\n🎉 Demo completed! Processed {len(sample_queries)} sample queries.")
        
    except Exception as e:
        print(f"❌ Demo Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_with_sample_queries()
    else:
        main()