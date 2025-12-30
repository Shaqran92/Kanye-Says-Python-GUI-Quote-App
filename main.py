# ============== IMPORTS ==============
from tkinter import *
from tkinter import messagebox, ttk
import requests
import json
import random
import threading
from pathlib import Path
from datetime import datetime
import pyperclip  

# ============== CONFIGURATION ==============
class Config:
    """Application configuration"""
    # Paths
    BASE_DIR = Path(__file__).parent if "__file__" in dir() else Path(".")
    IMAGES_DIR = BASE_DIR / "images"
    DATA_DIR = BASE_DIR / "data"
    
    # Files
    FAVORITES_FILE = DATA_DIR / "favorites.json"
    HISTORY_FILE = DATA_DIR / "history.json"
    
    # API
    API_URL = "https://api.kanye.rest"
    API_TIMEOUT = 10  # seconds
    
    # UI
    WINDOW_PADDING = 50
    CANVAS_WIDTH = 400
    CANVAS_HEIGHT = 400
    QUOTE_WIDTH = 250
    
    # Colors
    BG_COLOR = "#1a1a2e"
    CARD_COLOR = "#16213e"
    TEXT_COLOR = "#ffffff"
    ACCENT_COLOR = "#e94560"
    SUCCESS_COLOR = "#4ecca3"
    
    # Fonts
    QUOTE_FONT = ("Arial", 18, "bold")
    BUTTON_FONT = ("Arial", 10)
    STATS_FONT = ("Arial", 9)
    
    # Fallback quotes (when API is unavailable)
    FALLBACK_QUOTES = [
        "I'm not a businessman, I'm a business, man!",
        "I refuse to accept other people's ideas of happiness for me.",
        "Everything I'm not made me everything I am.",
        "I feel like I'm too busy writing history to read it.",
        "Life is 5% what happens and 95% how you react.",
        "Believe in your flyness, conquer your shyness.",
        "I don't even listen to rap. My apartment is too nice to listen to rap in.",
        "Keep your nose out the sky, keep your heart to God, and keep your face to the rising sun.",
        "I am Warhol. I am the No. 1 most impactful artist of our generation.",
        "My greatest pain in life is that I will never be able to see myself perform live.",
        "I hate when I'm on a flight and I wake up with a water bottle next to me.",
        "I feel calm but energized.",
        "I'm on the pursuit of awesomeness.",
        "Would you believe in what you believe in if you were the only one who believed it?"
    ]


# ============== QUOTE MANAGER ==============
class QuoteManager:
    """Manages quotes, history, and favorites"""
    
    def __init__(self):
        self.history = []
        self.favorites = []
        self.current_quote = ""
        self._load_data()
    
    def _load_data(self):
        """Load saved data from files"""
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load favorites
        if Config.FAVORITES_FILE.exists():
            try:
                with open(Config.FAVORITES_FILE, 'r') as f:
                    self.favorites = json.load(f)
            except:
                self.favorites = []
        
        # Load history
        if Config.HISTORY_FILE.exists():
            try:
                with open(Config.HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_data(self):
        """Save data to files"""
        try:
            Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(Config.FAVORITES_FILE, 'w') as f:
                json.dump(self.favorites, f, indent=2)
            
            with open(Config.HISTORY_FILE, 'w') as f:
                json.dump(self.history[-50:], f, indent=2)  # Keep last 50
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_to_history(self, quote: str):
        """Add quote to history"""
        entry = {
            "quote": quote,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(entry)
        self.current_quote = quote
    
    def toggle_favorite(self, quote: str) -> bool:
        """Toggle favorite status, returns True if added"""
        if quote in self.favorites:
            self.favorites.remove(quote)
            return False
        else:
            self.favorites.append(quote)
            return True
    
    def is_favorite(self, quote: str) -> bool:
        """Check if quote is in favorites"""
        return quote in self.favorites
    
    def get_random_favorite(self) -> str:
        """Get a random favorite quote"""
        if self.favorites:
            return random.choice(self.favorites)
        return ""


# ============== MAIN APPLICATION ==============
class KanyeQuoteApp:
    """Main Kanye Quote Application"""
    
    def __init__(self):
        self.window = Tk()
        self.window.title("🎤 Kanye Says...")
        self.window.config(
            padx=Config.WINDOW_PADDING,
            pady=Config.WINDOW_PADDING,
            bg=Config.BG_COLOR
        )
        self.window.resizable(False, False)
        
        # Initialize quote manager
        self.quote_manager = QuoteManager()
        
        # State
        self.is_loading = False
        self.auto_refresh = False
        self.auto_refresh_id = None
        
        # Setup UI
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        
        # Get initial quote
        self.get_quote()
    
    def _setup_ui(self):
        """Setup all UI components"""
        # Main Frame
        self.main_frame = Frame(self.window, bg=Config.BG_COLOR)
        self.main_frame.pack()
        
        # Title
        self.title_label = Label(
            self.main_frame,
            text="🎤 KANYE SAYS...",
            font=("Arial", 24, "bold"),
            bg=Config.BG_COLOR,
            fg=Config.ACCENT_COLOR
        )
        self.title_label.pack(pady=(0, 20))
        
        # Canvas for quote card
        self.canvas = Canvas(
            self.main_frame,
            width=Config.CANVAS_WIDTH,
            height=Config.CANVAS_HEIGHT,
            bg=Config.BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Try to load background image
        try:
            self.bg_photo = PhotoImage(file=Config.IMAGES_DIR / "background.png")
            self.canvas.create_image(
                Config.CANVAS_WIDTH // 2,
                Config.CANVAS_HEIGHT // 2,
                image=self.bg_photo
            )
        except:
            # Create gradient-like background if image not found
            self.canvas.create_rectangle(
                20, 20,
                Config.CANVAS_WIDTH - 20,
                Config.CANVAS_HEIGHT - 20,
                fill=Config.CARD_COLOR,
                outline=Config.ACCENT_COLOR,
                width=2
            )
        
        # Quote text
        self.quote_text = self.canvas.create_text(
            Config.CANVAS_WIDTH // 2,
            Config.CANVAS_HEIGHT // 2 - 20,
            text="Click Kanye to get a quote!",
            width=Config.QUOTE_WIDTH,
            fill=Config.TEXT_COLOR,
            font=Config.QUOTE_FONT,
            justify=CENTER
        )
        
        # Author text
        self.author_text = self.canvas.create_text(
            Config.CANVAS_WIDTH // 2,
            Config.CANVAS_HEIGHT - 60,
            text="- Kanye West",
            fill=Config.ACCENT_COLOR,
            font=("Arial", 12, "italic")
        )
        
        # Loading indicator
        self.loading_text = self.canvas.create_text(
            Config.CANVAS_WIDTH // 2,
            Config.CANVAS_HEIGHT // 2,
            text="",
            fill=Config.SUCCESS_COLOR,
            font=("Arial", 14)
        )
        
        # Favorite indicator
        self.favorite_indicator = self.canvas.create_text(
            Config.CANVAS_WIDTH - 40,
            40,
            text="",
            font=("Arial", 20),
            fill=Config.ACCENT_COLOR
        )
        
        # Button Frame
        self.button_frame = Frame(self.main_frame, bg=Config.BG_COLOR)
        self.button_frame.pack(pady=20)
        
        # Kanye button (main quote button)
        try:
            self.kanye_image = PhotoImage(file=Config.IMAGES_DIR / "kanye.png")
            self.quote_button = Button(
                self.button_frame,
                image=self.kanye_image,
                highlightthickness=0,
                bd=0,
                command=self.get_quote,
                bg=Config.BG_COLOR,
                activebackground=Config.BG_COLOR
            )
        except:
            self.quote_button = Button(
                self.button_frame,
                text="🎤 Get Quote",
                font=("Arial", 14, "bold"),
                bg=Config.ACCENT_COLOR,
                fg="white",
                padx=30,
                pady=15,
                command=self.get_quote
            )
        self.quote_button.pack(pady=10)
        
        # Action buttons frame
        self.action_frame = Frame(self.main_frame, bg=Config.BG_COLOR)
        self.action_frame.pack(pady=10)
        
        # Favorite button
        self.fav_button = Button(
            self.action_frame,
            text="❤️ Favorite",
            font=Config.BUTTON_FONT,
            bg="#e94560",
            fg="white",
            padx=10,
            pady=5,
            command=self.toggle_favorite
        )
        self.fav_button.pack(side=LEFT, padx=5)
        
        # Copy button
        self.copy_button = Button(
            self.action_frame,
            text="📋 Copy",
            font=Config.BUTTON_FONT,
            bg="#4ecca3",
            fg="white",
            padx=10,
            pady=5,
            command=self.copy_quote
        )
        self.copy_button.pack(side=LEFT, padx=5)
        
        # Share button
        self.share_button = Button(
            self.action_frame,
            text="🐦 Tweet",
            font=Config.BUTTON_FONT,
            bg="#1DA1F2",
            fg="white",
            padx=10,
            pady=5,
            command=self.share_quote
        )
        self.share_button.pack(side=LEFT, padx=5)
        
        # View favorites button
        self.view_fav_button = Button(
            self.action_frame,
            text="⭐ View Favorites",
            font=Config.BUTTON_FONT,
            bg="#f39c12",
            fg="white",
            padx=10,
            pady=5,
            command=self.show_favorites
        )
        self.view_fav_button.pack(side=LEFT, padx=5)
        
        # Options frame
        self.options_frame = Frame(self.main_frame, bg=Config.BG_COLOR)
        self.options_frame.pack(pady=10)
        
        # Auto-refresh checkbox
        self.auto_refresh_var = BooleanVar(value=False)
        self.auto_refresh_check = Checkbutton(
            self.options_frame,
            text="🔄 Auto-refresh (10s)",
            variable=self.auto_refresh_var,
            bg=Config.BG_COLOR,
            fg=Config.TEXT_COLOR,
            selectcolor=Config.CARD_COLOR,
            activebackground=Config.BG_COLOR,
            font=Config.STATS_FONT,
            command=self._toggle_auto_refresh
        )
        self.auto_refresh_check.pack(side=LEFT, padx=10)
        
        # Stats frame
        self.stats_frame = Frame(self.main_frame, bg=Config.BG_COLOR)
        self.stats_frame.pack(pady=10)
        
        self.stats_label = Label(
            self.stats_frame,
            text=self._get_stats_text(),
            font=Config.STATS_FONT,
            bg=Config.BG_COLOR,
            fg="gray"
        )
        self.stats_label.pack()
        
        # Keyboard hints
        self.hints_label = Label(
            self.main_frame,
            text="⌨️ Space=New Quote | F=Favorite | C=Copy | Esc=Quit",
            font=("Arial", 8),
            bg=Config.BG_COLOR,
            fg="gray"
        )
        self.hints_label.pack(pady=(10, 0))
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard bindings"""
        self.window.bind("<space>", lambda e: self.get_quote())
        self.window.bind("<Return>", lambda e: self.get_quote())
        self.window.bind("<f>", lambda e: self.toggle_favorite())
        self.window.bind("<F>", lambda e: self.toggle_favorite())
        self.window.bind("<c>", lambda e: self.copy_quote())
        self.window.bind("<C>", lambda e: self.copy_quote())
        self.window.bind("<Escape>", lambda e: self.quit_app())
    
    def _get_stats_text(self) -> str:
        """Get statistics text"""
        total_quotes = len(self.quote_manager.history)
        total_favorites = len(self.quote_manager.favorites)
        return f"📊 Quotes viewed: {total_quotes} | ❤️ Favorites: {total_favorites}"
    
    def _update_stats(self):
        """Update statistics display"""
        self.stats_label.config(text=self._get_stats_text())
    
    def _show_loading(self, show: bool):
        """Show or hide loading indicator"""
        self.is_loading = show
        if show:
            self.canvas.itemconfig(self.quote_text, text="")
            self.canvas.itemconfig(self.loading_text, text="⏳ Loading...")
            self.quote_button.config(state=DISABLED)
        else:
            self.canvas.itemconfig(self.loading_text, text="")
            self.quote_button.config(state=NORMAL)
    
    def _update_favorite_indicator(self):
        """Update the favorite indicator"""
        if self.quote_manager.is_favorite(self.quote_manager.current_quote):
            self.canvas.itemconfig(self.favorite_indicator, text="❤️")
            self.fav_button.config(text="💔 Unfavorite", bg="#888888")
        else:
            self.canvas.itemconfig(self.favorite_indicator, text="")
            self.fav_button.config(text="❤️ Favorite", bg="#e94560")
    
    def get_quote(self):
        """Fetch a new quote from API"""
        if self.is_loading:
            return
        
        # Use threading to prevent UI freeze
        thread = threading.Thread(target=self._fetch_quote)
        thread.daemon = True
        thread.start()
    
    def _fetch_quote(self):
        """Fetch quote in background thread"""
        self.window.after(0, lambda: self._show_loading(True))
        
        try:
            response = requests.get(
                Config.API_URL,
                timeout=Config.API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            quote = data.get("quote", "")
            
            if quote:
                self.window.after(0, lambda: self._display_quote(quote))
            else:
                raise ValueError("Empty quote received")
                
        except requests.exceptions.Timeout:
            self.window.after(0, lambda: self._handle_error("timeout"))
        except requests.exceptions.ConnectionError:
            self.window.after(0, lambda: self._handle_error("connection"))
        except Exception as e:
            print(f"API Error: {e}")
            self.window.after(0, lambda: self._handle_error("unknown"))
    
    def _display_quote(self, quote: str):
        """Display the quote on canvas"""
        self._show_loading(False)
        
        # Animate text appearance
        self.canvas.itemconfig(self.quote_text, text=f'"{quote}"')
        
        # Add to history
        self.quote_manager.add_to_history(quote)
        self.quote_manager.save_data()
        
        # Update UI
        self._update_favorite_indicator()
        self._update_stats()
    
    def _handle_error(self, error_type: str):
        """Handle API errors with fallback"""
        self._show_loading(False)
        
        # Get fallback quote
        fallback = random.choice(Config.FALLBACK_QUOTES)
        
        if error_type == "timeout":
            msg = "API timeout - here's a saved quote:"
        elif error_type == "connection":
            msg = "No internet - here's a saved quote:"
        else:
            msg = "Error occurred - here's a saved quote:"
        
        self.canvas.itemconfig(self.quote_text, text=f'"{fallback}"')
        self.quote_manager.add_to_history(fallback)
        self._update_favorite_indicator()
        self._update_stats()
        
        # Show subtle notification
        print(f"⚠️ {msg}")
    
    def toggle_favorite(self):
        """Toggle favorite status of current quote"""
        quote = self.quote_manager.current_quote
        if not quote:
            return
        
        is_added = self.quote_manager.toggle_favorite(quote)
        self.quote_manager.save_data()
        self._update_favorite_indicator()
        self._update_stats()
        
        # Visual feedback
        if is_added:
            self._flash_message("❤️ Added to favorites!")
        else:
            self._flash_message("💔 Removed from favorites")
    
    def _flash_message(self, message: str):
        """Show a temporary message"""
        original_text = self.canvas.itemcget(self.loading_text, 'text')
        self.canvas.itemconfig(self.loading_text, text=message)
        self.window.after(1500, lambda: self.canvas.itemconfig(
            self.loading_text, text=""
        ))
    
    def copy_quote(self):
        """Copy current quote to clipboard"""
        quote = self.quote_manager.current_quote
        if not quote:
            return
        
        full_quote = f'"{quote}" - Kanye West'
        
        try:
            pyperclip.copy(full_quote)
            self._flash_message("📋 Copied to clipboard!")
        except:
            # Fallback for systems without pyperclip
            try:
                self.window.clipboard_clear()
                self.window.clipboard_append(full_quote)
                self._flash_message("📋 Copied to clipboard!")
            except:
                self._flash_message("❌ Could not copy")
    
    def share_quote(self):
        """Open Twitter to share the quote"""
        quote = self.quote_manager.current_quote
        if not quote:
            return
        
        import webbrowser
        import urllib.parse
        
        tweet_text = f'"{quote}" - Kanye West #KanyeSays'
        encoded_text = urllib.parse.quote(tweet_text)
        twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        
        webbrowser.open(twitter_url)
        self._flash_message("🐦 Opening Twitter...")
    
    def show_favorites(self):
        """Show favorites in a new window"""
        if not self.quote_manager.favorites:
            messagebox.showinfo(
                "No Favorites",
                "You haven't saved any favorites yet!\n\n"
                "Click the ❤️ button to save quotes you love."
            )
            return
        
        # Create favorites window
        fav_window = Toplevel(self.window)
        fav_window.title("⭐ Favorite Quotes")
        fav_window.config(bg=Config.BG_COLOR, padx=20, pady=20)
        fav_window.geometry("500x400")
        
        # Title
        Label(
            fav_window,
            text="⭐ Your Favorite Kanye Quotes",
            font=("Arial", 16, "bold"),
            bg=Config.BG_COLOR,
            fg=Config.ACCENT_COLOR
        ).pack(pady=10)
        
        # Scrollable list
        list_frame = Frame(fav_window, bg=Config.BG_COLOR)
        list_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        listbox = Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_COLOR,
            font=("Arial", 11),
            selectmode=SINGLE,
            height=15
        )
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for i, quote in enumerate(self.quote_manager.favorites, 1):
            listbox.insert(END, f"{i}. {quote}")
        
        # Button frame
        btn_frame = Frame(fav_window, bg=Config.BG_COLOR)
        btn_frame.pack(pady=10)
        
        def use_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                quote = self.quote_manager.favorites[index]
                self._display_quote(quote)
                fav_window.destroy()
        
        def remove_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                quote = self.quote_manager.favorites[index]
                self.quote_manager.favorites.remove(quote)
                self.quote_manager.save_data()
                listbox.delete(index)
                self._update_stats()
        
        Button(
            btn_frame,
            text="📖 Use This Quote",
            bg=Config.SUCCESS_COLOR,
            fg="white",
            command=use_selected
        ).pack(side=LEFT, padx=5)
        
        Button(
            btn_frame,
            text="🗑️ Remove",
            bg=Config.ACCENT_COLOR,
            fg="white",
            command=remove_selected
        ).pack(side=LEFT, padx=5)
        
        Button(
            btn_frame,
            text="🎲 Random Favorite",
            bg="#9b59b6",
            fg="white",
            command=lambda: self._display_quote(
                self.quote_manager.get_random_favorite()
            ) or fav_window.destroy()
        ).pack(side=LEFT, padx=5)
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh feature"""
        if self.auto_refresh_var.get():
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        self.get_quote()
        self.auto_refresh_id = self.window.after(10000, self._start_auto_refresh)
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self.auto_refresh_id:
            self.window.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None
    
    def quit_app(self):
        """Clean quit"""
        self._stop_auto_refresh()
        self.quote_manager.save_data()
        self.window.quit()
    
    def run(self):
        """Start the application"""
        self.window.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.window.mainloop()


# ============== MAIN ==============
def main():
    app = KanyeQuoteApp()
    app.run()


if __name__ == "__main__":
    main()