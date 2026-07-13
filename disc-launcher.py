#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Lançador de Emuladores de Alto Desempenho
# Versão: 1.0.0
# Descrição: Carrega os perfis de desempenho e executa os emuladores diretamente
#            com argumentos de disco físico, otimizados para a GPU GTX 1060 (3GB)
#            e CPU i7-8700 (6 Cores/12 Threads) no Batocera.
#===============================================================================

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Importar o módulo de logging centralizado desenvolvido anteriormente
from logger import setup_logger

def get_emulationstation_env():
    """
    Scrape dinâmico de variáveis de ambiente da sessão gráfica ativa do EmulationStation.
    Garante suporte completo tanto a servidores gráficos X11 como Wayland (Sway) no Batocera.
    """
    env = os.environ.copy()
    try:
        pid = None
        # Varrer todos os processos no /proc para encontrar o emulationstation
        for proc_dir in os.listdir('/proc'):
            if proc_dir.isdigit():
                try:
                    with open(f'/proc/{proc_dir}/comm', 'r') as f:
                        comm = f.read().strip()
                    if comm == 'emulationstation':
                        pid = proc_dir
                        break
                except Exception:
                    continue

        if pid:
            # Ler as variáveis de /proc/<pid>/environ (separadas por \x00)
            with open(f'/proc/{pid}/environ', 'rb') as f:
                environ_data = f.read()
            for item in environ_data.split(b'\x00'):
                if b'=' in item:
                    key, val = item.split(b'=', 1)
                    key_str = key.decode('utf-8', errors='ignore')
                    val_str = val.decode('utf-8', errors='ignore')
                    # Copiar variáveis críticas de renderização, sessão de som e periféricos
                    if key_str in [
                        'DISPLAY', 'XAUTHORITY', 'WAYLAND_DISPLAY', 'XDG_RUNTIME_DIR',
                        'DBUS_SESSION_BUS_ADDRESS', 'PATH', 'USER', 'HOME'
                    ]:
                        env[key_str] = val_str
    except Exception:
        pass
    return env

class EmulatorLauncher:
    """
    Classe responsável por carregar perfis de emuladores e lançá-los com flags
    físicas de reprodução de CD-ROM/DVD (Vulkan, Multithreading, Speedhacks, etc.).
    """

    def __init__(self, log_dir="/userdata/system/logs/autodisc"):
        """Inicializa o logger e define o caminho dos perfis de emulação."""
        self.logger = setup_logger("disc-launcher", log_dir)
        self.profiles_dir = "/userdata/system/autodisc/profiles"

    def load_profile(self, emulator_name):
        """
        Tenta carregar o perfil JSON otimizado para o emulador solicitado.
        Retorna um dicionário com as configurações ou um perfil padrão caso falhe.
        """
        profile_path = Path(self.profiles_dir) / f"{emulator_name}.json"

        try:
            if profile_path.exists():
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    self.logger.info(f"Perfil de desempenho carregado com sucesso para '{emulator_name}'.")
                    return profile
            else:
                self.logger.warning(f"Perfil {profile_path} não encontrado. Utilizando parâmetros predefinidos de segurança.")
                return self.get_default_profile(emulator_name)
        except Exception as e:
            self.logger.error(f"Erro ao carregar perfil '{emulator_name}': {e}. Usando predefinições.")
            return self.get_default_profile(emulator_name)

    def get_default_profile(self, emulator_name):
        """Retorna uma configuração padrão e genérica para emulação estável."""
        return {
            "emulator": emulator_name,
            "video": {"backend": "vulkan", "vsync": True},
            "performance": {"multithreading": True, "speed_hacks": True}
        }

    def build_duckstation_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o DuckStation (PS1)."""
        cmd = [
            'duckstation-qt',
            '-fullscreen',
            '-batch',
            '-fastboot'
        ]

        # Otimizações de renderização via Vulkan
        video_cfg = profile.get('video', {})
        if video_cfg.get('backend', 'vulkan') == 'vulkan':
            cmd.extend(['-set', 'Display/Renderer=Vulkan'])

        # Resolução interna ajustada (4x é ideal para GTX 1060 em PS1)
        graphics_cfg = profile.get('graphics', {})
        res_mult = graphics_cfg.get('internal_resolution', '4x')
        mult_val = res_mult.replace('x', '')
        cmd.extend(['-set', f'Console/ResolutionScale={mult_val}'])

        # Alvo do leitor físico
        cmd.extend(['-disc', device])
        return cmd

    def build_pcsx2_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o PCSX2 (PS2)."""
        cmd = [
            'pcsx2',
            '--nogui',
            '--fullscreen'
        ]

        # Ativar Vulkan por padrão na GTX 1060
        video_cfg = profile.get('video', {})
        if video_cfg.get('renderer', 'vulkan') == 'vulkan':
            cmd.extend(['--renderer', 'vulkan'])

        # Indicar o leitor de discos físico ao PCSX2
        cmd.extend(['--disc', device])
        return cmd

    def build_dolphin_cmd(self, device, profile, console_type):
        """Desenha a linha de comando otimizada para o Dolphin (GameCube/Wii)."""
        cmd = [
            'dolphin-emu',
            '-e', device,
            '-f'  # Modo ecrã inteiro (fullscreen)
        ]

        # Configurar backend Vulkan se definido
        video_cfg = profile.get('video', {})
        if video_cfg.get('backend', 'vulkan') == 'vulkan':
            cmd.extend(['-v', 'vulkan'])

        return cmd

    def build_flycast_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o Flycast (Dreamcast)."""
        cmd = [
            'flycast',
            '--fullscreen',
            '--vulkan',
            '--disc', device
        ]
        return cmd

    def build_redream_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o Redream (Dreamcast)."""
        cmd = [
            'redream',
            '--fullscreen',
            '--vulkan',
            '--disc', device
        ]
        return cmd

    def build_rpcs3_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o RPCS3 (PS3)."""
        cmd = [
            'rpcs3',
            '--no-gui',
            '--fullscreen',
            '--vulkan',
            '--play', device
        ]
        return cmd

    def build_xemu_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o Xemu (Xbox Original)."""
        cmd = [
            'xemu',
            '-full-screen',
            '-vulkan',
            '-dvd_path', device
        ]
        return cmd

    def build_ppsspp_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o PPSSPP (PSP)."""
        cmd = [
            'PPSSPPQt',
            '--fullscreen',
            '--vulkan',
            device
        ]
        return cmd

    def launch(self, disc_type, emulator_name, device, label=None):
        """
        Resolve qual o emulador correto, gera o comando adequado usando o perfil,
        e executa-o de forma síncrona/bloqueante para manter o sistema focado no jogo.
        """
        profile = self.load_profile(emulator_name)

        # Mapeamento dinâmico de construtores de comandos em modo autónomo (Standalone)
        # Bypassa emulatorlauncher que não suporta blocos /dev/sr0 nativamente
        builders = {
            'duckstation': lambda d, p: self.build_duckstation_cmd(d, p),
            'pcsx2': lambda d, p: self.build_pcsx2_cmd(d, p),
            'dolphin': lambda d, p: self.build_dolphin_cmd(d, p, disc_type),
            'flycast': lambda d, p: self.build_flycast_cmd(d, p),
            'redream': lambda d, p: self.build_redream_cmd(d, p),
            'rpcs3': lambda d, p: self.build_rpcs3_cmd(d, p),
            'xemu': lambda d, p: self.build_xemu_cmd(d, p),
            'ppsspp': lambda d, p: self.build_ppsspp_cmd(d, p)
        }

        builder = builders.get(emulator_name)
        if not builder:
            self.logger.error(f"O emulador '{emulator_name}' não é suportado pelo construtor de lançamento físico.")
            return False

        cmd = builder(device, profile)
        self.logger.info(f"Comando de lançamento físico standalone gerado: {' '.join(cmd)}")

        try:
            # Executar o processo de forma síncrona, herdando a sessão gráfica
            env = get_emulationstation_env()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            self.logger.info(f"Sessão de jogo iniciada. PID: {process.pid}. Aguardando conclusão...")
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.logger.info("Sessão de jogo concluída normalmente pelo utilizador.")
                return True
            else:
                self.logger.error(f"O emulador terminou com código de saída {process.returncode}. Erros: {stderr}")
                return False

        except FileNotFoundError as e:
            self.logger.error(f"Erro ao executar o comando de lançamento físico: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado durante a execução do emulador: {e}")
            return False

def main():
    """Ponto de entrada do utilitário de lançamento."""
    parser = argparse.ArgumentParser(description='Batocera AutoDisc Launcher')
    parser.add_argument('--type', required=True, help='Tipo de consola do disco')
    parser.add_argument('--emulator', required=True, help='Nome do emulador a invocar')
    parser.add_argument('--device', required=True, help='Caminho do leitor de discos')
    parser.add_argument('--label', help='Título/Nome do jogo extraído')

    args = parser.parse_args()

    launcher = EmulatorLauncher()
    success = launcher.launch(args.type, args.emulator, args.device, args.label)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
