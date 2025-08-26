# LangGraph Organizational Agent System

A sophisticated LangGraph-based agent system for analyzing employee queries and routing them to specialized organizational agents. This system automatically categorizes employee requests, determines urgency levels, and routes them to the appropriate departmental agent (HR, Payroll, Benefits, IT Support, etc.).

## 🌟 Features

- **Intelligent Query Analysis**: Uses LLM-powered analysis to understand employee queries
- **Automatic Categorization**: Classifies queries into 8 different organizational categories
- **Urgency Assessment**: Evaluates query urgency on a 1-5 scale
- **Smart Routing**: Routes queries to specialized organizational agents
- **Approval Workflow**: Identifies queries requiring managerial approval
- **Extensible Architecture**: Easy to add new agent types and capabilities

## 🏗️ Architecture

The system uses LangGraph to create a workflow with the following components:

### Query Categories
- **HR Policies**: Company policies, procedures, handbook questions
- **Payroll**: Salary, wages, tax questions, pay stubs
- **Benefits**: Health insurance, retirement, PTO, vacation
- **Performance**: Performance reviews, goals, feedback
- **Training**: Learning opportunities, certifications, skill development
- **IT Support**: Technical issues, software, hardware, access
- **Facilities**: Office space, equipment, maintenance
- **General**: General questions not fitting other categories

### Specialized Agents
- **HR Assistant**: Handles HR policies, performance, training, and general queries
- **Payroll Specialist**: Manages payroll-related questions and issues
- **Benefits Coordinator**: Assists with employee benefits and PTO
- **IT Support**: Provides technical support and system access help

### Workflow Nodes
1. **Query Analysis**: Analyzes and categorizes incoming queries
2. **Query Routing**: Routes queries to appropriate specialized agents
3. **Query Processing**: Processes queries with the assigned agent
4. **Approval Check**: Determines if managerial approval is needed

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**:

Option A - Environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Option B - Create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

Option C - Pass directly in code:
```python
agent = LangGraphOrgAgent(openai_api_key="your-api-key")
```

### Basic Usage

```python
from langraph_org_agent import LangGraphOrgAgent

# Initialize the agent system
org_agent = LangGraphOrgAgent()

# Process an employee query
result = org_agent.process_employee_query(
    "I haven't received my paycheck this month. What should I do?"
)

print(f"Category: {result['analysis']['category']}")
print(f"Urgency: {result['analysis']['urgency']}/5")
print(f"Response: {result['response']}")
```

### Interactive Demo

Run the interactive demo:
```bash
python example_usage.py
```

Run the sample queries demo:
```bash
python example_usage.py --demo
```

## 📋 Example Queries and Expected Routing

| Query | Expected Category | Assigned Agent |
|-------|------------------|----------------|
| "I haven't received my paycheck" | payroll | Payroll Specialist |
| "What's our remote work policy?" | hr_policies | HR Assistant |
| "How do I enroll in health insurance?" | benefits | Benefits Coordinator |
| "My laptop won't connect to VPN" | it_support | IT Support |
| "I need time off next week" | benefits | Benefits Coordinator |
| "When is my performance review?" | performance | HR Assistant |

## 🔧 Customization

### Adding New Agent Types

1. **Create a new agent class**:
```python
class NewAgent(OrganizationalAgent):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            name="New Agent", 
            llm=llm, 
            specialty="Your specialty description"
        )
```

2. **Add to the QueryCategory enum**:
```python
class QueryCategory(str, Enum):
    # ... existing categories
    NEW_CATEGORY = "new_category"
```

3. **Update the agent mapping**:
```python
self.agents = {
    # ... existing mappings
    QueryCategory.NEW_CATEGORY: NewAgent(self.llm),
}
```

### Customizing Query Analysis

Modify the `QueryAnalyzer` class to adjust categorization logic:

```python
class QueryAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        # Customize the analysis prompt here
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "Your custom system prompt..."),
            ("human", "Analyze this query: {query}")
        ])
```

## 🧪 Testing

The system includes comprehensive test queries covering all categories. Run tests using:

```python
# Test with sample queries
python -c "
from langraph_org_agent import LangGraphOrgAgent
agent = LangGraphOrgAgent()
result = agent.process_employee_query('Test query here')
print(result)
"
```

## 📊 Query Analysis Structure

Each query returns a structured analysis:

```python
{
    "query": "Original employee query",
    "analysis": {
        "category": "payroll",
        "urgency": 4,
        "entities": ["paycheck", "month"],
        "intent": "Report missing paycheck",
        "requires_approval": False
    },
    "assigned_agent": "payroll",
    "response": "Agent response...",
    "messages": ["Processing messages..."]
}
```

## 🔒 Security Considerations

- API keys should be stored securely (environment variables or secure key management)
- Consider implementing authentication for production use
- Sensitive queries may require additional security measures
- Log queries appropriately while respecting privacy

## 🚀 Production Deployment

For production deployment, consider:

1. **Scalability**: Use async processing for high query volumes
2. **Monitoring**: Add logging and monitoring for query processing
3. **Database Integration**: Store query history and responses
4. **User Authentication**: Implement proper user authentication
5. **Rate Limiting**: Add rate limiting for API calls

## 📚 Dependencies

- `langgraph==0.2.16`: Graph-based workflow orchestration
- `langchain==0.3.0`: LLM framework and utilities
- `langchain-openai==0.2.0`: OpenAI integration
- `pydantic==2.8.2`: Data validation and settings management
- `python-dotenv==1.0.0`: Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is provided as-is for educational and development purposes.

## 🆘 Support

For issues or questions:

1. Check the error messages for configuration issues
2. Ensure your OpenAI API key is properly set
3. Verify all dependencies are installed correctly
4. Review the example usage for proper implementation patterns

## 🔄 Future Enhancements

- [ ] Add support for multiple LLM providers
- [ ] Implement conversation memory/context
- [ ] Add integration with ticketing systems
- [ ] Support for file attachments and document analysis
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Integration with company databases and systems