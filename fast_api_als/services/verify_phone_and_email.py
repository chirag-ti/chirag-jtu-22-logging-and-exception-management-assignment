import time
import httpx
import asyncio
import logging
from fast_api_als.constants import (
    ALS_DATA_TOOL_EMAIL_VERIFY_METHOD,
    ALS_DATA_TOOL_PHONE_VERIFY_METHOD,
    ALS_DATA_TOOL_SERVICE_URL,
    ALS_DATA_TOOL_REQUEST_KEY)

"""
How can you write log to understand what's happening in the code?
You also trying to undderstand the execution time factor.
"""
logger = logging.getLogger(__name__)
zero_time = time.time()

async def call_validation_service(url: str, topic: str, value: str, data: dict) -> None:  # 2
    if value == '':
        return
    async with httpx.AsyncClient() as client:  # 3
        response = await client.get(url)

    r = response.json()
    data[topic] = r
    logger.info(f'Called validation_services | time of execution is {time.time() - zero_time}')
    

async def verify_phone_and_email(email: str, phone_number: str) -> bool:
    email_validation_url = '{}?Method={}&RequestKey={}&EmailAddress={}&OutputFormat=json'.format(
        ALS_DATA_TOOL_SERVICE_URL,
        ALS_DATA_TOOL_EMAIL_VERIFY_METHOD,
        ALS_DATA_TOOL_REQUEST_KEY,
        email)
    phone_validation_url = '{}?Method={}&RequestKey={}&PhoneNumber={}&OutputFormat=json'.format(
        ALS_DATA_TOOL_SERVICE_URL,
        ALS_DATA_TOOL_PHONE_VERIFY_METHOD,
        ALS_DATA_TOOL_REQUEST_KEY,
        phone_number)
    email_valid = False
    phone_valid = False
    data = {}

    await asyncio.gather(
        call_validation_service(email_validation_url, "email", email, data),
        call_validation_service(phone_validation_url, "phone", phone_number, data),
    )
    if "email" in data:
        if data["email"]["DtResponse"]["Result"][0]["StatusCode"] in ("0", "1"):
            logger.info(f"Email:{email} is verified | time of execution is {time.time() - zero_time}")
            email_valid = True
        else:
            logger.error(f"Invalid email:{email} | time of execution is {time.time() - zero_time}")
    if "phone" in data:
        if data["phone"]["DtResponse"]["Result"][0]["IsValid"] == "True":
            logger.info(f"Phone:{phone_number} is verified | time of execution is {time.time() - zero_time}")
            phone_valid = True
        else:
            logger.error(f"Invalid Phone_number:{phone_number} | time of execution is {time.time() - zero_time}")
    return email_valid | phone_valid
