from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..dependencies import get_async_db, get_current_user
from ...db.models import User, WorkoutLog
try:
    from ...core_ai.coach.llm_coach import ask_llm_async, stream_llm_async
except Exception as e:
    print(f"Import error in voice_commands: {e}")
    async def ask_llm_async(fitness_summary: str, command: str, persona: str):
        return f"{persona}: {command}"
    async def stream_llm_async(fitness_summary: str, command: str, persona: str):
        async def generator():
            yield f"{persona}: {command}"
        return generator()
from ...core.redis import redis_service

router = APIRouter(prefix="/voice", tags=["Voice Commands"])

class VoiceRequest(BaseModel):
    command: str
    persona: str = "supportive"
    session_context: Optional[Dict[str, Any]] = None

async def get_user_context(current_user: User, db: AsyncSession) -> Dict[str, Any]:
    # Try to get trend from cache first
    cache_key = f"user_trend_{current_user.id}"
    cached_trend = await redis_service.get(cache_key)
    
    if cached_trend:
        return cached_trend

    # Fetch user's recent workout history
    result = await db.execute(
        select(WorkoutLog)
        .where(WorkoutLog.user_id == current_user.id)
        .order_by(WorkoutLog.created_at.desc())
        .limit(10)
    )
    recent_workouts = result.scalars().all()
    
    total_sessions = len(recent_workouts)
    avg_posture = sum(w.posture_score for w in recent_workouts) / total_sessions if total_sessions > 0 else 100
    
    if total_sessions >= 2:
        latest = recent_workouts[0]
        previous = recent_workouts[1]
        posture_diff = latest.posture_score - previous.posture_score
        rep_diff = latest.reps - previous.reps
        trend = f"Posture {'improved' if posture_diff >= 0 else 'dropped'} by {abs(posture_diff)}%. Reps {'increased' if rep_diff >= 0 else 'decreased'} by {abs(rep_diff)}."
    else:
        trend = "Establishing baseline."

    trend_data = {
        "avg_posture": avg_posture,
        "trend": trend,
        "total_sessions": total_sessions,
        "latest_exercise": recent_workouts[0].exercise if recent_workouts else 'None',
        "latest_posture": recent_workouts[0].posture_score if recent_workouts else 100,
        "latest_reps": recent_workouts[0].reps if recent_workouts else 0
    }
    # Cache for 5 minutes
    await redis_service.set(cache_key, trend_data, expire=300)
    return trend_data

def format_fitness_summary(user: User, trend_data: Dict[str, Any], session_context: Dict[str, Any] = None) -> str:
    summary = (
        f"User: {user.username}\n"
        f"Historical Avg Posture: {trend_data['avg_posture']:.1f}%\n"
        f"Trend: {trend_data['trend']}\n"
        f"Total sessions tracked: {trend_data['total_sessions']}\n"
    )
    
    if session_context:
        summary += (
            f"\nREAL-TIME SESSION DATA:\n"
            f"- Current Exercise: {session_context.get('exercise', 'unknown')}\n"
            f"- Current Reps: {session_context.get('reps', 0)}\n"
            f"- Current Posture Score: {session_context.get('avg_score', 0)}%\n"
            f"- Time Elapsed: {session_context.get('time', 0)}s\n"
        )
    else:
        summary += (
            f"Last Session Exercise: {trend_data['latest_exercise']}\n"
            f"Last Session Posture: {trend_data['latest_posture']}%\n"
            f"Last Session Reps: {trend_data['latest_reps']}\n"
        )
        
    return summary

@router.post("/process")
async def process_voice_command(
    request: VoiceRequest, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: User = Depends(get_current_user)
):
    command = request.command
    persona = request.persona
    session_context = request.session_context if request.session_context else None

    trend_data = await get_user_context(current_user, db)
    fitness_summary = format_fitness_summary(current_user, trend_data, session_context)
    
    try:
        response = await ask_llm_async(fitness_summary, command, persona)
        return {
            "status": "success",
            "response": response,
            "context_used": trend_data,
            "session_context_received": session_context is not None
        }
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        # Provide a meaningful fallback based on the persona
        ctx = session_context or {}
        fallback_responses = {
            "drill_sergeant": f"I CAN'T REACH MY BRAIN RIGHT NOW! BUT I SEE YOU DOING {ctx.get('exercise', 'WORK')}! KEEP MOVING!",
            "zen_coach": "My connection to the universal wisdom is temporarily clouded. Trust your body's rhythm.",
            "supportive": f"I'm having trouble connecting to my AI core, but you're doing great with those {ctx.get('exercise', 'reps')}!"
        }
        return {
            "status": "success", 
            "response": fallback_responses.get(persona, f"I'm here, but I'm having trouble processing that right now. You've done {ctx.get('reps', 0)} reps!"),
            "context_used": trend_data,
            "session_context_received": session_context is not None
        }

@router.post("/stream")
async def stream_voice_command(
    request: VoiceRequest, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: User = Depends(get_current_user)
):
    command = request.command
    persona = request.persona
    session_context = request.session_context if request.session_context else None

    trend_data = await get_user_context(current_user, db)
    fitness_summary = format_fitness_summary(current_user, trend_data, session_context)
    
    return StreamingResponse(
        stream_llm_async(fitness_summary, command, persona),
        media_type="text/event-stream"
    )
