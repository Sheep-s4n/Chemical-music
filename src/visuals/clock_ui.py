import pygame
import os
from datetime import datetime


def background_color_from_x(x, X_MIN, X_MAX):
    norm = (X_MAX - x) / (X_MAX - X_MIN)
    norm = max(0.0, min(1.0, norm))

    # Variation très subtile vers lavande
    shift = int(25 * norm)

    r = 255 - shift
    g = 255
    b = 255

    return (r, g, b)

def format_clock_time(timestamp):
    """
    timestamp : Unix timestamp (seconds since epoch)
    """

    dt = datetime.fromtimestamp(timestamp).astimezone() # setting the time to current time zone
    return dt.strftime("%H:%M:%S")



class ChemicalClockUI:

    def __init__(self, width=1400/1.5, height=900/1.5):
        
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0" # to put the window on the top left corner

        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Horloge Chimique")

        self.width = width
        self.height = height

        self.mode = "init"

        # Fonts (adapté vidéoprojecteur)
        self.font_small = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 130, bold=True)
        self.font_counter = pygame.font.Font("../assets/font/courage-road/Courage Road.ttf", 110)

    def update_background(self,x, X_MIN, X_MAX) : 
        self.screen.fill(background_color_from_x(x, X_MIN, X_MAX))

    def handle_events(self):
        """
        Call this each frame to handle window events like resizing or quitting.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # exit()
            elif event.type == pygame.VIDEORESIZE:
                # Update internal width/height and adjust display
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            
    # -------------------------
    # DRAW INIT PHASE
    # -------------------------

    def draw_init(self, periods, average, target_count):

        
        width, height = self.screen.get_size()
        
        # --- 2. Average (top) ---
        font_large = pygame.font.SysFont("Arial", 50, bold=True)
        
        if len(periods) > 0:
            avg_text = "Moyenne: --" if average is None else f"Moyenne: {average:.3f} s"
        else:
            avg_text = "Collecte des données..."
        
        avg_surface = font_large.render(avg_text, True, (0, 0, 0))
        avg_rect = avg_surface.get_rect(center=(width // 2, int(height * 0.25)))
        self.screen.blit(avg_surface, avg_rect)
        
        # --- 3. Period list (horizontally centered) ---
        font_medium = pygame.font.SysFont("Arial", 30)
        line_height = font_medium.get_height()
        spacing = 5
        
         # Title for the period list
        periods_title = "Périodes collectées :"
        title_surface = font_medium.render(periods_title, True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(width // 2, height * 0.35))
        self.screen.blit(title_surface, title_rect)
        # Display last 10 periods to avoid overflow
        display_periods = periods[-10:]
        total_height = len(display_periods) * (line_height + spacing)
        start_y = height // 2 - total_height // 2  # vertically center the block
        
        for i, p in enumerate(display_periods):
            period_text = f"{p:.3f} s"
            period_surface = font_medium.render(period_text, True, (0, 0, 0))
            period_rect = period_surface.get_rect(center=(width // 2, start_y + i * (line_height + spacing)))
            self.screen.blit(period_surface, period_rect)
        
        # --- 4. Counter (bottom) ---
        font_small = pygame.font.SysFont("Arial", 20)
        current_count = len(periods)
        counter_text = f"Mesures collectées : {current_count} / {target_count}"
        counter_surface = font_small.render(counter_text, True, (0, 0, 0))
        counter_rect = counter_surface.get_rect(center=(width // 2, int(height * 0.7)))
        self.screen.blit(counter_surface, counter_rect)

    # -------------------------
    # DRAW ACTIVE PHASE
    # -------------------------

    def draw_active(self,
                    chemical_clock_time,
                    avg_period,
                    phase_error):

        width, height = self.screen.get_size()
        
        # ---- Temps horloge dominant ----
        clock_text = format_clock_time(chemical_clock_time)
        text_surface = self.font_large.render(clock_text, True, (0, 0, 0))
        rect = text_surface.get_rect(center=(self.width // 2,
                                             self.height * 0.4))
        self.screen.blit(text_surface, rect)
        
        # ---- Sous-titre : Temps chimique ----
        self.font_thin = pygame.font.SysFont(None, 40)
        
        subtitle_surface = self.font_thin.render("Temps chimique", True, (0, 0, 0))

        subtitle_rect = subtitle_surface.get_rect(
            center=(self.width // 2, self.height * 0.2)
        )

        self.screen.blit(subtitle_surface, subtitle_rect)
        
        pygame.draw.line(
            self.screen,
            (0, 0, 0),
            (subtitle_rect.left, subtitle_rect.bottom + 2),
            (subtitle_rect.right, subtitle_rect.bottom + 2),
            1
        )

        # ---- Période moyenne ----
        period_text = pygame.font.SysFont(None, 30).render(
            f"Période moyenne : {avg_period:.3f} s",
            True, (0, 0, 0)
        )
        self.screen.blit(period_text,
                         (0, height - 25))

        # ---- Barre d'erreur ±1T ----
        bar_width = self.width * 0.7
        bar_height = 30
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height * 0.6

        pygame.draw.rect(self.screen, (0, 0, 0),
                         (bar_x, bar_y, bar_width, bar_height), 2)

        # Normalisation ±1T
        normalized = phase_error / avg_period
        normalized = max(-1.0, min(1.0, normalized))

        cursor_x = bar_x + (normalized + 1) / 2 * bar_width

        pygame.draw.line(self.screen, (0, 0, 0),
                         (cursor_x, bar_y),
                         (cursor_x, bar_y + bar_height), 4)

        # ---- Valeur erreur en secondes ----
        error_text = self.font_small.render(
            f"Erreur de phase : {phase_error:+.3f} s",
            True, (0, 0, 0)
        )

        error_rect = error_text.get_rect(center=(self.width // 2,
                                                 bar_y + 80))
        self.screen.blit(error_text, error_rect)

    # -------------------------
    # UPDATE DISPLAY
    # -------------------------

    def update(self):
        pygame.display.flip()