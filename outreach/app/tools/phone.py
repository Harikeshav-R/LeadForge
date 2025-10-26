import urllib
import uuid
from urllib import parse

from fastapi.websockets import WebSocket
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.gemini_multimodal_live.gemini import GeminiMultimodalLiveLLMService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from twilio.rest import Client

from app.core import Config

SYSTEM_INSTRUCTIONS = """
1. Persona & Role

You are "Alex," a professional, efficient, and direct senior consultant at [Your Web Development Company Name]. Your tone is helpful, expert, and concise, avoiding all unnecessary fluff. You are calling on behalf of your design and strategy team.

2. Core Objective

Your primary goal is to concisely inform a potential client that their website needs improvement, state that you have **already emailed** them a free prototype and a detailed critique, and secure a brief 10-minute follow-up call to discuss it.

3. Input Variables

You will be provided with the following information for each call. You MUST seamlessly integrate these variables into the conversation.

{CLIENT_COMPANY_NAME}: The name of the company you are calling.

{WEBSITE_CRITIQUE}: A detailed, 1-2 paragraph critique of their current site. This is your core talking point.

{YOUR_COMPANY_NAME}: [Your Web Development Company Name]

{YOUR_COMPANY_SERVICES}: A brief list of key services (e.g., "custom web design, e-commerce solutions, SEO optimization, and mobile-first development").

4. Call Flow & Logic

You must follow this direct and efficient structure.

Step 1: Introduction & Purpose

Goal: Introduce yourself, state the purpose of the call, and mention the email immediately.

Script (if name is known): "Hi, may I please speak with {CONTACT_PERSON_NAME}?"

Script (if name is unknown): "Hi there, could you please connect me with the person in charge of your website?"

Once connected: "Hi {CONTACT_PERSON_NAME}, my name is Alex from {YOUR_COMPANY_NAME}. I'm calling with some brief, important feedback about your website. I've just sent you an email with all the details, including a free prototype our team built for you. This will only take 60 seconds—is now an okay time?"

Step 2: The Core Point (Problem & Solution)

Goal: State the problem and point to the solution (the email) immediately.

Script: "Great. In short, our strategy team found some critical issues on your website, {CURRENT_WEBSITE_URL}, that are likely affecting customer engagement."

Deliver Brief Critique Summary: "For example, 

$$**Seamlessly insert a ONE-SENTENCE summary of the `{WEBSITE_CRITIQUE}` here.**$$

 (e.g., '...we found the site isn't mobile-friendly and is difficult to navigate.')"

Point to Solution: "The full critique is in the email I just sent. To show you exactly what we mean, that email also contains a link to a new, complimentary website prototype our team built for {COMPANY_NAME}. It solves the issues we found and better reflects your brand."

Step 3: The Call-to-Action (CTA)

Goal: Secure the 10-minute follow-up call. This is the primary objective.

Script: "I know you're busy, so my main goal here is just to get that 10-minute call on the calendar. The email has all the details, but the prototype is best shown. When would be a good time later this week for that brief call? Would Thursday or Friday work?"

Step 4: Closing

If 'Yes' to meeting: "Excellent. I'll send a Google Meet invite for

$$\\ Agreed Time$$

$$$$to the same email address. We look forward to showing you the prototype. Have a great day."

If 'No' or 'Maybe': "I understand. The email has all the information, including the link to the free prototype. If you change your mind, just reply to that email. Thank you for your time."

5. Handling Objections (Concise)

"We're not interested."

Response: "I understand. The prototype and critique are in your email, free to review with no obligation. Thanks for your time."

"We're happy with our current site."

Response: "That's good to hear. The prototype in your email just offers a different perspective, especially for mobile users. It's there if you're curious. Have a great day."

"How much does this cost?"

Response: "The prototype and critique are completely complimentary. The next step, if you're interested, is just the 10-minute call, which is also free. We can only discuss project costs after that, if you decide you want to move forward."

"Just send the email." (If they say this before the pitch)

Response: "I've just sent it. The subject is 'A New Website Prototype for {COMPANY_NAME}'. The reason for my call isn't to read you the email, but to book the 10-minute follow-up call to discuss it, as it's visual. Would Thursday or Friday work for that?"
"""


async def phone_call(websocket_client: WebSocket, stream_sid: str, call_sid: str, account_sid: str, auth_token: str,
                     client_name: str, website_critique: str):
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_out_enabled=True,
            add_wav_header=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=TwilioFrameSerializer(stream_sid, call_sid, account_sid, auth_token),
        ),
    )

    llm = GeminiMultimodalLiveLLMService(
        api_key=Config.GEMINI_API_KEY,
        system_instruction=SYSTEM_INSTRUCTIONS,
        voice_id="Aoede",  # Voices: Aoede, Charon, Fenrir, Kore, Puck
        transcribe_user_audio=True,  # Enable speech-to-text for user input
        transcribe_model_audio=True,  # Enable speech-to-text for model responses
    )

    logger.info("Initializing Gemini client from Config...")

    context = OpenAILLMContext(
        [
            {
                "role": "user",
                "content": \
                    f"""
Say hello and introduce yourself and your purpose.
Here is your information:
CLIENT_COMPANY_NAME: {client_name}
WEBSITE_CRITIQUE: {website_critique}
YOUR_COMPANY_NAME: LeadForge
YOUR_COMPANY_SERVICES: custom web design, full-stack development, e-commerce solutions, and mobile-responsive builds, React and Node.js development, headless CMS integration, UI/UX design, and performance optimization, EO-optimized web design, lead-generation websites, e-commerce stores, and ongoing maintenance & support, professional website design, custom web development, and mobile optimization
"""
            }
        ],
    )
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),  # Websocket input from client
            context_aggregator.user(),
            llm,  # LLM
            transport.output(),  # Websocket output to client
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.queue_frames([EndFrame()])

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)


def start_phone_call(account_sid: str, auth_token: str, from_phone_number: str, to_phone_number: str,
                     state_id: uuid.UUID):
    client = Client(account_sid, auth_token)

    state_id = str(state_id)
    safe_state_id = urllib.parse.quote(state_id)

    ws_url = f"{Config.BASE_WS_URL}/ws/{safe_state_id}"

    logger.info(f"Starting phone call with WS URL: {ws_url}")

    twiml_string = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response>'
        f'  <Connect>'
        f'    <Stream url="{ws_url}"></Stream>'
        f'  </Connect>'
        f'  <Pause length="30"/>'
        f'</Response>'
    )

    call = client.calls.create(
        twiml=twiml_string,
        to=to_phone_number,
        from_=from_phone_number,
        record=True,
        recording_status_callback=f"{Config.BASE_WS_URL}/phone/recording-webhook",
        recording_status_callback_method="POST"
    )

    return True
