import tkinter as tk
from tkinter import messagebox, ttk as ttk_orig
import ttkbootstrap as ttk
from datetime import datetime
import threading
import time
import requests
from PIL import Image, ImageTk
import io
import os

class CurrencyExchangeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Exchange Pro")
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate window size (80% of screen)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # API Configuration
        self.api_key = '4a9e5a154dadea8468beb73c'
        self.base_url = 'https://v6.exchangerate-api.com/v6'
        self.flag_api_base = 'https://flagcdn.com/w80'
        
        # Initialize caches
        self.rates_cache = {}
        self.flag_cache = {}
        self.last_update = None
        
        # Currency data including Arab and African currencies
        self.currency_data = {
            # Common currencies
            'USD': {'name': 'US Dollar', 'symbol': '$', 'flag': 'us'},
            'EUR': {'name': 'Euro', 'symbol': '€', 'flag': 'eu'},
            'GBP': {'name': 'British Pound', 'symbol': '£', 'flag': 'gb'},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'flag': 'jp'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'flag': 'au'},
            'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'flag': 'ca'},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr', 'flag': 'ch'},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'flag': 'cn'},
            
            # Arab currencies
            'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'flag': 'ae'},
            'SAR': {'name': 'Saudi Riyal', 'symbol': '﷼', 'flag': 'sa'},
            'EGP': {'name': 'Egyptian Pound', 'symbol': 'E£', 'flag': 'eg'},
            'KWD': {'name': 'Kuwaiti Dinar', 'symbol': 'د.ك', 'flag': 'kw'},
            'QAR': {'name': 'Qatari Riyal', 'symbol': 'ر.ق', 'flag': 'qa'},
            'BHD': {'name': 'Bahraini Dinar', 'symbol': '.د.ب', 'flag': 'bh'},
            'OMR': {'name': 'Omani Rial', 'symbol': 'ر.ع.', 'flag': 'om'},
            'JOD': {'name': 'Jordanian Dinar', 'symbol': 'د.ا', 'flag': 'jo'},
            'LBP': {'name': 'Lebanese Pound', 'symbol': 'ل.ل', 'flag': 'lb'},
            'IQD': {'name': 'Iraqi Dinar', 'symbol': 'ع.د', 'flag': 'iq'},
            
            # African currencies
            'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'flag': 'za'},
            'NGN': {'name': 'Nigerian Naira', 'symbol': '₦', 'flag': 'ng'},
            'KES': {'name': 'Kenyan Shilling', 'symbol': 'KSh', 'flag': 'ke'},
            'GHS': {'name': 'Ghanaian Cedi', 'symbol': '₵', 'flag': 'gh'},
            'MAD': {'name': 'Moroccan Dirham', 'symbol': 'د.م.', 'flag': 'ma'},
            'TND': {'name': 'Tunisian Dinar', 'symbol': 'د.ت', 'flag': 'tn'},
            'UGX': {'name': 'Ugandan Shilling', 'symbol': 'USh', 'flag': 'ug'},
            'TZS': {'name': 'Tanzanian Shilling', 'symbol': 'TSh', 'flag': 'tz'},
            'ETB': {'name': 'Ethiopian Birr', 'symbol': 'Br', 'flag': 'et'},
            
            # Other major currencies
            'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'flag': 'in'},
            'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'flag': 'br'},
            'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'flag': 'ru'},
            'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'flag': 'kr'},
            'SGD': {'name': 'Singapore Dollar', 'symbol': 'S$', 'flag': 'sg'},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'flag': 'nz'},
        }
        
        # Create main frame with modern style
        self.style = ttk.Style(theme="cosmo")
        
        # Configure styles with modern colors
        self.style.configure('Currency.TLabel', font=('Roboto', 16))
        self.style.configure('Symbol.TLabel', font=('Roboto', 20, 'bold'))
        self.style.configure('Title.TLabel', font=('Roboto', 36, 'bold'))
        self.style.configure('Result.TLabel', font=('Roboto', 28))
        
        # Modern color scheme
        self.colors = {
            'primary': '#2962ff',
            'secondary': '#718792',
            'background': '#ffffff',
            'card': '#f8f9fa',
            'success': '#00c853',
            'error': '#d50000'
        }
        
        # Configure modern styles
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('Card.TFrame', background=self.colors['card'])
        self.style.configure('Primary.TButton', font=('Roboto', 16))
        
        # Main container with padding scaled to window size
        padding = min(window_width, window_height) // 40
        self.container = ttk.Frame(self.root, padding=padding, style='TFrame')
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create modern header
        self.create_header()
        
        # Create main content area
        self.content = ttk.Frame(self.container, style='TFrame')
        self.content.pack(fill=tk.BOTH, expand=True, pady=padding)
        
        # Create conversion panel
        self.create_conversion_panel()
        
        # Bind events
        self.from_currency.bind('<<ComboboxSelected>>', self.on_currency_change)
        self.to_currency.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Start auto-refresh thread
        self.auto_refresh_thread = threading.Thread(target=self.auto_refresh_rates, daemon=True)
        self.auto_refresh_thread.start()

    def get_flag_image(self, country_code):
        """Get flag image from API or cache"""
        if country_code in self.flag_cache:
            return self.flag_cache[country_code]
            
        try:
            url = f"{self.flag_api_base}/{country_code}.png"
            response = requests.get(url)
            image_data = Image.open(io.BytesIO(response.content))
            image_data = image_data.resize((24, 24), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_data)
            self.flag_cache[country_code] = photo
            return photo
        except Exception as e:
            print(f"Error loading flag for {country_code}: {str(e)}")
            return None

    def create_header(self):
        """Create modern header with gradient effect"""
        self.header = ttk.Frame(self.container, style='Card.TFrame')
        self.header.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(
            self.header,
            text="💱 Currency Exchange Pro",
            style='Title.TLabel'
        )
        title.pack(pady=20)

    def create_conversion_panel(self):
        """Create the currency conversion panel with modern design"""
        # Amount input with floating label effect
        self.amount_frame = ttk.Frame(self.content, style='Card.TFrame')
        self.amount_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Label(
            self.amount_frame,
            text="Amount",
            style='Currency.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.amount_var = tk.StringVar()
        self.amount_var.trace('w', self.validate_amount)
        
        self.amount_entry = ttk.Entry(
            self.amount_frame,
            textvariable=self.amount_var,
            font=("Roboto", 28),
            width=20
        )
        self.amount_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Currency selection with flags in dropdown
        self.currency_frame = ttk.Frame(self.content, style='Card.TFrame')
        self.currency_frame.pack(fill=tk.X, pady=20, padx=20)
        
        # From currency
        from_label_frame = ttk.Frame(self.currency_frame)
        from_label_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            from_label_frame,
            text="From",
            style='Currency.TLabel'
        ).pack(side=tk.LEFT)
        
        self.from_flag_label = ttk.Label(from_label_frame)
        self.from_flag_label.pack(side=tk.LEFT, padx=5)
        
        self.from_currency = ttk.Combobox(
            self.currency_frame,
            values=[f"{code} - {data['name']} ({data['symbol']})" 
                   for code, data in sorted(self.currency_data.items())],
            font=("Roboto", 16),
            width=30,
            state="readonly"
        )
        self.from_currency.set("USD - US Dollar ($)")
        self.from_currency.pack(side=tk.LEFT, padx=10)
        
        # Swap button with modern design
        self.swap_button = ttk.Button(
            self.currency_frame,
            text="🔄",
            command=self.swap_currencies,
            width=3,
            style='Primary.TButton'
        )
        self.swap_button.pack(side=tk.LEFT, padx=20)
        
        # To currency
        to_label_frame = ttk.Frame(self.currency_frame)
        to_label_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            to_label_frame,
            text="To",
            style='Currency.TLabel'
        ).pack(side=tk.LEFT)
        
        self.to_flag_label = ttk.Label(to_label_frame)
        self.to_flag_label.pack(side=tk.LEFT, padx=5)
        
        self.to_currency = ttk.Combobox(
            self.currency_frame,
            values=[f"{code} - {data['name']} ({data['symbol']})" 
                   for code, data in sorted(self.currency_data.items())],
            font=("Roboto", 16),
            width=30,
            state="readonly"
        )
        self.to_currency.set("EUR - Euro (€)")
        self.to_currency.pack(side=tk.LEFT, padx=10)
        
        # Modern convert button
        self.convert_btn = ttk.Button(
            self.content,
            text="Convert",
            command=self.convert,
            style='Primary.TButton',
            width=20
        )
        self.convert_btn.pack(pady=30)
        
        # Result display with modern card design
        self.result_frame = ttk.Frame(self.content, style='Card.TFrame')
        self.result_frame.pack(fill=tk.X, pady=20, padx=20)
        
        self.result_var = tk.StringVar()
        self.result_label = ttk.Label(
            self.result_frame,
            textvariable=self.result_var,
            style='Result.TLabel'
        )
        self.result_label.pack(pady=30)
        
        # Update initial flags
        self.update_flags()

    def update_flags(self):
        """Update flag images in the UI"""
        from_code = self.from_currency.get().split(' - ')[0].lower()
        to_code = self.to_currency.get().split(' - ')[0].lower()
        
        from_flag = self.get_flag_image(self.currency_data[from_code.upper()]['flag'])
        to_flag = self.get_flag_image(self.currency_data[to_code.upper()]['flag'])
        
        if from_flag:
            self.from_flag_label.configure(image=from_flag)
            self.from_flag_label.image = from_flag
        
        if to_flag:
            self.to_flag_label.configure(image=to_flag)
            self.to_flag_label.image = to_flag

    def get_exchange_rates(self, base_currency):
        """Get exchange rates from the API"""
        if base_currency in self.rates_cache and self.last_update:
            # Use cached rates if less than 1 hour old
            if (datetime.now() - self.last_update).seconds < 3600:
                return self.rates_cache[base_currency]
        
        try:
            url = f"{self.base_url}/{self.api_key}/latest/{base_currency}"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200 and data.get('result') == 'success':
                self.rates_cache[base_currency] = data['conversion_rates']
                self.last_update = datetime.now()
                return data['conversion_rates']
            else:
                raise Exception(f"API Error: {data.get('error-type', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Failed to get exchange rates: {str(e)}")

    def validate_amount(self, *args):
        """Validate amount input to allow only numbers and decimal point"""
        value = self.amount_var.get()
        if value:
            # Allow empty string
            if value == "":
                return
            # Allow single decimal point
            if value.count('.') <= 1:
                # Remove any non-digit characters except decimal point
                filtered_value = ''.join(c for c in value if c.isdigit() or c == '.')
                # Ensure it starts with a digit if there's a decimal
                if '.' in filtered_value and not filtered_value.startswith('.'):
                    self.amount_var.set(filtered_value)
                elif '.' not in filtered_value:
                    self.amount_var.set(filtered_value)
                else:
                    self.amount_var.set(value[:-1])
            else:
                self.amount_var.set(value[:-1])

    def on_currency_change(self, event=None):
        """Handle currency selection change"""
        self.update_flags()
        if self.amount_var.get():
            self.convert()

    def swap_currencies(self):
        """Swap the from and to currencies with animation"""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        # Animate the swap
        self.swap_button.configure(text="⟳")
        
        def animate_swap():
            # Swap values
            self.from_currency.set(to_curr)
            self.to_currency.set(from_curr)
            
            # Reset button
            self.root.after(200, lambda: self.swap_button.configure(text="🔄"))
            
            # Update flags
            self.update_flags()
            
            # Auto-convert if there's a value
            if self.amount_var.get():
                self.convert()
        
        self.root.after(100, animate_swap)

    def convert(self):
        """Handle currency conversion with animations"""
        if not self.amount_var.get():
            messagebox.showerror("Error", "Please enter an amount")
            return
            
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("Error", "Please enter a positive amount")
                return
                
            from_curr = self.from_currency.get().split(' - ')[0]
            to_curr = self.to_currency.get().split(' - ')[0]
            
            # Show loading state
            self.convert_btn.configure(state='disabled')
            
            # Get exchange rates
            rates = self.get_exchange_rates(from_curr)
            rate = rates[to_curr]
            result = amount * rate
            
            # Format with currency symbols
            from_symbol = self.currency_data[from_curr]['symbol']
            to_symbol = self.currency_data[to_curr]['symbol']
            
            formatted_result = f"{from_symbol} {amount:,.2f} = {to_symbol} {result:,.2f}"
            rate_info = f"1 {from_curr} = {rate:.4f} {to_curr}"
            
            # Update result with animation
            self.result_var.set(f"{formatted_result}\n{rate_info}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.convert_btn.configure(state='normal')

    def auto_refresh_rates(self):
        """Auto-refresh rates every hour if there's a valid conversion"""
        while True:
            time.sleep(3600)  # 1 hour
            if self.amount_var.get() and self.result_var.get():
                self.convert()

def main():
    root = ttk.Window()
    app = CurrencyExchangeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
