from agents import SimulationAgent


class Receiver(SimulationAgent):
    def __init__(self, name: str):
        super().__init__(name)

    def receive_whole(self, message: list[int]):
        raise NotImplementedError("Method not implemented")

    def receive_chunk(self, message: list[int]):
        raise NotImplementedError("Method not implemented")

    def receive_whole_encoded(self, message: list[int]):
        raise NotImplementedError("Method not implemented")

    def receive_chunk_encoded(self, message: list[int]):
        raise NotImplementedError("Method not implemented")
