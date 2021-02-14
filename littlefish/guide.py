"""
A simple guide for reference.

A guide, a backup guide, an app package link and a minesweeping guide link
is included here.
The command requires to be invoked in groups.
"""

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from littlefish._policy import check, empty

guide = on_command(cmd='guide', aliases={'指南'},
                   rule=check('guide') & empty())

backup_guide = on_command(cmd='backupguide', aliases={'备用指南'},
                          rule=check('guide') & empty())

get_package = on_command(cmd='getpackage', aliases={'安装包', '安装链接'},
                         rule=check('guide') & empty())

ms_guide = on_command(cmd='msguide', aliases={'扫雷指南'},
                      rule=check('guide') & empty())

push_line = on_command(cmd='pushline', aliases={'推送线'},
                       rule=check('guide') & empty())


@guide.handle()
async def guide(bot: Bot, event: Event, state: dict):
    """Show guide page for littlefish."""
    guide_link = "用户指南详见: https://t0nyx1ang.github.io/littlefish/"
    await bot.send(event=event, message=guide_link, at_sender=True)


@backup_guide.handle()
async def guide(bot: Bot, event: Event, state: dict):
    """Show backup guide page for littlefish."""
    backup_link = "备用链接: https://github.com/T0nyX1ang/littlefish"
    await bot.send(event=event, message=backup_link, at_sender=True)


@get_package.handle()
async def getpackage(bot: Bot, event: Event, state: dict):
    """Show app package package."""
    app_link = "下载链接(小米浏览器需选择源文件下载): http://tapsss.com"
    await bot.send(event=event, message=app_link, at_sender=True)


@ms_guide.handle()
async def msguide(bot: Bot, event: Event, state: dict):
    """Show minesweeping guide."""
    ms_guide_link = "扫雷指南详见: http://tapsss.com/?post=189646"
    await bot.send(event=event, message=ms_guide_link, at_sender=True)


@push_line.handle()
async def push_line(bot: Bot, event: Event, state: dict):
    """Show minesweeping guide."""
    ms_guide_link = "纪录推送标准: http://tapsss.com/?post=388962"
    await bot.send(event=event, message=ms_guide_link, at_sender=True)
