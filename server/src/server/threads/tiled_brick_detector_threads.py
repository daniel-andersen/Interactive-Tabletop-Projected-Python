import time

from server import globals
from server.threads.server_thread import ServerThread


class TiledBrickDetectorThreadBase(ServerThread):
    def __init__(self, request_id, board_area, valid_positions, wait_for_position, callback_function):
        super().__init__(request_id)
        self.board_area = board_area
        self.valid_positions = valid_positions
        self.wait_for_position = wait_for_position
        self.callback_function = callback_function

    def _run(self):

        first_run = True

        while True:

            # Sleep a while
            if not first_run:
                time.sleep(0.01)

            first_run = True

            # Check if we have a board area image
            if self.board_area.area_image() is not TiledBrickDetectorKeepWaiting:

                # Update
                result = self.update()
                if result:
                    return result

            # No board area image
            else:

                # Give up if not waiting for position to return
                if not self.wait_for_position:
                    self.callback_function([])
                    return

                # Wait for board image
                continue

    def update(self):
        raise Exception("Function 'update' must be overridden!")


class TiledBricksDetectorThread(TiledBrickDetectorThreadBase):
    """
    Class capable of detecting multiple bricks among given positions.
    """
    def __init__(self, request_id, board_area, valid_positions, wait_for_position, callback_function):
        super().__init__(request_id, board_area, valid_positions, wait_for_position, callback_function)

    def update(self):

        # Detect bricks
        result = self.board_area.brick_detector.find_bricks_among_tiles(self.board_area, self.valid_positions)

        positions = [position for position, detected, propability in result if detected]

        # Got positions
        if len(positions) > 0 or not self.wait_for_position:
            return positions

        # Not waiting for positions
        if not self.wait_for_position:
            return []

        # Waiting for positions
        return TiledBrickDetectorKeepWaiting()


class TiledBrickDetectorThread(TiledBrickDetectorThreadBase):
    """
    Class capable of detecting single brick among given positions.
    """
    def __init__(self, request_id, board_area, valid_positions, target_position, wait_for_position, callback_function):
        super().__init__(request_id, board_area, valid_positions, wait_for_position, callback_function)
        self.target_position = target_position

    def update(self):

        # Detect bricks
        position, propabilities = self.board_area.brick_detector.find_brick_among_tiles(self.board_area, self.valid_positions)

        # Got position
        if position:

            # No specific target position
            if self.target_position is None:
                return position

            # Target position specified
            elif position[0] == self.target_position[0] and position[1] == self.target_position[1]:
                return position

        # Not waiting for position
        if not self.wait_for_position:
            return None

        # Waiting for position
        return TiledBrickDetectorKeepWaiting()


class TiledBrickMovementDetectorThread(TiledBrickDetectorThreadBase):
    """
    Class capable of detecting brick movement.
    """
    def __init__(self, request_id, board_area, valid_positions, initial_position, target_position, callback_function):
        super().__init__(request_id, board_area, valid_positions, wait_for_position=True, callback_function=callback_function)
        self.initial_position = initial_position
        self.target_position = target_position

    def update(self):

        # Detect brick position
        position, propabilities = self.board_area.brick_detector.find_brick_among_tiles(self.board_area, self.valid_positions)

        if not position:
            return TiledBrickDetectorKeepWaiting()

        # Update initial position
        if not self.initial_position:
            self.initial_position = position
            return TiledBrickDetectorKeepWaiting()

        # Check if moved away from initial position
        if position[0] != self.initial_position[0] or position[1] != self.initial_position[1]:

            # Return found position if no target defined
            if not self.target_position:
                return position, self.initial_position

            # Check moved to target position
            if self.target_position and position[0] == self.target_position[0] and position[1] == self.target_position[1]:
                return position, self.initial_position


class TiledBrickDetectorKeepWaiting(object):
    pass
