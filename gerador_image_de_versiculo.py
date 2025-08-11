import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageFilter, ImageDraw, ImageFont

OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FILENAME = "versiculo.png"

FONT_PATHS_TO_TRY = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

def find_font(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

FONT_PATH = find_font(FONT_PATHS_TO_TRY)

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    if not words:
        return [""]
    line = words[0]
    for w in words[1:]:
        test_line = f"{line} {w}"
        if get_text_size(draw, test_line, font)[0] <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines

def create_story_image(message, sender, bg_path, output_path=OUTPUT_FILENAME):
    # Open and resize background
    bg = Image.open(bg_path).convert("RGB")
    bg_ratio = bg.width / bg.height
    target_ratio = OUTPUT_WIDTH / OUTPUT_HEIGHT

    if bg_ratio > target_ratio:
        new_height = OUTPUT_HEIGHT
        new_width = int(bg_ratio * new_height)
    else:
        new_width = OUTPUT_WIDTH
        new_height = int(new_width / bg_ratio)

    bg_resized = bg.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - OUTPUT_WIDTH) // 2
    top = (new_height - OUTPUT_HEIGHT) // 2
    bg_cropped = bg_resized.crop((left, top, left + OUTPUT_WIDTH, top + OUTPUT_HEIGHT))
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=12))

    # Prepare canvas
    canvas = Image.new("RGB", (OUTPUT_WIDTH, OUTPUT_HEIGHT))
    canvas.paste(bg_blurred)
    draw = ImageDraw.Draw(canvas)

    # Load fonts
    if FONT_PATH:
        message_font = ImageFont.truetype(FONT_PATH, 80)
        sender_font = ImageFont.truetype(FONT_PATH, 40)
        footer_font = ImageFont.truetype(FONT_PATH, 30)
    else:
        message_font = sender_font = footer_font = ImageFont.load_default()

    margin_x = 80
    max_text_width = OUTPUT_WIDTH - 2 * margin_x

    # Wrap message text dynamically
    lines = wrap_text(draw, message, message_font, max_text_width)

    # Calculate total text height
    line_height = get_text_size(draw, "Ay", message_font)[1] + 12
    total_text_height = line_height * len(lines)

    # Position text roughly centered vertically
    current_y = (OUTPUT_HEIGHT - total_text_height) // 2

    # Draw message with shadow
    for line in lines:
        w, h = get_text_size(draw, line, message_font)
        x = (OUTPUT_WIDTH - w) // 2
        draw.text((x+3, current_y+3), line, font=message_font, fill=(0,0,0,180))
        draw.text((x, current_y), line, font=message_font, fill="white")
        current_y += line_height

    # Draw sender below message
    sender_text = f"— {sender}"
    sw, sh = get_text_size(draw, sender_text, sender_font)
    sx = (OUTPUT_WIDTH - sw) // 2
    sy = current_y + 20
    draw.text((sx+2, sy+2), sender_text, font=sender_font, fill=(0,0,0,180))
    draw.text((sx, sy), sender_text, font=sender_font, fill=(230,230,230))

    # Draw footer with arroba
    footer_text = "@elizeu.dev"
    fw, fh = get_text_size(draw, footer_text, footer_font)
    fx = (OUTPUT_WIDTH - fw) // 2
    fy = OUTPUT_HEIGHT - 60
    draw.text((fx+1, fy+1), footer_text, font=footer_font, fill=(0,0,0,180))
    draw.text((fx, fy), footer_text, font=footer_font, fill="white")

    canvas.save(output_path, "PNG")
    return output_path

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Imagens de Versículos - @elizeu.dev")
        self.root.geometry("720x480")

        self.bg_path = None

        tk.Label(root, text="Referência Bíblica:").pack(anchor="w", padx=10, pady=(10,0))
        self.text_entry = tk.Text(root, height=6)
        self.text_entry.pack(fill="x", padx=10)

        frame = tk.Frame(root)
        frame.pack(fill="x", padx=10, pady=8)
        tk.Label(frame, text="Referência Bíblica:").pack(side="left")
        self.sender_entry = tk.Entry(frame)
        self.sender_entry.pack(side="left", fill="x", expand=True, padx=(8,0))

        frame2 = tk.Frame(root)
        frame2.pack(fill="x", padx=10, pady=8)
        self.bg_label = tk.Label(frame2, text="Nenhuma imagem selecionada")
        self.bg_label.pack(side="left")
        tk.Button(frame2, text="Selecionar imagem de fundo", command=self.select_background).pack(side="right")

        frame3 = tk.Frame(root)
        frame3.pack(fill="x", padx=10, pady=8)
        tk.Button(frame3, text="Gerar Imagem", command=self.generate_story).pack(side="left")
        tk.Button(frame3, text="Sair", command=root.quit).pack(side="right")

    def select_background(self):
        path = filedialog.askopenfilename(title="Selecione a imagem de fundo", filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")])
        if path:
            self.bg_path = path
            self.bg_label.config(text=os.path.basename(path))

    def generate_story(self):
        message = self.text_entry.get("1.0", "end").strip()
        sender = self.sender_entry.get().strip() or "Anônimo"
        if not message:
            messagebox.showwarning("Atenção", "Por favor, insira o versículo.")
            return
        if not self.bg_path:
            messagebox.showwarning("Atenção", "Por favor, selecione uma imagem de fundo.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=OUTPUT_FILENAME, filetypes=[("PNG", "*.png")], title="Salvar story como")
        if not save_path:
            return
        try:
            result = create_story_image(message, sender, self.bg_path, save_path)
            messagebox.showinfo("Sucesso", f"Imagem gerada e salva em:\n{result}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
