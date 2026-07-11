#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Lançador de Emuladores Otimizado
# Versão: 1.0.0
# Descrição: Carrega os perfis de desempenho e executa os emuladores com parâmetros
#            otimizados para a GPU GTX 1060 (3GB) e CPU i7-8700 (6 Cores/12 Threads).
#===============================================================================

import os
import sys
import yaml
import argparse
import subprocess
from pathlib import Path

# Importar o módulo de logging centralizado desenvolvido anteriormente
from logger import setup_logger

class EmulatorLauncher:
    """
    Classe responsável por carregar perfis YAML de emuladores e lançá-los com flags
    específicas de desempenho (Vulkan, Multithreading, Speedhacks, etc.).
    """

    def __init__(self, log_dir="/userdata/system/logs/autodisc"):
        """Inicializa o logger e define o caminho dos perfis de emulação."""
        self.logger = setup_logger("disc-launcher", log_dir)
        self.profiles_dir = "/userdata/system/autodisc/profiles"

    def load_profile(self, emulator_name):
        """
        Tenta carregar o perfil YAML otimizado para o emulador solicitado.
        Retorna um dicionário com as configurações ou um perfil padrão caso falhe.
        """
        profile_path = Path(self.profiles_dir) / f"{emulator_name}.yaml"

        try:
            if profile_path.exists():
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = yaml.safe_load(f)
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
            'emulator': emulator_name,
            'video': {'backend': 'vulkan', 'vsync': True},
            'performance': {'multithreading': True, 'speed_hacks': True, 'shader_cache': True}
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
        # Em Batocera, o comando principal é 'pcsx2' ou 'PCSX2-QT'
        # Usamos '--fullscreen' e '--nogui' para emulação de estilo consola pura
        cmd = [
            'pcsx2',
            '--nogui',
            '--fullscreen'
        ]

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
            device
        ]
        return cmd

    def build_redream_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o Redream (Dreamcast)."""
        cmd = [
            'redream',
            '--fullscreen',
            device
        ]
        return cmd

    def build_rpcs3_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o RPCS3 (PS3)."""
        cmd = [
            'rpcs3',
            '--no-gui',
            '--fullscreen',
            '--play', device
        ]
        return cmd

    def build_xemu_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o Xemu (Xbox Original)."""
        cmd = [
            'xemu',
            '-full-screen',
            '-dvd_path', device
        ]
        return cmd

    def build_ppsspp_cmd(self, device, profile):
        """Desenha a linha de comando otimizada para o PPSSPP (PSP)."""
        cmd = [
            'PPSSPPQt',
            '--fullscreen',
            device
        ]
        return cmd

    def launch(self, disc_type, emulator_name, device, label=None):
        """
        Resolve qual o emulador correto, gera o comando adequado usando o perfil,
        e executa-o de forma síncrona/bloqueante para manter o sistema focado no jogo.
        """
        profile = self.load_profile(emulator_name)

        # Mapeamento dinâmico de construtores de comandos
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
            self.logger.error(f"O emulador '{emulator_name}' não é suportado pelo construtor do lançador.")
            return False

        cmd = builder(device, profile)
        self.logger.info(f"Comando de lançamento final gerado: {' '.join(cmd)}")

        # Desativar cursor do rato antes do lançamento do emulador
        subprocess.run(['unclutter', '-idle', '0'], capture_output=True)

        try:
            # Executar o processo do emulador de forma bloqueante
            # Em Batocera, isto suspende o EmulationStation em background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.logger.info(f"Emulador {emulator_name} iniciado com PID {process.pid}. A aguardar conclusão da sessão de jogo...")
            stdout, stderr = process.communicate()

            # Reativar cursor se necessário ao sair do emulador
            subprocess.run(['killall', 'unclutter'], capture_output=True)

            if process.returncode == 0:
                self.logger.info("Sessão de jogo concluída com sucesso pelo utilizador.")
                return True
            else:
                self.logger.error(f"O emulador terminou com código de erro {process.returncode}. Mensagem: {stderr}")
                return False
        except FileNotFoundError:
            self.logger.error(f"Erro Crítico: O executável do emulador '{emulator_name}' não foi encontrado no PATH do Batocera.")
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
