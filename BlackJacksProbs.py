import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os

class BlackjackApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Blackjack Probability Calculator")
        self.master.attributes("-alpha", 0.95)  # Set slight transparency

        # Use a style object to encourage a more modern look
        style = ttk.Style(self.master)
        style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic' to test different looks
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 14), background='lightgray', relief='flat')
        style.configure('TFrame', background='lightgray')
        style.configure('CardButton.TButton', padding=5)
        style.configure('SelectedCard.TButton', background='lightblue')
        style.configure('DealerCard.TButton', background='lightcoral')

        self.card_images = {}
        self.player_cards = []
        self.dealer_card = None

        self.setup_card_images()
        self.load_card_images()
        self.setup_gui()

    def setup_card_images(self):
        card_folder = 'cards/'
        os.makedirs(card_folder, exist_ok=True)
        for rank in '23456789TJQKA':
            for suit in 'shdc':
                card_code = f'{rank}{suit}'.upper()
                file_path = f'{card_folder}{rank.lower()}{suit}.png'
                if not os.path.exists(file_path):
                    self.generate_card_image(rank, suit, file_path)

    def generate_card_image(self, rank, suit, file_path):
        image = Image.new('RGB', (72, 96), 'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Arial.ttf", 24)  # Use a TrueType font for better appearance
        suit_symbols = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
        text = f'{rank}{suit_symbols[suit.lower()]}'
        draw.text((10, 30), text, font=font, fill='black')
        image.save(file_path)

    def load_card_images(self):
        card_folder = 'cards/'
        for rank in '23456789TJQKA':
            for suit in 'shdc':
                card_code = f'{rank}{suit}'.upper()
                file_path = f'{card_folder}{rank.lower()}{suit}.png'
                image = Image.open(file_path).resize((72, 96), Image.Resampling.LANCZOS)
                self.card_images[card_code] = ImageTk.PhotoImage(image)

    def setup_gui(self):
        frame = ttk.Frame(self.master, padding="3 3 12 12")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        ttk.Button(frame, text="Select Player Cards", command=lambda: self.show_card_selector(self.player_cards, 'blue')).grid(column=1, row=1, sticky=tk.W)
        ttk.Button(frame, text="Select Dealer Card", command=self.show_dealer_card_selector).grid(column=2, row=1, sticky=tk.W)

        self.result_label = ttk.Label(frame, text="Probabilities: Win: 0.00%, Draw: 0.00%, Lose: 0.00%", font=('Helvetica', 16))
        self.result_label.grid(column=1, row=2, columnspan=2, sticky=(tk.W, tk.E))

        self.explanation_label = ttk.Label(frame, text="The probabilities represent your chances of winning, drawing, or losing the hand based on 50,000 simulations.", font=('Helvetica', 12), wraplength=400)
        self.explanation_label.grid(column=1, row=3, columnspan=2, sticky=(tk.W, tk.E))

        self.suggestion_label = ttk.Label(frame, text="Suggestion: ", font=('Helvetica', 14), wraplength=400)
        self.suggestion_label.grid(column=1, row=4, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Calculate Probability", command=self.calculate_probability).grid(column=1, row=5, columnspan=2, sticky=tk.W)

    def show_card_selector(self, card_list, color):
        popup = Toplevel(self.master)
        popup.title("Select Cards")
        frame = ttk.Frame(popup, padding="3 3 12 12")
        frame.pack()

        row = 0
        col = 0
        for card_code, img in self.card_images.items():
            btn = ttk.Button(frame, image=img, style='CardButton.TButton')
            btn.image = img
            btn.grid(row=row, column=col, padx=5, pady=5)
            if card_code in card_list:
                if color == 'blue':
                    btn.config(style='SelectedCard.TButton')
            btn.bind("<Button-1>", lambda event, c=card_code, cl=card_list, b=btn, col=color: self.toggle_card(c, cl, b, col))
            col += 1
            if col % 10 == 0:
                row += 1
                col = 0

    def show_dealer_card_selector(self):
        popup = Toplevel(self.master)
        popup.title("Select Dealer Card")
        frame = ttk.Frame(popup, padding="3 3 12 12")
        frame.pack()

        row = 0
        col = 0
        for card_code, img in self.card_images.items():
            btn = ttk.Button(frame, image=img, style='CardButton.TButton')
            btn.image = img
            btn.grid(row=row, column=col, padx=5, pady=5)
            if card_code == self.dealer_card:
                btn.config(style='DealerCard.TButton')
            btn.bind("<Button-1>", lambda event, c=card_code, b=btn: self.set_dealer_card(c, b))
            col += 1
            if col % 10 == 0:
                row += 1
                col = 0

    def set_dealer_card(self, card_code, button):
        if self.dealer_card:
            for widget in button.master.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(style='CardButton.TButton')
        self.dealer_card = card_code
        button.config(style='DealerCard.TButton')
        self.update_gui()

    def toggle_card(self, card_code, card_list, button, color):
        if card_code in card_list:
            card_list.remove(card_code)
            button.config(style='CardButton.TButton')  # Default style
        else:
            card_list.append(card_code)
            if color == 'blue':
                button.config(style='SelectedCard.TButton')  # Highlighted style
        self.update_gui()

    def update_gui(self):
        selected_player_cards = ' '.join(self.player_cards)
        selected_dealer_card = self.dealer_card if self.dealer_card else "None"
        self.result_label.config(text=f"Selected Player Cards: {selected_player_cards}, Dealer Card: {selected_dealer_card}")

    def calculate_probability(self):
        if not self.player_cards or not self.dealer_card:
            messagebox.showerror("Error", "Please select at least 1 player card and 1 dealer card.")
            return

        deck = [f'{r}{s}' for r in '23456789TJQKA' for s in 'shdc' if f'{r}{s}' not in self.player_cards + [self.dealer_card]]
        win, draw, lose = self.simulate_blackjack(self.player_cards, self.dealer_card, deck, 50000)
        self.result_label.config(text=f"Probabilities: Win: {win:.2%}, Draw: {draw:.2%}, Lose: {lose:.2%}")
        
        suggestion = self.get_suggestion(self.player_cards, self.dealer_card)
        self.suggestion_label.config(text=f"Suggestion: {suggestion}")

    def simulate_blackjack(self, player_cards, dealer_card, deck, num_simulations=50000):
        win = 0
        draw = 0
        lose = 0

        for _ in range(num_simulations):
            deck_copy = deck[:]
            random.shuffle(deck_copy)

            player_total = self.calculate_hand_value(player_cards)
            dealer_total = self.calculate_hand_value([dealer_card, deck_copy.pop()])

            if dealer_total == 21:
                if player_total == 21:
                    draw += 1
                else:
                    lose += 1
                continue

            while player_total < 17:
                player_total += self.card_value(deck_copy.pop())
                if player_total > 21:
                    lose += 1
                    break

            if player_total > 21:
                continue

            while dealer_total < 17:
                dealer_total += self.card_value(deck_copy.pop())
                if dealer_total > 21:
                    win += 1
                    break

            if dealer_total > 21:
                continue

            if player_total > dealer_total:
                win += 1
            elif player_total == dealer_total:
                draw += 1
            else:
                lose += 1

        total_simulations = win + draw + lose
        return win / total_simulations, draw / total_simulations, lose / total_simulations

    def calculate_hand_value(self, cards):
        value = 0
        aces = 0
        for card in cards:
            v = self.card_value(card)
            value += v
            if v == 11:
                aces += 1

        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value

    def card_value(self, card):
        rank = card[0]
        if rank in 'TJQK':
            return 10
        elif rank == 'A':
            return 11
        else:
            return int(rank)

    def get_suggestion(self, player_cards, dealer_card):
        player_total = self.calculate_hand_value(player_cards)
        dealer_upcard_value = self.card_value(dealer_card)

        # Basic strategy rules for suggesting hit or stand
        if player_total >= 17:
            return "Stand"
        elif player_total <= 11:
            return "Hit"
        elif player_total == 12:
            if dealer_upcard_value in [4, 5, 6]:
                return "Stand"
            else:
                return "Hit"
        elif player_total in [13, 14, 15, 16]:
            if dealer_upcard_value in [2, 3, 4, 5, 6]:
                return "Stand"
            else:
                return "Hit"
        return "Stand"

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackApp(root)
    root.mainloop()
