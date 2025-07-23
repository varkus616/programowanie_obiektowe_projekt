import sys

import game_vars
import state_manager
import animator
import pygame
from my_utilities import *
from game_vars import *
from entity import *
from command import *
from event_system import *
from entity_systems import *
import pytmx


class GameState(state_manager.State):
    def __init__(self, state_manager, state_context):
        super().__init__(state_manager, state_context)

        self.state_context.ASSET_MANAGER.load_texture(DATA_PATH + "terrain.png")
        self.state_context.ASSET_MANAGER.load_sound(DATA_PATH + "projectile_sound.wav")


        self.sprite_sheet = SpriteSheet("terrain.png", 32, 32)

        self.EVENT_SYSTEM = EventSystem()

        self.ENTITY_MANAGER = EntityManager(self.EVENT_SYSTEM)

        self.COMMAND_SYSTEM = CommandSystem()
        self.RENDER_SYSTEM = RenderSystem(self.state_context.WINDOW, self.ENTITY_MANAGER)
        self.MOVEMENT_SYSTEM = MovementSystem()

        self.COLLISION_SYSTEM = CollisionSystem(self.state_context.WINDOW.get_size(),
                                                self.EVENT_SYSTEM)

        self.COLLISION_RESOLVER = CollisionResolver(self.EVENT_SYSTEM)

        self.HEALTH_SYSTEM = HealthSystem(self.EVENT_SYSTEM)
        self.INPUT_SYSTEM = InputSystem()

        self.FSM_SYSTEM = FSMSystem()



        self.map_data = None
        self.load_from_file("Maps/Dungeon/dungeon.tmx")
        self.player = None
        self.create_player()

        self.ENTITY_MANAGER.update(0)

        obstacles = self.ENTITY_MANAGER.get_map()

        gridw = game_vars.MAP_SIZE[0]
        gridh = game_vars.MAP_SIZE[1]
        self.map_grid = [[0 for y in range(gridw)] for x in range(gridh)]

        for node in obstacles:
            self.map_grid[node.y][node.x] = 1

        self.PATHFINDING_SYSTEM = PathfindingSystem(self.map_grid, self.player, self.state_context.WINDOW)

        self.path = None
        self.astar_timer = 0
        self.draw_boxes = False
        self.font = pygame.font.SysFont("comicsansms", 7)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_stack_switch("Menu State")
            if event.key == pygame.K_SPACE:

                pos: Vector2 = self.player.get_component(CMovement).position
                fsprite = self.sprite_sheet.get_sprite(421)

                mouse_pos = Vector2(0, 0)

                mouse_pos.x, mouse_pos.y = pygame.mouse.get_pos()

                f = ShootFireballCommand(pos, mouse_pos, self.ENTITY_MANAGER, fsprite, "Player")
                self.COMMAND_SYSTEM.add_command(f)

            if event.key == pygame.K_t:
                mvmnt: CMovement = self.player.get_component(CMovement)
                new_pos = pygame.mouse.get_pos()
                mvmnt.position.x = new_pos[0]
                mvmnt.position.y = new_pos[1]

            if event.key == pygame.K_e:
                if self.draw_boxes:
                    self.draw_boxes = False
                else:
                    self.draw_boxes = True

    def update(self, dt):
        self.INPUT_SYSTEM.update(self.ENTITY_MANAGER.get_entities())
        self.COMMAND_SYSTEM.execute_commands(dt)
        self.PATHFINDING_SYSTEM.update(self.ENTITY_MANAGER.get_entities())
        self.FSM_SYSTEM.update(self.ENTITY_MANAGER.get_entities(), self.map_grid, dt)
        self.ENTITY_MANAGER.update(dt)
        self.MOVEMENT_SYSTEM.update(self.ENTITY_MANAGER.get_entities(), dt)
        self.COLLISION_SYSTEM.update(dt)
        self.HEALTH_SYSTEM.update(self.ENTITY_MANAGER.get_entities())

        # print(world_to_grid(get_entity_pos(self.player), (32,32)))

        if position_changed(self.player):
            self.EVENT_SYSTEM.emit(EventType.PLAYER_POSITION_CHANGED,
                                   (self.ENTITY_MANAGER.get_entities(),
                                    get_entity_pos(self.player)))

    def render(self):
        self.RENDER_SYSTEM.render()
        self.PATHFINDING_SYSTEM.draw_paths(self.ENTITY_MANAGER.get_entities())
        # if self.draw_boxes:
        #     self.COLLISION_SYSTEM.draw_bounding_boxes(self.state_context.WINDOW)
        #     if self.path:
        #         for node in self.path:
        #             color = (0, 0, 255)
        #             pygame.draw.rect(self.state_context.WINDOW, color, (node.x * 32, r * 32,
        #                                                             32, 32), 3)
        #     if self.map_grid:
        #         for y, row in enumerate(self.map_grid):
        #             for x, column in enumerate(row):
        #                 color = (0, 255, 0)
        #                 if column == 1:
        #                     pygame.draw.rect(self.state_context.WINDOW, color, (x * SPRITE_SIZE, y * SPRITE_SIZE,
        #                                                                     SPRITE_SIZE, SPRITE_SIZE), 1)

    def load_from_file(self, name: str):
        try:
            self.map_data = pytmx.TiledMap(name)
            sprites = pygame.sprite.Group()

            for tileset in self.map_data.tilesets:
                img_src = tileset.source
                self.state_context.ASSET_MANAGER.load_texture(img_src)

            for layer in self.map_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    print(f"Layer size:{layer.width, layer.height}")
                    for x, y, gid in layer:
                        if gid == 0:
                            continue
                        tile_image = self.map_data.get_tile_image_by_gid(gid)
                        if tile_image:
                            tileset = self.map_data.get_tileset_from_gid(gid)

                            img_src = tileset.source

                            texture = self.state_context.ASSET_MANAGER.get_texture(img_src)

                            if texture:
                                factory = TileFactory(self.ENTITY_MANAGER, self.state_context, tileset)
                                tile_entity = factory.create_entity(img_src, tile_image, x, y, layer.name)

            for obj in self.map_data.objects:
                pos = Vector2(obj.x, obj.y)
                obj_type = obj.type
                i = 0
                if obj_type == "Enemy":
                    if i < 1:
                        factory = EnemyFactory(self.ENTITY_MANAGER, self.sprite_sheet)
                        enemy_entity = factory.create_entity(pos)
                        i += 1

        except FileNotFoundError as msg:
            print(f"CANNOT LOAD MAP ( FILE NOT FOUND ):{name}", msg)
            exit(1)

    def create_player(self):
        player_sprite = self.sprite_sheet.get_sprite(132)

        self.player = self.ENTITY_MANAGER.create_entity()
        self.player.name = "Player"

        self.player.add_component(CRender(player_sprite))
        self.player.add_component(CMovement(15, 15))
        self.player.add_component(CHealth(100))
        self.player.add_component(CCollision(player_sprite.get_rect().copy()))
        self.player.add_component(CType("Player"))
        self.player.add_component(CAttack(10, 0.5))
        # self.player.add_component(CState(self.player))
        self.player.add_component(CInput())
        self.player.add_component(CEquipment())

        self.ENTITY_MANAGER.add_entity(self.player)

        self.ENTITY_MANAGER.update(0)


def cast_ray(screen, player_pos, mouse_pos):
    ox, oy = player_pos
    mx, my = mouse_pos
    dx, dy = mx - ox, my - oy

    distance = math.sqrt(dx**2 + dy**2)
    if distance != 0:
        dx, dy = dx / distance, dy / distance

    pygame.draw.line(screen, (0, 255, 0), player_pos, mouse_pos)


