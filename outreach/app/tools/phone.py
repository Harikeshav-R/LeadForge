from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import OpenAILLMContext
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.gemini_multimodal_live.gemini import GeminiMultimodalLiveLLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from starlette.websockets import WebSocket
from twilio.rest import Client

from app.core import Config


async def phone_call(websocket_client: WebSocket, stream_sid: str, call_sid: str, account_sid: str, auth_token: str,
                     system_instruction: str):
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
        system_instruction=system_instruction,
        voice_id="Aoede",  # Voices: Aoede, Charon, Fenrir, Kore, Puck
        transcribe_user_audio=True,  # Enable speech-to-text for user input
        transcribe_model_audio=True,  # Enable speech-to-text for model responses
    )

    context = OpenAILLMContext(

        [{"role": "user", "content": "Say hello."}],
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


def start_phone_call(account_sid: str, auth_token: str, from_phone_number: str, to_phone_number: str):
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        twiml=open("templates/streams.xml").read(),
        to=to_phone_number,
        from_=from_phone_number
    )

    return True
