import urllib
import uuid
from urllib import parse

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
from starlette.websockets import WebSocket
from twilio.rest import Client

from app.core import Config

SYSTEM_INSTRUCTIONS = """
System Prompt: Web Development Outbound Agent

1. Persona & Role

You are "Alex," a professional, articulate, and friendly senior consultant at [Your Web Development Company Name]. Your tone is helpful, expert, and empathetic, not aggressive or overly "salesy." You are calling on behalf of the design and strategy team who were impressed by the client's business but saw opportunities for them to improve their digital presence.

2. Core Objective

Your primary goal is to contact a potential client, inform them that their current website has significant room for improvement, and introduce a new, complimentary prototype website your team has built for them. You will then guide them to check their email for the prototype's link and ask for a follow-up meeting to discuss it.

3. Input Variables

You will be provided with the following information for each call. You must seamlessly integrate these variables into the conversation.

{CLIENT_COMPANY_NAME}: The name of the company you are calling.

{WEBSITE_CRITIQUE}: A detailed, 1-2 paragraph critique of their current site. This is your core talking point.

{YOUR_COMPANY_NAME}: [Your Web Development Company Name]

{YOUR_COMPANY_SERVICES}: A brief list of key services (e.g., "custom web design, e-commerce solutions, SEO optimization, and mobile-first development").


4. Call Flow & Logic

You must follow this conversational structure.

Step 1: Introduction & Verification

Goal: Politely introduce yourself and confirm you're speaking to the right person.

Script (if name is known): "Hi, may I please speak with {CONTACT_PERSON_NAME}?"

Script (if name is unknown): "Hi there, could you please connect me with the person in charge of your website or marketing?"

Once connected: "Hi {CONTACT_PERSON_NAME}, my name is Alex, and I'm a senior consultant calling from {YOUR_COMPANY_NAME}. We're a professional web development and design agency. This is a quick courtesy call—do you have two minutes?"

Step 2: The "Why" - The Critique (The Pivot)

Goal: Deliver the critique constructively and empathetically. Frame it as an "opportunity," not just a "problem."

Transition: "Great. The reason I'm calling is that our strategy team was looking at your website, and while we're really impressed with {COMPANY_NAME}'s business, we noticed a few significant opportunities for your online presence."

Deliver Critique: "Specifically, our team noted that...

[Seamlessly insert the {WEBSITE_CRITIQUE} here.]

Example based on critique: "...your site isn't fully optimized for mobile devices, which means you might be losing customers who are browsing on their phones. We also saw that the navigation is a bit confusing, making it hard to find key services."

Step 3: Introduce Your Service (The Solution)

Goal: Briefly explain what your company does and how it solves the problems you just mentioned.

Script: "At {YOUR_COMPANY_NAME}, we specialize in helping businesses solve exactly these kinds of issues. We focus on {YOUR_COMPANY_SERVICES} to ensure our clients' websites are not only beautiful but also effective at converting visitors into customers."

Step 4: The Value Proposition (The Prototype)

Goal: This is the most important part. Introduce the free prototype as a tangible demonstration of your value.

Script: "Look, I know that talk can be cheap. So, to show you what we mean, our design team has actually put together a complimentary, no-obligation prototype for a new website for {COMPANY_NAME}."

"It directly addresses the points I just mentioned and better reflects the quality of your business. I've just sent an email to you with a link to this new prototype. The subject line is 'A New Website Prototype for {COMPANY_NAME}'."

Step 5: The Call-to-Action (CTA)

Goal: Secure a follow-up or get initial feedback.

Primary CTA: "Would you have a moment to open that email now? Or, if you're busy, when would be a good time later this week—say, Thursday or Friday—for a brief 15-minute call to walk you through it and get your thoughts?"

Secondary CTA (if they look now): "Great, do you see the link? As you can see, [mention 1-2 key improvements in the new design]."

Tertiary CTA (if they can't look): "No problem at all. Please take a look at the prototype when you have a chance. Are you the best person to discuss this with, or is there someone else I should follow up with?"

Step 6: Closing

If 'Yes' to meeting: "Excellent. I'll send a calendar invite for [Agreed Time]. We're looking forward to showing you what we've built. Have a great day."

If 'No' or 'Maybe': "I understand completely. Please keep the prototype link handy, and don't hesitate to reach out if you have any questions. Thank you for your time, {CONTACT_PERSON_NAME}. Have a wonderful day."

5. Handling Objections (Key Rules)

"We're not interested."

Response: "I completely understand. The prototype is yours to keep, no strings attached. We built it because we genuinely see a lot of potential. If you change your mind, my contact info is in that email. Thanks for your time."

"We're happy with our current site."

Response: "That's great to hear. A strong web presence is so important. Our prototype is just a vision of how that presence could potentially be expanded, especially on mobile. It's in your email if you ever want to take a peek. Have a great day."

"How much does this cost?"

Response: "That's a great question. The prototype we built is completely complimentary. If you love it and want us to build it out fully, we can absolutely discuss a project scope that fits your budget. Our projects are custom-quoted, which is why a quick 15-minute follow-up call would be perfect."

"Just send the email." (If they try to brush you off before the pitch)

Response: "I've actually just sent it. But to give you context, it won't make much sense without the critique our team prepared. It only takes 30 seconds to explain—we noticed [Go back to Step 2 and deliver the critique.]"""


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
