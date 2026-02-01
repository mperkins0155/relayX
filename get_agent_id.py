"""
Simple script to list all agents directly from Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("Error: SUPABASE_URL or SUPABASE_ANON_KEY not found in environment variables")
    print("Make sure you have a .env file in the root directory")
    exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

try:
    # Query all agents
    response = supabase.table('agents').select('*').order('created_at', desc=True).execute()
    
    if not response.data:
        print("No agents found in database.")
        exit(0)
    
    print("\n" + "="*80)
    print("ALL AGENTS IN DATABASE")
    print("="*80 + "\n")
    
    for i, agent in enumerate(response.data, 1):
        print(f"{i}. Agent: {agent.get('name', 'Unnamed')}")
        print(f"   ID: {agent['id']}")
        print(f"   User ID: {agent.get('user_id', 'N/A')}")
        print(f"   Active: {agent.get('is_active', False)}")
        print(f"   Created: {agent.get('created_at', 'N/A')}")
        
        # Show first 100 chars of prompt
        prompt = agent.get('prompt_text', agent.get('resolved_system_prompt', ''))
        if prompt:
            preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
            print(f"   Prompt: {preview}")
        
        print("-" * 80 + "\n")
    
    print("\n" + "="*80)
    print(f"Total agents found: {len(response.data)}")
    print("="*80 + "\n")
    
    # Look for landing page agent
    landing_agents = [a for a in response.data if 'landing' in a.get('name', '').lower() or 'demo' in a.get('name', '').lower() or 'relayx' in a.get('name', '').lower()]
    
    if landing_agents:
        print("\n🎯 SUGGESTED LANDING PAGE AGENTS:")
        for agent in landing_agents:
            print(f"   ✅ {agent['name']}")
            print(f"      ID: {agent['id']}")
            print()
    else:
        print("\n⚠️  No agent with 'landing', 'demo', or 'relayx' in name found.")
        print("   You can use any of the agents listed above, or create a new one.\n")
        
except Exception as e:
    print(f"Error fetching agents: {e}")
    import traceback
    traceback.print_exc()
