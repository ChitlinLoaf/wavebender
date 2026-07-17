from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Device:
    device_id: str
    name: str
    category: str
    produces: Set[str] = field(default_factory=set)
    accepts: Set[str] = field(default_factory=set)
    required: bool = False
    status: str = "conceptual"

    def can_produce(self, signal: str) -> bool:
        return signal in self.produces

    def can_accept(self, signal: str) -> bool:
        return signal in self.accepts


@dataclass
class Connection:
    connection_id: str
    source: str
    target: str
    signal: str
    direction: str = "forward"
    purpose: str = ""


class SignalGraph:
    def __init__(self) -> None:
        self.devices: Dict[str, Device] = {}
        self.connections: List[Connection] = []

    def add_device(self, device: Device) -> None:
        if device.device_id in self.devices:
            raise ValueError("Duplicate device ID: " + device.device_id)
        self.devices[device.device_id] = device

    def connect(self, connection: Connection) -> None:
        if connection.source not in self.devices:
            raise KeyError("Unknown source: " + connection.source)

        if connection.target not in self.devices:
            raise KeyError("Unknown target: " + connection.target)

        self.connections.append(connection)

    def validate_connection(self, connection: Connection) -> dict:
        source = self.devices.get(connection.source)
        target = self.devices.get(connection.target)

        checks = {
            "source_exists": source is not None,
            "target_exists": target is not None,
            "source_can_produce": False,
            "target_can_accept": False,
        }

        if source is not None:
            checks["source_can_produce"] = source.can_produce(
                connection.signal
            )

        if target is not None:
            checks["target_can_accept"] = target.can_accept(
                connection.signal
            )

        checks["valid"] = all(checks.values())
        return checks

    def validate_all(self) -> dict:
        results = {}

        for connection in self.connections:
            results[connection.connection_id] = (
                self.validate_connection(connection)
            )

        return {
            "passed": all(
                result["valid"]
                for result in results.values()
            ),
            "connection_count": len(results),
            "results": results,
        }

    def describe_routes(self) -> List[str]:
        descriptions = []

        for connection in self.connections:
            arrow = (
                "<-->"
                if connection.direction == "bidirectional"
                else "-->"
            )

            descriptions.append(
                "{} {} {} [{}]".format(
                    connection.source,
                    arrow,
                    connection.target,
                    connection.signal,
                )
            )

        return descriptions


def build_default_graph() -> SignalGraph:
    graph = SignalGraph()

    graph.add_device(Device(
        device_id="audio_source",
        name="Instrument or Microphone",
        category="audio_source",
        produces={"analog_audio"},
        required=True,
    ))

    graph.add_device(Device(
        device_id="audio_interface",
        name="Audio Interface",
        category="audio_interface",
        produces={"digital_audio", "analog_audio"},
        accepts={"analog_audio", "digital_audio"},
        required=True,
    ))

    graph.add_device(Device(
        device_id="computer",
        name="Computer Running Smart DAW",
        category="processor",
        produces={"digital_audio", "midi"},
        accepts={"digital_audio", "midi"},
        required=True,
        status="available",
    ))

    graph.add_device(Device(
        device_id="monitors",
        name="Monitors or Headphones",
        category="audio_output",
        produces={"acoustic_sound"},
        accepts={"analog_audio"},
        required=True,
    ))

    graph.add_device(Device(
        device_id="midi_instrument",
        name="MIDI Instrument or Controller",
        category="midi_source",
        produces={"midi"},
        accepts={"midi"},
    ))

    graph.add_device(Device(
        device_id="midi_interface",
        name="MIDI Interface",
        category="data_interface",
        produces={"midi"},
        accepts={"midi"},
    ))

    graph.connect(Connection(
        connection_id="audio_input_path",
        source="audio_source",
        target="audio_interface",
        signal="analog_audio",
        purpose="Capture microphone or instrument audio",
    ))

    graph.connect(Connection(
        connection_id="audio_to_computer",
        source="audio_interface",
        target="computer",
        signal="digital_audio",
        purpose="Record audio into the DAW",
    ))

    graph.connect(Connection(
        connection_id="computer_to_audio",
        source="computer",
        target="audio_interface",
        signal="digital_audio",
        purpose="Return DAW playback",
    ))

    graph.connect(Connection(
        connection_id="audio_monitor_path",
        source="audio_interface",
        target="monitors",
        signal="analog_audio",
        purpose="Send playback to monitors",
    ))

    graph.connect(Connection(
        connection_id="midi_instrument_path",
        source="midi_instrument",
        target="midi_interface",
        signal="midi",
        purpose="Capture MIDI performance",
    ))

    graph.connect(Connection(
        connection_id="midi_to_computer",
        source="midi_interface",
        target="computer",
        signal="midi",
        direction="bidirectional",
        purpose="Exchange MIDI messages",
    ))

    return graph


if __name__ == "__main__":
    graph = build_default_graph()
    result = graph.validate_all()

    print("SMART DAW SIGNAL GRAPH")
    print("=" * 72)

    for route in graph.describe_routes():
        print(route)

    print("-" * 72)
    print("Validation passed :", result["passed"])
    print("Connections       :", result["connection_count"])
