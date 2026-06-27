import os
from src.agent import chat

def test_agent_with_arxiv():
    print("Testing the agent with an arXiv query...")
    # This query should prompt the agent to use the 'fetch_arxiv_paper' tool.
    user_message = "Please fetch and extract the main points of the arXiv paper with ID 2310.01526"
    user_id = "test_user"
    
    try:
        res = chat(user_id=user_id, user_message=user_message)
        reply = res["reply"] if isinstance(res, dict) else res
        print("\n=== AGENT RESPONSE ===")
        print(reply)
        print("======================\n")
        
        # Verify the reply contains some relevant keywords from the paper or mentions the paper
        if "modern" in reply.lower() or "code review" in reply.lower() or "systematic" in reply.lower():
            print("SUCCESS: Agent successfully fetched and summarized the paper!")
            return True
        else:
            print("WARNING: Agent responded but keywords were not found. Please review the response manually.")
            return False
            
    except Exception as e:
        print(f"Error during agent execution: {e}")
        return False

if __name__ == "__main__":
    test_agent_with_arxiv()
