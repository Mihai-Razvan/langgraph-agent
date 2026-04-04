from fastapi import FastAPI

from services.agent_service import Agent

app = FastAPI()
agent = Agent()

@app.post("/call")
def ask_message(user_message: str):
    return agent.invoke(user_message=user_message, thread_id="1")