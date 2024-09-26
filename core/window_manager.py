class WindowManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WindowManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.registry = {}
        return cls._instance

    def register_window(self, obj_name, window):
        self.registry[obj_name] = window

    def find_window(self, obj_name):
        return self.registry.get(obj_name, None)

    # 提供访问单例的接口
