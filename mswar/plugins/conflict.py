from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER, GROUP
from nonebot.log import logger
from .core import is_enabled
from .global_value import CURRENT_CONFLICT_COUNTER, CURRENT_ENABLED
import nonebot

@on_command('conflict', aliases=('打架', '嘭[CQ:face,id=146]'), permission=SUPERUSER | GROUP, only_to_me=False)
async def conflict(session: CommandSession):
    if not is_enabled(session.event):
        session.finish()

    group_id = session.event['group_id']
    if group_id not in CURRENT_CONFLICT_COUNTER:
        CURRENT_CONFLICT_COUNTER[group_id] = 0
    if CURRENT_CONFLICT_COUNTER[group_id] < 5:
        CURRENT_CONFLICT_COUNTER[group_id] += 1
        await session.send('小爆')

@nonebot.scheduler.scheduled_job('cron', hour='0,12', minute=0, second=0, misfire_grace_time=30)
async def _():
    for group_id in CURRENT_ENABLED.keys():
        if CURRENT_ENABLED[group_id]:
            CURRENT_CONFLICT_COUNTER[key] = 0
    logger.info('The PONG counter is resumed now ...')
