from LLMAgent.LLMAgent import Agent
import json
import os
import pika

def start(message, channel):
    json_body = json.loads(message)
    agent = Agent()
    res = agent.invoke_llm(json_body["comany_name"])
    try:
        channel.basic_publish(
            exchange= "",
            routing_key = os.getenv("COMPANY_ACTS_QUEUE"),
            body= json.dumps(res),
            properties = pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as e:
        return "failed to publish message"