"""
Module which contains the function for connecting to SMTP server and sending an email message
"""
import aiosmtplib
import constants
from email.message import EmailMessage
import asyncio


async def sendToken(emails: [str], token: str):
    message = EmailMessage()
    message["From"] = constants.SMTP_SENT_FROM
    message["To"] = emails[0]
    message["Subject"] = constants.SMTP_SUBJECT
    message.set_content(constants.SMTP_BODY.format(token=token))

    await aiosmtplib.send(
        message,
        sender=constants.SMTP_SENT_FROM,
        recipients=emails,
        hostname=constants.SMTP_HOST,
        port=constants.SMTP_PORT,
        username=constants.SMTP_USER,
        password=constants.SMTP_PASS,
        use_tls=True
    )
    
#driver test
if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(sendToken(["email@cccc.ccc"], "333TOKENSAMPLE111"))