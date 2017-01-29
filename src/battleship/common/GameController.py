from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from .constants import Orientation, Direction, ErrorCode
from .errorHandler.BattleshipError import BattleshipError

#Controller for Battleship+
class GameController:

    def __init__(self, game_id):
        self._battlefield = object
        self._turn_counter = 0
        self._game_started = False
        self._game_id = game_id


    #create a new battlefield
    def createBattlefield(self, length, ships):
        self._battlefield = Battlefield(length, ships)
        print("Battlefield {}x{} created.".format(length, length))

    def placeShip(self, ship_id, x_pos, y_pos, orientation):
        self._battlefield.place(ship_id, x_pos, y_pos, orientation)

    def startGame(self):
        if self._battlefield.placementFinished():
            self._game_started = True
            print("All ships are well placed. Game: {} started!".format(self._game_id))
        else:
            self._game_started = False
            print("Placement not finished.")

    #move your own ship on your battlefield
    def move(self, ship_id, direction):
        if self._game_started:
            if self._battlefield.move(ship_id, direction):
                print("ship:{} moved to:{}".format(ship_id, direction))
            else:
                print("error - ship not moved")

    #strike at the coordinates on the enemy battlefield
    def strike(self, x_pos, y_pos):
        if self._game_started:
            print("strike at x={},y={}".format(x_pos, y_pos))
            if self._battlefield.strike(x_pos, y_pos):
                print("got it!")
            else:
                print("fail!")

    #shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if self._game_started:
            print("shoot at x={}, y={}".format(x_pos, y_pos))
            self._battlefield.shoot(x_pos, y_pos)

    def abort(self):
        print("Game: {} aborted!".format(self._game_id))
        self = None




    #run the game controller with parameter:
    #   battlefieldlength
    #   ships_table: carrier, battleship, cruiser, destroyer, submarine
    #def run(self, length, ships_table):
    def run(self, cmd):

        if cmd[0] == "create":
            length = cmd[1]
            ships_table = cmd[2]

            if len(ships_table) == 5:
                if length < 27 and length > 9:

                    #create ships
                    id = 0
                    ships = []
                    for i in range(5):
                        shipCount = ships_table[i]
                        for _ in range(shipCount):
                            id = id + 1
                            if i == 0:
                                ships.append(AircraftCarrier(id, 0, 0, Orientation.EAST))
                            if i == 1:
                                ships.append(Battleship(id, 0, 0, Orientation.EAST))
                            if i == 2:
                                ships.append(Cruiser(id, 0, 0, Orientation.EAST))
                            if i == 3:
                                ships.append(Destroyer(id, 0, 0, Orientation.EAST))
                            if i == 4:
                                ships.append(Submarine(id, 0, 0, Orientation.EAST))

                    #create battlefield
                    self.createBattlefield(length, ships)

                else:
                    raise BattleshipError(ErrorCode.SYNTAX_INVALID_BOARD_SIZE)
            else:
                pass

        # def place(self, ship_id, x_pos, y_pos, orientation):
        if cmd[0] == "place":
            ship_id = cmd[1]
            x_pos = cmd[2]
            y_pos = cmd[3]
            orientation = cmd[4]

            self.placeShip(ship_id, x_pos, y_pos, orientation)

            #if all ships are places and the game starts
            self.startGame()

        #def move(self, ship_id, direction)
        #wird nur die funktion benötigt
        if cmd[0] == "move":
            ship_id = cmd[1]
            direction = cmd[2]

            self.move(ship_id, direction)

        #def strike(self, x_pos, y_pos)
        if cmd[0] == "strike":
            x_pos = cmd[1]
            y_pos = cmd[2]

            self.strike(x_pos, y_pos)

        #if cmd[0] == "shoot":
            #x_pos = cmd[1]
            #y_pos = cmd[2]

            #self.shoot(x_pos, y_pos)

        if cmd[0] == "abort":
            self.abort()




