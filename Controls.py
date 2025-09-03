import pygame

joysticks = {}

#------------------------SETUP----------------------------
def controlsSetup():
    pygame.init()

    
#---------------------HOTSWAP SUPPORT---------------------
def checkHotswap():
	for event in pygame.event.get():
			#hotswapping
		if event.type == pygame.JOYDEVICEADDED:#setup new joystick if one is connected
			joy = pygame.joystick.Joystick(event.device_index)
			joysticks[joy.get_instance_id()] = joy
			print("New Controller")
			
		if event.type == pygame.JOYDEVICEREMOVED:#remove joystick if one is disconnected
			del joysticks[event.instance_id()]
			print("Controller Lost")


#--------------------INPUTS AND OUTPUTS-----------------------
#control ids are found on pygame documentation

#right joystick
def joyRightUpDown():
    for joystick in joysticks.values():
        return joystick.get_axis(4)

def joyRightLeftRight():
    for joystick in joysticks.values():
        return joystick.get_axis(3)

def joyRightButton():
    for joystick in joysticks.values():
        return joystick.get_button(9)


#left joystick
def joyLeftUpDown():
    for joystick in joysticks.values():
        return joystick.get_axis(1)

def joyLeftLeftRight():
    for joystick in joysticks.values():
        return joystick.get_axis(0)

def joyLeftButton():
    for joystick in joysticks.values():
        return joystick.get_button(8)

#triggers
def triggerRight():
    for joystick in joysticks.values():
        return joystick.get_axis(5)

def triggerLeft():
    for joystick in joysticks.values():
        return joystick.get_axis(2)

#buttons
def buttonA():
    for joystick in joysticks.values():
        return joystick.get_button(0)

def buttonB():
    for joystick in joysticks.values():
        return joystick.get_button(1)

def buttonX():
    for joystick in joysticks.values():
        return joystick.get_button(2)

def buttonX():
    for joystick in joysticks.values():
        return joystick.get_button(3)

def destroy():
    pygame.quit()



    
