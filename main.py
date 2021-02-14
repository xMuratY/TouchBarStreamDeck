import PyTouchBar
import asyncio
from PyTouchBar.constants import Color
from pyslobs import SlobsConnection, ScenesService, connection
from tkinter import *
import threading

root = Tk()
PyTouchBar.prepare_tk_windows(root)

idlist = []
nameList = []
buttonList = []

def appmain():
    PyTouchBar.set_touchbar(buttonList)
    root.mainloop()

async def setbtncolor(id):
    for button in buttonList:
        btnid = idlist[nameList.index( button.title )]
        if id == btnid:
            button.color = PyTouchBar.Color.green
        else:
            button.color = PyTouchBar.Color.red

async def setscene(selid):
    sceneService = ScenesService(conn)
    #setbtncolor(selid)
    await sceneService.make_scene_active(selid)
    
def setscenecaller(id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setscene(id))
    loop.close()

def onTouchBarButtonClicked(button):
    id = idlist[nameList.index( button.title )]
    _thread = threading.Thread( target= setscenecaller, args=(id,) )
    _thread.start()

async def list_all_scenes(conn):
    sceneService = ScenesService(conn)
    scenes = await sceneService.get_scenes()
    active_sceneid = await sceneService.active_scene_id()
    for scene in scenes:
        idlist.append(scene.id)
        nameList.append(scene.name)
        btnColor = PyTouchBar.Color.red
        if ( scene.id == active_sceneid ):
            btnColor = PyTouchBar.Color.green
        buttonList.append( PyTouchBar.TouchBarItems.Button(title = scene.name, action = onTouchBarButtonClicked, color=btnColor) )

    appmain()

async def main():
    global conn
    token = "streamlabs-remote-control-token" #streamlabs obs -> remotecontrol -> show details -> api key
    conn = connection.SlobsConnection(token, "192.168.1.24", 59650) #streaming pc local ip
    await asyncio.gather(
            conn.background_processing(),
            list_all_scenes(conn),
            )
    await conn.close()

asyncio.run(main())
