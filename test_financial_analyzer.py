import asyncio
from agents.financial.financial_agent import FinancialAgent

async def test_analysis():
    agent = FinancialAgent(memory_path="memory/test_financial.json")
    
    # Test document analysis
    result = await agent.process({
        "type": "analyze_document",
        "pdf_path": "test_documents/your_financial_doc.pdf",  # Update with your test document
        "force_refresh": True
    })
    
    print("Analysis result:", result)

if __name__ == "__main__":
    asyncio.run(test_analysis())
