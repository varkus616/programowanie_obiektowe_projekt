from entity_components import *
from pygame.math import Vector2


class Command(abc.ABC):
    def __init__(self, should_undo: bool = False):
        self.should_undo = should_undo

    @abc.abstractmethod
    def execute(self, dt):
        raise NotImplemented

    @abc.abstractmethod
    def undo(self):
        raise NotImplemented

    def perform(self, dt):
        if self.should_undo:
            self.undo()
        else:
            self.execute(dt)


class MoveCommand(Command):
    def __init__(self, entity, dx: float, dy: float, should_undo: bool = False):
        super().__init__(should_undo)
        self.entity = entity
        self.dx = dx
        self.dy = dy

    def execute(self, dt):
        if self.entity.has_component(CMovement):
            movement_component: CMovement = self.entity.get_component(CMovement)
            movement_component.speed += Vector2(self.dx, self.dy)

    def undo(self):
        if self.entity.has_component(CMovement):
            movement_component: CMovement = self.entity.get_component(CMovement)
            # if movement_component.velocity.length() > 0:
            # movement_component.velocity -= Vector2(self.dx, self.dy)


class ShootFireballCommand(Command):
    def __init__(self, start_pos: Vector2,
                 direction: Vector2,
                 entity_manager,
                 fireball_sprite: Sprite,
                 owner: str,
                 should_undo: bool = False):
        super().__init__(should_undo)
        self.start_pos: Vector2 = start_pos
        direction_pos: Vector2 = direction
        self.entity_manager = entity_manager
        self.fireball_sprite: Sprite = fireball_sprite

        self.direction: Vector2 = direction_pos - self.start_pos
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.owner = owner

    def execute(self, dt):
        e = self.entity_manager.create_entity()
        e.name = "Projectile"
        render_component: CRender = CRender(self.fireball_sprite)
        movement_component: CMovement = CMovement(
            self.start_pos.x,
            self.start_pos.y
        )

        coll_rect: pygame.Rect = render_component.sprite.get_rect()
        collision_component: CCollision = CCollision(coll_rect.copy())
        movement_component.speed = Vector2(2, 2)
        movement_component.velocity = movement_component.speed.elementwise() * self.direction

        e.add_component(render_component)
        e.add_component(movement_component)
        e.add_component(collision_component)
        e.add_component(CType("Projectile"))
        e.add_component(COwner(self.owner))
        e.add_component(CHealth())
        e.add_component(CAttack(10, 0))

        self.entity_manager.add_entity(e)
        # print(f"Entity {e} shoots fireball!")

    def undo(self):
        pass