from core import *

# Chart Server
os.popen(f'start python web/index.py', 'r')

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
    app.run()
