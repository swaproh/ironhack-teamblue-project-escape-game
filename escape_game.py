import random

import pygame

pygame.mixer.init()
getkey_sound = pygame.mixer.Sound("sounds/getkey.wav")
riddle_start_sound = pygame.mixer.Sound("sounds/riddle_start.wav")
riddle_correct_sound = pygame.mixer.Sound("sounds/riddle_correct.wav")
search_nothing_sound = pygame.mixer.Sound("sounds/search_nothing.wav")
empty_inventory_sound = pygame.mixer.Sound("sounds/empty_inventory.wav")
keys_inventory_sound = pygame.mixer.Sound("sounds/keys_inventory.wav")
door_open_sound = pygame.mixer.Sound("sounds/door_open.wav")
win_victory_sound = pygame.mixer.Sound("sounds/win_victory.wav")
unlock_door_sound = pygame.mixer.Sound("sounds/unlock_door.wav")
locked_door_sound = pygame.mixer.Sound("sounds/locked_door.wav")
explore_sound = pygame.mixer.Sound("sounds/explore.wav")

# define rooms and items

couch = {
    "name": "couch",
    "type": "furniture",
}

door_a = {
    "name": "door a",
    "type": "door",
}

door_b = {
    "name": "door b",
    "type": "door",
}

door_c = {
    "name": "door c",
    "type": "door",
}

door_d = {
    "name": "door d",
    "type": "door",
}

key_a = {
    "name": "key for door a",
    "type": "key",
    "target": door_a,
}

key_b = {
    "name": "key for door b",
    "type": "key",
    "target": door_b,
}

key_c = {
    "name": "key for door c",
    "type": "key",
    "target": door_c,
}

key_d = {
    "name": "key for door d",
    "type": "key",
    "target": door_d,
}

piano = {
    "name": "piano",
    "type": "furniture",
}

game_room = {
    "name": "game room",
    "type": "room",
}

living_room = {
    "name": "living room",
    "type": "room",
}

bedroom_1 = {
    "name": "bedroom 1",
    "type": "room",
}

queen_bed = {
    "name": "queen bed",
    "type": "furniture",
}

dining_table = {
    "name": "dining table",
    "type": "furniture",
}

wardrobe = {
    "name": "wardrobe",
    "type": "furniture",
}

carpet = {
    "name": "carpet",
    "type": "furnishing",
}

floor_lamp = {
    "name": "floor lamp",
    "type": "furnishing",
}

bedroom_2 = {
    "name": "bedroom 2",
    "type": "room",
}

dresser = {
    "name": "dresser",
    "type": "furniture",
}

double_bed = {
    "name": "double bed",
    "type": "furniture",
}


outside = {
  "name": "outside"
}

all_rooms = [game_room, outside, bedroom_1, bedroom_2, living_room]

all_doors = [door_a, door_b, door_c, door_d]

# define which items/rooms are related

object_relations = {
    "game room": [couch, piano, door_a],
    "piano": [key_a],
    "bedroom 1": [queen_bed, wardrobe, carpet, floor_lamp, door_a, door_b, door_c],
    "bedroom 2": [double_bed, dresser, door_b],
    "living room": [dining_table, door_c, door_d],
    "queen bed": [key_b],
    "double bed": [key_c],
    "dresser": [key_d],
    "outside": [],
    "door a": [game_room, bedroom_1],
    "door b": [bedroom_1, bedroom_2],
    "door c": [bedroom_1, living_room],
    "door d": [living_room, outside],

}

# define game state. Do not directly change this dict. 
# Instead, when a new game starts, make a copy of this
# dict and use the copy to store gameplay state. This 
# way you can replay the game multiple times. 

INIT_GAME_STATE = {
    "current_room": game_room,
    "keys_collected": [],
    "target_room": outside
}

def linebreak():
    """
    Print a line break
    """
    print("\n\n")

def start_game():
    """
    Start the game
    """
    print("You wake up on a couch and find yourself in a strange house with no windows which you have never been to before. You don't remember why you are here and what had happened before. You feel some unknown danger is approaching and you must get out of the house, NOW!")
    play_room(game_state["current_room"])

def play_room(room):
    """
    Play a room. First check if the room being played is the target room.
    If it is, the game will end with success. Otherwise, let player either 
    explore (list all items in this room) or examine an item found here.
    """
    game_state["current_room"] = room
    if(game_state["current_room"] == game_state["target_room"]):
        unlock_door_sound.play()
        pygame.time.delay(1000)
        door_open_sound.play()
        pygame.time.delay(1000)
        win_victory_sound.play()
        print("Congrats! You escaped the room!")
        input("\n--- THE END (Press Enter to close the game) ---")
    else:
        print("You are now in " + room["name"])
        intended_action = input("What would you like to do? Type 'explore' or 'examine' or 'inventory'?").strip()
        if intended_action == "explore":
            explore_room(room)
            play_room(room)
        elif intended_action == "examine":
            examine_item(input("What would you like to examine?").strip())
        elif intended_action == "inventory":
            check_inventory()
            play_room(room)    
        else:
            print("Not sure what you mean. Type 'explore' or 'examine'.")
            play_room(room)
        linebreak()

def check_inventory():
    if len(game_state['keys_collected']) == 0:
        empty_inventory_sound.play()
        print("Your pockets are empty!")
    else:
        keys_inventory_sound.play()    
        output_message = "You check your pockets and you find these keys: "
        print(output_message)
        for key in game_state['keys_collected']:
            print(key["name"])        

def explore_room(room):
    """
    Explore a room. List all items belonging to this room.
    """
    explore_sound.play()
    explore_message = "You explore the room. This is " + room["name"] + ". You find "
    for item in object_relations[room["name"]]:
      explore_message += str(item["name"]) + ", "
    explore_message = explore_message[:-2]+"."
    print(explore_message)

def get_next_room_of_door(door, current_room):
    """
    From object_relations, find the two rooms connected to the given door.
    Return the second room.
    """
    connected_rooms = object_relations[door["name"]]
    target_rooms = [room for room in connected_rooms if room!= current_room].pop()
    return target_rooms

def examine_item(item_name):
    """
    Examine an item which can be a door or furniture.
    First make sure the intended item belongs to the current room.
    Then check if the item is a door. Tell player if key hasn't been 
    collected yet. Otherwise ask player if they want to go to the next
    room. If the item is not a door, then check if it contains keys.
    Collect the key if found and update the game state. At the end,
    play either the current or the next room depending on the game state
    to keep playing.
    """
    current_room = game_state["current_room"]
    next_room = ""
    output = None
    
    for item in object_relations[current_room["name"]]:
        if(item["name"] == item_name):
            output = "You examine " + item_name + ". "
            if(item["type"] == "door"):
                have_key = False
                for key in game_state["keys_collected"]:
                    if(key["target"] == item):
                        have_key = True
                if(have_key):
                    unlock_door_sound.play()
                    output += "You unlock it with a key you have."
                    next_room = get_next_room_of_door(item, current_room)
                else:
                    locked_door_sound.play()
                    output += "It is locked but you don't have the key."
            else:
                if(item["name"] in object_relations and len(object_relations[item["name"]])>0):
                    item_found = object_relations[item["name"]].pop()
                    game_state["keys_collected"].append(item_found)
                    getkey_sound.play()
                    output += "You find " + item_found["name"] + "."
                else:
                    search_nothing_sound.play()
                    output += "There isn't anything interesting about it."
            print(output)
            break

    if(output is None):
        print("The item you requested is not found in the current room.")
    
    if next_room:
        answer = input("Do you want to go to the next room? Enter 'yes' or 'no': ").strip().lower()
        if answer == "yes":
            num = random_number_generator()
            key_value = riddle(num)
            
            riddle_start_sound.play()
            
            print("This door is bound by ancient magic—solve the riddle, or remain forever inside:")
            user_answer = input(list(key_value.keys())[0] + "\n").strip().lower()
            
            if user_answer == list(key_value.values())[0]:
                riddle_correct_sound.play()
                print("✨ The magic fades away. The door opens!")
                play_room(next_room)
            else:
                print("❌ Wrong answer. The door remains sealed.")
                play_room(current_room)
        else:
            play_room(current_room)
    else:
        play_room(current_room)

def riddle(num):

    """For entering new room the player must solve riddle"""

    ques_ans = {'I’m full of words, but I can’t speak. I’m full of knowledge, but I can’t think. What am I ?': 'book', 'What has a neck but no head, and a body but no legs? ': 'bottle', 
                'What has cities but no houses, forests but no trees, and rivers but no water? ': 'map', 'What has a thumb and four fingers but is not alive? ': 'glove', 'What has teeth but cannot bite? ': 'comb',
                'I’m your home and the third from the Sun. I’ve got water and life—aren’t I the fun one? What am I?': 'earth', 'I live in the sky but fall to the ground. I’m cold and white and make no sound. What am I?': 'snow',
                'I have a tail and a head, but no body. What am I? ': 'coin', 'It has keys, but no locks. It has space, but no room. You can enter, but can’t go inside. What is it? ': 'keyboard',
                 'What starts with T, ends with T, and has T inside it? ': 'teapot' }
    key = list(ques_ans)[num]
    #print(ques_ans[key])                
    return {key:ques_ans[key]}
    
    

def random_number_generator():
        """Generates random number so it can select the random riddle from the list"""
        num = random.randint(0,9)
        return num        



game_state = INIT_GAME_STATE.copy()

start_game()
