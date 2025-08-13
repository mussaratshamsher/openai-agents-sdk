from agents import Runner, set_tracing_disabled
from my_agent.my_agents import assistant
from my_hooks.my_run_hooks import MyRunHooks


set_tracing_disabled(True)


# user_input = input("Enter your Query:")

res = Runner.run_sync(
    assistant,
    # input=user_input,
    input="2*3=?",
    hooks=MyRunHooks()
)

print(res.final_output)