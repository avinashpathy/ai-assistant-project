import os
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP, run_tool
from Utilities.utilities import log

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

MAX_STEPS = 10

messages = []

messages.append({
    "role": "system",
    "content": "Act like a very humble agent and respond always under 20 words."
})

while True:
    
    user_input = input("\nAvinash:")
    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break
    
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

# Chained Tool Calling
    for step in range(MAX_STEPS):
        response  = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
    )
    
        msg = response.choices[0].message
        
        messages.append(msg)
        
        if not msg.tool_calls:
            break
        
        log(f"Step {step+1}: model requested {len(msg.tool_calls)} tool calls")
        
        for tool_call in msg.tool_calls:
            result = run_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        
    else:
        fallback = "Sorry, I could not finish within the step limit."
        messages.append({
            "role": "assistant",
            "content": fallback
        })
        print("Assistant: "+ fallback)
        continue
    
    messages.append({
        "role": "assistant",
        "content": msg.content
    })
    
    print("Assistant: " + (msg.content or ""))
    

