import PyTouchBar
import asyncio
from pyslobs import ScenesService, connection, StreamingService
import threading
import pygame

idlist = []
nameList = []
buttonList = []

async def setbtncolor(id):
    for button in buttonList:
        btnid = idlist[nameList.index( button.title )]
        if id == btnid:
            button.color = PyTouchBar.Color.green
        else:
            button.color = PyTouchBar.Color.red

async def onSceneChanged(k,v):
    await setbtncolor(v["id"])

async def onStreamingStatusChanged(k,v):
    if v == "live":
        golive_btn.title = "Stop Streaming"
        golive_btn.color = PyTouchBar.Color.green
        golive_btn.image = "NSTouchBarRecordStopTemplate"
    elif v == "offline":
        golive_btn.title = "Go Live"
        golive_btn.color = PyTouchBar.Color.red
        golive_btn.image = "NSTouchBarRecordStartTemplate"
    elif v == "starting":
        golive_btn.title = "Starting"
        golive_btn.color = PyTouchBar.Color.yellow
        golive_btn.image = "NSPlayTemplate"
    elif v == "ending":
        golive_btn.title = "Ending"
        golive_btn.color = PyTouchBar.Color.yellow
        golive_btn.image = "NSPauseTemplate"

def asynceventcaller(fn,id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if id == "":
        loop.run_until_complete(fn())
    else:
        loop.run_until_complete(fn(id))
    loop.close()

def onTouchBarButtonClicked(button):
    id = idlist[nameList.index( button.title )]
    _thread = threading.Thread( target= asynceventcaller, args=(sceneService.make_scene_active,id,) )
    _thread.start()

def onStreamControl(button):
    _thread = threading.Thread( target= asynceventcaller, args=(streamService.toggle_streaming,"",) )
    _thread.start()

async def list_all_scenes(conn):
    global sceneService
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

    await sceneService.scene_switched.subscribe(onSceneChanged)

    global streamService
    streamService = StreamingService(conn)
    stream_status = await streamService.get_model()
    
    await streamService.streaming_status_change.subscribe(onStreamingStatusChanged)    
    
    golivebtn_title = "Stop Streaming"
    golivebtn_color = PyTouchBar.Color.green
    golivebtn_image = "NSTouchBarRecordStopTemplate"
    if "streaming_status='offline'" not in stream_status:
        golivebtn_title = "Go Live"
        golivebtn_color = PyTouchBar.Color.red
        golivebtn_image = "NSTouchBarRecordStartTemplate"
    
    global golive_btn
    golive_btn = PyTouchBar.TouchBarItems.Button(title=golivebtn_title, color=golivebtn_color, action=onStreamControl, image = golivebtn_image)
    scenepopover = PyTouchBar.TouchBarItems.Popover(buttonList, title="Scene Controller")
    PyTouchBar.set_touchbar([golive_btn, scenepopover])

async def mainloop(conn):
    await asyncio.sleep(5)
    pygame.init()
    surface = pygame.display.set_mode((200,10))
    PyTouchBar.prepare_pygame()
    pygame.display.set_caption('TouchBarStreamDeck')
    while True:
            await asyncio.sleep(0.03)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    await conn.close()
                    asyncio.get_event_loop().stop()
                    asyncio.get_running_loop().stop()
                    exit()
                    break

async def main():
    global conn
    token = "streamlabs-remote-control-token" #streamlabs obs -> remotecontrol -> show details -> api key
    conn = connection.SlobsConnection(token, "192.168.1.24", 59650) #streaming pc local ip
    await asyncio.gather(
            conn.background_processing(),
            list_all_scenes(conn),
            mainloop(conn)
            )
    exit()

asyncio.run(main())
