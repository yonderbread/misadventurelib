# misadventurelib
>**A fork of adventurelib**

This library aims to use a lot of the base functionality from the `adventurelib` library, but add a lot of useful features
to easily make things in your text adventures more dynamic. One of the main issues I found while making games with `adventurelib`
was that when you created a room, added directions and such, it was a real pain to make different room states that you could
switch between. Here's a quick example of how `misadventurelib` addresses this problem.

```py
from misadventure.lib import *
from misadventure.room import RoomState, Room

livingroom = Room()
livingroom.lights_on = True

livingroom_lights_on = RoomState(
    '''
You are in your livingroom. The lights are on.
''')
livingroom_lights_on.add_names('livingroom')

livingroom_lights_off = RoomState('''
You are in your livingroom. It is pitch black.
You can't see a thing!
''')
livingroom_lights_off.add_names('livingroom')

livingroom.add_state('lights_off', livingroom_lights_off)
livingroom.add_state('lights_on', livingroom_lights_on)
livingroom.set_state('lights_on')

current_room = livingroom


@when('say SOMETHING')
def say_stuff(something):
    print(f'You say, "{something}".')


@when('look')
def look():
    print(str(current_room))


@when('turn THING STATE')
def turn_on_off(thing, state):
    if thing == 'light':
        if livingroom.lights_on:
            if state == 'on':
                print('The lights are already on!')
            elif state == 'off':
                current_room.set_state('lights_off')
                current_room.lights_on = False
                print('You turned off the lights.')
            else:
                print('What?')
        else:
            if state == 'on':
                current_room.set_state('lights_on')
                current_room.lights_on = True
                print('You turn the lights back on, much better!')
            elif state == 'off':
                print('The lights are already off!')
            else:
                print('What?')
    else:
        print(f'I don\'t know what {thing} is!')
    look()

start(help=False)
```

*And here's the result..*
```bash
> look
You are in your livingroom. The lights are on.

> turn light off
You turned off the lights.
You are in your livingroom. It is pitch black.
You can't see a thing!

> look
You are in your livingroom. It is pitch black.
You can't see a thing!

> turn light on
You turn the lights back on, much better!
You are in your livingroom. The lights are on.
```

## More features and documentation coming soon!

### TODO:
- Add multiple transports for text adventures so that they aren't limited to just the terminal
- Add Discord.py utils so you can play your text adventures in Discord!
