import asyncio
from .automation_system import *
from .automation_web import *
from .automation_misc import *

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("googlesearch"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("googlesearch"))
            funcs.append(fun)
        elif command.startswith("youtubesearch"):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtubesearch "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(system, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No Functions found for {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
