from fastapi import APIRouter

from core.wisdom_injector import get_wisdom_briefing

router = APIRouter(prefix="/api/wisdom", tags=["wisdom"])


@router.get("")
async def wisdom(task_description: str, api_key_hash: str):
    return await get_wisdom_briefing(task_description=task_description, api_key_hash=api_key_hash)
