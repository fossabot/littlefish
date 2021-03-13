"""
A policy module which will handle the rules of the commands.

The module will load the policy file by the location.
About the policy file:
The policy file should be a valid json file, which contains the
following information. Please note that the json file should not
contain any annotations.
{
    "bot_id": {
        // config for this bot
        "group_id": {
            // config for this group
            "command": {
                "+": [1, 2, 3], // this should be the whitelist
                "-": [4, 5, 6], // this should be the blacklist
                "@": true // this should be the boardcast option
            }
            // config for another command
        }
        "another_group_id": {
            // config for another group
        }
    }
    "another_bot_id": {
        "another_group_id": {
            // config for another group
        }
        // config for another group
    }
    // config for another bot
}

How is it works?
The policy checker will allow/deny a command by several key-value
matches. On the bot/group level, if the bot/group key doesn't exist,
the checker will allow the command; on the whitelist/blacklist level,
if the sender appears in the whitelist AND doesn't appear in the black-
list, the checker will allow the command, or it will block the command.
Please note that, when a whitelist/blacklist key doesn' exist, the
checker will assume the whitelist/blacklist doesn't exist and allow
the command on the whitelist/blacklist level. About the boardcasting
feature, you need to enable it manually in the configuration, or it
is disabled by default. About the empty feature, you can enforce 0
arguments in a command.

How to use?
The checker is wrapped as a nonebot.rule.Rule, you can use it in any
commands containing the keyword argument 'rule'. The policy config will
be reloaded on every startup of the bot itself. The boardcast is wrapped
as a normal decorator, you need to decorate the function only.

Additional features:
* Create/Revoke a temporary policy: this will create/revoke a temporary
policy into the memory, but not saved into the policy file on disk.
"""

import nonebot
import json
import os
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent
from nonebot.rule import Rule
from .config import Config

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())
policy_config_location = os.path.join(os.getcwd(), plugin_config.policy_config_location)

try:
    with open(policy_config_location, 'r', encoding='utf-8') as f:
        policy_config = json.loads(f.read())
        logger.info('Policy file is loaded ...')
        logger.debug('Policy control data: %s' % policy_config)
except Exception:
    policy_config = {}
    logger.warning('Failed to load policy file, using empty policy file ...')


def check(command_name: str, event_type: Event = GroupMessageEvent) -> Rule:
    """Check the policy of each command by name."""
    _name = command_name

    async def _check(bot: Bot, event: Event, state: dict) -> bool:
        """A rule wrapper for each command."""
        logger.debug('Checking command: [%s].' % _name)
        if not isinstance(event, event_type):
            return False

        bid = f'{event.self_id}'
        gid = f'{event.group_id}'
        sid = event.user_id
        try:
            # Check the whitelist policy by name.
            in_whitelist = ('+' not in policy_config[bid][gid][_name] or sid in policy_config[bid][gid][_name]['+'])

            # Check the blacklist policy by name.
            not_in_blacklist = ('-' not in policy_config[bid][gid][_name] or sid not in policy_config[bid][gid][_name]['-'])

            # Combine the whitelist and blacklist together
            return in_whitelist and not_in_blacklist
        except Exception:
            return True

    return Rule(_check)


def empty() -> bool:
    """Ensure the arguments of a command is empty."""

    async def _empty(bot: Bot, event: Event, state: dict) -> bool:
        """A rule wrapper for each command."""
        logger.debug('Checking empty arguments ...')
        try:
            return str(event.message).strip() == state['_prefix']['raw_command']
        except Exception:
            return False

    return Rule(_empty)


def boardcast(command_name: str) -> bool:
    """Check the policy of each boardcast by name."""
    _name = command_name
    allowed = [
        (bid, gid)
        for bid in policy_config.keys()
        for gid in policy_config[bid].keys()
        if _name in policy_config[bid][gid] and '@' in policy_config[bid][gid][_name] and policy_config[bid][gid][_name]['@']
    ]

    def wrapper(func):
        """A wrapper for the checker."""

        async def _check() -> None:
            """Check the policy of the boardcast."""
            logger.debug('Checking boardcast: [%s].' % _name)
            await func(allowed)

        return _check

    return wrapper


def create(command_name: str, bot_id: str, group_id: str, policy_content: dict):
    """Create a temporary policy into the memory."""
    policy_config.setdefault(bot_id, {})
    policy_config[bot_id].setdefault(group_id, {})
    policy_config[bot_id][group_id].setdefault(command_name, {})
    policy_config[bot_id][group_id][command_name] = policy_content
    logger.debug('A temporary policy [%s] was added to the policy control' % command_name)


def revoke(command_name: str, bot_id: str, group_id: str):
    """Revoke a temporary policy from the memory."""
    try:
        policy_config[bot_id][group_id].pop(command_name)
        logger.debug('A temporary policy [%s] was revoked from the policy control' % command_name)
    except Exception:
        logger.debug('Failed to revoke the temporary policy, the policy may be revoked already.')
