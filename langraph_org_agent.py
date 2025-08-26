"""
LangGraph Agent for Analyzing Queries and Routing to Organizational Agents
"""

import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from enum import Enum
from dataclasses import dataclass
import operator

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QueryCategory(str, Enum):
    """Categories of employee-related queries"""
    HR_POLICIES = "hr_policies"
    PAYROLL = "payroll"
    BENEFITS = "benefits"
    PERFORMANCE = "performance"
    TRAINING = "training"
    IT_SUPPORT = "it_support"
    FACILITIES = "facilities"
    GENERAL = "general"

class QueryAnalysis(BaseModel):
    """Structure for query analysis results"""
    category: QueryCategory = Field(description="The category of the employee query")
    urgency: int = Field(description="Urgency level from 1-5, where 5 is most urgent")
    entities: List[str] = Field(description="Key entities extracted from the query")
    intent: str = Field(description="The main intent of the query")
    requires_approval: bool = Field(description="Whether this query requires managerial approval")

class AgentState(TypedDict):
    """State that gets passed between nodes in the graph"""
    messages: Annotated[List[BaseMessage], operator.add]
    query: str
    analysis: Optional[QueryAnalysis]
    assigned_agent: Optional[str]
    response: Optional[str]
    next_action: Optional[str]

class QueryAnalyzer:
    """Analyzes incoming queries to determine routing and handling"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert query analyzer for employee-related requests.
            Analyze the query and categorize it appropriately.
            
            Categories:
            - hr_policies: Questions about HR policies, procedures, handbook
            - payroll: Salary, wages, tax questions, pay stubs
            - benefits: Health insurance, retirement, PTO, vacation
            - performance: Performance reviews, goals, feedback
            - training: Learning opportunities, certifications, skill development
            - it_support: Technical issues, software, hardware, access
            - facilities: Office space, equipment, maintenance
            - general: General questions not fitting other categories
            
            Consider urgency based on:
            - 5: Emergency (security breach, injury, system down)
            - 4: High (payroll errors, urgent deadlines)
            - 3: Medium (policy clarifications, routine requests)
            - 2: Low (general information, future planning)
            - 1: Very low (suggestions, non-urgent inquiries)"""),
            ("human", "Analyze this employee query: {query}")
        ])
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a query and return structured analysis"""
        chain = self.analysis_prompt | self.llm.with_structured_output(QueryAnalysis)
        return chain.invoke({"query": query})

class OrganizationalAgent:
    """Base class for organizational agents"""
    
    def __init__(self, name: str, llm: ChatOpenAI, specialty: str):
        self.name = name
        self.llm = llm
        self.specialty = specialty
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are {name}, a specialized organizational agent for {specialty}.
            You help employees with queries related to your area of expertise.
            Provide helpful, accurate, and professional responses.
            If you cannot fully answer a question, suggest appropriate next steps or escalation."""),
            ("human", "{query}")
        ])
    
    def process_query(self, query: str, analysis: QueryAnalysis) -> str:
        """Process a query and return a response"""
        chain = self.prompt | self.llm
        response = chain.invoke({
            "query": query,
            "analysis": analysis.model_dump()
        })
        return response.content

class HRAgent(OrganizationalAgent):
    """HR specialist agent"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            name="HR Assistant", 
            llm=llm, 
            specialty="Human Resources policies, procedures, and employee relations"
        )

class PayrollAgent(OrganizationalAgent):
    """Payroll specialist agent"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            name="Payroll Specialist", 
            llm=llm, 
            specialty="Payroll processing, salary questions, and tax-related inquiries"
        )

class BenefitsAgent(OrganizationalAgent):
    """Benefits specialist agent"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            name="Benefits Coordinator", 
            llm=llm, 
            specialty="Employee benefits, insurance, retirement plans, and PTO"
        )

class ITSupportAgent(OrganizationalAgent):
    """IT support specialist agent"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(
            name="IT Support", 
            llm=llm, 
            specialty="Technical support, software issues, and system access"
        )

class LangGraphOrgAgent:
    """Main LangGraph agent orchestrator"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        # Initialize LLM
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4",
            temperature=0.1
        )
        
        # Initialize components
        self.query_analyzer = QueryAnalyzer(self.llm)
        
        # Initialize organizational agents
        self.agents = {
            QueryCategory.HR_POLICIES: HRAgent(self.llm),
            QueryCategory.PAYROLL: PayrollAgent(self.llm),
            QueryCategory.BENEFITS: BenefitsAgent(self.llm),
            QueryCategory.IT_SUPPORT: ITSupportAgent(self.llm),
            QueryCategory.PERFORMANCE: HRAgent(self.llm),  # HR handles performance
            QueryCategory.TRAINING: HRAgent(self.llm),     # HR handles training
            QueryCategory.FACILITIES: ITSupportAgent(self.llm),  # IT handles facilities
            QueryCategory.GENERAL: HRAgent(self.llm)       # HR handles general queries
        }
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        def analyze_query_node(state: AgentState) -> AgentState:
            """Node to analyze the incoming query"""
            query = state["query"]
            analysis = self.query_analyzer.analyze_query(query)
            
            return {
                **state,
                "analysis": analysis,
                "messages": [AIMessage(content=f"Query analyzed: {analysis.intent}")]
            }
        
        def route_query_node(state: AgentState) -> AgentState:
            """Node to route query to appropriate agent"""
            analysis = state["analysis"]
            if not analysis:
                return {**state, "assigned_agent": "hr_policies"}
            
            assigned_agent = analysis.category.value
            return {
                **state,
                "assigned_agent": assigned_agent
            }
        
        def process_query_node(state: AgentState) -> AgentState:
            """Node to process query with assigned agent"""
            query = state["query"]
            analysis = state["analysis"]
            assigned_agent = state["assigned_agent"]
            
            # Get the appropriate agent
            category = QueryCategory(assigned_agent)
            agent = self.agents[category]
            
            # Process the query
            response = agent.process_query(query, analysis)
            
            return {
                **state,
                "response": response,
                "messages": [AIMessage(content=response)]
            }
        
        def check_approval_needed(state: AgentState) -> str:
            """Conditional edge to check if approval is needed"""
            analysis = state["analysis"]
            if analysis and analysis.requires_approval:
                return "approval_needed"
            return "completed"
        
        def approval_node(state: AgentState) -> AgentState:
            """Node to handle approval requirements"""
            approval_msg = ("This request requires managerial approval. "
                          "Your request has been forwarded to your supervisor.")
            
            return {
                **state,
                "response": state["response"] + "\n\n" + approval_msg,
                "messages": [AIMessage(content=approval_msg)]
            }
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_query", analyze_query_node)
        workflow.add_node("route_query", route_query_node)
        workflow.add_node("process_query", process_query_node)
        workflow.add_node("approval", approval_node)
        
        # Add edges
        workflow.add_edge("analyze_query", "route_query")
        workflow.add_edge("route_query", "process_query")
        workflow.add_conditional_edges(
            "process_query",
            check_approval_needed,
            {
                "approval_needed": "approval",
                "completed": END
            }
        )
        workflow.add_edge("approval", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_query")
        
        return workflow.compile()
    
    def process_employee_query(self, query: str) -> Dict[str, Any]:
        """Process an employee query through the agent system"""
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query,
            analysis=None,
            assigned_agent=None,
            response=None,
            next_action=None
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "query": query,
            "analysis": result["analysis"].model_dump() if result["analysis"] else None,
            "assigned_agent": result["assigned_agent"],
            "response": result["response"],
            "messages": [msg.content for msg in result["messages"]]
        }
    
    def get_agent_capabilities(self) -> Dict[str, str]:
        """Get information about available agents and their capabilities"""
        return {
            agent_type.value: agent.specialty 
            for agent_type, agent in self.agents.items()
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the agent system
    try:
        org_agent = LangGraphOrgAgent()
        
        # Example queries
        test_queries = [
            "I haven't received my paycheck this month. What should I do?",
            "What is our company policy on remote work?",
            "How do I enroll in the health insurance plan?",
            "My laptop is not connecting to the company VPN",
            "I want to request time off for next week",
            "Can you help me understand my 401k options?"
        ]
        
        print("=== LangGraph Organizational Agent System ===\n")
        print("Available agent capabilities:")
        for agent_type, capability in org_agent.get_agent_capabilities().items():
            print(f"  {agent_type}: {capability}")
        print("\n" + "="*50 + "\n")
        
        # Process each test query
        for i, query in enumerate(test_queries, 1):
            print(f"Query {i}: {query}")
            print("-" * 40)
            
            result = org_agent.process_employee_query(query)
            
            print(f"Category: {result['analysis']['category']}")
            print(f"Urgency: {result['analysis']['urgency']}/5")
            print(f"Assigned Agent: {result['assigned_agent']}")
            print(f"Response: {result['response']}")
            print("\n" + "="*50 + "\n")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your OPENAI_API_KEY environment variable.")