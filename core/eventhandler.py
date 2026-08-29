from inspect import signature
from typing import Callable
import pygame, sys
import weakref

def function_to_string(*functions: tuple[Callable]):
    str_functions = []
    for f in functions:
        if f is None: str_functions.append('NONE') # if there is no function, the string is NONE
        
        # Adds a function the the list of string functions in form module.func(params)
        elif f.__module__  == '__main__':
            str_functions.append(f'{f.__name__}{signature(f)}')
        else:
            str_functions.append(f'{f.__module__}.{f.__name__}{signature(f)}')
    
    if len(functions) == 1: return str_functions[0]
    else: return str_functions

class EventHandler:
    instances = weakref.WeakSet() # keeps a list of currently open event handlers
    pygame_key_to_string = {}

    # Define an EventHandler object with an associated keybind and event (function) #
    def __init__(self, keybind: int = None, *kwargs,
                 keyup: Callable = None, keyup_params: list = None, keydown: Callable=None, keydown_params: list = None,
                 quit: Callable=None, quit_params: list=None):
        if isinstance(keybind, str):
            self.keybind = pygame.key.key_code(keybind) # for string inputs
        elif isinstance(keybind, int):
            self.keybind = keybind # for pygame key inputs
        elif keybind == None:
            pass
        else:
            raise TypeError("Keybind must be of type str or a pygame key of type int")
        self.keyup = keyup
        self.keydown = keydown
        self.keydown_params = keydown_params

        self.quit = quit
        EventHandler.instances.add(self) # keeps track of all the instances of EventHandlers
    
    # UTILITY METHODS #
    # String and representation of an EventHandler object #
    def __str__(self):
        # defines the str representation of the function as func(params)
        keyup_str, keydown_str, quit_str = function_to_string(self.keyup, self.keydown, self.quit)

        return f"'{self.get_key_name()}' --> keyup: {keyup_str}, keydown: {keydown_str}, quit: {quit_str}"
    
    def __repr__(self): return self.__str__()
    
    def get_key_name(self):
        if self.keybind is None: return "NONE"
        else: return pygame.key.name(self.keybind) # get the name of the associated key
    
    # FUNCTIONAL METHODS #
    # Handle an event #
    @classmethod
    def handle(cls, global_event: list[pygame.event.Event]):
        for event in global_event:
            match event.type:
                case pygame.KEYDOWN: cls.keydown(event)
                case pygame.KEYUP: cls.keyup(event)
                case pygame.QUIT:
                    cls.quit(event)
                    pygame.quit()
                    sys.exit()
    
    @classmethod
    def keydown(cls, event: pygame.event.Event):
        for instance in cls.instances:
            if event.key == instance.keybind and not instance.keydown is None:
                instance.keydown(*instance.keydown_params)
    
    @classmethod
    def keyup(cls, event: pygame.event.Event):
        for instance in cls.instances:
            if event.key == instance.keybind and not instance.keyup is None:
                instance.keyup()
          
    @classmethod      
    def quit(cls, event: pygame.event.Event):
        for instance in cls.instances and not instance.quit is None:
            instance.quit()
