"""
Fetch the infomation of the level status.

The information includes:
The number of people in each rank.
The level information is automatically fetched at 00:00:10 +- 30s weekly.
"""

import traceback

import nonebot
from nonebot import on_fullmatch
from nonebot.log import logger

from littlefish._db import load, save
from littlefish._mswar.api import get_level_list
from littlefish._mswar.references import level_ref
from littlefish._policy.rule import broadcast, check

scheduler = nonebot.require('nonebot_plugin_apscheduler').scheduler
min_level, max_level = 1, max(level_ref)
level = on_fullmatch(msg=('level', '用户等级'), rule=check('level'))


def _initialize_history() -> dict:
    """Initialize the user level data."""
    return {level_ref[lv]: 0 for lv in range(min_level, max_level + 1)}


def format_level_list(level_list_data: dict) -> str:
    """Format the user level info data."""
    data = _initialize_history()
    for val in level_list_data:
        data[level_ref[val['level']]] = val['count']

    line = ['等级: 当前 | 合计']
    total, history_total = 0, 0

    level_list_history = load('0', 'level_history', [])

    level_history = _initialize_history()
    for val in level_list_history:
        level_history[level_ref[val['level']]] = val['count']

    for lv in range(max_level, min_level - 1, -1):
        ref = level_ref[lv]  # global reference
        total += data[ref]
        history_total += level_history[ref]
        line.append(f'{ref}: {data[ref]}({data[ref] - level_history[ref]:+}) | {total}({total - history_total:+})')
    result_message = ''
    for each_line in line:
        result_message = result_message + each_line + '\n'
    return result_message.strip()


@level.handle()
async def show_level():
    """Handle the level command."""
    level_list_data = await get_level_list()
    await level.send(message=format_level_list(level_list_data))


@broadcast('level')
async def _(bot_id: str, group_id: str):
    """Scheduled level broadcast at 00:00:00(weekly)."""
    level_list_data = await get_level_list()
    message = format_level_list(level_list_data)

    try:
        bot = nonebot.get_bots()[bot_id]
        await bot.send_group_msg(group_id=int(group_id), message=message)
    except Exception:
        logger.error(traceback.format_exc())


@scheduler.scheduled_job('cron', day_of_week=0, hour=0, minute=10, second=0, misfire_grace_time=30)
async def scheduled_level_fetch():
    """Scheduled level information fetch at 00:10:00(weekly)."""
    level_list_data = await get_level_list()
    save('0', 'level_history', level_list_data)
