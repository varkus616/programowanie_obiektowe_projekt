class EventType:
    ENTITY_ADDED = "entity_added"
    ENTITY_REMOVED = "entity_removed"
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"
    ENTITY_COLLISION = "entity_collision"
    PLAYER_POSITION_CHANGED = "player_position_changed"


class EventSystem:
    def __init__(self):
        self.listeners = {
            EventType.ENTITY_ADDED: [],
            EventType.ENTITY_REMOVED: [],
            EventType.COMPONENT_ADDED: [],
            EventType.COMPONENT_REMOVED: [],
            EventType.ENTITY_COLLISION: [],
            EventType.PLAYER_POSITION_CHANGED: [],
        }

    def register_listener(self, event_type, listener):
        if event_type in self.listeners:
            self.listeners[event_type].append(listener)

    def remove_listener(self, event_type, listener_to_remove):
        if event_type in self.listeners:
            if listener_to_remove in self.listeners[event_type]:
                self.listeners[event_type].remove(listener_to_remove)

    def emit(self, event_type: EventType, data):
        if EventType.ENTITY_ADDED:
            pass
        else:
            print(f"EVENT: Type({event_type}), Data({data})")
        if event_type in self.listeners:
            # print(f"EMITED EVENT: ({event_type}, {data})")
            for listener in self.listeners[event_type]:
                listener(data)
