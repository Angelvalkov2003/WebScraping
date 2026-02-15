"""GUI за уеб скрейпинг на новини – избор на сайт, линк, извличане заглавие/снимка/текст."""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Union

from scrapers.base import ArticleData
from scrapers.registry import get_available_sites, get_scraper_by_name, get_scraper_for_url

PRESET_LINKS: dict[str, list[str]] = {
    "12 Punto": [
        "https://12punto.com.tr/gundem/chpden-meclis-baskani-kurtulmusun-anayasaya-aykiri-tesebbus-yorumuna-tepki-ilgileniyorsa-atalay-kararini-uygulasin-111020",
        "https://12punto.com.tr/gundem/bogazici-universitesinde-yurt-acilisi-sebebiyle-kampuse-giris-yasaklandi-cumhurbaskani-erdogan-gelecek-iddiasi-111016",
        "https://12punto.com.tr/gundem/osman-gokcekten-iddia-ozgur-ozel-kursuyu-isgal-edin-dedi-111034",
        "https://12punto.com.tr/ekonomi/istanbulda-toplu-tasimaya-zam-16-subattan-itibaren-111011",
        "https://12punto.com.tr/ekonomi/tmsfnin-el-koydugu-banka-satiliyor-tarih-belli-oldu-111198",
        "https://12punto.com.tr/spor/galatasaray-juventus-macinin-hakemi-aciklandi-111211",
    ],
    "Nova TV": [
        "https://nova.bg/news/view/2026/02/13/527075/%D1%81%D1%8A%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D0%B5%D1%82%D0%BE-%D0%BD%D0%B0-15-%D0%B3%D0%BE%D0%B4%D0%B8%D1%88%D0%BD%D0%BE%D1%82%D0%BE-%D0%BC%D0%BE%D0%BC%D0%B8%D1%87%D0%B5-%D0%B2-%D0%BF%D0%B8%D1%80%D0%BE%D0%B3%D0%BE%D0%B2-%D0%B5-%D1%81%D1%82%D0%B0%D0%B1%D0%B8%D0%BB%D0%B8%D0%B7%D0%B8%D1%80%D0%B0%D0%BD%D0%BE-%D0%BD%D0%BE-%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%B0-%D1%82%D0%B5%D0%B6%D0%BA%D0%BE/",
        "https://nova.bg/news/view/2026/02/13/527078/%D0%B8%D0%B7%D0%BA%D1%83%D1%81%D1%82%D0%B2%D0%B5%D0%BD-%D0%B8%D0%BD%D1%82%D0%B5%D0%BB%D0%B5%D0%BA%D1%82-%D0%B5-%D1%81%D1%80%D0%B5%D0%B4-%D0%BA%D0%B0%D0%BD%D0%B4%D0%B8%D0%B4%D0%B0%D1%82%D0%B8%D1%82%D0%B5-%D0%B7%D0%B0-%D0%B4%D0%B5%D0%BF%D1%83%D1%82%D0%B0%D1%82%D0%B8-%D0%B2-%D0%BA%D0%BE%D0%BB%D1%83%D0%BC%D0%B1%D0%B8%D1%8F/",
        "https://nova.bg/news/view/2026/02/13/526049/%D1%88%D0%BE%D0%BA%D0%BE%D0%BB%D0%B0%D0%B4-%D0%B2%D0%B5%D1%80%D0%BC%D1%83%D1%82-%D0%B8-%D0%B2%D0%B8%D0%BD%D0%BE-%D0%B8%D1%82%D0%B0%D0%BB%D0%B8%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D1%8F%D1%82-%D0%B3%D1%80%D0%B0%D0%B4-%D0%B2-%D0%BA%D0%BE%D0%B9%D1%82%D0%BE-%D0%B6%D0%B8%D0%B2%D0%BE%D1%82%D1%8A%D1%82-%D0%BF%D1%80%D0%B5%D0%B7-%D0%B7%D0%B8%D0%BC%D0%B0%D1%82%D0%B0-%D0%B5-%D0%BD%D0%B0%D0%B9-%D1%81%D0%BB%D0%B0%D0%B4%D1%8A%D0%BA-%D1%81%D0%BD%D0%B8%D0%BC%D0%BA%D0%B8/",
        "https://nova.bg/news/view/2026/02/12/526884/%D0%B1%D1%80%D0%B8%D1%82%D0%BD%D0%B8-%D1%81%D0%BF%D0%B8%D1%8A%D1%80%D1%81-%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B2%D0%B0-%D0%BF%D1%80%D0%B0%D0%B2%D0%B0%D1%82%D0%B0-%D0%B2%D1%8A%D1%80%D1%85%D1%83-%D1%86%D0%B5%D0%BB%D0%B8%D1%8F-%D1%81%D0%B8-%D0%BC%D1%83%D0%B7%D0%B8%D0%BA%D0%B0%D0%BB%D0%B5%D0%BD-%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3/",
        "https://nova.bg/news/view/2026/02/12/527050/%D1%80%D1%83%D0%BC%D1%8A%D0%BD%D0%B8%D1%8F-%D0%BE%D1%89%D0%B5-%D0%BD%D0%B5-%D0%B5-%D1%80%D0%B5%D1%88%D0%B8%D0%BB%D0%B0-%D0%B4%D0%B0%D0%BB%D0%B8-%D0%B4%D0%B0-%D1%81%D0%B5-%D0%BF%D1%80%D0%B8%D1%81%D1%8A%D0%B5%D0%B4%D0%B8%D0%BD%D0%B8-%D0%BA%D1%8A%D0%BC-%D1%81%D1%8A%D0%B2%D0%B5%D1%82%D0%B0-%D0%B7%D0%B0-%D0%BC%D0%B8%D1%80-%D0%BD%D0%B0-%D1%82%D1%80%D1%8A%D0%BC%D0%BF/",
        "https://nova.bg/news/view/2026/02/12/526869/%D0%BF%D1%80%D0%B8%D0%BD%D1%86-%D1%83%D0%B8%D0%BB%D1%8F%D0%BC-%D0%B7%D0%B0%D1%81%D0%B0%D0%B4%D0%B8-%D0%B4%D1%80%D1%8A%D0%B2%D1%87%D0%B5-%D0%B2-%D0%BF%D1%83%D1%81%D1%82%D0%B8%D0%BD%D1%8F%D1%82%D0%B0-%D0%B2-%D0%BF%D0%BE%D1%81%D0%BB%D0%B5%D0%B4%D0%BD%D0%B8%D1%8F-%D0%B4%D0%B5%D0%BD-%D0%BE%D1%82-%D0%B2%D0%B8%D0%B7%D0%B8%D1%82%D0%B0%D1%82%D0%B0-%D1%81%D0%B8-%D0%B2-%D1%80%D0%B8%D1%8F%D0%B4-%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE/",
        "https://nova.bg/news/view/2026/02/14/527132/%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8-%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B0%D0%B2%D0%B0%D1%85%D0%B0-%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B0-%D0%BA%D0%BE%D1%8F%D1%82%D0%BE-%D1%82%D0%B8%D1%85%D0%BE-%D1%81%D0%B5-%D0%B5-%D0%BF%D1%80%D0%B5%D0%B2%D1%8A%D1%80%D0%BD%D0%B0%D0%BB%D0%B0-%D0%B2-%D1%87%D0%B5%D1%80%D0%BD%D0%B0-%D0%B4%D1%83%D0%BF%D0%BA%D0%B0-%D1%81%D0%BD%D0%B8%D0%BC%D0%BA%D0%B0/",
    ],
}


def _bind_paste_copy(widget: Union[tk.Entry, tk.Text]):
    def on_paste(event):
        try:
            widget.insert(tk.INSERT, widget.clipboard_get())
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
        self.url_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row2, text="Копирай", width=8, command=lambda: self._copy_field(self.url_var.get)).pack(side=tk.LEFT, padx=(0, 8))
        self.btn_scrape = ttk.Button(row2, text="Извлечи", command=self._on_scrape)
        self.btn_scrape.pack(side=tk.RIGHT)
        _bind_paste_copy(self.url_combo)
        self._update_url_dropdown()

        # Резултати
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Label(main, text="Резултат", font=("", 10, "bold")).pack(anchor=tk.W)

        # Панел с резултати (заглавие, снимка, текст)
        result_frame = ttk.LabelFrame(main, text="Извлечени данни", padding=6)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # Заглавие – tk.Entry + бутон Копирай
        ttk.Label(result_frame, text="Заглавие:").pack(anchor=tk.W)
        row_title = ttk.Frame(result_frame)
        row_title.pack(fill=tk.X, pady=(0, 6))
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(row_title, textvariable=self.title_var)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row_title, text="Копирай", width=8, command=lambda: self._copy_field(self.title_var.get)).pack(side=tk.RIGHT)
        _bind_paste_copy(self.title_entry)

        # Линк към снимка – tk.Entry + бутон Копирай
        ttk.Label(result_frame, text="Линк към снимка:").pack(anchor=tk.W)
        row_image = ttk.Frame(result_frame)
        row_image.pack(fill=tk.X, pady=(0, 6))
        self.image_var = tk.StringVar()
        self.image_entry = tk.Entry(row_image, textvariable=self.image_var)
        self.image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row_image, text="Копирай", width=8, command=lambda: self._copy_field(self.image_var.get)).pack(side=tk.RIGHT)
        _bind_paste_copy(self.image_entry)

        # Текст на новината – изричен paste/copy + бутон Копирай
        ttk.Label(result_frame, text="Текст на новината:").pack(anchor=tk.W)
        self.text_frame = ttk.Frame(result_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        self.text_widget = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, height=12)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        row_text_btn = ttk.Frame(result_frame)
        row_text_btn.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(row_text_btn, text="Копирай", width=8, command=self._copy_text_field).pack(side=tk.LEFT)
        _bind_paste_copy(self.text_widget)

    def _copy_field(self, get_text):
        text = (get_text() or "").strip()
        if not text:
            messagebox.showinfo("Копиране", "Няма текст за копиране.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Копиране", "Текстът е копиран в клипборда.")

    def _copy_text_field(self):
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Копиране", "Няма текст за копиране.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Копиране", "Текстът е копиран в клипборда.")

    def _on_site_changed(self, event=None):
        self._update_url_dropdown()

    def _update_url_dropdown(self):
        site = self.site_var.get().strip()
        links = PRESET_LINKS.get(site, [])
        self.url_combo["values"] = tuple(links)
        if links:
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
