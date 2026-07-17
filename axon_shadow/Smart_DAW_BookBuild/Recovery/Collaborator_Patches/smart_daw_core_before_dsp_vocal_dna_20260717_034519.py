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

# === SMART_DAW_GUI_PATCH_START ===

# Pythonista mobile-studio GUI appended by Page 2, Block 17.
# The original Device, Connection, SignalGraph, and routing engine remain intact.

from pathlib import Path as _GUIPath
from datetime import datetime as _GUIDatetime
import json as _gui_json
import traceback as _gui_traceback

try:
    import ui as _gui_ui
except Exception:
    _gui_ui = None

try:
    import sound as _gui_sound
except Exception:
    _gui_sound = None

_GUI_PROJECT = _GUIPath.home() / 'Documents' / 'Smart_DAW_BookBuild'
_GUI_STATE = _GUI_PROJECT / 'smart_daw_state.json'
_GUI_LOG = _GUI_PROJECT / 'smart_daw_build.log'
_GUI_M4A = _GUI_PROJECT / 'Audio_Library' / 'Recent_M4A'


def gui_load_state():
    if not _GUI_STATE.exists():
        return {}

    try:
        return _gui_json.loads(
            _GUI_STATE.read_text(encoding='utf-8')
        )
    except Exception as exc:
        return {'load_error': repr(exc)}


def gui_runtime_log(action, detail=''):
    _GUI_PROJECT.mkdir(parents=True, exist_ok=True)

    timestamp = _GUIDatetime.now().isoformat(
        timespec='seconds'
    )

    with _GUI_LOG.open('a', encoding='utf-8') as handle:
        handle.write(
            '[{}] GUI ACTION={} DETAIL={}\n'.format(
                timestamp,
                action,
                str(detail).replace('\n', ' '),
            )
        )


def gui_recent_recordings(limit=100):
    _GUI_M4A.mkdir(parents=True, exist_ok=True)

    recordings = []

    for path in _GUI_M4A.glob('*.m4a'):
        try:
            stat = path.stat()
            recordings.append({
                'name': path.name,
                'path': str(path),
                'size_bytes': stat.st_size,
                'modified_timestamp': stat.st_mtime,
                'modified': _GUIDatetime.fromtimestamp(
                    stat.st_mtime
                ).isoformat(timespec='seconds'),
            })
        except Exception:
            continue

    recordings.sort(
        key=lambda item: item['modified_timestamp'],
        reverse=True,
    )

    return recordings[:limit]


def gui_recovered_engines(limit=100):
    state = gui_load_state()

    return (
        state
        .get('recovered_vocal_engines', {})
        .get('ranked_candidates', [])
    )[:limit]


def gui_summary_lines():
    state = gui_load_state()

    artifact_counts = (
        state
        .get('artifact_scan', {})
        .get('category_counts', {})
    )

    service_count = (
        state
        .get('secure_services', {})
        .get('available_capability_count', 0)
    )

    graph = None
    graph_status = 'UNAVAILABLE'
    graph_devices = 0
    graph_connections = 0

    try:
        graph = build_default_graph()
        validation = graph.validate_all()
        graph_status = (
            'PASS' if validation.get('passed') else 'FAIL'
        )
        graph_devices = len(graph.devices)
        graph_connections = len(graph.connections)
    except Exception as exc:
        graph_status = 'ERROR: {}'.format(exc)

    return [
        'SMART DAW — MOBILE STUDIO',
        '=' * 62,
        'Project: {}'.format(_GUI_PROJECT),
        'Core signal graph: {}'.format(graph_status),
        'Signal devices: {}'.format(graph_devices),
        'Signal connections: {}'.format(graph_connections),
        'Current page: {}'.format(
            state.get('current_page', '?')
        ),
        'Current block: {}'.format(
            state.get('current_block', '?')
        ),
        '',
        'MOBILE AUDIO LIBRARY',
        '-' * 62,
        'Recent M4A recordings: {}'.format(
            len(gui_recent_recordings())
        ),
        '',
        'RECOVERED PROJECT INTELLIGENCE',
        '-' * 62,
        'Audio artifacts: {}'.format(
            artifact_counts.get('audio', 0)
        ),
        'Vocal artifacts: {}'.format(
            artifact_counts.get('vocal', 0)
        ),
        'DSP artifacts: {}'.format(
            artifact_counts.get('dsp', 0)
        ),
        'Smart artifacts: {}'.format(
            artifact_counts.get('smart_features', 0)
        ),
        'Interface artifacts: {}'.format(
            artifact_counts.get('interfaces', 0)
        ),
        'Ranked prior engines: {}'.format(
            len(gui_recovered_engines())
        ),
        'Detected secure capabilities: {}'.format(
            service_count
        ),
    ]


class SmartDAWMobileController:
    def __init__(self):
        self.view = None
        self.table = None
        self.output = None
        self.status = None
        self.rows = []
        self.mode = 'summary'
        self.player = None

    def write_output(self, content):
        if isinstance(content, str):
            text = content
        else:
            text = '\n'.join(str(line) for line in content)

        if self.output is not None:
            self.output.text = text

        print(text)

    def set_status(self, text):
        if self.status is not None:
            self.status.text = text

        gui_runtime_log('STATUS', text)

    def load_table(self):
        if self.table is None:
            return

        data_source = _gui_ui.ListDataSource([
            row.get('title', 'Untitled')
            for row in self.rows
        ])

        data_source.text_color = 'white'
        data_source.font = ('<system>', 12)
        data_source.action = self.row_selected

        self.table.data_source = data_source
        self.table.delegate = data_source
        self.table.reload()

    def show_summary(self, sender=None):
        self.mode = 'summary'
        self.rows = []
        self.load_table()
        self.write_output(gui_summary_lines())
        self.set_status('Project summary loaded')

    def show_recordings(self, sender=None):
        self.mode = 'recordings'
        recordings = gui_recent_recordings()

        self.rows = [
            {
                'title': item['name'],
                'path': item['path'],
                'detail': '{} bytes | {}'.format(
                    item['size_bytes'],
                    item['modified'],
                ),
            }
            for item in recordings
        ]

        self.load_table()
        self.write_output([
            'RECENT M4A RECORDINGS',
            '=' * 62,
            '{} file(s) available'.format(len(recordings)),
            '',
            'Tap a recording to play it.',
        ])
        self.set_status(
            '{} recordings loaded'.format(len(recordings))
        )

    def show_engines(self, sender=None):
        self.mode = 'engines'
        engines = gui_recovered_engines()

        self.rows = []

        for engine in engines:
            categories = ', '.join(
                engine.get('categories', [])
            )

            self.rows.append({
                'title': 'Score {} — {}'.format(
                    engine.get('score', 0),
                    engine.get('name', 'Unknown'),
                ),
                'path': engine.get('path', ''),
                'detail': categories,
            })

        self.load_table()
        self.write_output([
            'RECOVERED VOCAL / DSP / SMART ENGINES',
            '=' * 62,
            '{} candidate(s) ranked'.format(len(engines)),
            '',
            'Tap an engine to inspect its path and category.',
        ])
        self.set_status(
            '{} recovered engines loaded'.format(len(engines))
        )

    def show_routes(self, sender=None):
        self.mode = 'routes'
        self.rows = []

        try:
            graph = build_default_graph()
            validation = graph.validate_all()
            routes = graph.describe_routes()

            self.write_output([
                'SMART DAW SIGNAL ROUTING',
                '=' * 62,
                *routes,
                '-' * 62,
                'Validation: {}'.format(
                    'PASS'
                    if validation.get('passed')
                    else 'FAIL'
                ),
            ])
            self.set_status('Signal routes validated')

        except Exception as exc:
            self.write_output(_gui_traceback.format_exc())
            self.set_status('Route error: {}'.format(exc))

        self.load_table()

    def stop_audio(self, sender=None):
        errors = []

        try:
            if self.player is not None:
                self.player.stop()
        except Exception as exc:
            errors.append(repr(exc))

        try:
            if _gui_sound is not None:
                _gui_sound.stop_all_effects()
        except Exception as exc:
            errors.append(repr(exc))

        self.player = None

        if errors:
            self.set_status(
                'Stop completed with warning: {}'.format(
                    '; '.join(errors)
                )
            )
        else:
            self.set_status('Audio stopped')

    def row_selected(self, sender):
        selected_row = sender.selected_row

        if selected_row is None or selected_row < 0:
            return

        if selected_row >= len(self.rows):
            return

        row = self.rows[selected_row]
        path_text = row.get('path', '')

        self.write_output([
            row.get('title', 'Untitled'),
            '=' * 62,
            row.get('detail', ''),
            '',
            'PATH',
            path_text,
        ])

        if self.mode != 'recordings':
            self.set_status(
                'Selected {}'.format(row.get('title', 'item'))
            )
            return

        if _gui_sound is None:
            self.set_status('Pythonista sound module unavailable')
            return

        path = _GUIPath(path_text)

        if not path.exists():
            self.set_status('Recording file no longer exists')
            return

        try:
            self.stop_audio()
            self.player = _gui_sound.Player(str(path))
            self.player.play()
            self.set_status('Playing {}'.format(path.name))

        except Exception as exc:
            self.write_output(_gui_traceback.format_exc())
            self.set_status('Playback failed: {}'.format(exc))

    def refresh(self, sender=None):
        if self.mode == 'recordings':
            self.show_recordings()
        elif self.mode == 'engines':
            self.show_engines()
        elif self.mode == 'routes':
            self.show_routes()
        else:
            self.show_summary()

    def build(self):
        if _gui_ui is None:
            raise RuntimeError(
                'Pythonista ui module is required.'
            )

        screen_width, screen_height = _gui_ui.get_screen_size()
        width = min(screen_width, 1000)
        height = min(screen_height, 760)

        root = _gui_ui.View(
            frame=(0, 0, width, height),
            name='Smart DAW Mobile Studio',
        )
        root.background_color = '#101319'

        title = _gui_ui.Label(
            frame=(12, 8, width - 24, 42)
        )
        title.text = 'SMART DAW — MOBILE STUDIO'
        title.font = ('<system-bold>', 20)
        title.text_color = 'white'
        title.alignment = _gui_ui.ALIGN_CENTER
        root.add_subview(title)

        controls = [
            ('Summary', self.show_summary),
            ('Recordings', self.show_recordings),
            ('Engines', self.show_engines),
            ('Routes', self.show_routes),
            ('Refresh', self.refresh),
            ('Stop', self.stop_audio),
        ]

        gap = 6
        button_width = (width - 24 - gap * 5) / 6.0

        for index, control in enumerate(controls):
            title_text, action = control

            button = _gui_ui.Button(
                frame=(
                    12 + index * (button_width + gap),
                    56,
                    button_width,
                    42,
                )
            )
            button.title = title_text
            button.font = ('<system-bold>', 12)
            button.background_color = '#29313d'
            button.tint_color = 'white'
            button.corner_radius = 7
            button.action = action
            root.add_subview(button)

        content_top = 110
        status_height = 40
        content_height = height - content_top - status_height - 18
        table_width = max(250, width * 0.43)

        table = _gui_ui.TableView(
            frame=(
                12,
                content_top,
                table_width,
                content_height,
            )
        )
        table.background_color = '#171b22'
        table.tint_color = 'white'
        table.row_height = 48
        root.add_subview(table)

        output = _gui_ui.TextView(
            frame=(
                table_width + 20,
                content_top,
                width - table_width - 32,
                content_height,
            )
        )
        output.background_color = '#171b22'
        output.text_color = 'white'
        output.font = ('Menlo', 10)
        output.editable = False
        root.add_subview(output)

        status = _gui_ui.Label(
            frame=(
                12,
                height - status_height - 8,
                width - 24,
                status_height,
            )
        )
        status.background_color = '#242b35'
        status.text_color = 'white'
        status.font = ('<system>', 12)
        status.alignment = _gui_ui.ALIGN_CENTER
        status.corner_radius = 7
        root.add_subview(status)

        self.view = root
        self.table = table
        self.output = output
        self.status = status

        self.show_summary()
        return root

    def present(self):
        view = self.build()
        view.present(
            'fullscreen',
            hide_title_bar=False,
        )


def launch_smart_daw_gui():
    controller = SmartDAWMobileController()
    controller.present()
    gui_runtime_log('GUI_LAUNCHED', _GUI_PROJECT)
    return controller


# === SMART_DAW_GUI_PATCH_END ===

# === CHAPTER_2_HIERARCHY_GUI_PATCH_START ===

def smart_daw_project_hierarchy_lines():
    state = gui_load_state()
    project = state.get('project_hierarchy', {})
    lines = [
        'PROJECT → TRACKS → REGIONS → EVENTS',
        '=' * 62,
        'Project ID: {}'.format(
            project.get('project_id', 'unknown')
        ),
        '',
    ]

    for track_item in project.get('tracks', []):
        lines.append(
            'TRACK: {} [{}]'.format(
                track_item.get('name'),
                track_item.get('track_type'),
            )
        )

        for region_item in track_item.get('regions', []):
            lines.append(
                '  REGION: {} | start={} | length={}'.format(
                    region_item.get('name'),
                    region_item.get('start_beats'),
                    region_item.get('length_beats'),
                )
            )

            for event_item in region_item.get('events', []):
                lines.append(
                    '    EVENT: {} | beat={} | duration={}'.format(
                        event_item.get('event_type'),
                        event_item.get('position_beats'),
                        event_item.get('duration_beats'),
                    )
                )

        lines.append('')

    return lines


def smart_daw_project_chooser_lines():
    state = gui_load_state()
    chooser = state.get('project_chooser', {})
    selected = chooser.get('selected') or {}

    lines = [
        'PROJECT CHOOSER',
        '=' * 62,
        'Selected: {}'.format(
            selected.get('title', 'None')
        ),
        '',
    ]

    for index, item in enumerate(
        chooser.get('entries', []),
        start=1,
    ):
        lines.append(
            '{:02d}. {} | {} | {} Hz'.format(
                index,
                item.get('chooser_type'),
                item.get('title'),
                item.get('sample_rate', 'default'),
            )
        )

    return lines


def smart_daw_track_factory_lines():
    state = gui_load_state()
    result = state.get('new_track_factory_result', {})
    lines = [
        'NEW TRACK FACTORY',
        '=' * 62,
        'Validation: {}'.format(
            'PASS' if result.get('passed') else 'FAIL'
        ),
        '',
    ]

    for track_item in result.get('tracks', []):
        lines.append(
            '{} | {} | channel={} | input_required={}'.format(
                track_item.get('track_type'),
                track_item.get('name'),
                track_item.get('channel'),
                track_item.get('requires_input'),
            )
        )

    return lines


def smart_daw_show_hierarchy(self, sender=None):
    self.mode = 'hierarchy'
    self.rows = []
    self.load_table()
    self.write_output(
        smart_daw_project_hierarchy_lines()
    )
    self.set_status('Project hierarchy loaded')


def smart_daw_show_chooser(self, sender=None):
    self.mode = 'chooser'
    self.rows = []
    self.load_table()
    self.write_output(
        smart_daw_project_chooser_lines()
    )
    self.set_status('Project chooser loaded')


def smart_daw_show_track_factory(self, sender=None):
    self.mode = 'track_factory'
    self.rows = []
    self.load_table()
    self.write_output(
        smart_daw_track_factory_lines()
    )
    self.set_status('Track factory loaded')


SmartDAWMobileController.show_hierarchy = (
    smart_daw_show_hierarchy
)
SmartDAWMobileController.show_chooser = (
    smart_daw_show_chooser
)
SmartDAWMobileController.show_track_factory = (
    smart_daw_show_track_factory
)


def launch_smart_daw_chapter_2_dashboard():
    controller = SmartDAWMobileController()
    view = controller.build()

    width = view.width
    y_position = 104
    button_width = (width - 36) / 3.0

    controls = [
        ('Hierarchy', controller.show_hierarchy),
        ('Project Chooser', controller.show_chooser),
        ('Track Factory', controller.show_track_factory),
    ]

    for index, pair in enumerate(controls):
        title_text, action = pair
        button = _gui_ui.Button(
            frame=(
                12 + index * (button_width + 6),
                y_position,
                button_width,
                38,
            )
        )
        button.title = title_text
        button.font = ('<system-bold>', 11)
        button.background_color = '#354052'
        button.tint_color = 'white'
        button.corner_radius = 7
        button.action = action
        view.add_subview(button)

    controller.table.y = 150
    controller.table.height = max(
        200,
        controller.table.height - 46,
    )
    controller.output.y = 150
    controller.output.height = max(
        200,
        controller.output.height - 46,
    )

    view.present(
        'fullscreen',
        hide_title_bar=False,
    )

    gui_runtime_log(
        'CHAPTER_2_DASHBOARD_LAUNCHED',
        _GUI_PROJECT,
    )

    return controller


# === CHAPTER_2_HIERARCHY_GUI_PATCH_END ===

# === PROJECT_HANDLING_GUI_PATCH_START ===

def project_handling_state_lines(section='startup'):
    state = gui_load_state()
    lines = []

    if section == 'startup':
        data = state.get('startup_preferences', {})
        lines = [
            'STARTUP ACTIONS',
            '=' * 62,
            'Selected: {}'.format(
                data.get('selected_action', 'unknown')
            ),
            'Fallback used: {}'.format(
                data.get('fallback_used', False)
            ),
            '',
        ]

        for action_id, item in data.get(
            'available_actions', {}
        ).items():
            marker = (
                'ACTIVE'
                if action_id == data.get('selected_action')
                else 'READY'
            )
            lines.append(
                '{} | {} | {}'.format(
                    marker,
                    action_id,
                    item.get('label'),
                )
            )

    elif section == 'recent':
        data = state.get('project_registry', {})
        lines = [
            'RECENT PROJECTS',
            '=' * 62,
            'Active: {}'.format(
                data.get('active_project_id')
            ),
            '',
        ]

        for item in data.get('recent_projects', []):
            lines.append(
                '{:02d}. {} | {} | {}'.format(
                    item.get('registry_rank', 0),
                    item.get('project_type'),
                    item.get('title'),
                    item.get('opened_at') or 'unknown time',
                )
            )

    elif section == 'imports':
        data = state.get('compatible_imports', {})
        lines = [
            'COMPATIBLE IMPORTS',
            '=' * 62,
            'Compatible files: {}'.format(
                data.get('compatible_count', 0)
            ),
            '',
        ]

        for item in data.get('files', [])[:80]:
            lines.append(
                '{} | {} | {}'.format(
                    item.get('extension'),
                    item.get('format'),
                    item.get('path'),
                )
            )

    elif section == 'workspace':
        data = state.get('multi_project_workspace', {})
        lines = [
            'MULTI-PROJECT WORKSPACE',
            '=' * 62,
            'Active: {}'.format(
                data.get('active_project_id')
            ),
            '',
        ]

        for item in data.get('project_windows', []):
            lines.append(
                '{} | window {} | {} | {}'.format(
                    'ACTIVE' if item.get('is_active') else 'OPEN',
                    item.get('window_order'),
                    item.get('project_type'),
                    item.get('title'),
                )
            )

    elif section == 'save':
        data = state.get('save_engine', {})
        lines = [
            'SAVE AND RECOVERY',
            '=' * 62,
            'Project: {}'.format(
                data.get('active_project_id')
            ),
            'Manual save: {}'.format(
                data.get('manual_save_enabled')
            ),
            'Autosave: {}'.format(
                data.get('autosave_enabled')
            ),
            'Autosave interval: {} seconds'.format(
                data.get('autosave_interval_seconds')
            ),
            'Last hash: {}'.format(
                data.get('last_saved_hash')
            ),
            '',
            'CHECKPOINTS',
            '-' * 62,
        ]

        for item in reversed(data.get('checkpoints', [])):
            lines.append(
                '{} | {} | {}'.format(
                    item.get('checkpoint_id'),
                    item.get('created_at'),
                    item.get('sha256'),
                )
            )

    return lines


def project_handling_show(self, section):
    self.mode = 'project_handling_' + section
    self.rows = []
    self.load_table()
    self.write_output(
        project_handling_state_lines(section)
    )
    self.set_status(
        'Project handling view: {}'.format(section)
    )


def show_startup_actions(self, sender=None):
    project_handling_show(self, 'startup')


def show_recent_projects(self, sender=None):
    project_handling_show(self, 'recent')


def show_compatible_imports(self, sender=None):
    project_handling_show(self, 'imports')


def show_project_workspace(self, sender=None):
    project_handling_show(self, 'workspace')


def show_save_recovery(self, sender=None):
    project_handling_show(self, 'save')


SmartDAWMobileController.show_startup_actions = show_startup_actions
SmartDAWMobileController.show_recent_projects = show_recent_projects
SmartDAWMobileController.show_compatible_imports = show_compatible_imports
SmartDAWMobileController.show_project_workspace = show_project_workspace
SmartDAWMobileController.show_save_recovery = show_save_recovery


def launch_project_handling_dashboard():
    controller = SmartDAWMobileController()
    view = controller.build()
    width = view.width
    button_gap = 5
    button_width = (width - 24 - button_gap * 4) / 5.0

    controls = [
        ('Startup', controller.show_startup_actions),
        ('Recent', controller.show_recent_projects),
        ('Imports', controller.show_compatible_imports),
        ('Workspace', controller.show_project_workspace),
        ('Save', controller.show_save_recovery),
    ]

    for index, pair in enumerate(controls):
        title_text, action = pair
        button = _gui_ui.Button(
            frame=(
                12 + index * (button_width + button_gap),
                148,
                button_width,
                38,
            )
        )
        button.title = title_text
        button.font = ('<system-bold>', 11)
        button.background_color = '#3b4659'
        button.tint_color = 'white'
        button.corner_radius = 7
        button.action = action
        view.add_subview(button)

    controller.table.y = 194
    controller.output.y = 194
    controller.table.height = max(
        180, controller.table.height - 90
    )
    controller.output.height = max(
        180, controller.output.height - 90
    )

    controller.show_startup_actions()

    view.present(
        'fullscreen',
        hide_title_bar=False,
    )

    gui_runtime_log(
        'PROJECT_HANDLING_DASHBOARD_LAUNCHED',
        _GUI_PROJECT,
    )

    return controller


# === PROJECT_HANDLING_GUI_PATCH_END ===

# === PROJECT_PROTECTION_GUI_PATCH_START ===

def project_protection_lines(section='backup'):
    state = gui_load_state()
    lines = []

    if section == 'backup':
        data = state.get('backup_321_policy', {})
        lines = [
            'THREE-TWO-ONE BACKUP POLICY',
            '=' * 62,
            'Status: {}'.format(
                'PASS' if data.get('passed') else 'FAIL'
            ),
            'Minimum copies: {}'.format(
                data.get('minimum_copies')
            ),
            'Minimum media types: {}'.format(
                data.get('minimum_media_types')
            ),
            'Offsite copies: {}'.format(
                data.get('minimum_offsite_copies')
            ),
            '',
        ]

        for item in data.get('copies', []):
            lines.append(
                '{} | {} | {}'.format(
                    item.get('copy_id'),
                    item.get('media_type'),
                    item.get('location'),
                )
            )

    elif section == 'lifecycle':
        package = state.get('project_package', {})
        lifecycle = state.get('project_lifecycle', {})
        lines = [
            'PROJECT PACKAGE AND LIFECYCLE',
            '=' * 62,
            'Name: {}'.format(
                lifecycle.get('current_name')
            ),
            'Package: {}'.format(
                package.get('package_name')
            ),
            'Self-contained: {}'.format(
                package.get('self_contained')
            ),
            'Assets included: {}'.format(
                package.get('include_audio_assets')
            ),
            'Credentials included: {}'.format(
                package.get('include_credentials')
            ),
        ]

    elif section == 'templates':
        templates = state.get('adaptive_templates', {})
        lines = [
            'ADAPTIVE PROJECT TEMPLATES',
            '=' * 62,
        ]

        for template_id, item in templates.items():
            lines.extend([
                '{} | score={}'.format(
                    template_id,
                    item.get('readiness_score'),
                ),
                '  {}'.format(item.get('name')),
                '  tracks={}'.format(
                    len(item.get('tracks', []))
                ),
                '  workflow_steps={}'.format(
                    len(item.get('smart_workflow', []))
                ),
                '',
            ])

    elif section == 'alternatives':
        data = state.get('project_alternatives_engine', {})
        lines = [
            'PROJECT ALTERNATIVES',
            '=' * 62,
            'Active: {}'.format(
                data.get('active_alternative_id')
            ),
            '',
        ]

        for item in data.get('alternatives', []):
            lines.append(
                '{} | {} | {}'.format(
                    item.get('category'),
                    item.get('name'),
                    item.get('alternative_id'),
                )
            )

    elif section == 'settings':
        data = state.get('complete_project_settings', {})
        settings = data.get('settings', {})
        lines = [
            'COMPLETE PROJECT SETTINGS',
            '=' * 62,
            'Status: {}'.format(
                'PASS' if data.get('passed') else 'FAIL'
            ),
            '',
        ]

        for category, values in settings.items():
            lines.append(category.upper())
            lines.append('-' * 62)

            for key, value in values.items():
                lines.append(
                    '{}: {}'.format(key, value)
                )

            lines.append('')

    return lines


def project_protection_show(self, section):
    self.mode = 'project_protection_' + section
    self.rows = []
    self.load_table()
    self.write_output(
        project_protection_lines(section)
    )
    self.set_status(
        'Project protection view: {}'.format(section)
    )


def show_backup_policy(self, sender=None):
    project_protection_show(self, 'backup')


def show_project_lifecycle(self, sender=None):
    project_protection_show(self, 'lifecycle')


def show_adaptive_templates(self, sender=None):
    project_protection_show(self, 'templates')


def show_project_alternatives(self, sender=None):
    project_protection_show(self, 'alternatives')


def show_complete_settings(self, sender=None):
    project_protection_show(self, 'settings')


SmartDAWMobileController.show_backup_policy = show_backup_policy
SmartDAWMobileController.show_project_lifecycle = show_project_lifecycle
SmartDAWMobileController.show_adaptive_templates = show_adaptive_templates
SmartDAWMobileController.show_project_alternatives = show_project_alternatives
SmartDAWMobileController.show_complete_settings = show_complete_settings


def launch_project_protection_dashboard():
    controller = SmartDAWMobileController()
    view = controller.build()
    width = view.width
    gap = 5
    button_width = (width - 24 - gap * 4) / 5.0

    controls = [
        ('Backups', controller.show_backup_policy),
        ('Lifecycle', controller.show_project_lifecycle),
        ('Templates', controller.show_adaptive_templates),
        ('Alternatives', controller.show_project_alternatives),
        ('Settings', controller.show_complete_settings),
    ]

    for index, pair in enumerate(controls):
        title_text, action = pair
        button = _gui_ui.Button(
            frame=(
                12 + index * (button_width + gap),
                148,
                button_width,
                38,
            )
        )
        button.title = title_text
        button.font = ('<system-bold>', 10)
        button.background_color = '#46536a'
        button.tint_color = 'white'
        button.corner_radius = 7
        button.action = action
        view.add_subview(button)

    controller.table.y = 194
    controller.output.y = 194
    controller.table.height = max(
        180, controller.table.height - 90
    )
    controller.output.height = max(
        180, controller.output.height - 90
    )

    controller.show_backup_policy()

    view.present(
        'fullscreen',
        hide_title_bar=False,
    )

    gui_runtime_log(
        'PROJECT_PROTECTION_DASHBOARD_LAUNCHED',
        _GUI_PROJECT,
    )

    return controller


# === PROJECT_PROTECTION_GUI_PATCH_END ===

# === COLLABORATOR_FEATURE_PATCH_START ===

def collaborator_feature_report():
    state = gui_load_state()
    feature = state.get('collaborator_feature', {})

    return [
        'COLLABORATOR FEATURE',
        '=' * 62,
        'Enabled: {}'.format(feature.get('enabled', False)),
        'Schema version: {}'.format(feature.get('schema_version', 1)),
        'Updated: {}'.format(feature.get('updated_at', 'not yet run')),
        '',
        'This feature was added without replacing the base GUI.',
    ]


def show_collaborator_feature(self, sender=None):
    self.mode = 'collaborator_feature'
    self.rows = []
    self.load_table()
    self.write_output(collaborator_feature_report())
    self.set_status('Collaborator feature loaded')


SmartDAWMobileController.show_collaborator_feature = (
    show_collaborator_feature
)


def launch_collaborator_feature_dashboard():
    controller = SmartDAWMobileController()
    view = controller.build()

    width = view.width
    button = _gui_ui.Button(
        frame=(12, 148, width - 24, 40)
    )
    button.title = 'Collaborator Feature'
    button.font = ('<system-bold>', 12)
    button.background_color = '#46536a'
    button.tint_color = 'white'
    button.corner_radius = 7
    button.action = controller.show_collaborator_feature
    view.add_subview(button)

    controller.table.y = 196
    controller.output.y = 196
    controller.table.height = max(
        180, controller.table.height - 92
    )
    controller.output.height = max(
        180, controller.output.height - 92
    )

    controller.show_collaborator_feature()

    view.present(
        'fullscreen',
        hide_title_bar=False,
    )

    gui_runtime_log(
        'COLLABORATOR_FEATURE_LAUNCHED',
        _GUI_PROJECT,
    )

    return controller

# === COLLABORATOR_FEATURE_PATCH_END ===
