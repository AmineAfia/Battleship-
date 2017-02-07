from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from .constants import Orientation, Direction, ErrorCode
from .errorHandler.BattleshipError import BattleshipError
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType


# Controller for Battleship
class GameController:

    def __init__(self, game_id, client):
        self._battlefield = object
        self._turn_counter = 0
        self._game_started = False
        self._game_id = game_id

        self._round_time = 0
        self._options = 0
        self._username = ""
        self._password = ""

        self._client = client

    @property
    def ships(self):
        return self._battlefield.ships

    @property
    def length(self):
        return self._battlefield.length

    def get_ship_id_from_location(self, pos_x, pos_y):
        result = self._battlefield.get_ship_id_from_location(pos_x, pos_y)
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_NO_SHIP_AT_LOCATION)

    def get_next_ship_id_to_place(self):
        result = self._battlefield.get_next_ship_id_to_place()
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_NO_MORE_SHIP_TO_PLACE)

    def get_next_ship_id_by_type_to_place(self, ship_type):
        result = self._battlefield.get_next_ship_id_by_type_to_place(ship_type)
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_NO_MORE_SHIP_TO_PLACE_OF_TYPE)

    def get_ship_type_by_id(self, ship_id):
        result = self._battlefield.get_ship_type_by_id(ship_id)
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_SHIP_ID_DOES_NOT_EXIST)

    # create a new battlefield
    def create_battlefield(self, length, ships_table):
        if 9 < length < 27:
            identification = 0
            ships = []
            for i in range(5):
                ship_count = ships_table[i]
                for _ in range(ship_count):
                    identification += 1
                    if i == 0:
                        ships.append(AircraftCarrier(identification, 0, 0, Orientation.EAST))
                    elif i == 1:
                        ships.append(Battleship(identification, 0, 0, Orientation.EAST))
                    elif i == 2:
                        ships.append(Cruiser(identification, 0, 0, Orientation.EAST))
                    elif i == 3:
                        ships.append(Destroyer(identification, 0, 0, Orientation.EAST))
                    elif i == 4:
                        ships.append(Submarine(identification, 0, 0, Orientation.EAST))
            self._battlefield = Battlefield(length, ships, ships_table)
            print("Battlefield {}x{} created.".format(length, length))
            if length * length * 0.3 > self._battlefield.calc_filled():
                return True
            else:
                raise BattleshipError(ErrorCode.PARAMETER_TOO_MANY_SHIPS)
        else:
            raise BattleshipError(ErrorCode.SYNTAX_INVALID_BOARD_SIZE)

    def place_ship(self, ship_id, x_pos, y_pos, orientation):
        if self._battlefield.no_border_crossing(x_pos, y_pos):
            if self._battlefield.ship_id_exists(ship_id):
                if self._battlefield.no_ship_at_place(x_pos, y_pos):
                    try:
                        orientation = Orientation(orientation)
                    except ValueError:
                        # return False
                        raise BattleshipError(ErrorCode.SYNTAX_INVALID_PARAMETER)
                    if self._battlefield.place(ship_id, x_pos, y_pos, orientation):
                        return True
                    else:
                        return False
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
        else:
            raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

    def start_game(self):
        if self._battlefield.placement_finished():
            self._game_started = True
            print("All ships are well placed. Game: {} started!".format(self._game_id))
            return True
        else:
            self._game_started = False
            print("Placement not finished.")
            return False

    # move your own ship on your battlefield
    def move(self, ship_id, direction):
        if self._game_started:
            if self._battlefield.ship_id_exists(ship_id):
                if self._battlefield.ship_is_moveable(ship_id):
                    x_pos, y_pos = self._battlefield.get_ship_coordinate(ship_id)
                    if self._battlefield.no_ship_at_place_but(x_pos, y_pos, ship_id):
                        x_pos, y_pos = self._battlefield.get_move_coordinate(ship_id, direction)
                        if self._battlefield.no_border_crossing(x_pos, y_pos):
                            try:
                                direction = Direction(direction)
                            except ValueError:
                                raise BattleshipError(ErrorCode.SYNTAX_INVALID_PARAMETER)
                            if self._battlefield.move(ship_id, direction):
                                print("ship:{} moved to:{}".format(ship_id, direction))
                                return True
                            else:
                                print("ship not moved")
                                return False
                        else:
                            raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
                    else:
                        raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_SHIP_IMMOVABLE)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
        else:
            print("game not started")
            return False

    # strike at the coordinates on the enemy battlefield
    def strike(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                if self._battlefield.no_strike_at_place(x_pos, y_pos):
                    print("strike at x={},y={}".format(x_pos, y_pos))
                    if self._battlefield.strike(x_pos, y_pos):
                        # todo call UI strike(x,y)
                        print("got it!")
                    else:
                        print("fail!")
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_ALREADY_HIT_POSITION)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
        else:
            print("game not started")
            return False

    # shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                if self._battlefield.no_hit_at_place(x_pos, y_pos):
                    if self._battlefield.shoot(x_pos, y_pos):
                        print("shoot at x={}, y={}".format(x_pos, y_pos))
                        return True
                    else:
                        return False
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_ALREADY_HIT_POSITION)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
        else:
            print("game not started")
            return False

    def all_ships_sunk(self):
        return self._battlefield.all_ships_sunk()

    def abort(self):
        print("Game: {} aborted!".format(self._game_id))
        self = None
        return True

    # interface to client
    # DO NOT CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def run(self, msg: ProtocolMessage):

        if msg.type == ProtocolMessageType.CREATE_GAME:
            length = msg.parameters["board_size"]
            ships_table = msg.parameters["num_ships"]
            self._battlefield = self.create_battlefield(length, ships_table)


        elif msg.type == ProtocolMessageType.PLACE:
            ship_positions = msg.parameters["ship_positions"]
            ship_id = 0
            result = True
            if len(ship_positions.positions) == self._battlefield.count_ships():
                for ship_position in ship_positions.positions:
                    ship_id += 1
                    x_pos = ship_position.position.horizontal
                    y_pos = ship_position.position.vertical
                    orientation = ship_position.orientation
                    if not self._battlefield.place(ship_id, x_pos, y_pos, orientation):
                        result = False
            else:
                raise BattleshipError(ErrorCode.PARAMETER_WRONG_NUMBER_OF_SHIPS)
            return result

        #if msg.type == ProtocolMessageType.START_GAME:
            #self.start_game()

        # todo: not the clients turn and turn counter invalid
        elif msg.type == ProtocolMessageType.MOVE:
            ship_id = msg.parameters["ship_id"]
            direction = msg.parameters["direction"]
            if self.move(ship_id, direction):
                return True
            else:
                return False


        # todo: not the clients turn and turn counter invalid
        elif msg.type == ProtocolMessageType.SHOOT:
            x_pos = msg.parameters["ship_position"].position.horizontal
            y_pos = msg.parameters["ship_position"].position.vertical
            if self._battlefield.strike(x_pos, y_pos):
                # todo call UI for strike(x,y)
                return True
            else:
                return False

        elif msg.type == ProtocolMessageType.ABORT:
            self.abort()

        # unknown command
        else:
            raise BattleshipError(ErrorCode.UNKNOWN)