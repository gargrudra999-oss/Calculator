"""
Modern Dark-Navy Tkinter Dashboard GUI for the Financial Risk Calculator.

Built exclusively with Python's built-in tkinter, tkinter.ttk, and
tkinter.messagebox modules. Uses Unicode symbols and canvas bars without
any external images, icons, fonts, or libraries.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from calculations import FinancialCalculator, ValidationError, format_inr
from database import DatabaseError


class Theme:
    """Centralized color palette and typography tokens."""

    BG_MAIN = "#0B132B"
    SIDEBAR_BG = "#111B36"
    CARD_BG = "#1C2541"
    CARD_ALT = "#233054"
    INPUT_BG = "#131C35"
    BORDER = "#2F4172"

    ACCENT = "#3A86FF"
    ACCENT_HOVER = "#5C9CFF"
    ACCENT_DARK = "#2563EB"

    SUCCESS = "#2EC4B6"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"
    DANGER_DARK = "#DC2626"

    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#CBD5E1"
    TEXT_MUTED = "#8EA0C2"

    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = (FONT_FAMILY, 20, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 10)
    FONT_SECTION = (FONT_FAMILY, 12, "bold")
    FONT_CARD_TITLE = (FONT_FAMILY, 9, "bold")
    FONT_METRIC = (FONT_FAMILY, 17, "bold")
    FONT_METRIC_SM = (FONT_FAMILY, 14, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9)


def configure_ttk_styles(root):
    """Configure ttk styles on top of the 'clam' theme for dark-navy widgets."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "Dark.TCombobox",
        fieldbackground=Theme.INPUT_BG,
        background=Theme.CARD_ALT,
        foreground=Theme.TEXT_PRIMARY,
        arrowcolor=Theme.TEXT_PRIMARY,
        bordercolor=Theme.BORDER,
        lightcolor=Theme.BORDER,
        darkcolor=Theme.BORDER,
        padding=6,
    )
    style.map(
        "Dark.TCombobox",
        fieldbackground=[("readonly", Theme.INPUT_BG)],
        foreground=[("readonly", Theme.TEXT_PRIMARY)],
        selectbackground=[("readonly", Theme.INPUT_BG)],
        selectforeground=[("readonly", Theme.TEXT_PRIMARY)],
    )

    # Style the Combobox dropdown listbox cleanly
    root.option_add("*TCombobox*Listbox.background", Theme.CARD_BG)
    root.option_add("*TCombobox*Listbox.foreground", Theme.TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.selectBackground", Theme.ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", Theme.TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.font", Theme.FONT_BODY)

    style.configure(
        "History.Treeview",
        background=Theme.CARD_BG,
        foreground=Theme.TEXT_PRIMARY,
        fieldbackground=Theme.CARD_BG,
        bordercolor=Theme.BORDER,
        borderwidth=0,
        rowheight=32,
        font=Theme.FONT_BODY,
    )
    style.configure(
        "History.Treeview.Heading",
        background=Theme.CARD_ALT,
        foreground=Theme.TEXT_PRIMARY,
        bordercolor=Theme.BORDER,
        relief="flat",
        font=Theme.FONT_BODY_BOLD,
        padding=(8, 8),
    )
    style.map(
        "History.Treeview",
        background=[("selected", Theme.ACCENT_DARK)],
        foreground=[("selected", Theme.TEXT_PRIMARY)],
    )
    style.map(
        "History.Treeview.Heading",
        background=[("active", Theme.ACCENT)],
    )

    style.configure(
        "Dark.Vertical.TScrollbar",
        background=Theme.CARD_ALT,
        troughcolor=Theme.BG_MAIN,
        bordercolor=Theme.BG_MAIN,
        arrowcolor=Theme.TEXT_SECONDARY,
        relief="flat",
    )
    style.configure(
        "Dark.Horizontal.TScrollbar",
        background=Theme.CARD_ALT,
        troughcolor=Theme.BG_MAIN,
        bordercolor=Theme.BG_MAIN,
        arrowcolor=Theme.TEXT_SECONDARY,
        relief="flat",
    )


def create_action_button(
    parent,
    text,
    command,
    bg=Theme.ACCENT,
    hover_bg=Theme.ACCENT_HOVER,
    fg=Theme.TEXT_PRIMARY,
    font=Theme.FONT_BODY_BOLD,
    padx=16,
    pady=9,
):
    """Create a flat, responsive button with hover color feedback."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        font=font,
        bd=0,
        relief="flat",
        cursor="hand2",
        padx=padx,
        pady=pady,
    )
    btn.bind("<Enter>", lambda _e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=bg))
    return btn


class ScrollableFrame(tk.Frame):
    """Scrollable container so content never clips on smaller screens."""

    def __init__(self, parent, bg=Theme.BG_MAIN):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.v_scroll = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            style="Dark.Vertical.TScrollbar",
        )
        self.inner = tk.Frame(self.canvas, bg=bg)

        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self.bind("<Destroy>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.inner_id, width=event.width)

    def _on_mousewheel(self, event):
        if (
            self.winfo_ismapped()
            and self.inner.winfo_height() > self.canvas.winfo_height()
        ):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, _event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event):
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass


class ResultCard(tk.Frame):
    """Styled dark-navy KPI / result display card with top accent bar."""

    def __init__(self, parent, title, initial_value="--", subtitle="", accent=Theme.ACCENT):
        super().__init__(
            parent,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
        )
        self.stripe = tk.Frame(self, bg=accent, height=3)
        self.stripe.pack(fill="x", side="top")

        body = tk.Frame(self, bg=Theme.CARD_BG, padx=16, pady=14)
        body.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            body,
            text=title.upper(),
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_CARD_TITLE,
            anchor="w",
        )
        self.title_label.pack(fill="x")

        self.value_label = tk.Label(
            body,
            text=initial_value,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_METRIC,
            anchor="w",
            pady=4,
        )
        self.value_label.pack(fill="x")

        self.subtitle_label = tk.Label(
            body,
            text=subtitle,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="w",
        )
        self.subtitle_label.pack(fill="x")

    def update_card(self, value, subtitle=None, value_color=None, accent=None):
        """Update displayed metric value and optional styling."""
        self.value_label.configure(text=value)
        if value_color is not None:
            self.value_label.configure(fg=value_color)
        if subtitle is not None:
            self.subtitle_label.configure(text=subtitle)
        if accent is not None:
            self.stripe.configure(bg=accent)


class BaseCalculatorView(tk.Frame):
    """Shared base class for calculator views providing layout, validation & DB saving."""

    def __init__(self, parent, app, title, subtitle):
        super().__init__(parent, bg=Theme.BG_MAIN)
        self.app = app
        self.calculator = app.calculator
        self.db = app.db

        self.scroll = ScrollableFrame(self, bg=Theme.BG_MAIN)
        self.scroll.pack(fill="both", expand=True)
        self.content = tk.Frame(self.scroll.inner, bg=Theme.BG_MAIN, padx=28, pady=24)
        self.content.pack(fill="both", expand=True)

        # Page header
        header = tk.Frame(self.content, bg=Theme.BG_MAIN)
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text=title,
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_TITLE,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            header,
            text=subtitle,
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SUBTITLE,
            anchor="w",
            pady=2,
        ).pack(fill="x")

    def create_card(self, parent, title=None, padding=18):
        """Create a bordered dark-navy panel with optional section heading."""
        outer = tk.Frame(
            parent,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=padding,
            pady=padding,
        )
        if title:
            tk.Label(
                outer,
                text=title,
                bg=Theme.CARD_BG,
                fg=Theme.TEXT_PRIMARY,
                font=Theme.FONT_SECTION,
                anchor="w",
            ).pack(fill="x", pady=(0, 12))
        return outer

    def add_input_field(self, parent, label_text, default_val="", hint="", on_enter=None):
        """Render a labeled entry field inside an input form card and return its StringVar."""
        block = tk.Frame(parent, bg=Theme.CARD_BG)
        block.pack(fill="x", pady=(0, 12))

        label_row = tk.Frame(block, bg=Theme.CARD_BG)
        label_row.pack(fill="x", pady=(0, 4))

        tk.Label(
            label_row,
            text=label_text,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY_BOLD,
            anchor="w",
        ).pack(side="left")

        if hint:
            tk.Label(
                label_row,
                text=hint,
                bg=Theme.CARD_BG,
                fg=Theme.TEXT_MUTED,
                font=Theme.FONT_SMALL,
                anchor="e",
            ).pack(side="right")

        var = tk.StringVar(value=default_val)
        entry = tk.Entry(
            block,
            textvariable=var,
            bg=Theme.INPUT_BG,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY,
            highlightbackground=Theme.BORDER,
            highlightcolor=Theme.ACCENT,
            highlightthickness=1,
            relief="flat",
            font=Theme.FONT_BODY,
        )
        entry.pack(fill="x", ipady=7)
        if on_enter is not None:
            entry.bind("<Return>", lambda _e: on_enter())
        return var, entry

    def create_status_banner(self, parent):
        """Create a reusable inline status/error banner below action buttons."""
        label = tk.Label(
            parent,
            text="",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
            anchor="w",
            justify="left",
            wraplength=340,
            pady=6,
        )
        label.pack(fill="x", pady=(10, 0))
        return label

    def show_error_status(self, status_label, message):
        """Display an inline validation error message."""
        status_label.configure(
            text=f"⚠ {message}",
            bg="#3B1A24",
            fg="#FCA5A5",
            padx=10,
            pady=8,
        )

    def show_success_status(self, status_label, message):
        """Display an inline success/saved confirmation message."""
        status_label.configure(
            text=f"✓ {message}",
            bg="#123539",
            fg=Theme.SUCCESS,
            padx=10,
            pady=8,
        )

    def clear_status(self, status_label):
        """Reset inline status banner."""
        status_label.configure(text="", bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED, padx=0, pady=6)

    def save_to_history(self, category, input_summary, result_summary):
        """Persist a calculation to SQLite3 and notify app views."""
        record_id = self.db.add_record(category, input_summary, result_summary)
        self.app.notify_history_updated()
        return record_id

    def draw_ratio_bar(self, canvas, primary_val, secondary_val, primary_color, secondary_color):
        """Draw a horizontal two-segment ratio bar on a Tkinter Canvas."""
        canvas._ratio_args = (primary_val, secondary_val, primary_color, secondary_color)
        canvas.delete("all")
        width = max(canvas.winfo_width(), 320)
        height = 16
        total = primary_val + secondary_val

        canvas.create_rectangle(0, 0, width, height, fill=Theme.INPUT_BG, outline="")
        if total <= 0:
            return

        p_ratio = max(0.0, min(1.0, primary_val / total))
        split_x = int(round(width * p_ratio))

        if split_x > 0:
            canvas.create_rectangle(0, 0, split_x, height, fill=primary_color, outline="")
        if split_x < width:
            canvas.create_rectangle(split_x, 0, width, height, fill=secondary_color, outline="")

    def bind_ratio_bar_resize(self, canvas):
        """Redraw a ratio bar automatically when the canvas width changes."""
        canvas._ratio_args = None

        def _on_resize(_event):
            args = getattr(canvas, "_ratio_args", None)
            if args is not None:
                self.draw_ratio_bar(canvas, *args)

        canvas.bind("<Configure>", _on_resize)


class DashboardHomeView(BaseCalculatorView):
    """Dashboard home screen with live SQLite stats, quick launch cards, and recent activity."""

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            title="Financial Risk Dashboard",
            subtitle="100% Offline Python Desktop Suite  •  Local SQLite3 Storage  •  Indian Rupee (₹)",
        )

        # Top KPI Summary Row
        kpi_grid = tk.Frame(self.content, bg=Theme.BG_MAIN)
        kpi_grid.pack(fill="x", pady=(0, 20))
        for col in range(4):
            kpi_grid.columnconfigure(col, weight=1, uniform="kpi")

        self.kpi_total = ResultCard(
            kpi_grid, "Saved Calculations", "0", "Stored in SQLite3", accent=Theme.ACCENT
        )
        self.kpi_total.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.kpi_top_cat = ResultCard(
            kpi_grid, "Most Used Module", "None yet", "By saved count", accent=Theme.SUCCESS
        )
        self.kpi_top_cat.grid(row=0, column=1, sticky="nsew", padx=5)

        self.kpi_latest = ResultCard(
            kpi_grid, "Last Calculation", "None yet", "Timestamp", accent=Theme.WARNING
        )
        self.kpi_latest.grid(row=0, column=2, sticky="nsew", padx=5)

        self.kpi_mode = ResultCard(
            kpi_grid, "System Status", "Offline Ready", "No internet required", accent=Theme.ACCENT
        )
        self.kpi_mode.grid(row=0, column=3, sticky="nsew", padx=(10, 0))

        # Modules Quick-Launch Grid
        tk.Label(
            self.content,
            text="Calculator Modules",
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_SECTION,
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        modules_grid = tk.Frame(self.content, bg=Theme.BG_MAIN)
        modules_grid.pack(fill="x", pady=(0, 20))
        modules_grid.columnconfigure(0, weight=1, uniform="mod")
        modules_grid.columnconfigure(1, weight=1, uniform="mod")

        module_specs = [
            (
                "loan_emi",
                "▣  Loan EMI Calculator",
                "Compute monthly EMI, total interest payable, and total repayment across years or months (including 0% loans).",
                Theme.ACCENT,
            ),
            (
                "compound_interest",
                "◈  Compound Interest Calculator",
                "Project compounding returns across Annual, Semi-Annual, Quarterly, Monthly, or Daily compounding intervals.",
                Theme.SUCCESS,
            ),
            (
                "investment_growth",
                "↗  Investment Growth Calculator",
                "Combine an initial lump sum with monthly SIP contributions to project total invested capital, profit, and future value.",
                Theme.ACCENT,
            ),
            (
                "risk_simulator",
                "△  Financial Risk Simulator",
                "Compare Low, Moderate, and High hypothetical return scenarios with editable assumptions and scenario spreads.",
                Theme.WARNING,
            ),
        ]

        for idx, (page_key, mod_title, mod_desc, accent) in enumerate(module_specs):
            r, c = divmod(idx, 2)
            pad_x = (0, 8) if c == 0 else (8, 0)
            card = tk.Frame(
                modules_grid,
                bg=Theme.CARD_BG,
                highlightbackground=Theme.BORDER,
                highlightthickness=1,
            )
            card.grid(row=r, column=c, sticky="nsew", padx=pad_x, pady=(0, 12))

            tk.Frame(card, bg=accent, height=3).pack(fill="x")
            inner = tk.Frame(card, bg=Theme.CARD_BG, padx=18, pady=16)
            inner.pack(fill="both", expand=True)

            tk.Label(
                inner,
                text=mod_title,
                bg=Theme.CARD_BG,
                fg=Theme.TEXT_PRIMARY,
                font=Theme.FONT_SECTION,
                anchor="w",
            ).pack(fill="x")

            tk.Label(
                inner,
                text=mod_desc,
                bg=Theme.CARD_BG,
                fg=Theme.TEXT_SECONDARY,
                font=Theme.FONT_SMALL,
                anchor="w",
                justify="left",
                wraplength=390,
                pady=8,
            ).pack(fill="x")

            btn_row = tk.Frame(inner, bg=Theme.CARD_BG)
            btn_row.pack(fill="x", pady=(4, 0))
            create_action_button(
                btn_row,
                "Open Module →",
                command=lambda k=page_key: self.app.show_view(k),
                bg=Theme.CARD_ALT,
                hover_bg=Theme.ACCENT,
                padx=14,
                pady=6,
            ).pack(side="left")

        # Recent Activity Card
        recent_header = tk.Frame(self.content, bg=Theme.BG_MAIN)
        recent_header.pack(fill="x", pady=(4, 8))

        tk.Label(
            recent_header,
            text="Recent Calculation Activity",
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_SECTION,
            anchor="w",
        ).pack(side="left")

        create_action_button(
            recent_header,
            "View Full History →",
            command=lambda: self.app.show_view("history"),
            bg=Theme.CARD_ALT,
            hover_bg=Theme.ACCENT,
            padx=12,
            pady=5,
            font=Theme.FONT_SMALL,
        ).pack(side="right")

        self.recent_card = self.create_card(self.content, padding=14)
        self.recent_card.pack(fill="x")

        self.recent_container = tk.Frame(self.recent_card, bg=Theme.CARD_BG)
        self.recent_container.pack(fill="x")

        self.refresh_data()

    def refresh_data(self):
        """Reload live statistics and latest 5 records from SQLite."""
        try:
            stats = self.db.get_summary_stats()
            records = self.db.get_all_records()[:5]
        except DatabaseError as exc:
            self.kpi_total.update_card("Error", str(exc), value_color=Theme.DANGER)
            return

        total = stats["total"]
        self.kpi_total.update_card(str(total), f"{total} record(s) in local DB")

        by_cat = stats["by_category"]
        if by_cat:
            top_cat = max(by_cat, key=by_cat.get)
            self.kpi_top_cat.update_card(top_cat, f"{by_cat[top_cat]} calculation(s)")
        else:
            self.kpi_top_cat.update_card("None yet", "Run any calculator")

        latest = stats["latest"]
        if latest:
            self.kpi_latest.update_card(latest["category"], latest["created_at"])
        else:
            self.kpi_latest.update_card("None yet", "No saved history")

        for child in self.recent_container.winfo_children():
            child.destroy()

        if not records:
            tk.Label(
                self.recent_container,
                text="No calculations recorded yet. Open any module above to run your first calculation.",
                bg=Theme.CARD_BG,
                fg=Theme.TEXT_MUTED,
                font=Theme.FONT_BODY,
                anchor="w",
                pady=8,
            ).pack(fill="x")
            return

        for idx, rec in enumerate(records):
            row_bg = Theme.CARD_ALT if idx % 2 == 0 else Theme.CARD_BG
            row = tk.Frame(self.recent_container, bg=row_bg, padx=10, pady=8)
            row.pack(fill="x", pady=2)

            tk.Label(
                row,
                text=f"#{rec['id']}  {rec['category']}",
                bg=row_bg,
                fg=Theme.ACCENT_HOVER,
                font=Theme.FONT_BODY_BOLD,
                width=22,
                anchor="w",
            ).pack(side="left")

            preview_text = rec["results"]
            if len(preview_text) > 92:
                preview_text = preview_text[:89] + "..."

            tk.Label(
                row,
                text=preview_text,
                bg=row_bg,
                fg=Theme.TEXT_PRIMARY,
                font=Theme.FONT_SMALL,
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=(8, 12))

            tk.Label(
                row,
                text=rec["created_at"],
                bg=row_bg,
                fg=Theme.TEXT_MUTED,
                font=Theme.FONT_SMALL,
                anchor="e",
            ).pack(side="right")


class LoanEMIView(BaseCalculatorView):
    """Module 1: Loan EMI Calculator View."""

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            title="Loan EMI Calculator",
            subtitle="Calculate Equated Monthly Installments, total interest payable, and total repayment.",
        )

        body = tk.Frame(self.content, bg=Theme.BG_MAIN)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2, uniform="emi")
        body.columnconfigure(1, weight=3, uniform="emi")

        # Left: Input Card
        form_card = self.create_card(body, title="Loan Parameters")
        form_card.grid(row=0, column=0, sticky="new", padx=(0, 12))

        self.amount_var, _ = self.add_input_field(
            form_card, "Loan Amount (₹)", "500000", "Principal > 0", on_enter=self.calculate
        )
        self.rate_var, _ = self.add_input_field(
            form_card, "Annual Interest Rate (%)", "8.5", "0% supported", on_enter=self.calculate
        )

        # Duration + unit selector
        dur_block = tk.Frame(form_card, bg=Theme.CARD_BG)
        dur_block.pack(fill="x", pady=(0, 14))
        tk.Label(
            dur_block,
            text="Loan Duration",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY_BOLD,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        dur_row = tk.Frame(dur_block, bg=Theme.CARD_BG)
        dur_row.pack(fill="x")
        self.duration_var = tk.StringVar(value="5")
        dur_entry = tk.Entry(
            dur_row,
            textvariable=self.duration_var,
            bg=Theme.INPUT_BG,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY,
            highlightbackground=Theme.BORDER,
            highlightcolor=Theme.ACCENT,
            highlightthickness=1,
            relief="flat",
            font=Theme.FONT_BODY,
        )
        dur_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        dur_entry.bind("<Return>", lambda _e: self.calculate())

        self.unit_var = tk.StringVar(value="Years")
        unit_combo = ttk.Combobox(
            dur_row,
            textvariable=self.unit_var,
            values=("Years", "Months"),
            state="readonly",
            width=10,
            style="Dark.TCombobox",
            font=Theme.FONT_BODY,
        )
        unit_combo.pack(side="right")

        btn_row = tk.Frame(form_card, bg=Theme.CARD_BG)
        btn_row.pack(fill="x", pady=(6, 0))
        create_action_button(btn_row, "Calculate EMI", self.calculate).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        create_action_button(
            btn_row,
            "Reset",
            self.reset_fields,
            bg=Theme.CARD_ALT,
            hover_bg=Theme.BORDER,
        ).pack(side="right")

        self.status_label = self.create_status_banner(form_card)

        # Right: Results Panel
        results_col = tk.Frame(body, bg=Theme.BG_MAIN)
        results_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self.card_emi = ResultCard(
            results_col, "Monthly EMI", "₹0.00", "Equated monthly installment", accent=Theme.ACCENT
        )
        self.card_emi.pack(fill="x", pady=(0, 12))

        sub_row = tk.Frame(results_col, bg=Theme.BG_MAIN)
        sub_row.pack(fill="x", pady=(0, 12))
        sub_row.columnconfigure(0, weight=1, uniform="sub")
        sub_row.columnconfigure(1, weight=1, uniform="sub")

        self.card_interest = ResultCard(
            sub_row, "Total Interest", "₹0.00", "Interest cost over tenure", accent=Theme.WARNING
        )
        self.card_interest.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_total = ResultCard(
            sub_row, "Total Repayment", "₹0.00", "Principal + Interest", accent=Theme.SUCCESS
        )
        self.card_total.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        breakdown_card = self.create_card(results_col, title="Repayment Breakdown")
        breakdown_card.pack(fill="x")

        self.breakdown_label = tk.Label(
            breakdown_card,
            text="Enter loan parameters and click 'Calculate EMI' to inspect principal vs. interest split.",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY,
            anchor="w",
            justify="left",
            wraplength=460,
        )
        self.breakdown_label.pack(fill="x", pady=(0, 10))

        self.bar_canvas = tk.Canvas(
            breakdown_card, height=16, bg=Theme.INPUT_BG, highlightthickness=0
        )
        self.bar_canvas.pack(fill="x", pady=(0, 8))
        self.bind_ratio_bar_resize(self.bar_canvas)

        legend = tk.Frame(breakdown_card, bg=Theme.CARD_BG)
        legend.pack(fill="x")
        tk.Label(
            legend, text="■ Principal", bg=Theme.CARD_BG, fg=Theme.ACCENT, font=Theme.FONT_SMALL
        ).pack(side="left", padx=(0, 16))
        tk.Label(
            legend, text="■ Interest", bg=Theme.CARD_BG, fg=Theme.WARNING, font=Theme.FONT_SMALL
        ).pack(side="left")

    def calculate(self):
        """Validate inputs, calculate EMI, update UI, and save to SQLite."""
        self.clear_status(self.status_label)
        try:
            res = self.calculator.calculate_loan_emi(
                self.amount_var.get(),
                self.rate_var.get(),
                self.duration_var.get(),
                self.unit_var.get(),
            )
        except ValidationError as exc:
            self.show_error_status(self.status_label, str(exc))
            return

        emi_str = format_inr(res["monthly_emi"])
        int_str = format_inr(res["total_interest"])
        tot_str = format_inr(res["total_repayment"])

        months = res["total_months"]
        months_disp = f"{int(months)}" if abs(months - round(months)) < 1e-6 else f"{months:.2f}"
        inst_word = "installment" if months_disp == "1" else "installments"

        self.card_emi.update_card(emi_str, f"For {months_disp} monthly {inst_word}")
        self.card_interest.update_card(
            int_str,
            "Zero-interest loan" if res["annual_rate"] == 0 else f"At {res['annual_rate']:.2f}% p.a.",
        )
        self.card_total.update_card(tot_str, f"Principal: {format_inr(res['loan_amount'])}")

        if res["total_repayment"] > 0:
            principal_pct = (res["loan_amount"] / res["total_repayment"]) * 100.0
            interest_pct = (res["total_interest"] / res["total_repayment"]) * 100.0
        else:
            principal_pct = 0.0
            interest_pct = 0.0
        self.breakdown_label.configure(
            text=(
                f"Principal Share: {principal_pct:.1f}% ({format_inr(res['loan_amount'])})   •   "
                f"Interest Share: {interest_pct:.1f}% ({int_str})"
            )
        )
        self.draw_ratio_bar(
            self.bar_canvas,
            res["loan_amount"],
            res["total_interest"],
            Theme.ACCENT,
            Theme.WARNING,
        )

        input_summary = (
            f"Loan: {format_inr(res['loan_amount'])}, "
            f"Rate: {res['annual_rate']:.2f}%, "
            f"Duration: {res['duration']:g} {res['duration_unit']}"
        )
        result_summary = (
            f"EMI: {emi_str} | Total Interest: {int_str} | Total Repayment: {tot_str}"
        )
        try:
            rec_id = self.save_to_history("Loan EMI", input_summary, result_summary)
            self.show_success_status(
                self.status_label, f"Calculated & saved to History (ID #{rec_id})."
            )
        except DatabaseError as exc:
            self.show_error_status(self.status_label, str(exc))

    def reset_fields(self):
        """Reset Loan EMI inputs and clear displayed results."""
        self.amount_var.set("")
        self.rate_var.set("")
        self.duration_var.set("")
        self.unit_var.set("Years")
        self.card_emi.update_card("₹0.00", "Equated monthly installment")
        self.card_interest.update_card("₹0.00", "Interest cost over tenure")
        self.card_total.update_card("₹0.00", "Principal + Interest")
        self.breakdown_label.configure(
            text="Enter loan parameters and click 'Calculate EMI' to inspect principal vs. interest split."
        )
        self.bar_canvas._ratio_args = None
        self.bar_canvas.delete("all")
        self.clear_status(self.status_label)


class CompoundInterestView(BaseCalculatorView):
    """Module 2: Compound Interest Calculator View."""

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            title="Compound Interest Calculator",
            subtitle="Compute compound growth across different compounding frequencies.",
        )

        body = tk.Frame(self.content, bg=Theme.BG_MAIN)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2, uniform="ci")
        body.columnconfigure(1, weight=3, uniform="ci")

        form_card = self.create_card(body, title="Compounding Inputs")
        form_card.grid(row=0, column=0, sticky="new", padx=(0, 12))

        self.principal_var, _ = self.add_input_field(
            form_card, "Principal Amount (₹)", "100000", "Principal > 0", on_enter=self.calculate
        )
        self.rate_var, _ = self.add_input_field(
            form_card, "Annual Interest Rate (%)", "7.5", "0% supported", on_enter=self.calculate
        )
        self.years_var, _ = self.add_input_field(
            form_card, "Duration (Years)", "10", "Up to 100 yrs", on_enter=self.calculate
        )

        freq_block = tk.Frame(form_card, bg=Theme.CARD_BG)
        freq_block.pack(fill="x", pady=(0, 14))
        tk.Label(
            freq_block,
            text="Compounding Frequency",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY_BOLD,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.freq_var = tk.StringVar(value="Quarterly")
        freq_combo = ttk.Combobox(
            freq_block,
            textvariable=self.freq_var,
            values=tuple(FinancialCalculator.COMPOUNDING_FREQUENCIES.keys()),
            state="readonly",
            style="Dark.TCombobox",
            font=Theme.FONT_BODY,
        )
        freq_combo.pack(fill="x")

        btn_row = tk.Frame(form_card, bg=Theme.CARD_BG)
        btn_row.pack(fill="x", pady=(6, 0))
        create_action_button(btn_row, "Calculate Interest", self.calculate).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        create_action_button(
            btn_row,
            "Reset",
            self.reset_fields,
            bg=Theme.CARD_ALT,
            hover_bg=Theme.BORDER,
        ).pack(side="right")

        self.status_label = self.create_status_banner(form_card)

        results_col = tk.Frame(body, bg=Theme.BG_MAIN)
        results_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self.card_final = ResultCard(
            results_col, "Final Amount", "₹0.00", "Maturity value", accent=Theme.ACCENT
        )
        self.card_final.pack(fill="x", pady=(0, 12))

        sub_row = tk.Frame(results_col, bg=Theme.BG_MAIN)
        sub_row.pack(fill="x", pady=(0, 12))
        sub_row.columnconfigure(0, weight=1, uniform="ci_sub")
        sub_row.columnconfigure(1, weight=1, uniform="ci_sub")

        self.card_ci = ResultCard(
            sub_row, "Compound Interest", "₹0.00", "Accrued compound return", accent=Theme.SUCCESS
        )
        self.card_ci.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_earned = ResultCard(
            sub_row, "Total Interest Earned", "₹0.00", "Gain over principal", accent=Theme.SUCCESS
        )
        self.card_earned.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        breakdown_card = self.create_card(results_col, title="Principal vs. Interest Composition")
        breakdown_card.pack(fill="x")

        self.breakdown_label = tk.Label(
            breakdown_card,
            text="Enter principal, rate, duration, and frequency to calculate compound growth.",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY,
            anchor="w",
            justify="left",
            wraplength=460,
        )
        self.breakdown_label.pack(fill="x", pady=(0, 10))

        self.bar_canvas = tk.Canvas(
            breakdown_card, height=16, bg=Theme.INPUT_BG, highlightthickness=0
        )
        self.bar_canvas.pack(fill="x", pady=(0, 8))
        self.bind_ratio_bar_resize(self.bar_canvas)

        legend = tk.Frame(breakdown_card, bg=Theme.CARD_BG)
        legend.pack(fill="x")
        tk.Label(
            legend, text="■ Principal", bg=Theme.CARD_BG, fg=Theme.ACCENT, font=Theme.FONT_SMALL
        ).pack(side="left", padx=(0, 16))
        tk.Label(
            legend, text="■ Interest Earned", bg=Theme.CARD_BG, fg=Theme.SUCCESS, font=Theme.FONT_SMALL
        ).pack(side="left")

    def calculate(self):
        """Validate inputs, calculate compound interest, update UI, and save history."""
        self.clear_status(self.status_label)
        try:
            res = self.calculator.calculate_compound_interest(
                self.principal_var.get(),
                self.rate_var.get(),
                self.years_var.get(),
                self.freq_var.get(),
            )
        except ValidationError as exc:
            self.show_error_status(self.status_label, str(exc))
            return

        ci_str = format_inr(res["compound_interest"])
        final_str = format_inr(res["final_amount"])
        earned_str = format_inr(res["total_interest_earned"])
        total_periods = res["periods_per_year"] * res["years"]

        self.card_final.update_card(
            final_str,
            f"Compounded {res['frequency_label']} ({total_periods:g} periods)",
        )
        self.card_ci.update_card(ci_str, f"At {res['annual_rate']:.2f}% annual rate")
        self.card_earned.update_card(
            earned_str,
            f"Return multiple: {(res['final_amount'] / res['principal']):.2f}x",
        )

        if res["final_amount"] > 0:
            p_pct = (res["principal"] / res["final_amount"]) * 100.0
            i_pct = (res["compound_interest"] / res["final_amount"]) * 100.0
        else:
            p_pct = 0.0
            i_pct = 0.0
        self.breakdown_label.configure(
            text=(
                f"Principal: {p_pct:.1f}% ({format_inr(res['principal'])})   •   "
                f"Interest Earned: {i_pct:.1f}% ({earned_str})"
            )
        )
        self.draw_ratio_bar(
            self.bar_canvas,
            res["principal"],
            res["compound_interest"],
            Theme.ACCENT,
            Theme.SUCCESS,
        )

        input_summary = (
            f"Principal: {format_inr(res['principal'])}, "
            f"Rate: {res['annual_rate']:.2f}%, "
            f"Duration: {res['years']:g} yrs, "
            f"Freq: {res['frequency_label']}"
        )
        result_summary = (
            f"Compound Interest: {ci_str} | Final Amount: {final_str} | "
            f"Total Interest Earned: {earned_str}"
        )
        try:
            rec_id = self.save_to_history("Compound Interest", input_summary, result_summary)
            self.show_success_status(
                self.status_label, f"Calculated & saved to History (ID #{rec_id})."
            )
        except DatabaseError as exc:
            self.show_error_status(self.status_label, str(exc))

    def reset_fields(self):
        """Reset Compound Interest inputs and outputs."""
        self.principal_var.set("")
        self.rate_var.set("")
        self.years_var.set("")
        self.freq_var.set("Annually")
        self.card_final.update_card("₹0.00", "Maturity value")
        self.card_ci.update_card("₹0.00", "Accrued compound return")
        self.card_earned.update_card("₹0.00", "Gain over principal")
        self.breakdown_label.configure(
            text="Enter principal, rate, duration, and frequency to calculate compound growth."
        )
        self.bar_canvas._ratio_args = None
        self.bar_canvas.delete("all")
        self.clear_status(self.status_label)


class InvestmentGrowthView(BaseCalculatorView):
    """Module 3: Investment Growth Calculator View."""

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            title="Investment Growth Calculator",
            subtitle="Project wealth creation from initial capital plus recurring monthly investments (SIP).",
        )

        body = tk.Frame(self.content, bg=Theme.BG_MAIN)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2, uniform="inv")
        body.columnconfigure(1, weight=3, uniform="inv")

        form_card = self.create_card(body, title="Investment Plan")
        form_card.grid(row=0, column=0, sticky="new", padx=(0, 12))

        self.initial_var, _ = self.add_input_field(
            form_card, "Initial Investment (₹)", "50000", "0 or more", on_enter=self.calculate
        )
        self.monthly_var, _ = self.add_input_field(
            form_card, "Monthly Investment (₹)", "10000", "0 or more", on_enter=self.calculate
        )
        self.return_var, _ = self.add_input_field(
            form_card, "Annual Expected Return (%)", "12", "0% supported", on_enter=self.calculate
        )
        self.years_var, _ = self.add_input_field(
            form_card, "Investment Duration (Years)", "10", "Up to 100 yrs", on_enter=self.calculate
        )

        btn_row = tk.Frame(form_card, bg=Theme.CARD_BG)
        btn_row.pack(fill="x", pady=(6, 0))
        create_action_button(btn_row, "Calculate Growth", self.calculate).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        create_action_button(
            btn_row,
            "Reset",
            self.reset_fields,
            bg=Theme.CARD_ALT,
            hover_bg=Theme.BORDER,
        ).pack(side="right")

        self.status_label = self.create_status_banner(form_card)

        results_col = tk.Frame(body, bg=Theme.BG_MAIN)
        results_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self.card_fv = ResultCard(
            results_col, "Future Value", "₹0.00", "Projected portfolio value", accent=Theme.ACCENT
        )
        self.card_fv.pack(fill="x", pady=(0, 12))

        sub_row = tk.Frame(results_col, bg=Theme.BG_MAIN)
        sub_row.pack(fill="x", pady=(0, 12))
        sub_row.columnconfigure(0, weight=1, uniform="inv_sub")
        sub_row.columnconfigure(1, weight=1, uniform="inv_sub")

        self.card_invested = ResultCard(
            sub_row, "Total Investment", "₹0.00", "Total out-of-pocket capital", accent=Theme.ACCENT
        )
        self.card_invested.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_profit = ResultCard(
            sub_row, "Estimated Profit", "₹0.00", "Projected wealth gain", accent=Theme.SUCCESS
        )
        self.card_profit.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        breakdown_card = self.create_card(results_col, title="Capital vs. Wealth Gain")
        breakdown_card.pack(fill="x")

        self.breakdown_label = tk.Label(
            breakdown_card,
            text="Enter your initial lump sum, monthly contribution, expected return, and duration.",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY,
            anchor="w",
            justify="left",
            wraplength=460,
        )
        self.breakdown_label.pack(fill="x", pady=(0, 10))

        self.bar_canvas = tk.Canvas(
            breakdown_card, height=16, bg=Theme.INPUT_BG, highlightthickness=0
        )
        self.bar_canvas.pack(fill="x", pady=(0, 8))
        self.bind_ratio_bar_resize(self.bar_canvas)

        legend = tk.Frame(breakdown_card, bg=Theme.CARD_BG)
        legend.pack(fill="x")
        tk.Label(
            legend, text="■ Total Invested", bg=Theme.CARD_BG, fg=Theme.ACCENT, font=Theme.FONT_SMALL
        ).pack(side="left", padx=(0, 16))
        tk.Label(
            legend, text="■ Estimated Profit", bg=Theme.CARD_BG, fg=Theme.SUCCESS, font=Theme.FONT_SMALL
        ).pack(side="left")

    def calculate(self):
        """Validate inputs, compute investment growth, update UI, and save to SQLite."""
        self.clear_status(self.status_label)
        try:
            res = self.calculator.calculate_investment_growth(
                self.initial_var.get(),
                self.monthly_var.get(),
                self.return_var.get(),
                self.years_var.get(),
            )
        except ValidationError as exc:
            self.show_error_status(self.status_label, str(exc))
            return

        inv_str = format_inr(res["total_investment"])
        prof_str = format_inr(res["estimated_profit"])
        fv_str = format_inr(res["future_value"])

        gain_pct = (
            (res["estimated_profit"] / res["total_investment"]) * 100.0
            if res["total_investment"] > 0
            else 0.0
        )
        month_word = "month" if res["total_months"] == 1 else "months"

        self.card_fv.update_card(
            fv_str, f"After {res['total_months']} {month_word} at {res['annual_return']:.2f}% p.a."
        )
        self.card_invested.update_card(
            inv_str,
            f"Initial: {format_inr(res['initial_investment'])} + {res['total_months']}×{format_inr(res['monthly_investment'])}",
        )
        self.card_profit.update_card(prof_str, f"Total return: +{gain_pct:.1f}%")

        if res["future_value"] > 0:
            inv_share = (res["total_investment"] / res["future_value"]) * 100.0
            prof_share = (res["estimated_profit"] / res["future_value"]) * 100.0
        else:
            inv_share = 0.0
            prof_share = 0.0
        self.breakdown_label.configure(
            text=(
                f"Invested Share: {inv_share:.1f}% ({inv_str})   •   "
                f"Profit Share: {prof_share:.1f}% ({prof_str})"
            )
        )
        self.draw_ratio_bar(
            self.bar_canvas,
            res["total_investment"],
            res["estimated_profit"],
            Theme.ACCENT,
            Theme.SUCCESS,
        )

        input_summary = (
            f"Initial: {format_inr(res['initial_investment'])}, "
            f"Monthly: {format_inr(res['monthly_investment'])}, "
            f"Return: {res['annual_return']:.2f}%, "
            f"Duration: {res['years']:g} yrs"
        )
        result_summary = (
            f"Total Investment: {inv_str} | Estimated Profit: {prof_str} | Future Value: {fv_str}"
        )
        try:
            rec_id = self.save_to_history("Investment Growth", input_summary, result_summary)
            self.show_success_status(
                self.status_label, f"Calculated & saved to History (ID #{rec_id})."
            )
        except DatabaseError as exc:
            self.show_error_status(self.status_label, str(exc))

    def reset_fields(self):
        """Reset Investment Growth inputs and outputs."""
        self.initial_var.set("")
        self.monthly_var.set("")
        self.return_var.set("")
        self.years_var.set("")
        self.card_fv.update_card("₹0.00", "Projected portfolio value")
        self.card_invested.update_card("₹0.00", "Total out-of-pocket capital")
        self.card_profit.update_card("₹0.00", "Projected wealth gain")
        self.breakdown_label.configure(
            text="Enter your initial lump sum, monthly contribution, expected return, and duration."
        )
        self.bar_canvas._ratio_args = None
        self.bar_canvas.delete("all")
        self.clear_status(self.status_label)


class RiskSimulatorView(BaseCalculatorView):
    """Module 4: Financial Risk Simulator View with three clearly labeled hypothetical scenarios."""

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            title="Financial Risk Simulator",
            subtitle="Compare Low, Moderate, and High return assumptions to evaluate upside and downside risk.",
        )

        # Mandatory Hypothetical Notice Banner
        notice = tk.Frame(
            self.content,
            bg="#2E2314",
            highlightbackground=Theme.WARNING,
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        notice.pack(fill="x", pady=(0, 16))
        tk.Label(
            notice,
            text=(
                "⚠ HYPOTHETICAL SCENARIO ANALYSIS: All Low, Moderate, and High projections below "
                "are hypothetical illustrations based on your chosen return assumptions. "
                "Actual market returns vary and losses are possible."
            ),
            bg="#2E2314",
            fg="#FDE68A",
            font=Theme.FONT_SMALL,
            anchor="w",
            justify="left",
            wraplength=860,
        ).pack(fill="x")

        body = tk.Frame(self.content, bg=Theme.BG_MAIN)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2, uniform="risk")
        body.columnconfigure(1, weight=3, uniform="risk")

        # Left: Simulation Inputs & Editable Assumptions
        form_card = self.create_card(body, title="Simulation Inputs & Assumptions")
        form_card.grid(row=0, column=0, sticky="new", padx=(0, 12))

        self.initial_var, _ = self.add_input_field(
            form_card, "Initial Investment (₹)", "100000", "0 or more", on_enter=self.calculate
        )
        self.monthly_var, _ = self.add_input_field(
            form_card, "Monthly Investment (₹)", "5000", "0 or more", on_enter=self.calculate
        )
        self.years_var, _ = self.add_input_field(
            form_card, "Investment Horizon (Years)", "10", "Up to 100 yrs", on_enter=self.calculate
        )

        tk.Frame(form_card, bg=Theme.BORDER, height=1).pack(fill="x", pady=(4, 12))

        tk.Label(
            form_card,
            text="Hypothetical Annual Return Assumptions (%)",
            bg=Theme.CARD_BG,
            fg=Theme.WARNING,
            font=Theme.FONT_BODY_BOLD,
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self.low_rate_var, _ = self.add_input_field(
            form_card, "Low Return Assumption (%)", "5", "Supports negative/0%", on_enter=self.calculate
        )
        self.mod_rate_var, _ = self.add_input_field(
            form_card, "Moderate Return Assumption (%)", "11", "Supports negative/0%", on_enter=self.calculate
        )
        self.high_rate_var, _ = self.add_input_field(
            form_card, "High Return Assumption (%)", "16", "Supports negative/0%", on_enter=self.calculate
        )

        btn_row = tk.Frame(form_card, bg=Theme.CARD_BG)
        btn_row.pack(fill="x", pady=(6, 0))
        create_action_button(btn_row, "Run Simulation", self.calculate).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        create_action_button(
            btn_row,
            "Reset Defaults",
            self.reset_defaults,
            bg=Theme.CARD_ALT,
            hover_bg=Theme.BORDER,
        ).pack(side="right")

        self.status_label = self.create_status_banner(form_card)

        # Right: Scenario Cards + Differences
        results_col = tk.Frame(body, bg=Theme.BG_MAIN)
        results_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        scenarios_row = tk.Frame(results_col, bg=Theme.BG_MAIN)
        scenarios_row.pack(fill="x", pady=(0, 12))
        for c in range(3):
            scenarios_row.columnconfigure(c, weight=1, uniform="scen")

        self.card_low = self._create_scenario_card(
            scenarios_row, "HYPOTHETICAL: LOW RETURN", Theme.DANGER
        )
        self.card_low["frame"].grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_mod = self._create_scenario_card(
            scenarios_row, "HYPOTHETICAL: MODERATE", Theme.WARNING
        )
        self.card_mod["frame"].grid(row=0, column=1, sticky="nsew", padx=3)

        self.card_high = self._create_scenario_card(
            scenarios_row, "HYPOTHETICAL: HIGH RETURN", Theme.SUCCESS
        )
        self.card_high["frame"].grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # Scenario Differences Card
        diff_card = self.create_card(
            results_col, title="Scenario Spread & Differences (Hypothetical)"
        )
        diff_card.pack(fill="x", pady=(0, 12))

        diff_grid = tk.Frame(diff_card, bg=Theme.CARD_BG)
        diff_grid.pack(fill="x")
        for c in range(3):
            diff_grid.columnconfigure(c, weight=1, uniform="diff")

        self.diff_high_low = ResultCard(
            diff_grid, "High vs. Low Spread", "₹0.00", "Total range width", accent=Theme.ACCENT
        )
        self.diff_high_low.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.diff_mod_low = ResultCard(
            diff_grid, "Moderate vs. Low", "₹0.00", "Baseline uplift", accent=Theme.WARNING
        )
        self.diff_mod_low.grid(row=0, column=1, sticky="nsew", padx=3)

        self.diff_high_mod = ResultCard(
            diff_grid, "High vs. Moderate", "₹0.00", "Upside potential", accent=Theme.SUCCESS
        )
        self.diff_high_mod.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # Visual Comparison Bars
        chart_card = self.create_card(
            results_col, title="Hypothetical Value Comparison"
        )
        chart_card.pack(fill="x")

        self.invested_ref_label = tk.Label(
            chart_card,
            text="Total Capital Invested: ₹0.00  |  Run simulation to compare scenarios.",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="w",
        )
        self.invested_ref_label.pack(fill="x", pady=(0, 10))

        self._last_scenarios = None
        self.compare_canvas = tk.Canvas(
            chart_card, height=118, bg=Theme.CARD_BG, highlightthickness=0
        )
        self.compare_canvas.pack(fill="x")
        self.compare_canvas.bind(
            "<Configure>",
            lambda _e: self._draw_comparison_bars(self._last_scenarios)
            if self._last_scenarios is not None
            else None,
        )

    def _create_scenario_card(self, parent, header_text, accent):
        frame = tk.Frame(
            parent,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
        )
        tk.Frame(frame, bg=accent, height=3).pack(fill="x")
        inner = tk.Frame(frame, bg=Theme.CARD_BG, padx=12, pady=12)
        inner.pack(fill="both", expand=True)

        tk.Label(
            inner,
            text=header_text,
            bg=Theme.CARD_BG,
            fg=accent,
            font=Theme.FONT_CARD_TITLE,
            anchor="w",
        ).pack(fill="x")

        rate_lbl = tk.Label(
            inner,
            text="Assumption: --%",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
            anchor="w",
            pady=2,
        )
        rate_lbl.pack(fill="x")

        value_lbl = tk.Label(
            inner,
            text="₹0.00",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_METRIC_SM,
            anchor="w",
            pady=4,
        )
        value_lbl.pack(fill="x")

        pnl_lbl = tk.Label(
            inner,
            text="Profit/Loss: ₹0.00",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="w",
        )
        pnl_lbl.pack(fill="x")

        return {
            "frame": frame,
            "rate": rate_lbl,
            "value": value_lbl,
            "pnl": pnl_lbl,
        }

    def _update_scenario_card(self, card, data):
        card["rate"].configure(text=f"Hypothetical Rate: {data['annual_rate']:.2f}% p.a.")
        card["value"].configure(text=format_inr(data["future_value"]))

        pnl = data["profit_or_loss"]
        if pnl < 0:
            pnl_text = f"Est. Loss: {format_inr(pnl)}"
            pnl_color = Theme.DANGER
        elif pnl > 0:
            pnl_text = f"Est. Profit: +{format_inr(pnl)}"
            pnl_color = Theme.SUCCESS
        else:
            pnl_text = f"Break-even: {format_inr(0.0)}"
            pnl_color = Theme.TEXT_SECONDARY
        card["pnl"].configure(text=pnl_text, fg=pnl_color)

    def _draw_comparison_bars(self, scenarios):
        """Draw horizontal bars comparing Low, Moderate, and High hypothetical values."""
        self._last_scenarios = scenarios
        canvas = self.compare_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 440)
        items = [
            ("Low (Hypothetical)", scenarios["low"]["future_value"], Theme.DANGER),
            ("Moderate (Hypothetical)", scenarios["moderate"]["future_value"], Theme.WARNING),
            ("High (Hypothetical)", scenarios["high"]["future_value"], Theme.SUCCESS),
        ]
        max_val = max((max(val, 0.0) for _lbl, val, _col in items), default=1.0)
        if max_val <= 0:
            max_val = 1.0

        bar_area_x = 165
        max_bar_w = max(width - bar_area_x - 20, 120)

        for idx, (label, val, color) in enumerate(items):
            y_top = 8 + idx * 38
            canvas.create_text(
                4,
                y_top + 11,
                text=label,
                fill=Theme.TEXT_SECONDARY,
                font=Theme.FONT_SMALL,
                anchor="w",
            )
            canvas.create_rectangle(
                bar_area_x,
                y_top,
                bar_area_x + max_bar_w,
                y_top + 22,
                fill=Theme.INPUT_BG,
                outline="",
            )
            bar_w = int(round((max(val, 0.0) / max_val) * max_bar_w))
            if bar_w > 0:
                canvas.create_rectangle(
                    bar_area_x,
                    y_top,
                    bar_area_x + bar_w,
                    y_top + 22,
                    fill=color,
                    outline="",
                )
            canvas.create_text(
                bar_area_x + 8,
                y_top + 11,
                text=format_inr(val),
                fill=Theme.TEXT_PRIMARY,
                font=Theme.FONT_SMALL,
                anchor="w",
            )

    def calculate(self):
        """Validate assumptions, simulate 3 hypothetical scenarios, update UI & save."""
        self.clear_status(self.status_label)
        try:
            res = self.calculator.simulate_financial_risk(
                self.initial_var.get(),
                self.monthly_var.get(),
                self.years_var.get(),
                self.low_rate_var.get(),
                self.mod_rate_var.get(),
                self.high_rate_var.get(),
            )
        except ValidationError as exc:
            self.show_error_status(self.status_label, str(exc))
            return

        sc = res["scenarios"]
        diffs = res["differences"]

        self._update_scenario_card(self.card_low, sc["low"])
        self._update_scenario_card(self.card_mod, sc["moderate"])
        self._update_scenario_card(self.card_high, sc["high"])

        self.diff_high_low.update_card(
            format_inr(diffs["high_vs_low"]),
            f"High ({sc['high']['annual_rate']:.1f}%) minus Low ({sc['low']['annual_rate']:.1f}%)",
        )
        self.diff_mod_low.update_card(
            format_inr(diffs["moderate_vs_low"]),
            f"Mod ({sc['moderate']['annual_rate']:.1f}%) minus Low ({sc['low']['annual_rate']:.1f}%)",
        )
        self.diff_high_mod.update_card(
            format_inr(diffs["high_vs_moderate"]),
            f"High ({sc['high']['annual_rate']:.1f}%) minus Mod ({sc['moderate']['annual_rate']:.1f}%)",
        )

        self.invested_ref_label.configure(
            text=(
                f"Total Capital Invested: {format_inr(res['total_investment'])}  •  "
                f"Horizon: {res['years']:g} years ({res['total_months']} months)  •  "
                "All values are HYPOTHETICAL"
            )
        )
        self._draw_comparison_bars(sc)

        input_summary = (
            f"Initial: {format_inr(res['initial_investment'])}, "
            f"Monthly: {format_inr(res['monthly_investment'])}, "
            f"Years: {res['years']:g}, "
            f"Hypothetical Rates (L/M/H): {sc['low']['annual_rate']:.2f}% / "
            f"{sc['moderate']['annual_rate']:.2f}% / {sc['high']['annual_rate']:.2f}%"
        )
        result_summary = (
            f"[Hypothetical] Low: {format_inr(sc['low']['future_value'])} "
            f"(P/L {format_inr(sc['low']['profit_or_loss'])}) | "
            f"Mod: {format_inr(sc['moderate']['future_value'])} "
            f"(P/L {format_inr(sc['moderate']['profit_or_loss'])}) | "
            f"High: {format_inr(sc['high']['future_value'])} "
            f"(P/L {format_inr(sc['high']['profit_or_loss'])}) | "
            f"High-Low Diff: {format_inr(diffs['high_vs_low'])}"
        )
        try:
            rec_id = self.save_to_history("Risk Simulator", input_summary, result_summary)
            self.show_success_status(
                self.status_label, f"Hypothetical simulation saved to History (ID #{rec_id})."
            )
        except DatabaseError as exc:
            self.show_error_status(self.status_label, str(exc))

    def reset_defaults(self):
        """Restore default hypothetical assumptions and clear results."""
        self.initial_var.set("100000")
        self.monthly_var.set("5000")
        self.years_var.set("10")
        self.low_rate_var.set("5")
        self.mod_rate_var.set("11")
        self.high_rate_var.set("16")

        for card in (self.card_low, self.card_mod, self.card_high):
            card["rate"].configure(text="Assumption: --%")
            card["value"].configure(text="₹0.00")
            card["pnl"].configure(text="Profit/Loss: ₹0.00", fg=Theme.TEXT_SECONDARY)

        self.diff_high_low.update_card("₹0.00", "Total range width")
        self.diff_mod_low.update_card("₹0.00", "Baseline uplift")
        self.diff_high_mod.update_card("₹0.00", "Upside potential")
        self.invested_ref_label.configure(
            text="Total Capital Invested: ₹0.00  |  Run simulation to compare scenarios."
        )
        self._last_scenarios = None
        self.compare_canvas.delete("all")
        self.clear_status(self.status_label)


class HistoryView(tk.Frame):
    """Module 5: Calculation History View backed by SQLite3."""

    CATEGORIES = ("All", "Loan EMI", "Compound Interest", "Investment Growth", "Risk Simulator")

    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_MAIN, padx=28, pady=24)
        self.app = app
        self.db = app.db

        # Header
        header = tk.Frame(self, bg=Theme.BG_MAIN)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text="Calculation History",
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_TITLE,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            header,
            text="View, inspect, refresh, or remove locally stored SQLite3 calculation records.",
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SUBTITLE,
            anchor="w",
            pady=2,
        ).pack(fill="x")

        # Toolbar
        toolbar = tk.Frame(
            self,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        toolbar.pack(fill="x", pady=(0, 12))

        tk.Label(
            toolbar,
            text="Filter Category:",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY_BOLD,
        ).pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            toolbar,
            textvariable=self.filter_var,
            values=self.CATEGORIES,
            state="readonly",
            width=18,
            style="Dark.TCombobox",
            font=Theme.FONT_BODY,
        )
        filter_combo.pack(side="left", padx=(0, 16))
        filter_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_records())

        self.count_label = tk.Label(
            toolbar,
            text="0 record(s)",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
        )
        self.count_label.pack(side="left")

        create_action_button(
            toolbar,
            "Clear All History",
            self.clear_all,
            bg=Theme.DANGER_DARK,
            hover_bg=Theme.DANGER,
            padx=12,
            pady=6,
            font=Theme.FONT_SMALL,
        ).pack(side="right", padx=(8, 0))

        create_action_button(
            toolbar,
            "Delete Selected",
            self.delete_selected,
            bg=Theme.CARD_ALT,
            hover_bg=Theme.DANGER_DARK,
            padx=12,
            pady=6,
            font=Theme.FONT_SMALL,
        ).pack(side="right", padx=(8, 0))

        create_action_button(
            toolbar,
            "↻ Refresh",
            self.refresh_records,
            bg=Theme.ACCENT,
            hover_bg=Theme.ACCENT_HOVER,
            padx=12,
            pady=6,
            font=Theme.FONT_SMALL,
        ).pack(side="right")

        # Treeview Table Container
        table_card = tk.Frame(
            self,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=2,
            pady=2,
        )
        table_card.pack(fill="both", expand=True, pady=(0, 12))

        columns = ("id", "category", "input_details", "results", "created_at")
        self.tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            style="History.Treeview",
            selectmode="browse",
        )

        self.tree.heading("id", text="ID", anchor="center")
        self.tree.heading("category", text="Category", anchor="w")
        self.tree.heading("input_details", text="Input Details", anchor="w")
        self.tree.heading("results", text="Results", anchor="w")
        self.tree.heading("created_at", text="Date & Time", anchor="center")

        self.tree.column("id", width=55, minwidth=45, anchor="center", stretch=False)
        self.tree.column("category", width=145, minwidth=120, anchor="w", stretch=False)
        self.tree.column("input_details", width=290, minwidth=200, anchor="w")
        self.tree.column("results", width=320, minwidth=220, anchor="w")
        self.tree.column("created_at", width=155, minwidth=140, anchor="center", stretch=False)

        v_scroll = ttk.Scrollbar(
            table_card,
            orient="vertical",
            command=self.tree.yview,
            style="Dark.Vertical.TScrollbar",
        )
        h_scroll = ttk.Scrollbar(
            table_card,
            orient="horizontal",
            command=self.tree.xview,
            style="Dark.Horizontal.TScrollbar",
        )
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

        # Selected Record Inspector
        inspector = tk.Frame(
            self,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        inspector.pack(fill="x")

        tk.Label(
            inspector,
            text="Selected Record Details",
            bg=Theme.CARD_BG,
            fg=Theme.ACCENT_HOVER,
            font=Theme.FONT_CARD_TITLE,
            anchor="w",
        ).pack(fill="x")

        self.detail_label = tk.Label(
            inspector,
            text="Select a row in the table above to inspect its full inputs and results.",
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="w",
            justify="left",
            wraplength=680,
            pady=4,
        )
        self.detail_label.pack(fill="x")
        inspector.bind(
            "<Configure>",
            lambda e: self.detail_label.configure(wraplength=max(e.width - 36, 300)),
        )

        self.refresh_records()

    def refresh_records(self):
        """Reload records from SQLite3 using the active category filter."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            records = self.db.get_all_records(self.filter_var.get())
        except DatabaseError as exc:
            messagebox.showerror("Database Error", str(exc), parent=self)
            return

        for rec in records:
            self.tree.insert(
                "",
                "end",
                iid=str(rec["id"]),
                values=(
                    rec["id"],
                    rec["category"],
                    rec["input_details"],
                    rec["results"],
                    rec["created_at"],
                ),
            )

        self.count_label.configure(text=f"Showing {len(records)} record(s)")
        self.detail_label.configure(
            text="Select a row in the table above to inspect its full inputs and results."
        )

    def _on_row_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if not values:
            return
        rec_id, category, inputs, results, created_at = values
        self.detail_label.configure(
            text=(
                f"ID #{rec_id}  •  {category}  •  {created_at}\n"
                f"Inputs:  {inputs}\n"
                f"Results: {results}"
            )
        )

    def delete_selected(self):
        """Delete the currently selected record from SQLite3."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection",
                "Please select a history record in the table to delete.",
                parent=self,
            )
            return

        record_id = selected[0]
        confirm = messagebox.askyesno(
            "Delete Record",
            f"Are you sure you want to delete calculation record #{record_id}?",
            parent=self,
        )
        if not confirm:
            return

        try:
            self.db.delete_record(record_id)
            self.refresh_records()
            self.app.notify_history_updated(exclude_history=True)
        except DatabaseError as exc:
            messagebox.showerror("Database Error", str(exc), parent=self)

    def clear_all(self):
        """Delete all records from SQLite3 after user confirmation."""
        try:
            existing = self.db.get_all_records()
        except DatabaseError as exc:
            messagebox.showerror("Database Error", str(exc), parent=self)
            return

        if not existing:
            messagebox.showinfo(
                "History Empty",
                "There are no calculation records to clear.",
                parent=self,
            )
            return

        confirm = messagebox.askyesno(
            "Clear All History",
            f"Delete all {len(existing)} saved calculation record(s)? This cannot be undone.",
            parent=self,
        )
        if not confirm:
            return

        try:
            self.db.clear_all_records()
            self.refresh_records()
            self.app.notify_history_updated(exclude_history=True)
        except DatabaseError as exc:
            messagebox.showerror("Database Error", str(exc), parent=self)


class FinancialRiskApp(tk.Tk):
    """Main desktop application window managing sidebar navigation and module views."""

    NAV_ITEMS = [
        ("home", "⌂   Dashboard Home"),
        ("loan_emi", "▣   Loan EMI"),
        ("compound_interest", "◈   Compound Interest"),
        ("investment_growth", "↗   Investment Growth"),
        ("risk_simulator", "△   Risk Simulator"),
        ("history", "☰   Calculation History"),
    ]

    def __init__(self, db_manager, calculator=None):
        super().__init__()
        self.db = db_manager
        self.calculator = calculator if calculator is not None else FinancialCalculator()

        self.title("Financial Risk Calculator — Offline Python Suite")
        self.geometry("1220x760")
        self.minsize(1020, 660)
        self.configure(bg=Theme.BG_MAIN)

        configure_ttk_styles(self)

        self.nav_buttons = {}
        self.views = {}
        self.active_key = None

        self._build_layout()
        self.show_view("home")

    def _build_layout(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=Theme.SIDEBAR_BG, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=Theme.SIDEBAR_BG, padx=20, pady=22)
        brand.pack(fill="x")

        tk.Label(
            brand,
            text="₹  FinRisk Suite",
            bg=Theme.SIDEBAR_BG,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 16, "bold"),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            brand,
            text="Financial Risk Calculator",
            bg=Theme.SIDEBAR_BG,
            fg=Theme.ACCENT_HOVER,
            font=Theme.FONT_SMALL,
            anchor="w",
            pady=2,
        ).pack(fill="x")

        tk.Frame(sidebar, bg=Theme.BORDER, height=1).pack(fill="x", padx=16, pady=(0, 14))

        nav_container = tk.Frame(sidebar, bg=Theme.SIDEBAR_BG, padx=12)
        nav_container.pack(fill="x")

        for key, label in self.NAV_ITEMS:
            btn = tk.Button(
                nav_container,
                text=label,
                command=lambda k=key: self.show_view(k),
                bg=Theme.SIDEBAR_BG,
                fg=Theme.TEXT_SECONDARY,
                activebackground=Theme.CARD_ALT,
                activeforeground=Theme.TEXT_PRIMARY,
                font=Theme.FONT_BODY_BOLD,
                anchor="w",
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=14,
                pady=11,
            )
            btn.pack(fill="x", pady=3)
            btn.bind("<Enter>", lambda _e, k=key: self._on_nav_hover(k, True))
            btn.bind("<Leave>", lambda _e, k=key: self._on_nav_hover(k, False))
            self.nav_buttons[key] = btn

        # Footer badge in sidebar
        footer = tk.Frame(sidebar, bg=Theme.SIDEBAR_BG, padx=18, pady=16)
        footer.pack(side="bottom", fill="x")
        tk.Frame(footer, bg=Theme.BORDER, height=1).pack(fill="x", pady=(0, 10))
        tk.Label(
            footer,
            text="●  Offline Mode Active",
            bg=Theme.SIDEBAR_BG,
            fg=Theme.SUCCESS,
            font=Theme.FONT_SMALL,
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            footer,
            text="Local SQLite3 Database",
            bg=Theme.SIDEBAR_BG,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
            anchor="w",
        ).pack(fill="x")

        # Vertical divider
        tk.Frame(self, bg=Theme.BORDER, width=1).pack(side="left", fill="y")

        # Main Content Area
        self.main_area = tk.Frame(self, bg=Theme.BG_MAIN)
        self.main_area.pack(side="right", fill="both", expand=True)

        self.views["home"] = DashboardHomeView(self.main_area, self)
        self.views["loan_emi"] = LoanEMIView(self.main_area, self)
        self.views["compound_interest"] = CompoundInterestView(self.main_area, self)
        self.views["investment_growth"] = InvestmentGrowthView(self.main_area, self)
        self.views["risk_simulator"] = RiskSimulatorView(self.main_area, self)
        self.views["history"] = HistoryView(self.main_area, self)

    def _on_nav_hover(self, key, entering):
        if key == self.active_key:
            return
        btn = self.nav_buttons[key]
        if entering:
            btn.configure(bg=Theme.CARD_BG, fg=Theme.TEXT_PRIMARY)
        else:
            btn.configure(bg=Theme.SIDEBAR_BG, fg=Theme.TEXT_SECONDARY)

    def show_view(self, key):
        """Switch the active page and update sidebar highlighting."""
        if key not in self.views:
            return

        if self.active_key is not None and self.active_key in self.views:
            self.views[self.active_key].pack_forget()

        self.active_key = key
        view = self.views[key]
        view.pack(fill="both", expand=True)

        if key == "home":
            view.refresh_data()
        elif key == "history":
            view.refresh_records()

        for nav_key, btn in self.nav_buttons.items():
            if nav_key == key:
                btn.configure(bg=Theme.ACCENT, fg=Theme.TEXT_PRIMARY)
            else:
                btn.configure(bg=Theme.SIDEBAR_BG, fg=Theme.TEXT_SECONDARY)

    def notify_history_updated(self, exclude_history=False):
        """Keep Dashboard Home and History views synchronized after DB writes/deletes."""
        if "home" in self.views:
            self.views["home"].refresh_data()
        if not exclude_history and "history" in self.views and self.active_key == "history":
            self.views["history"].refresh_records()
