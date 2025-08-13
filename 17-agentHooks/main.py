from agents import Runner, set_tracing_disabled
from my_agent.my_agents import assistant

set_tracing_disabled(True)
# user_input = input("Enter your Query:")
res = Runner.run_sync(
    starting_agent=assistant,
    # input=user_input,
    input="2+2=?",
    context={"id": "4"},
)

print(res.final_output)