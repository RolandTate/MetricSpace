from Core.MetricSpaceCore import MetricSpaceData


class StringData(MetricSpaceData):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("StringData only support str type data")
        self.value = value

    def get(self):
        return self.value

    def __len__(self):
        return len(self.value)

    def __eq__(self, other):
        if not isinstance(other, StringData):
            return False
        return self.value == other.value

    def __repr__(self):
        return f'StringData("{self.value}")'

    def __str__(self):
        return self.value
