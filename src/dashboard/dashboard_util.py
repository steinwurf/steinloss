class Data_Presenter(object):
    __instance = None

    def __init__(self):
        if Data_Presenter.__instance is not None:
            raise RuntimeError("Cannot init class twice, as it is as singelton")
        else:
            self.data = []
            Data_Presenter.__instance = self

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            Data_Presenter()
        return cls.__instance

    @classmethod
    def clear_instance(cls):
        cls.__instance = None

    def append(self, test_data):
        self.data = self.data + test_data

    pointer = 0

    def read(self):
        data = []

        data_len = len(self.data)
        for i in range(self.pointer, data_len):
            data.append(self.data[i])

        self.pointer = data_len

        return data
