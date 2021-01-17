from core import *
from web.index import run_server


@app.receiver("GroupMessage")
async def event_gm(app: Mirai, message: MessageChain, group: Group, member: Member,source: Source):
    await run_command("group", {
        Mirai: app,
        Group: group,
        Member: member,
        MessageChain: message,
        Source: source
    })

if __name__ == "__main__":
    # Chart Server
    Thread(target=run_server).start()
    # Mirai-Python app
    app.run()
