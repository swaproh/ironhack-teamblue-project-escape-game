import random
import pygame

pygame.mixer.init()

getkeysound = pygame.mixer.Sound("sounds/getkey.wav")
riddlestartsound = pygame.mixer.Sound("sounds/riddlestart.wav")
riddlecorrectsound = pygame.mixer.Sound("sounds/riddlecorrect.wav")
searchnothingsound = pygame.mixer.Sound("sounds/searchnothing.wav")
emptyinventorysound = pygame.mixer.Sound("sounds/emptyinventory.wav")
keysinventorysound = pygame.mixer.Sound("sounds/keysinventory.wav")
dooropensound = pygame.mixer.Sound("sounds/dooropen.wav")
winvictorysound = pygame.mixer.Sound("sounds/winvictory.wav")
unlockdoorsound = pygame.mixer.Sound("sounds/unlockdoor.wav")
lockeddoorsound = pygame.mixer.Sound("sounds/lockeddoor.wav")
exploresound = pygame.mixer.Sound("sounds/explore.wav")

# OPTIONAL sound for data logs (safe fallback if file doesn't exist)
try:
    datalogsound = pygame.mixer.Sound("sounds/datalog.wav")
except Exception:
    datalogsound = None

# ----------------------------
# DATA LOGS (fun facts / trivia)
# ----------------------------
DATA_LOGS = [
    "Data Log #1: A spreadsheet is often the first tool people use to work with data.",
    "Data Log #2: Rows usually represent observations, and columns represent features.",
    "Data Log #3: More data does not always mean better results.",
    "Data Log #4: Visualizing data helps humans understand patterns faster than raw numbers.",
    "Data Log #5: Data ethics is about using data in a fair and responsible way.",
]

# Probability settings
DATA_LOG_CHANCE = 0.80       # 80% chance to find a data log when examining furniture (if it has no key)
EXTRA_DATA_LOG_CHANCE = 0.50 # 50% chance to find a data log even if furniture *does* have a key


# ----------------------------
# Define rooms and items
# ----------------------------

couch = {"name": "couch", "type": "furniture"}

doora = {"name": "door a", "type": "door"}
doorb = {"name": "door b", "type": "door"}
doorc = {"name": "door c", "type": "door"}
doord = {"name": "door d", "type": "door"}

keya = {"name": "key for door a", "type": "key", "target": doora}
keyb = {"name": "key for door b", "type": "key", "target": doorb}
keyc = {"name": "key for door c", "type": "key", "target": doorc}
keyd = {"name": "key for door d", "type": "key", "target": doord}

piano = {"name": "piano", "type": "furniture"}

gameroom = {"name": "game room", "type": "room"}
livingroom = {"name": "living room", "type": "room"}
bedroom1 = {"name": "bedroom 1", "type": "room"}
bedroom2 = {"name": "bedroom 2", "type": "room"}

queenbed = {"name": "queen bed", "type": "furniture"}
diningtable = {"name": "dining table", "type": "furniture"}
wardrobe = {"name": "wardrobe", "type": "furniture"}
carpet = {"name": "carpet", "type": "furnishing"}
floorlamp = {"name": "floor lamp", "type": "furnishing"}
dresser = {"name": "dresser", "type": "furniture"}
doublebed = {"name": "double bed", "type": "furniture"}

outside = {"name": "outside"}

allrooms = [gameroom, outside, bedroom1, bedroom2, livingroom]
alldoors = [doora, doorb, doorc, doord]


# ----------------------------
# Define which items/rooms are related
# ----------------------------

objectrelations = {
    "game room": [couch, piano, doora],
    "piano": [keya],
    "bedroom 1": [queenbed, wardrobe, carpet, floorlamp, doora, doorb, doorc],
    "bedroom 2": [doublebed, dresser, doorb],
    "living room": [diningtable, doorc, doord],
    "queen bed": [keyb],
    "double bed": [keyc],
    "dresser": [keyd],
    "outside": [],
    "door a": [gameroom, bedroom1],
    "door b": [bedroom1, bedroom2],
    "door c": [bedroom1, livingroom],
    "door d": [livingroom, outside],
}


# ----------------------------
# Define game state.
# ----------------------------
INITGAMESTATE = {
    "currentroom": gameroom,
    "previousroom": None,     # NEW: so we can send the player back if they fail the final quiz
    "keyscollected": [],
    "targetroom": outside,
    "datalogsfound": [],      # stores found data logs
}


def linebreak():
    print("\n\n")


def startgame():
    print(
        "You wake up on a couch and find yourself in a strange house with no windows which you have never been to before. "
        "You don't remember why you are here and what had happened before. "
        "You feel some unknown danger is approaching and you must get out of the house, NOW!"
    )
    playroom(gamestate["currentroom"])


def playroom(room):
    # Track previous room before moving (so we can kick them back on quiz failure)
    gamestate["previousroom"] = gamestate.get("currentroom")
    gamestate["currentroom"] = room

    # If target room reached, run final quiz BEFORE winning
    if gamestate["currentroom"] == gamestate["targetroom"]:
        print("\n🌟 You step outside... but a FINAL DATA SCIENCE SEAL blocks your escape!\n")
        passed = final_quiz()

        if passed:
            unlockdoorsound.play()
            pygame.time.delay(800)
            dooropensound.play()
            pygame.time.delay(800)
            winvictorysound.play()
            print("\n✅ Congrats! You escaped the room AND passed the final quiz!")
            input("\n--- THE END (Press Enter to close the game) ---")
            return
        else:
            lockeddoorsound.play()
            print("\n❌ The seal remains. You are forced back inside to try again!\n")
            fallback = gamestate["previousroom"] if gamestate["previousroom"] else livingroom
            playroom(fallback)
            return

    print("You are now in " + room["name"])
    intendedaction = input(
        "What would you like to do? Type 'explore' or 'examine' or 'inventory' or 'datalogs'? "
    ).strip().lower()

    if intendedaction == "explore":
        exploreroom(room)
        playroom(room)
    elif intendedaction == "examine":
        examineitem(input("What would you like to examine? ").strip().lower())
    elif intendedaction == "inventory":
        checkinventory()
        playroom(room)
    elif intendedaction == "datalogs":
        checkdatalogs()
        playroom(room)
    else:
        print("Not sure what you mean. Type 'explore' or 'examine' or 'inventory' or 'datalogs'.")
        playroom(room)

    linebreak()


def checkinventory():
    if len(gamestate["keyscollected"]) == 0:
        emptyinventorysound.play()
        print("Your pockets are empty!")
    else:
        keysinventorysound.play()
        print("You check your pockets and you find these keys:")
        for key in gamestate["keyscollected"]:
            print("- " + key["name"])


def checkdatalogs():
    if len(gamestate["datalogsfound"]) == 0:
        print("You haven't found any data logs yet.")
    else:
        print("📘 Data Logs you have collected:")
        for i, log in enumerate(gamestate["datalogsfound"], start=1):
            print(f"{i}. {log}")


def exploreroom(room):
    exploresound.play()
    exploremessage = "You explore the room. This is " + room["name"] + ". You find "
    for item in objectrelations[room["name"]]:
        exploremessage += str(item["name"]) + ", "
    exploremessage = exploremessage[:-2] + "."
    print(exploremessage)


def getnextroomofdoor(door, currentroom):
    connectedrooms = objectrelations[door["name"]]
    targetroom = [r for r in connectedrooms if r != currentroom].pop()
    return targetroom


def maybe_give_data_log():
    remaining = [log for log in DATA_LOGS if log not in gamestate["datalogsfound"]]
    log = random.choice(remaining) if remaining else random.choice(DATA_LOGS)
    gamestate["datalogsfound"].append(log)

    if datalogsound:
        datalogsound.play()

    return log


def examineitem(itemname):
    currentroom = gamestate["currentroom"]
    nextroom = ""
    output = None

    for item in objectrelations[currentroom["name"]]:
        if item["name"] == itemname:
            output = "You examine " + itemname + ". "

            if item["type"] == "door":
                havekey = False
                for key in gamestate["keyscollected"]:
                    if key["target"] == item:
                        havekey = True
                        break

                if havekey:
                    unlockdoorsound.play()
                    output += "You unlock it with a key you have."
                    nextroom = getnextroomofdoor(item, currentroom)
                else:
                    lockeddoorsound.play()
                    output += "It is locked but you don't have the key."

            else:
                has_hidden = item["name"] in objectrelations and len(objectrelations[item["name"]]) > 0

                if has_hidden and random.random() < EXTRA_DATA_LOG_CHANCE:
                    log = maybe_give_data_log()
                    output += f"\n📟 You discover a Data Log tucked away:\n“{log}”"

                if has_hidden:
                    itemfound = objectrelations[item["name"]].pop()
                    gamestate["keyscollected"].append(itemfound)
                    getkeysound.play()
                    output += "\nYou find " + itemfound["name"] + "."
                else:
                    if random.random() < DATA_LOG_CHANCE:
                        log = maybe_give_data_log()
                        output += f"📟 You find a Data Log:\n“{log}”"
                    else:
                        searchnothingsound.play()
                        output += "There isn't anything interesting about it."

            print(output)
            break

    if output is None:
        print("The item you requested is not found in the current room.")

    if nextroom:
        answer = input("Do you want to go to the next room? Enter 'yes' or 'no': ").strip().lower()
        if answer == "yes":
            num = randomnumbergenerator()
            keyvalue = riddle(num)

            riddlestartsound.play()
            print("This door is bound by ancient magic—solve the riddle, or remain forever inside:")
            useranswer = input(list(keyvalue.keys())[0] + "\n").strip().lower()

            if useranswer == list(keyvalue.values())[0]:
                riddlecorrectsound.play()
                print("✨ The magic fades away. The door opens!")
                playroom(nextroom)
            else:
                print("❌ Wrong answer. The door remains sealed.")
                playroom(currentroom)
        else:
            playroom(currentroom)
    else:
        playroom(currentroom)


def riddle(num):
    quesans = {
        "I’m full of words, but I can’t speak. I’m full of knowledge, but I can’t think. What am I ?": "book",
        "What has a neck but no head, and a body but no legs? ": "bottle",
        "What has cities but no houses, forests but no trees, and rivers but no water? ": "map",
        "What has a thumb and four fingers but is not alive? ": "glove",
        "What has teeth but cannot bite? ": "comb",
        "I’m your home and the third from the Sun. I’ve got water and life—aren’t I the fun one? What am I?": "earth",
        "I live in the sky but fall to the ground. I’m cold and white and make no sound. What am I?": "snow",
        "I have a tail and a head, but no body. What am I? ": "coin",
        "It has keys, but no locks. It has space, but no room. You can enter, but can’t go inside. What is it? ": "keyboard",
        "What starts with T, ends with T, and has T inside it? ": "teapot",
    }
    key = list(quesans)[num]
    return {key: quesans[key]}


def randomnumbergenerator():
    return random.randint(0, 9)


# ----------------------------
# FINAL QUIZ (True/False) - NEW
# ----------------------------
def ask_true_false(question, correct_bool):
    while True:
        ans = input(question + " (true/false): ").strip().lower()
        if ans in ["true", "t"]:
            return correct_bool is True
        if ans in ["false", "f"]:
            return correct_bool is False
        print("Please type 'true'/'t' or 'false'/'f'.")


def final_quiz():
    """
    Player must answer 5 True/False questions correctly to win.
    Mix of true and false statements (beginner-friendly).
    """
    # You can customize / expand this bank easily
    QUIZ_BANK = [
        ("Rows usually represent observations, and columns represent features.", True),
        ("A spreadsheet is never used in data science.", False),
        ("Visualizing data can help you spot patterns faster than raw numbers.", True),
        ("More data always guarantees better results.", False),
        ("Data ethics includes using data responsibly and fairly.", True),
    ]

    print("📚 FINAL QUIZ: Answer 5 True/False questions correctly to escape!\n")

    questions = random.sample(QUIZ_BANK, 5)
    score = 0

    for i, (q, correct) in enumerate(questions, start=1):
        print(f"Q{i}: ", end="")
        if ask_true_false(q, correct):
            print("✅ Correct!\n")
            score += 1
        else:
            print("❌ Wrong.\n")

    if score == 5:
        print("🏆 Perfect score! The seal dissolves.\n")
        return True
    else:
        print(f"Score: {score}/5. You need 5/5 to break the seal.\n")
        return False


gamestate = INITGAMESTATE.copy()
startgame()
