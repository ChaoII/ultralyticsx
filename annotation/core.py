import enum


class DrawingStatus(enum.Enum):
    Select = 0
    Draw = 1


class DrawingStatusManager:
    def __init__(self):
        self.draw_status = DrawingStatus.Select

    def set_drawing_status(self, status: DrawingStatus):
        self.draw_status = status

    def get_drawing_status(self):
        return self.draw_status


drawing_status_manager = DrawingStatusManager()
