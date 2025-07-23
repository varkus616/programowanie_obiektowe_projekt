from entity_components import *
from event_system import *
import pygame
from abc import ABC, abstractmethod


class EntityManager:
    """This class is a container for entities in the game."""
    def __init__(self, event_system: EventSystem):
        self.__entities = []
        self.__enemies = []
        self.__items = []
        self.__mobs = []
        self.__projectiles = []
        self.__to_remove = []
        self.__to_add = []
        self.__map_grid = []

        self.__components = {}

        self.event_system = event_system
        self.event_system.register_listener(EventType.ENTITY_REMOVED, self.on_entity_removed)

    def create_entity(self) -> 'Entity':
        entity = Entity._create(self)
        return entity

    def add_entity(self, entity: 'Entity'):
        self.__to_add.append(entity)
        self.event_system.emit(EventType.ENTITY_ADDED, entity)

    def _add_entities(self, dt):
        for entity in self.__to_add:
            if entity.has_component(CNode):
                self.__map_grid.append(entity.get_component(CNode).node)
            # if entity.name == ''
            # if entity.name == "Enemy":
            #     self.__enemies.append(entity)
            # elif entity.name == "Projectile":
            #     self.__projectiles.append(entity)

            self.__entities.append(entity)
        self.__to_add.clear()

    def remove_entity(self, entity: 'Entity'):
        self.__to_remove.append(entity)
        self.event_system.emit(EventType.ENTITY_REMOVED, entity)

    def _remove_entities(self, dt):
        for entity in self.__to_remove:
            if entity.has_component(CNode):
                self.__map_grid.remove(entity.get_component(CNode).node)
            # if entity.name == "Enemy":
            #     self.__enemies.remove(entity)
            # elif entity.name == "Projectile":
            #     self.__projectiles.remove(entity)

            entity_id = entity.id

            for component_list in self.__components.values():
                if entity_id < len(component_list):
                    component_list[entity_id] = None

            self.__entities.remove(entity)
            entity = None
        self.__to_remove.clear()

    def clear_entities(self):
        self.__entities.clear()
        self.__enemies.clear()
        self.__items.clear()
        self.__mobs.clear()
        self.__projectiles.clear()
        self.__components.clear()

    def add_component(self, entity_id: int, component: Component):
        component_type_name = type(component).__name__
        if component_type_name not in self.__components:
            self.__components[component_type_name] = []

        component_list: list = self.__components[component_type_name]

        while len(component_list) <= entity_id:
            component_list.append(None)

        component_list[entity_id] = component

    def remove_component(self, entity_id: int, component: Component):
        component_type_name = type(component).__name__
        if component_type_name in self.__components:
            component_list = self.__components[component_type_name]
            if entity_id < len(component_list):
                component_list[entity_id] = None

    def get_component(self, entity_id: int, component_type: type) -> 'Component':
        component_type_name = component_type.__name__
        if component_type_name in self.__components:
            component_list = self.__components[component_type_name]
            if entity_id < len(component_list):
                return component_list[entity_id]
        return None

    def has_component(self, entity_id: int, component_type: type) -> bool:
        component_type_name = component_type.__name__
        if component_type_name in self.__components:
            component_list = self.__components[component_type_name]
            return entity_id < len(component_list) and component_list[entity_id] is not None
        return False

    def on_entity_removed(self, entity):
        self.__to_remove.append(entity)

    def update(self, dt):
        self._add_entities(dt)
        self._remove_entities(dt)

    def get_entities(self):
        return self.__entities

    def get_entities_id_with_component(self, component_type: type) -> list:
        component_type_name = component_type.__name__
        if component_type_name in self.__components:
            component_list = self.__components[component_type_name]
            return [idx for idx, comp in enumerate(component_list) if comp is not None]
        return []

    def get_map(self):
        return self.__map_grid


class Entity:
    _id = 0

    def __init__(self, entity_manager: EntityManager):
        self.name = ""
        self.id = Entity._id
        Entity._id += 1

        self.entity_manager: EntityManager = entity_manager

    def __str__(self):
        # self.entity_manager.get
        return f"Entity(id:{self.id} - {self.name})"

    def add_component(self, component: Component):
        self.entity_manager.add_component(self.id, component)

    def remove_component(self, component: Component):
        self.entity_manager.remove_component(self.id, component)

    def get_component(self, component_type: type) -> Component:
        return self.entity_manager.get_component(self.id, component_type)

    def has_component(self, component_type: type) -> bool:
        return self.entity_manager.has_component(self.id, component_type)

    @classmethod
    def _create(cls, entity_manager: 'EntityManager') -> 'Entity':
        return cls(entity_manager)


def damage_entity(entity, other_entity):
    entity_attack = entity.get_component(CAttack)

    other_entity_health = other_entity.get_component(CHealth)

    if entity_attack and other_entity_health:
        other_entity_health.hp -= entity_attack.dmg


class AbstractEntityFactory(ABC):
    @abstractmethod
    def create_entity(self):
        pass


class ProjectileFactory(AbstractEntityFactory):
    def __init__(self, entity_manager, fireball_sprite, start_pos, direction, owner):
        self.entity_manager = entity_manager
        self.fireball_sprite = fireball_sprite
        self.start_pos = start_pos
        self.direction = direction
        self.owner = owner

    def create_entity(self):
        e = self.entity_manager.create_entity()
        e.name = "Projectile"
        render_component = CRender(self.fireball_sprite)
        movement_component = CMovement(
            self.start_pos.x,
            self.start_pos.y
        )

        coll_rect = render_component.sprite.get_rect()
        collision_component = CCollision(coll_rect.copy())
        movement_component.velocity = Vector2(200, 200)
        movement_component.velocity = movement_component.velocity.elementwise() * self.direction
        movement_component.friction_coefficient = 0.0005

        e.add_component(render_component)
        e.add_component(movement_component)
        e.add_component(collision_component)
        e.add_component(CType("Projectile"))
        e.add_component(COwner(self.owner))
        e.add_component(CHealth())
        e.add_component(CAttack(10, 0))

        self.entity_manager.add_entity(e)
        return e


class EnemyFactory(AbstractEntityFactory):
    def __init__(self, entity_manager, sprite_sheet):
        self.entity_manager = entity_manager
        self.sprite_sheet = sprite_sheet

    def create_entity(self, pos):
        e = self.entity_manager.create_entity()
        e.name = "Enemy"
        render_component = CRender(self.sprite_sheet.get_sprite(148))
        render_component.sprite.set_position(pos)

        movement_component = CMovement(pos.x, pos.y)
        movement_component.friction_coefficient = 1

        health_component = CHealth()

        collision_component = CCollision(render_component.sprite.get_rect().copy())

        e.add_component(render_component)
        e.add_component(movement_component)
        e.add_component(health_component)
        e.add_component(collision_component)
        e.add_component(CType("Enemy"))
        e.add_component(CAttack(10, 1))
        e.add_component(CState(e))
        e.add_component(CPathfindingData())

        self.entity_manager.add_entity(e)
        return e


class TileFactory(AbstractEntityFactory):
    def __init__(self, entity_manager, state_context, tileset):
        self.entity_manager = entity_manager
        self.asset_manager = state_context.ASSET_MANAGER
        self.tileset = tileset

    def create_entity(self, img_src, tile_image, x, y, layer_name):
        texture = self.asset_manager.get_texture(img_src)
        if texture:

            e = self.entity_manager.create_entity()
            e.name = "Tile"
            tile_width, tile_height = self.tileset.tilewidth, self.tileset.tileheight

            rect = tile_image[1]
            posx, posy = rect[0], rect[1]

            sprite_rect = pygame.Rect(posx, posy, tile_width, tile_height)
            sprite = Sprite(texture, sprite_rect)
            render_component = CRender(sprite)

            movement_component = CMovement(x * tile_width, y * tile_height)

            if layer_name == "Walls":
                e.add_component(CType("Obstacle"))
                e.add_component(CCollision(sprite_rect.copy()))
                node_component: CNode = CNode(Node(x,
                                                   y, False))
                e.add_component(node_component)


            e.add_component(movement_component)
            e.add_component(render_component)
            self.entity_manager.add_entity(e)
            return e
        else:
            return None


