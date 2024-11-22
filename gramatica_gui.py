import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import List

class Grammar:
    def __init__(self, productions: dict, start_symbol: str):
        self.productions = productions
        self.start_symbol = start_symbol

    def generate_strings(self, num_strings=5, max_steps=10) -> List[str]:
        raise NotImplementedError("Este método debe implementarse en subclases.")

class RegularGrammar(Grammar):
    def generate_strings(self, num_strings=5, max_steps=10) -> List[str]:
        strings = []
        for _ in range(num_strings):
            current_string = self.start_symbol
            steps = 0
            while any(c.isupper() for c in current_string) and steps < max_steps:
                next_string = ""
                for symbol in current_string:
                    if symbol.isupper():
                        possible_productions = self.productions.get(symbol, [])
                        chosen_production = random.choice(possible_productions)
                        next_string += chosen_production
                    else:
                        next_string += symbol
                current_string = next_string
                steps += 1
            strings.append(current_string)
        return strings

class IndependentContextGrammar(Grammar):
    def generate_strings(self, num_strings=5, max_steps=10) -> List[str]:
        strings = []
        for _ in range(num_strings):
            current_string = [self.start_symbol]
            steps = 0
            while any(symbol.isupper() for symbol in current_string) and steps < max_steps:
                new_string = []
                for symbol in current_string:
                    if symbol.isupper():
                        production = random.choice(self.productions.get(symbol, [symbol]))
                        new_string.extend(production)
                    else:
                        new_string.append(symbol)
                current_string = new_string
                steps += 1
            strings.append("".join(current_string))
        return strings

class GrammarApp:
    def __init__(self, raiz):
        self.root = raiz
        self.root.title("Generador de Cadenas para Gramáticas")
        
        # Variables de interfaz
        self.grammar_type = tk.StringVar(value="regular")
        self.start_symbol = tk.StringVar(value="S")
        self.num_strings = tk.IntVar(value=5)
        self.max_steps = tk.IntVar(value=10)
        self.productions_text = tk.StringVar()
        
        # Configuración de la interfaz
        ttk.Label(raiz, text="Seleccione el tipo de gramática:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(raiz, text="Regular", variable=self.grammar_type, value="regular").grid(row=0, column=1)
        ttk.Radiobutton(raiz, text="Independiente de Contexto", variable=self.grammar_type, value="context_free").grid(row=0, column=2)
        
        ttk.Label(raiz, text="Símbolo inicial:").grid(row=1, column=0, sticky="w")
        ttk.Entry(raiz, textvariable=self.start_symbol, width=5).grid(row=1, column=1, sticky="w")
        
        ttk.Label(raiz, text="Producciones (formato: A->aB|b):").grid(row=2, column=0, sticky="w")
        ttk.Entry(raiz, textvariable=self.productions_text, width=40).grid(row=2, column=1, columnspan=2, sticky="w")
        
        ttk.Label(raiz, text="Número de cadenas:").grid(row=3, column=0, sticky="w")
        ttk.Entry(raiz, textvariable=self.num_strings, width=5).grid(row=3, column=1, sticky="w")
        
        ttk.Label(raiz, text="Pasos máximos de generación:").grid(row=4, column=0, sticky="w")
        ttk.Entry(raiz, textvariable=self.max_steps, width=5).grid(row=4, column=1, sticky="w")
        
        ttk.Button(raiz, text="Generar Cadenas", command=self.generate_strings).grid(row=5, column=0, columnspan=3)
        
        self.output_text = tk.Text(raiz, width=50, height=10)
        self.output_text.grid(row=6, column=0, columnspan=3)
    
    def parse_productions(self):
        """
        Convierte las producciones ingresadas por el usuario en un diccionario.
        """
        productions = {}
        productions_input = self.productions_text.get()
        for production in productions_input.split(","):
            head, body = production.split("->")
            productions[head.strip()] = [alt.strip() for alt in body.split("|")]
        return productions
    
    def generate_strings(self):
        """
        Genera las cadenas válidas según los parámetros de la interfaz.
        """
        try:
            productions = self.parse_productions()
            start_symbol = self.start_symbol.get()
            num_strings = self.num_strings.get()
            max_steps = self.max_steps.get()
            
            if self.grammar_type.get() == "regular":
                grammar = RegularGrammar(productions, start_symbol)
            else:
                grammar = IndependentContextGrammar(productions, start_symbol)
            
            strings = grammar.generate_strings(num_strings, max_steps)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "\n".join(strings))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar cadenas: {str(e)}")

# Inicializar la aplicación
raiz = tk.Tk()
app = GrammarApp(raiz)
raiz.mainloop()