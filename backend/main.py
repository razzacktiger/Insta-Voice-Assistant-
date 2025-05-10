from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from .prompts import INSTRUCTIONS
from livekit.plugins import (
    openai,
    noise_cancellation,
    silero
)

# Import tool functions from api.py
from .api import (
    get_user_account_info,
    answer_from_company_kb,
    summarize_interaction_for_next_session
)

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=INSTRUCTIONS,
            functions=[
                get_user_account_info,
                answer_from_company_kb,
                summarize_interaction_for_next_session
            ]
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    # TODO: Re-evaluate how to get the specific user_firebase_id for the session.
    # The JobContext (ctx) itself does not have a direct 'participant' attribute or 'userdata' dict.
    # User identity will likely be determined when the agent processes an event
    # from a specific participant in the room, or if passed via job metadata.

    room_sid = await ctx.room.sid  # Await the sid
    print(
        f"Agent session starting for room: {ctx.room.name} (SID: {room_sid})")
    # Removed placeholder for ctx.userdata as it's not directly on JobContext

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="alloy"
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
