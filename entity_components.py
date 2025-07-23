import abc
import pygame

import game_vars
from game_vars import Vector2
from my_utilities import *
from abc import *


class Component(abc.ABC):
    pass


class CRender(Component):

    def __init__(self, sprite: Sprite):
        self.sprite = sprite


class CInput(Component):
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False


class CMovement(Component):
    def __init__(self, posx: float, posy: float):
        self.position = Vector2(x=posx, y=posy)
        self.previous_position = self.position.copy()
        self.speed = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def apply_force(self, force: Vector2):
        self.velocity += force

    def __str__(self):
        return f"Pos:{self.position} Vel:{self.velocity} Speed:{self.speed} Acc:{self.acceleration}"


class CHealth(Component):
    def __init__(self, max_health: int = 100):
        self.max_hp = max_health
        self.hp = max_health


class CCollision(Component):
    def __init__(self, rect: pygame.Rect):
        self.shape = rect
        self.type = "Box"
        self.position = Vector2(0.0, 0.0)


class CType(Component):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Type({self.value})"


class COwner(Component):
    def __init__(self, owner_entity):
        self.owner = owner_entity

    def __str__(self):
        return f"Owner:({self.owner})"


class CAttack(Component):
    def __init__(self, attack_dmg, attack_speed):
        self.dmg = attack_dmg
        self.attack_timer = 0
        self.attack_speed = attack_speed


class CEquipment(Component):
    def __init__(self):
        pass


class CState:
    def __init__(self, entity):
        self.state_machine = StateMachine(IdleState(entity))


class CPathfindingData:
    def __init__(self):
        self.path = None
        self.need_update = False


class CNode(Component):
    def __init__(self, node):
        self.node: 'Node' = node


class Node:
    def __init__(self, x, y, walkable):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = 0
        self.parent = None

    def __repr__(self):
        return f"Node:({self.x},{self.y})"

    def __str__(self):
        return f"Node:({self.x},{self.y})"

    def __lt__(self, other):
        return self.f_cost < other.f_cost


class BaseEntityState(ABC):
    def __init__(self, entity):
        self.entity = entity

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def execute(self, delta_time: float):
        pass


class IdleState(BaseEntityState):
    def enter(self):
        pass
        # if self.entity.name != "Projectile":
        #     print(f"Entering IdleState for {self.entity}")

    def exit(self):
        pass
        # if self.entity.name != "Projectile":
        #     print(f"Exiting IdleState for {self.entity}")

    def execute(self, delta_time: float):
        if self._should_start_moving_towards_player():
            self.start_moving_towards_player()

    def _should_start_moving_towards_player(self):
        return self.player_is_in_enemy_sight()

    def start_moving_towards_player(self):
        path_component: CPathfindingData = self.entity.get_component(CPathfindingData)
        path_component.need_update = True
        path_to_player = path_component.path
        if path_to_player is not None:
            state_machine = self.entity.get_component(CState).state_machine
            state_machine.change_state(MovingState(self.entity))

    def player_is_in_enemy_sight(self):
        return self.is_player_within_range() and not self.is_obstacle_between_enemy_and_player()

    def is_player_within_range(self):
        return True

    def is_obstacle_between_enemy_and_player(self):
        return False


class MovingState(BaseEntityState):
    def __init__(self, entity):
        super().__init__(entity)
        self.current_node = None

    def enter(self):
        print(f"Moving entered: {self.entity}")

    def exit(self):
        print(f"Moving exited: {self.entity}")

    def execute(self, delta_time: float):
        if self.entity.has_component(CPathfindingData):
            pathfinding_component: CPathfindingData = self.entity.get_component(CPathfindingData)
            path_to_follow = pathfinding_component.path

            if pathfinding_component.need_update:
                self.current_node = None
                return

            if self.current_node is None and path_to_follow:
                self.current_node = path_to_follow.pop(0)

            if self.current_node:
                self.move_to_node(delta_time)

            if (not path_to_follow or len(path_to_follow) < 1) and not self.current_node:
                state_machine: StateMachine = self.entity.get_component(CState).state_machine
                state_machine.change_state(IdleState(self.entity))

    def move_to_node(self, delta_time: float):
        targetx, targety = grid_to_world(self.current_node, (SPRITE_SIZE, SPRITE_SIZE))
        target = Vector2(targetx, targety)

        movement_comp: CMovement = self.entity.get_component(CMovement)

        distance = (target - movement_comp.position)
        direction = distance
        if distance.length() > 0:
            direction = distance.normalize()

        # max_seek_speed = 0.5
        desired_velocity = direction #* max_seek_speed
        steering = desired_velocity - movement_comp.velocity
        print(self.current_node,target, distance)
        movement_comp.velocity += steering

        if (movement_comp.position - target).length() < SPRITE_SIZE:
            self.current_node = None


class KnockbackState(BaseEntityState):
    def __init__(self, entity, direction, force):
        super().__init__(entity)
        self.direction = direction
        self.force = force

    def enter(self):
        print(f"Entering KnockBack {self.entity.name}")
        movement_component: CMovement = self.entity.get_component(CMovement)
        movement_component.apply_force(self.direction * self.force)

    def exit(self):
        print(f"Exiting KnockBack {self.entity.name}")
        movement_component: CMovement = self.entity.get_component(CMovement)
        movement_component.velocity = Vector2(0, 0)  # Stop knockback

    def execute(self, delta_time: float):
        state_component: CState = self.entity.get_component(CState)
        state_component.state_machine.state_timer -= delta_time
        if state_component.state_machine.state_timer <= 0:
            state_component.state_machine.change_state(IdleState(self.entity))


class StateMachine:
    def __init__(self, initial_state: BaseEntityState):
        self.current_state = initial_state
        self.current_state.enter()
        self.state_timer = 0

    def change_state(self, new_state: BaseEntityState, duration: float = 0):
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()
        self.state_timer = duration

    def update(self, delta_time: float):
        self.current_state.execute(delta_time)


def get_entity_pos(entity):
    if entity:
        if entity.has_component(CMovement):
            mvm = entity.get_component(CMovement)
            return mvm.position
    return None


def position_changed(entity):
    if entity:
        if entity.has_component(CMovement):
            mvm: CMovement = entity.get_component(CMovement)
            return mvm.previous_position != mvm.position


def map_node_pos_to_world_pos(map_node: Node):
    return map_node.x * SPRITE_SIZE, map_node.y * SPRITE_SIZE