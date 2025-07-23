import keyword
import platform
from threading import Timer
import copy
import pygame.time

import game_vars
from entity_components import *
from command import MoveCommand
from event_system import *
from entity import damage_entity


class RenderSystem:
    def __init__(self, window, entity_manager):
        self.window = window
        self.entity_manager: 'EntityManager' = entity_manager

    def render(self):
        renderable_entities = self.entity_manager.get_entities()
        for entity in renderable_entities:
            if entity.has_component(CMovement):
                render_component: CRender = entity.get_component(CRender)
                movement_component: CMovement = entity.get_component(CMovement)
                render_component.sprite.set_position(tuple(movement_component.position))
                render_component.sprite.draw(self.window)

                if entity.has_component(CHealth):
                    health_component: CHealth = entity.get_component(CHealth)
                    type_component: CType = entity.get_component(CType)
                    if type_component.value != "Projectile":
                        self.__draw_health_bar(health_component, render_component, movement_component, self.window)

    def __draw_health_bar(self, health_component: CHealth,
                          render_component: CRender,
                          movement_component: CMovement,
                          window):
        x, y = movement_component.position

        health_bar_len = render_component.sprite.get_rect().w
        health_bar_ratio = health_component.max_hp / health_bar_len
        if health_bar_ratio > 0:
            pygame.draw.rect(window, (255, 0, 0),
                             (x, y-2, health_component.hp / health_bar_ratio, 5))
            pygame.draw.rect(window, (255, 255, 255),
                             (x, y-2, health_bar_len, 7), 2)


class HealthSystem:

    def __init__(self, event_system):
        self.event_system = event_system

    def update(self, entities):
        for entity in entities:
            if entity.has_component(CHealth):
                entity_health: CHealth = entity.get_component(CHealth)
                if entity_health.hp <= 0:
                    self.event_system.emit(EventType.ENTITY_REMOVED, entity)


class MovementSystem:
    def update(self, entities, delta_time: float):
        for entity in entities:
            if entity.has_component(CMovement):
                movement_component: CMovement = entity.get_component(CMovement)

                movement_component.previous_position = movement_component.position.copy()

                if entity.has_component(CInput):
                    movement_component.velocity = Vector2(0, 0)
                    input_component: CInput = entity.get_component(CInput)
                    if input_component.up:
                        movement_component.velocity.y = -1
                    if input_component.down:
                        movement_component.velocity.y = 1
                    if input_component.left:
                        movement_component.velocity.x = -1
                    if input_component.right:
                        movement_component.velocity.x = 1

                    if movement_component.velocity.length() > 0:
                        movement_component.velocity.normalize()

                # movement_component.velocity += movement_component.speed * delta_time
                movement_component.velocity += movement_component.acceleration * delta_time
                movement_component.position += movement_component.velocity
                movement_component.acceleration = Vector2(0, 0)

                if entity.has_component(CCollision):
                    collider: CCollision = entity.get_component(CCollision)
                    collider.position = movement_component.position
                    collider.shape.x = collider.position.x
                    collider.shape.y = collider.position.y


class CommandSystem:
    def __init__(self):
        self.command_queue = []

    def add_command(self, command):
        self.command_queue.append(command)

    def remove_command(self, command):
        if command in self.command_queue:
            self.command_queue.remove(command)

    def clear_commands(self):
        self.command_queue = []

    def execute_commands(self, dt):
        for command in self.command_queue:
            # print(command)
            command.perform(dt)
        self.clear_commands()


class CollisionSystem:
    def __init__(self, world_size: tuple, event_system: EventSystem):
        self.collidable_entities = []
        self.world_size = world_size
        self.event_system = event_system

        self.event_system.register_listener(EventType.COMPONENT_ADDED, self.on_component_added)
        self.event_system.register_listener(EventType.COMPONENT_REMOVED, self.on_component_removed)
        self.event_system.register_listener(EventType.ENTITY_REMOVED, self.on_entity_removed)
        self.event_system.register_listener(EventType.ENTITY_ADDED, self.on_entity_added)

    def on_entity_added(self, entity):
        if entity.has_component(CCollision):
            self.collidable_entities.append(entity)

    def on_component_added(self, data):
        entity, component_type = data
        if component_type == CCollision:
            self.collidable_entities.append(entity)

    def on_component_removed(self, data):
        entity, component_type = data
        if component_type == CCollision:
            self.collidable_entities.remove(entity)

    def on_entity_removed(self, entity):
        if entity in self.collidable_entities:
            self.collidable_entities.remove(entity)

    def update(self, dt):
        world_size_x, world_size_y = self.world_size
        for entity in self.collidable_entities:
            if entity.has_component(CCollision):

                collider: CCollision = entity.get_component(CCollision)

                if (collider.position.x + collider.shape.width >= world_size_x
                        or collider.position.x <= 0
                        or collider.position.y + collider.shape.height >= world_size_y
                        or collider.position.y <= 0):
                    self.event_system.emit(EventType.ENTITY_COLLISION, (dt, entity, None))

                for other_entity in self.collidable_entities:
                    if entity == other_entity:
                        continue
                    if other_entity.has_component(CCollision):

                        other_collider = other_entity.get_component(CCollision)

                        if self.check_collision(collider, other_collider):
                            self.event_system.emit(EventType.ENTITY_COLLISION, (dt, entity, other_entity))

    @staticmethod
    def check_collision(collider: CCollision,
                        other_collider: CCollision) -> bool:
        if collider.type == "Box" and other_collider.type == "Box":
            pos1 = collider.position
            pos2 = other_collider.position

            box1 = collider.shape
            box2 = collider.shape

            bb1 = (pos1.x + box1.w,
                   pos1.y + box1.h)

            bb2 = (pos2.x + box2.w,
                   pos2.y + box2.h)

            return pos1.x < bb2[0] and \
                bb1[0] > pos2.x and \
                pos1.y < bb2[1] and bb1[1] > pos2.y

        return False

    def draw_bounding_boxes(self, window: pygame.surface.Surface):
        for entity in self.collidable_entities:
            color = (255, 0, 0)
            if entity.name == "Player":
                color = (175, 70, 140)
            collidable: CCollision = entity.get_component(CCollision)
            pygame.draw.rect(window, color, collidable.shape, 2)


class CollisionResolver:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.event_system.register_listener(EventType.ENTITY_COLLISION, self.resolve_collision)

    def resolve_collision(self, data):
        dt, entity, other_entity = data
        entity_type = entity.get_component(CType)

        if not other_entity:  # Entity out of map
            self._handle_out_of_map_collision(entity, entity_type)
            return

        collision_handlers = {
            'Player': self._handle_player_collision,
            'Enemy': self._handle_enemy_collision,
            'Obstacle': self._handle_obstacle_collision,
        }

        handler = collision_handlers.get(entity_type.value)
        if handler:
            other_entity_type = other_entity.get_component(CType)
            handler(dt, entity, other_entity, other_entity_type)

    def _handle_out_of_map_collision(self, entity, entity_type):
        if entity_type.value == "Player":
            player_mvm = entity.get_component(CMovement)
            player_mvm.position = player_mvm.previous_position
        else:
            self.event_system.emit(EventType.ENTITY_REMOVED, entity)

    def _handle_player_collision(self, dt, player, other_entity, other_entity_type):
        collision_responses = {
            'Enemy': self._player_collides_with_enemy,
            'Projectile': self._player_collides_with_projectile,
            'Obstacle': self._obstacle_entity_collision,
        }
        self._process_collision_response(dt, player, other_entity, other_entity_type, collision_responses)

    def _handle_enemy_collision(self, dt, enemy, other_entity, other_entity_type):
        collision_responses = {
            'Player': self._player_collides_with_enemy,
            'Projectile': self._projectile_collides_with_entity,
            'Obstacle': self._obstacle_entity_collision,
        }
        self._process_collision_response(dt, enemy, other_entity, other_entity_type, collision_responses)

    def _handle_obstacle_collision(self, dt, obstacle, other_entity, other_entity_type):
        collision_responses = {
            'Player': self._obstacle_entity_collision,
            'Enemy': self._obstacle_entity_collision,
            'Projectile': self._obstacle_projectile_collision,
        }
        self._process_collision_response(dt, obstacle, other_entity, other_entity_type, collision_responses)

    def _process_collision_response(self, dt, entity, other_entity, other_entity_type, collision_responses):
        response = collision_responses.get(other_entity_type.value)
        if response:
            response(dt, entity, other_entity, other_entity_type)

    def _obstacle_entity_collision(self, dt, entity, other_entity, other_entity_type):
        entity_type = entity.get_component(CType)
        other_entity_type = other_entity.get_component(CType)

        if entity_type.value == "Obstacle":
            self.__obstacle_collision(entity, other_entity)
        elif other_entity_type.value == "Obstacle":
            self.__obstacle_collision(other_entity, entity)
        else:
            return

    def __obstacle_collision(self, obstacle, other_entity):
        entity_movement = other_entity.get_component(CMovement)
        entity_movement.position = entity_movement.previous_position

        if other_entity.has_component(CPathfindingData):
            pathfinding_component = other_entity.get_component(CPathfindingData)
            pathfinding_component.need_update = True

    def _projectile_collides_with_entity(self, dt, entity, other_entity, other_entity_type):
        entity_type = entity.get_component(CType)
        other_entity_type = other_entity.get_component(CType)

        if entity_type.value == "Projecitle":
            self.__projectile_collision(entity, other_entity)

        elif other_entity_type.value == "Projectile":
            self.__projectile_collision(other_entity, entity)
        else:
            return

    def _obstacle_projectile_collision(self, dt, entity, other_entity, other_entity_type):
        if other_entity_type.value == "Projectile":
            self.event_system.emit(EventType.ENTITY_REMOVED, entity)
            self.event_system.emit(EventType.ENTITY_REMOVED, other_entity)


    def __projectile_collision(self, projectile, entity):
        damage_entity(projectile, entity)

        projectile_mvm: CMovement = projectile.get_component(CMovement)

        knockback_direction: Vector2 = projectile_mvm.velocity

        if knockback_direction.length() > 0:
            knockback_direction.normalize()

        state_machine: StateMachine = entity.get_component(CState).state_machine
        state_machine.change_state(KnockbackState(entity, knockback_direction, 2.5), 0.1)

        self.event_system.emit(EventType.ENTITY_REMOVED, projectile)

    def _player_collides_with_enemy(self, dt, player: 'Entity', enemy: 'Entity', other_entity_type):

        player_health = player.get_component(CHealth)
        player_attack = player.get_component(CAttack)

        enemy_health = enemy.get_component(CHealth)
        enemy_attack = enemy.get_component(CAttack)

        if player_health and player_attack and enemy_attack and enemy_health:

            player_attack.attack_timer += dt
            enemy_attack.attack_timer += dt

            player_mvm: CMovement = player.get_component(CMovement)
            enemy_mvm: CMovement = enemy.get_component(CMovement)

            if player_attack.attack_timer >= player_attack.attack_speed:
                enemy_health.hp -= player_attack.dmg
                player_attack.attack_timer = 0

                state_machine: StateMachine = enemy.get_component(CState).state_machine
                if player_mvm.velocity.length() != 0:
                    knockback_dir = player_mvm.velocity.normalize()
                else:
                    knockback_dir = enemy_mvm.position - player_mvm.position

                state_machine.change_state(KnockbackState(enemy, knockback_dir, 2), 0.5)

            if enemy_attack.attack_timer >= enemy_attack.attack_speed:
                player_health.hp -= enemy_attack.dmg
                enemy_attack.attack_timer = 0

    def _player_collides_with_projectile(self, dt, player, projectile, other_entity_type ):
        print(f"{player} - {projectile} Collision!")


class InputSystem:
    def update(self, entities):
        keys = pygame.key.get_pressed()
        for entity in entities:
            if entity.has_component(CInput):
                input_component: CInput = entity.get_component(CInput)
                input_component.up = keys[pygame.K_w]
                input_component.down = keys[pygame.K_s]
                input_component.left = keys[pygame.K_a]
                input_component.right = keys[pygame.K_d]


class FSMSystem:
    def update(self, entites, map_grid, dt):
        for entity in entites:
            if entity.has_component(CState):
                state_machine: StateMachine = entity.get_component(CState).state_machine
                state_machine.update(dt)


class PathfindingSystem:

    def __init__(self, map_grid: list, player: 'Entity', window):
        self.map_grid: list = map_grid
        self.player = player
        self.window = window

    def update(self, entities):
        for entity in entities:
            if entity.has_component(CPathfindingData):
                pathfinding_component: CPathfindingData = entity.get_component(CPathfindingData)

                if pathfinding_component.need_update:
                    player_pos = get_entity_pos(self.player)
                    entity_pos = get_entity_pos(entity)

                    pathfinding_component.path = a_star_search(self.map_grid,
                                                               world_to_grid(entity_pos, (SPRITE_SIZE, SPRITE_SIZE)),
                                                               world_to_grid(player_pos, (SPRITE_SIZE, SPRITE_SIZE)))
                    pathfinding_component.need_update = False

                # if position_changed(self.player):
                #     pathfinding_component.need_update = True

    def draw_paths(self, entities):
        for i, entity in enumerate(entities):
            if entity.has_component(CPathfindingData):
                pathfinding_component: CPathfindingData = entity.get_component(CPathfindingData)
                if pathfinding_component.path:
                    for node in pathfinding_component.path:
                        color = (255 % i, 0, 255 % i)
                        pygame.draw.rect(self.window, color, (node[0] * SPRITE_SIZE, node[1] * SPRITE_SIZE,
                                                                            SPRITE_SIZE, SPRITE_SIZE), 1)