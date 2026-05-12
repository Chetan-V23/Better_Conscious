from LLMAgent.LLMAgent import Agent
import json
import os
import pika
from logger import logger

def start(message, channel):
    try:
        logger.info(f"Processing message: {message}")
        json_body = json.loads(message)
        company_name = json_body.get("company_name")
        logger.info(f"Extracted company name: {company_name}")
        
        agent = Agent()
        logger.info(f"Created LLM Agent for {company_name}")
        
        res = agent.invoke_llm(company_name)
        logger.info(f"LLM invocation completed for {company_name}")
        
        try:
            queue_name = os.getenv("COMPANY_ACTS_QUEUE")
            logger.info(f"Publishing result to queue: {queue_name}")
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(res),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            logger.info(f"Successfully published result for {company_name}")
            return None
        except Exception as e:
            logger.error(f"Failed to publish message to queue: {e}", exc_info=True)
            return "failed to publish message"
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from message: {e}", exc_info=True)
        return "failed to parse JSON"
    except Exception as e:
        logger.error(f"Unexpected error in start function: {e}", exc_info=True)
        return "unexpected error"