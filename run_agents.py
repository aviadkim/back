import sys
import os
from agent_scripts import run_agent
from agent_definitions import agents

filepath = sys.argv[1]

for agent in agents:
    print(f"{agent} Report:\\n{run_agent(agent, filepath)}")
    print('-'*40)
