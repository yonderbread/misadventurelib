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
    print(current_room.current_state.description)


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
