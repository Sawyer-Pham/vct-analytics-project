"""Desktop matchup selector. Run with: python app.py."""

from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


DATABASE_PATH = Path(__file__).resolve().parent / "vlr.db"


def load_teams(database_path=DATABASE_PATH):
    """Read the existing dataset without creating or modifying a database."""
    with sqlite3.connect(database_path.as_uri() + "?mode=ro", uri=True) as conn:
        return conn.execute(
            "SELECT team_id, team_name, region FROM teams "
            "ORDER BY team_name COLLATE NOCASE, team_id"
        ).fetchall()


class MatchupSelector(ttk.Frame):
    def __init__(self, parent, teams):
        super().__init__(parent, padding=32)
        self.pack(fill="both", expand=True)
        self.teams = {
            f"{name} · {region or 'Unknown region'} (#{team_id})": team_id
            for team_id, name, region in teams
        }
        self.team_a = tk.StringVar()
        self.team_b = tk.StringVar()
        self.matchup = tk.StringVar(value="Select two teams to set up your matchup.")
        self.selected_team_ids = None
        self.predictor = None
        self.prediction = tk.StringVar()
        self.team_names = {team_id: name for team_id, name, _ in teams}

        ttk.Label(self, text="VCT Match Predictor", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(
            self, text=f"Choose your matchup from {len(teams)} teams in your dataset."
        ).pack(anchor="w", pady=(8, 28))

        selectors = ttk.Frame(self)
        selectors.pack(fill="x")
        selectors.columnconfigure(0, weight=1)
        selectors.columnconfigure(2, weight=1)
        for column, label, variable in (
            (0, "Team A", self.team_a), (2, "Team B", self.team_b)
        ):
            ttk.Label(selectors, text=label, font=("Segoe UI", 12, "bold")).grid(
                row=0, column=column, sticky="w", pady=(0, 8)
            )
            dropdown = ttk.Combobox(
                selectors, textvariable=variable, state="readonly", width=38
            )
            dropdown.grid(row=1, column=column, sticky="ew")
            if column == 0:
                self.dropdown_a = dropdown
            else:
                self.dropdown_b = dropdown
        ttk.Label(selectors, text="VS", padding=16).grid(row=1, column=1)
        ttk.Separator(self).pack(fill="x", pady=28)
        ttk.Label(self, textvariable=self.matchup, wraplength=720).pack(anchor="w")
        self.predict_button = ttk.Button(self, text="Predict winner", command=self.predict_matchup)
        self.predict_button.pack(anchor="w", pady=(16, 12))
        ttk.Label(self, textvariable=self.prediction, wraplength=720,
                  font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(self, text="Estimates use stored historical data and are not guaranteed outcomes.",
                  foreground="#666666").pack(anchor="w", pady=(12, 0))
        self.team_a.trace_add("write", self.update_matchup)
        self.team_b.trace_add("write", self.update_matchup)
        self.update_matchup()

    def update_matchup(self, *_):
        self.prediction.set("")
        a, b = self.team_a.get(), self.team_b.get()
        self.dropdown_a["values"] = [name for name in self.teams if name != b]
        self.dropdown_b["values"] = [name for name in self.teams if name != a]
        self.selected_team_ids = None
        if a and b and a != b:
            self.selected_team_ids = (self.teams[a], self.teams[b])
            self.matchup.set(f"Selected matchup: {a}  vs  {b}")
        else:
            self.matchup.set("Select two different teams to set up your matchup.")
        self.predict_button["state"] = "normal" if self.selected_team_ids else "disabled"

    def predict_matchup(self):
        if not self.selected_team_ids:
            return
        try:
            if self.predictor is None:
                from predictor import MatchPredictor
                self.predictor = MatchPredictor()
            team_a, team_b = self.selected_team_ids
            probability_a = self.predictor.predict(team_a, team_b)
            winner = team_a if probability_a >= 0.5 else team_b
            self.prediction.set(
                f"Predicted winner: {self.team_names[winner]}\n"
                f"{self.team_names[team_a]}: {probability_a:.1%}   |   "
                f"{self.team_names[team_b]}: {1 - probability_a:.1%}"
            )
        except (ImportError, OSError, sqlite3.Error, ValueError, KeyError) as exc:
            self.prediction.set("Prediction unavailable.")
            messagebox.showerror("Cannot predict matchup", str(exc))


def main():
    root = tk.Tk()
    root.title("VCT Match Predictor")
    root.geometry("900x460")
    root.minsize(780, 440)
    try:
        teams = load_teams()
        if len(teams) < 2:
            raise ValueError("The dataset needs at least two teams to select a matchup.")
    except (sqlite3.Error, ValueError) as exc:
        messagebox.showerror("Cannot load teams", f"Could not load teams from {DATABASE_PATH}:\n{exc}")
        root.destroy()
        return
    MatchupSelector(root, teams)
    root.mainloop()


if __name__ == "__main__":
    main()
