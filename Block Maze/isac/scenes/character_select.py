import pygame
from isac.core.scene import Scene
from isac.settings import WIDTH, HEIGHT, WHITE, BLUE, GREEN, RED
from isac.characters import get_character, GLASS, CRYSTAL

class CharacterSelectScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 64)
        self.selected_character = 0  # 0, 1, 2, or 3
        # Calculate box dimensions and positions
        self.box_width = 140  # Slightly smaller to fit 4 characters
        self.box_height = 200
        self.box_padding = 10  # Less padding to fit 4 characters
        self.box_y = HEIGHT // 2 - self.box_height // 2
        
        # Character definitions with their types
        self.character_defs = [
            ("crystal", (200, 50, 50)),
            ("glass", (180, 220, 255)),
            ("diamond", (255, 215, 0))  # Gold color for Diamond
        ]
        
        # Calculate total width needed for all boxes
        total_width = (self.box_width * len(self.character_defs) + 
                      self.box_padding * (len(self.character_defs) - 1))
        
        # Calculate starting x position to center the boxes
        self.start_x = (WIDTH - total_width) // 2
        
        self.characters = []
        
        for char_type, color in self.character_defs:
            try:
                # Get character data
                char_data = get_character(char_type)
                
                # Load and scale the character image
                img_path = char_data.sprite_paths.get('default', '')
                if img_path:
                    char_img = pygame.image.load(img_path).convert_alpha()
                    # Scale the image while maintaining aspect ratio
                    img_width = self.box_width - 60
                    aspect_ratio = char_img.get_height() / char_img.get_width()
                    img_height = int(img_width * aspect_ratio)
                    char_img = pygame.transform.scale(char_img, (img_width, img_height))
                else:
                    char_img = None
                
                # Add character to the list
                self.characters.append({
                    "name": char_data.name,
                    "color": color,
                    "description": char_data.description,
                    "image": char_img,
                    "type": char_type
                })
                
            except Exception as e:
                print(f"Error loading character {char_type}: {e}")
                # Add a placeholder if loading fails
                self.characters.append({
                    "name": char_type.capitalize(),
                    "color": color,
                    "description": "Character unavailable",
                    "image": None,
                    "type": char_type
                })
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_character = (self.selected_character - 1) % 3
            elif event.key == pygame.K_RIGHT:
                self.selected_character = (self.selected_character + 1) % 3
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                from .play import PlayScene
                # Get the selected character's type
                char_type = self.characters[self.selected_character]['type']
                self.game.change_scene(PlayScene, character_type=char_type)
                return
            elif event.key == pygame.K_ESCAPE:
                from .menu import MenuScene
                self.game.change_scene(MenuScene)
        
        # Handle mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if click is within any character box
            num_chars = len(self.character_defs)
            total_width = (self.box_width * num_chars + 
                         self.box_padding * (num_chars - 1))
            start_x = (WIDTH - total_width) // 2
            
            for i in range(num_chars):
                box_x = start_x + i * (self.box_width + self.box_padding)
                box_rect = pygame.Rect(box_x, self.box_y, self.box_width, self.box_height)
                if box_rect.collidepoint(mouse_x, mouse_y):
                    from .play import PlayScene
                    # Get the selected character's type
                    char_type = self.characters[i]['type']
                    self.game.change_scene(PlayScene, character_type=char_type)
                    return
    
    def update(self, dt: float) -> None:
        # Check for mouse hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        num_chars = len(self.character_defs)
        total_width = (self.box_width * num_chars + 
                      self.box_padding * (num_chars - 1))
        start_x = (WIDTH - total_width) // 2
        
        for i in range(num_chars):
            box_x = start_x + i * (self.box_width + self.box_padding)
            box_rect = pygame.Rect(box_x, self.box_y, self.box_width, self.box_height)
            if box_rect.collidepoint(mouse_x, mouse_y):
                self.selected_character = i
                break
    
    def draw(self, surface: pygame.Surface) -> None:
        # Draw title
        title = self.title_font.render("Select Your Character", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Calculate layout for character boxes
        num_chars = len(self.character_defs)
        total_width = (self.box_width * num_chars + 
                      self.box_padding * (num_chars - 1))
        start_x = (WIDTH - total_width) // 2
        
        # Draw character boxes
        for i, char in enumerate(self.characters):
            # Calculate box position
            box_x = start_x + i * (self.box_width + self.box_padding)
            
            # Draw box
            box_rect = pygame.Rect(box_x, self.box_y, self.box_width, self.box_height)
            border_color = GREEN if i == self.selected_character else WHITE
            pygame.draw.rect(surface, border_color, box_rect, 2)
            
            # Draw character preview (just a colored box for now)
            preview_rect = pygame.Rect(
                box_x + 5, self.box_y + 5, 
                self.box_width - 10, self.box_height - 30
            )
            pygame.draw.rect(surface, char["color"], preview_rect)
            
            # Draw character name
            char_name = char["name"]
            name_text = self.small.render(char_name, True, WHITE)
            surface.blit(
                name_text, 
                (box_x + self.box_width // 2 - name_text.get_width() // 2, 
                 self.box_y + self.box_height - 20)
            )
            
            # Draw background for the character (in case the image has transparency)
            pygame.draw.rect(surface, (30, 30, 30), preview_rect)
            
            if char.get('image'):
                # If there's an image, draw it centered in the character box
                img_rect = char['image'].get_rect(center=preview_rect.center)
                surface.blit(char['image'], img_rect.topleft)
            else:
                # Fallback to colored rectangle if no image is available
                pygame.draw.rect(surface, char["color"], preview_rect)
            
            # Draw character name (centered at the bottom of the box)
            name_surf = self.small.render(char["name"], True, WHITE)
            surface.blit(name_surf, 
                        (box_x + (self.box_width - name_surf.get_width()) // 2, 
                         self.box_y + self.box_height - 40))
        
        # Draw instructions
        instructions = self.small.render("Click on a character or use LEFT/RIGHT to select, ENTER to confirm", 
                                        True, BLUE)
        back_text = self.small.render("ESC to go back", True, BLUE)
        surface.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 60))
        surface.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 30))
