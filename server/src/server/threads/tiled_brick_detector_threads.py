import time

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
                time.sleep(self.fixed_update_delay)

            first_run = True

            # Check if stopped
            if self.stopped:
                return

            # Check if we have a board area image
            if self.board_area.area_image() is not None:

                # Update
                if self.update():
                    return

            # No board area image
            else:

                # Give up if not waiting for position to return
                if not self.wait_for_position:
                    self._callback(lambda: self.callback_function([]))
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
        result = self.board_area.brick_detector.find_bricks_among_tiles(self.valid_positions)

        positions = [position for position, detected, propability in result if detected]

        # Got positions
        if len(positions) > 0 or not self.wait_for_position:
            self._callback(lambda: self.callback_function(positions))
            return True

        # Not waiting for positions
        if not self.wait_for_position:
            self._callback(lambda: self.callback_function([]))
            return True

        # Waiting for positions
        return False


class TiledBrickDetectorThread(TiledBrickDetectorThreadBase):
    """
    Class capable of detecting single brick among given positions.
    """
    def __init__(self, request_id, board_area, valid_positions, target_position, wait_for_position, callback_function):
        super().__init__(request_id, board_area, valid_positions, wait_for_position, callback_function)
        self.target_position = target_position

    def update(self):

        # Detect bricks
        position, propabilities = self.board_area.brick_detector.find_brick_among_tiles(self.valid_positions)

        # Got position
        if position:

            # No specific target position
            if self.target_position is None:
                self._callback(lambda: self.callback_function(position))
                return True

            # Target position specified
            elif position[0] == self.target_position[0] and position[1] == self.target_position[1]:
                self._callback(lambda: self.callback_function(position))
                return True

        # Not waiting for position
        if not self.wait_for_position:
            self._callback(lambda: self.callback_function(None))
            return True

        # Waiting for position
        return False


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
        position, propabilities = self.board_area.brick_detector.find_brick_among_tiles(self.valid_positions)

        if not position:
            return False

        # Update initial position
        if not self.initial_position:
            self.initial_position = position
            return False

        # Check if moved away from initial position
        if position[0] != self.initial_position[0] or position[1] != self.initial_position[1]:

            # Return found position if no target defined
            if not self.target_position:
                self._callback(lambda: self.callback_function(position, self.initial_position))
                return True

            # Check moved to target position
            if self.target_position and position[0] == self.target_position[0] and position[1] == self.target_position[1]:
                self._callback(lambda: self.callback_function(position, self.initial_position))
                return True
