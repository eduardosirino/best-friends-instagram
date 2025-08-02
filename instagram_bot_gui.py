import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import queue
import time
from datetime import datetime
import sys
import os

# Importar o bot (assumindo que o arquivo anterior se chama instagram_bot.py)
from instagram_bot import InstagramCloseFriendsBot

# Simulação do bot para demonstração (remover quando importar o real)
class MockInstagramCloseFriendsBot:
    def __init__(self, headless=False, speed_mode="normal"):
        self.headless = headless
        self.speed_mode = speed_mode
        self.running = False
        
    def adicionar_melhores_amigos(self):
        # Simulação do processo
        import random
        total_followers = random.randint(30, 80)
        
        self.log_callback("Driver configurado com sucesso", "SUCCESS")
        time.sleep(1)
        self.log_callback("Login realizado com sucesso", "SUCCESS")
        time.sleep(2)
        self.log_callback("Navegou para página de melhores amigos", "SUCCESS")
        time.sleep(1)
        self.log_callback(f"Encontrados {total_followers} seguidores para adicionar", "INFO")
        
        added_count = 0
        speed_delays = {"fast": 0.2, "normal": 0.5, "slow": 1.0}
        delay = speed_delays.get(self.speed_mode, 0.5)
        
        for i in range(total_followers):
            if not self.running:
                break
                
            success = random.random() > 0.1  # 90% success rate
            if success:
                added_count += 1
                
            if (i + 1) % 10 == 0 or i == total_followers - 1:
                self.log_callback(f"Progresso: {added_count}/{total_followers} seguidores adicionados", "INFO")
                self.stats_callback(i + 1, total_followers, added_count, (i + 1) - added_count)
                
            time.sleep(delay)
            
        self.log_callback(f"Processo concluído. {added_count} seguidores adicionados aos melhores amigos", "SUCCESS")
        return True
    
    def cleanup(self):
        self.running = False
        
    def __enter__(self):
        self.running = True
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False


class InstagramBotGUI:
    def __init__(self):
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Janela principal
        self.root = ctk.CTk()
        self.root.title("Instagram Close Friends Bot")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Variáveis
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.speed_var = tk.StringVar(value="normal")
        self.headless_var = tk.BooleanVar()
        self.running = False
        self.bot_thread = None
        self.bot_instance = None
        
        # Queue para comunicação entre threads
        self.log_queue = queue.Queue()
        self.stats_queue = queue.Queue()
        
        # Estatísticas
        self.stats = {
            "processed": 0,
            "total": 0,
            "success": 0,
            "failed": 0
        }
        
        self.setup_ui()
        self.process_queues()
        
    def setup_ui(self):
        # Grid principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo - Configurações
        self.setup_config_panel()
        
        # Painel direito - Status e Logs
        self.setup_status_panel()
        
    def setup_config_panel(self):
        # Frame principal esquerdo
        config_frame = ctk.CTkFrame(self.root, corner_radius=15)
        config_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            config_frame, 
            text="Instagram Close Friends Bot",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            config_frame,
            text="Adicione seguidores aos melhores amigos automaticamente",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Seção Credenciais
        cred_label = ctk.CTkLabel(
            config_frame,
            text="Credenciais",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        cred_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Email
        email_label = ctk.CTkLabel(config_frame, text="Email/Username:")
        email_label.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.email_entry = ctk.CTkEntry(
            config_frame,
            textvariable=self.email_var,
            placeholder_text="seu.email@exemplo.com",
            height=40,
            corner_radius=10
        )
        self.email_entry.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Senha
        password_label = ctk.CTkLabel(config_frame, text="Senha:")
        password_label.grid(row=5, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.password_entry = ctk.CTkEntry(
            config_frame,
            textvariable=self.password_var,
            placeholder_text="••••••••",
            show="*",
            height=40,
            corner_radius=10
        )
        self.password_entry.grid(row=6, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        # Seção Configurações
        config_label = ctk.CTkLabel(
            config_frame,
            text="Configurações",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        config_label.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Velocidade
        speed_label = ctk.CTkLabel(config_frame, text="Velocidade de Execução:")
        speed_label.grid(row=8, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.speed_combo = ctk.CTkComboBox(
            config_frame,
            variable=self.speed_var,
            values=["fast", "normal", "slow"],
            height=40,
            corner_radius=10,
            state="readonly"
        )
        self.speed_combo.grid(row=9, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Modo invisível
        self.headless_check = ctk.CTkCheckBox(
            config_frame,
            text="Modo Invisível (Headless)",
            variable=self.headless_var,
            font=ctk.CTkFont(size=14)
        )
        self.headless_check.grid(row=10, column=0, padx=20, pady=10, sticky="w")
        
        # Botões de controle
        button_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        button_frame.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Iniciar Bot",
            command=self.start_bot,
            height=50,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2D2D2D",
            hover_color="#404040"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Parar",
            command=self.stop_bot,
            height=50,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#666666",
            hover_color="#808080",
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Descrições das velocidades
        speed_desc = ctk.CTkTextbox(
            config_frame,
            height=80,
            corner_radius=10,
            font=ctk.CTkFont(size=12)
        )
        speed_desc.grid(row=12, column=0, padx=20, pady=(0, 20), sticky="ew")
        speed_desc.insert("1.0", 
            "Velocidades:\n"
            "• Rápido: 0.1-0.3s entre ações (máxima velocidade)\n"
            "• Normal: 0.3-0.8s entre ações (equilibrado)\n"
            "• Lento: 0.5-1.2s entre ações (mais seguro)"
        )
        speed_desc.configure(state="disabled")
        
    def setup_status_panel(self):
        # Frame principal direito
        status_frame = ctk.CTkFrame(self.root, corner_radius=15)
        status_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(1, weight=1)
        
        # Estatísticas
        stats_label = ctk.CTkLabel(
            status_frame,
            text="Estatísticas",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        stats_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Grid de estatísticas
        stats_grid = ctk.CTkFrame(status_frame, fg_color="transparent")
        stats_grid.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        stats_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Estatísticas individuais
        self.processed_frame = self.create_stat_card(stats_grid, "Processados", "0", 0, 0)
        self.total_frame = self.create_stat_card(stats_grid, "Total", "0", 0, 1)
        self.success_frame = self.create_stat_card(stats_grid, "Sucessos", "0", 1, 0, "#2D5A2D")
        self.failed_frame = self.create_stat_card(stats_grid, "Falhas", "0", 1, 1, "#5A2D2D")
        
        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(status_frame)
        self.progress_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Progresso",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(5, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.grid(row=2, column=0, padx=15, pady=(0, 15))
        
        # Logs
        logs_label = ctk.CTkLabel(
            status_frame,
            text="Logs de Execução",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        logs_label.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="w")
        
        # Área de logs
        self.logs_text = ctk.CTkTextbox(
            status_frame,
            corner_radius=10,
            font=ctk.CTkFont(size=12)
        )
        self.logs_text.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Botão limpar logs
        clear_button = ctk.CTkButton(
            status_frame,
            text="Limpar Logs",
            command=self.clear_logs,
            height=35,
            corner_radius=8,
            fg_color="#666666",
            hover_color="#808080"
        )
        clear_button.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
    def create_stat_card(self, parent, title, value, row, col, color="#2D2D2D"):
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        value_label.grid(row=0, column=0, padx=15, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="#CCCCCC"
        )
        title_label.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        return {"frame": frame, "value": value_label, "title": title_label}
        
    def add_log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.logs_text.insert("end", log_entry)
        self.logs_text.see("end")
        
        # Colorir logs baseado no nível
        if level == "SUCCESS":
            # Implementar coloração se necessário
            pass
        elif level == "ERROR":
            pass
            
    def clear_logs(self):
        self.logs_text.delete("1.0", "end")
        self.reset_stats()
        
    def reset_stats(self):
        self.stats = {"processed": 0, "total": 0, "success": 0, "failed": 0}
        self.update_stats_display()
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        
    def update_stats_display(self):
        self.processed_frame["value"].configure(text=str(self.stats["processed"]))
        self.total_frame["value"].configure(text=str(self.stats["total"]))
        self.success_frame["value"].configure(text=str(self.stats["success"]))
        self.failed_frame["value"].configure(text=str(self.stats["failed"]))
        
        if self.stats["total"] > 0:
            progress = self.stats["processed"] / self.stats["total"]
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"{int(progress * 100)}%")
            
    def start_bot(self):
        # Validações
        if not self.email_var.get().strip():
            messagebox.showerror("Erro", "Email/Username é obrigatório!")
            return
            
        if not self.password_var.get().strip():
            messagebox.showerror("Erro", "Senha é obrigatória!")
            return
            
        if self.running:
            return
            
        # Atualizar interface
        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.email_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.speed_combo.configure(state="disabled")
        self.headless_check.configure(state="disabled")
        
        # Limpar logs e stats
        self.clear_logs()
        
        # Iniciar bot em thread separada
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
    def stop_bot(self):
        if self.bot_instance:
            self.bot_instance.cleanup()
            
        self.running = False
        self.add_log("Bot interrompido pelo usuário", "WARNING")
        self.reset_interface()
        
    def reset_interface(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.email_entry.configure(state="normal")
        self.password_entry.configure(state="normal")
        self.speed_combo.configure(state="readonly")
        self.headless_check.configure(state="normal")
        
    def run_bot(self):
        try:
            # Usar o bot real quando disponível
            self.bot_instance = InstagramCloseFriendsBot(
                headless=self.headless_var.get(),
                speed_mode=self.speed_var.get()
            )
            
            # Para demonstração, usar mock
            # self.bot_instance = MockInstagramCloseFriendsBot(
            #     headless=self.headless_var.get(),
            #     speed_mode=self.speed_var.get()
            # )
            
            # Configurar callbacks
            self.bot_instance.log_callback = self.log_callback
            self.bot_instance.stats_callback = self.stats_callback
            
            with self.bot_instance as bot:
                # Atualizar credenciais (implementar no bot real)
                # credenciais.email_instagram = self.email_var.get()
                # credenciais.password_instagram = self.password_var.get()
                
                bot.adicionar_melhores_amigos()
                
        except Exception as e:
            self.log_queue.put(("ERROR", f"Erro durante execução: {str(e)}"))
        finally:
            self.root.after(100, self.reset_interface)
            
    def log_callback(self, message, level):
        self.log_queue.put((level, message))
        
    def stats_callback(self, processed, total, success, failed):
        self.stats_queue.put({
            "processed": processed,
            "total": total,
            "success": success,
            "failed": failed
        })
        
    def process_queues(self):
        # Processar logs
        try:
            while True:
                level, message = self.log_queue.get_nowait()
                self.add_log(message, level)
        except queue.Empty:
            pass
            
        # Processar estatísticas
        try:
            while True:
                stats = self.stats_queue.get_nowait()
                self.stats.update(stats)
                self.update_stats_display()
        except queue.Empty:
            pass
            
        # Reagendar
        self.root.after(100, self.process_queues)
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Verificar se customtkinter está instalado
    try:
        import customtkinter
    except ImportError:
        print("CustomTkinter não está instalado!")
        print("Instale com: pip install customtkinter")
        sys.exit(1)
        
    app = InstagramBotGUI()
    app.run()