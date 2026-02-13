"""
GUI за уеб скрейпинг на новини.
Избор на тип сайт (12 Punto и др.), въвеждане на линк, извличане на заглавие, снимка и текст.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Union

from scrapers.base import ArticleData
from scrapers.registry import get_available_sites, get_scraper_by_name, get_scraper_for_url

# Предварително записани линкове по тип сайт (за падащото меню „Линк“)
PRESET_LINKS: dict[str, list[str]] = {
    "12 Punto": [
        "https://12punto.com.tr/gundem/chpden-meclis-baskani-kurtulmusun-anayasaya-aykiri-tesebbus-yorumuna-tepki-ilgileniyorsa-atalay-kararini-uygulasin-111020",
        "https://12punto.com.tr/gundem/bogazici-universitesinde-yurt-acilisi-sebebiyle-kampuse-giris-yasaklandi-cumhurbaskani-erdogan-gelecek-iddiasi-111016",
    ],
}


def _bind_paste_copy(widget: Union[tk.Entry, tk.Text]):
    """Осигурява работещ Paste (Ctrl+V) и Copy (Ctrl+C) на Windows."""
    def on_paste(event):
        try:
            text = widget.clipboard_get()
            if isinstance(widget, tk.Text):
                widget.insert(tk.INSERT, text)
            else:
                widget.insert(tk.INSERT, text)
            return "break"
        except tk.TclError:
            pass

    def on_copy(event):
        try:
            if isinstance(widget, tk.Text):
                sel = widget.get(tk.SEL_FIRST, tk.SEL_LAST) if widget.tag_ranges(tk.SEL) else ""
            else:
                sel = widget.selection_get() if widget.selection_present() else ""
            if sel:
                widget.clipboard_clear()
                widget.clipboard_append(sel)
            return "break"
        except tk.TclError:
            pass

    def on_cut(event):
        try:
            if isinstance(widget, tk.Text):
                if widget.tag_ranges(tk.SEL):
                    sel = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    widget.clipboard_clear()
                    widget.clipboard_append(sel)
            else:
                if widget.selection_present():
                    sel = widget.selection_get()
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    widget.clipboard_clear()
                    widget.clipboard_append(sel)
            return "break"
        except tk.TclError:
            pass

    widget.bind("<Control-v>", on_paste)
    widget.bind("<Control-V>", on_paste)
    widget.bind("<Control-c>", on_copy)
    widget.bind("<Control-C>", on_copy)
    widget.bind("<Control-x>", on_cut)
    widget.bind("<Control-X>", on_cut)

    def show_context_menu(event):
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Постави (Ctrl+V)", command=lambda: on_paste(None))
        menu.add_command(label="Копирай (Ctrl+C)", command=lambda: on_copy(None))
        menu.add_command(label="Изрежи (Ctrl+X)", command=lambda: on_cut(None))
        menu.tk_popup(event.x_root, event.y_root)

    widget.bind("<Button-3>", show_context_menu)


def run_scrape(url: str, site_name: Optional[str]) -> ArticleData:
    """Run scraper and return article data."""
    if site_name:
        scraper = get_scraper_by_name(site_name)
        if not scraper:
            raise ValueError(f"Не е намерен скрейпър за: {site_name}")
    else:
        scraper = get_scraper_for_url(url)
        if not scraper:
            raise ValueError("Този тип сайт все още не се поддържа. Изберете '12 Punto' или линк от 12punto.com.tr")
    return scraper.scrape(url)


class ScraperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Уеб скрейпинг – новини")
        self.root.minsize(500, 450)
        self.root.geometry("700x600")

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Ред 1: Тип сайт
        row1 = ttk.Frame(main)
        row1.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row1, text="Тип сайт:").pack(side=tk.LEFT, padx=(0, 8))
        self.site_var = tk.StringVar(value=get_available_sites()[0] if get_available_sites() else "")
        self.site_combo = ttk.Combobox(
            row1,
            textvariable=self.site_var,
            values=get_available_sites(),
            state="readonly",
            width=25,
        )
        self.site_combo.pack(side=tk.LEFT)
        self.site_combo.bind("<<ComboboxSelected>>", self._on_site_changed)

        # Ред 2: Линк – падащо меню с предзаписани линкове (и възможност за свой)
        row2 = ttk.Frame(main)
        row2.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row2, text="Линк:").pack(side=tk.LEFT, padx=(0, 8))
        self.url_var = tk.StringVar()
        self.url_combo = ttk.Combobox(
            row2,
            textvariable=self.url_var,
            width=55,
            state="normal",  # може да се избира от списъка или да се въвежда/поставя свой линк
        )
        self.url_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        _bind_paste_copy(self.url_combo)
        self._update_url_dropdown()
        self.btn_scrape = ttk.Button(row2, text="Извлечи", command=self._on_scrape)
        self.btn_scrape.pack(side=tk.RIGHT)

        # Резултати
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Label(main, text="Резултат", font=("", 10, "bold")).pack(anchor=tk.W)

        # Панел с резултати (заглавие, снимка, текст)
        result_frame = ttk.LabelFrame(main, text="Извлечени данни", padding=6)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # Заглавие – tk.Entry + изричен paste/copy
        ttk.Label(result_frame, text="Заглавие:").pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(result_frame, textvariable=self.title_var)
        self.title_entry.pack(fill=tk.X, pady=(0, 6))
        _bind_paste_copy(self.title_entry)

        # Линк към снимка – tk.Entry + изричен paste/copy
        ttk.Label(result_frame, text="Линк към снимка:").pack(anchor=tk.W)
        self.image_var = tk.StringVar()
        self.image_entry = tk.Entry(result_frame, textvariable=self.image_var)
        self.image_entry.pack(fill=tk.X, pady=(0, 6))
        _bind_paste_copy(self.image_entry)

        # Текст на новината – изричен paste/copy
        ttk.Label(result_frame, text="Текст на новината:").pack(anchor=tk.W)
        self.text_frame = ttk.Frame(result_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        self.text_widget = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, height=12)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        _bind_paste_copy(self.text_widget)

    def _on_site_changed(self, event=None):
        """При смяна на тип сайт обновява списъка с линкове в падащото меню."""
        self._update_url_dropdown()

    def _update_url_dropdown(self):
        """Попълва падащото меню „Линк“ с предзаписани линкове за избрания сайт."""
        site = self.site_var.get().strip()
        links = PRESET_LINKS.get(site, [])
        self.url_combo["values"] = links
        if links and not self.url_var.get().strip():
            self.url_var.set(links[0])

    def _on_scrape(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Внимание", "Въведете линк.")
            return
        site_name = self.site_var.get().strip() or None
        self.btn_scrape.configure(state="disabled")
        self.root.update()
        try:
            data = run_scrape(url, site_name)
            self._show_result(data)
        except Exception as e:
            messagebox.showerror("Грешка", str(e))
        finally:
            self.btn_scrape.configure(state="normal")

    def _show_result(self, data: ArticleData):
        self.title_var.set(data.title)
        self.image_var.set(data.image_url or "")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, data.text)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ScraperApp().run()
