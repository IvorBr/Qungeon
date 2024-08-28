import pygame
from scripts.game_objects import QuantumObject, gates, gate_info_image, control_gates
from scripts.common_functions import add_text, set_dragging

class ItemSlot(pygame.sprite.Sprite):
    """Represents a slot for an item in the hotbar."""
    def __init__(self, x, y, count, item_name):
        """Initializes the item slot with position, item count, and item name."""
        super().__init__()
        self.image = pygame.Surface([50, 50], pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 150, 150), pygame.Rect(1, 1, 47, 47))
        pygame.draw.rect(self.image, (100, 100, 100), self.image.get_rect(), 2, 3)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.original_image = self.image
        self.name = item_name

        self.count = count
        self.effect = gates.get(item_name)
        self.origin_x = 0
        self.origin_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False

        # Setup hover image for displaying additional item info
        info_image = gate_info_image.get(item_name)
        if info_image:
            rect = info_image.get_rect()
            hover_width = int(rect.width * 0.5)
            hover_height = int(rect.height * 0.5)
            background_width = hover_width + 20
            background_height = hover_height + 20

            self.hover_image = pygame.Surface((background_width, background_height), pygame.SRCALPHA)
            pygame.draw.rect(self.hover_image, (150, 150, 150), pygame.Rect(1, 1, background_width - 2, background_height - 2))
            pygame.draw.rect(self.hover_image, (100, 100, 100), pygame.Rect(0, 0, background_width, background_height), 2, 3)

            scaled_image = pygame.transform.scale(info_image, (hover_width, hover_height))
            hover_image_pos = ((background_width - hover_width) // 2, (background_height - hover_height) // 2)
            self.hover_image.blit(scaled_image, hover_image_pos)

            self.hover_image_rect = self.hover_image.get_rect()

    def hover(self, screen):
        """Draws the hover image at the mouse position if the slot is not being dragged."""
        if not self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.hover_image_rect.topleft = (mouse_x, mouse_y - 45)
            screen.blit(self.hover_image, self.hover_image_rect)

class Hotbar(pygame.sprite.Sprite):
    """ Represents the hotbar which holds item slots."""
    def __init__(self):
        """Initializes the hotbar with a background image and slot management."""
        super().__init__()
        self.image = pygame.Surface([435, 50])
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = 175
        self.rect.y = 525
        self.slots = {}
        self.sprites = pygame.sprite.Group()
        self.font = pygame.font.Font(None, 24)
    
    def change_item_text(self, slot, item, count=0):
        """Updates the text displayed on the item slot."""
        add_text(slot, item)
        if count:
            add_text(slot, f'x{count}', 0, 30)

    def add_item(self, item, count):
        """Adds an item to the hotbar or updates the existing slot if it already contains the item."""
        if item in self.slots:
            slot = self.slots[item]
            slot.count += count
            slot.image = slot.original_image
            self.change_item_text(slot, item, str(slot.count))
            return slot
        else:
            new_slot = ItemSlot(self.rect.x + len(self.slots) * 55, self.rect.y, count, item)
            self.change_item_text(new_slot, item, str(count))
            self.slots[item] = new_slot
            self.sprites.add(new_slot)
            return new_slot

    def remove_by_key(self, key):
        """Removes or updates an item slot based on the key."""
        slot = self.slots[key]
        slot.count -= 1
        if slot.count <= 0:
            slot.kill()
            self.slots.pop(key)
            self.update_slots()
        else:
            slot.image = slot.original_image
            self.change_item_text(slot, key, str(slot.count))

    def remove_item(self, game, event, key):
        """Removes an item from the hotbar and applies its effect to a game object if applicable."""
        slot = self.slots.get(key)
        if not slot:
            return

        for _, obj in game.objects.items():
            if isinstance(obj, QuantumObject):
                if obj.rect.collidepoint(event.pos) and game.player.distance(obj.position[0], obj.position[1]):
                    if key in control_gates:
                        set_dragging(obj, event)
                        obj.control = key
                        return
                    else:
                        obj.apply_effect(game, slot.effect)
                    self.remove_by_key(key)
                    break

    def handle_mouse_up(self):
        """Placeholder for handling mouse release events."""
        pass
    
    def update_slots(self):
        """Updates the position of all item slots in the hotbar."""
        for i, (name, slot) in enumerate(self.slots.items()):
            slot.rect.x = self.rect.x + i * 55
