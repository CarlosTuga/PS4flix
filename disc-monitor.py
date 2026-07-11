#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Serviço Monitor de Discos Óticos (Daemon)
# Versão: 1.0.0
# Descrição: Monitoriza em background a inserção e remoção de discos no leitor /dev/sr0,
#            identifica a consola correspondente e inicia o emulador otimizado.
#===============================================================================

import os
import sys
import time
import yaml
import signal
import struct
import re
import subprocess
from pathlib import Path
from threading import Thread

# Importar o módulo de logging centralizado desenvolvido anteriormente
from logger import setup_logger

# Definição de caminhos absolutos do sistema
CONFIG_PATH = "/userdata/system/configs/autodisc/config.yaml"
LOG_DIR = "/userdata/system/logs/autodisc"
SERVICE_NAME = "disc-monitor"

class DiscMonitor:
    """
    Classe principal responsável pelo ciclo de vida do daemon de monitorização de discos.
    Suporta deteção ativa através do blkid e leitura direta de assinaturas e ficheiros.
    """

    def __init__(self):
        """Inicializa as variáveis de controlo, lê as configurações e cria o logger."""
        self.logger = setup_logger(SERVICE_NAME, LOG_DIR)
        self.config = self.load_config()
        self.running = True

        # Parâmetros de hardware e temporização definidos pelo utilizador ou padrões seguros
        self.device_path = self.config.get('device', {}).get('path', '/dev/sr0')
        self.mount_point = self.config.get('device', {}).get('mount_point', '/mnt/disc_temp')
        self.polling_interval = self.config.get('polling_interval', 2)
        self.stabilization_delay = self.config.get('timing', {}).get('disc_stabilization', 3)

        self.last_status = None
        self.monitor_thread = None

        # Configurar interceção de sinais do sistema para encerramento limpo
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_config(self):
        """Carrega e valida o ficheiro de configuração YAML principal."""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.logger.info("Ficheiro de configuração carregado com sucesso.")
                    return config
            else:
                self.logger.warning(f"Configuração não encontrada em {CONFIG_PATH}. Usando predefinições.")
                return self.default_config()
        except Exception as e:
            self.logger.error(f"Erro ao analisar o ficheiro de configuração: {e}. Usando predefinições.")
            return self.default_config()

    def default_config(self):
        """Predefinições seguras caso a configuração falte ou esteja corrompida."""
        return {
            'device': {
                'path': '/dev/sr0',
                'mount_point': '/mnt/disc_temp'
            },
            'polling_interval': 2,
            'timing': {
                'disc_stabilization': 3
            },
            'emulators': {
                'psx': 'duckstation',
                'ps2': 'pcsx2',
                'segacd': 'retroarch',
                'saturn': 'retroarch',
                'dreamcast': 'flycast',
                'gamecube': 'dolphin',
                'wii': 'dolphin',
                'xbox': 'xemu',
                'ps3': 'rpcs3',
                'psp': 'ppsspp'
            },
            'notifications': {
                'enabled': True,
                'timeout': 5000
            }
        }

    def signal_handler(self, signum, frame):
        """Garante que o daemon fecha de forma segura ao receber ordens de encerramento."""
        self.logger.info(f"Sinal de paragem {signum} recebido. Encerrando o serviço...")
        self.running = False

        # Desmontar qualquer partição que tenha ficado montada temporariamente
        self.unmount_device()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        self.logger.info("Monitor de discos desligado com sucesso.")
        sys.exit(0)

    def unmount_device(self):
        """Tenta desmontar de forma segura o ponto de montagem temporário."""
        if os.path.ismount(self.mount_point):
            self.logger.info(f"A desmontar ponto de montagem {self.mount_point}...")
            subprocess.run(['umount', '-f', self.mount_point], capture_output=True)

    def get_device_status(self):
        """
        Determina se existe um disco inserido e pronto para leitura física.
        Retorna 'inserted', 'empty' ou 'error'.
        """
        if not os.path.exists(self.device_path):
            return 'empty'

        try:
            # blkid retorna código 0 se houver partição ou sistema de ficheiros legível no leitor
            res = subprocess.run(
                ['blkid', self.device_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0 and res.stdout.strip():
                return 'inserted'

            # Verificação alternativa caso o disco seja apenas de áudio (CDDA) ou de formato cru
            # blkid pode retornar vazio mas o leitor ter dados
            res_ioctl = subprocess.run(
                ['setcd', '-i', self.device_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "Disc found" in res_ioctl.stdout or "volume found" in res_ioctl.stdout:
                return 'inserted'

            return 'empty'
        except subprocess.TimeoutExpired:
            self.logger.warning("Tempo limite expirado ao interrogar o leitor de discos.")
            return 'error'
        except Exception as e:
            self.logger.error(f"Erro ao interrogar o estado físico do leitor: {e}")
            return 'error'

    def read_raw_sectors(self):
        """
        Efetua a leitura de assinaturas de baixo nível (RAW) diretamente do dispositivo.
        Crucial para consolas antigas que usam formatos híbridos de CD-ROM (Saturn, Sega CD, Dreamcast).
        """
        try:
            with open(self.device_path, 'rb') as f:
                # Ler os primeiros 32KB para abranger o setor de boot padrão (setor 0 e setor 16)
                header = f.read(36864)

                # Assinaturas da Sega Saturn (geralmente nos primeiros bytes do setor 0)
                if b"SEGA SEGASATURN" in header:
                    return 'saturn', "Jogo de Sega Saturn"

                # Assinaturas da Sega CD / Mega CD
                if b"SEGA MEGA_CD" in header or b"SEGA MEGADRIVE" in header:
                    return 'segacd', "Jogo de Sega CD"

                # Assinaturas da Dreamcast GD-ROM
                if b"SEGA SECURED" in header or b"SEGA ENTERPRISES" in header or b"1ST_READ.BIN" in header:
                    return 'dreamcast', "Jogo de Sega Dreamcast"
        except Exception as e:
            self.logger.debug(f"Leitura de setores físicos RAW indisponível: {e}")
        return None, None

    def extract_ps3_title(self, sfo_path):
        """
        Parser de baixo nível para ficheiros PARAM.SFO (Sony Index File) do PlayStation 3.
        Extrai o título de jogo real codificado em UTF-8 de forma extremamente eficiente.
        """
        try:
            with open(sfo_path, 'rb') as f:
                data = f.read()

            # Validar cabeçalho do ficheiro SFO (\x00PSF)
            if data[:4] == b'\x00PSF':
                key_table_start, data_table_start, index_count = struct.unpack('<III', data[8:20])
                for i in range(index_count):
                    offset = 20 + i * 16
                    key_offset, _, _, _, data_offset = struct.unpack('<HHIII', data[offset:offset+16])

                    # Ler a chave correspondente da tabela de chaves
                    key_pos = key_table_start + key_offset
                    key_end = data.find(b'\x00', key_pos)
                    key = data[key_pos:key_end].decode('utf-8', errors='ignore')

                    # Se encontrarmos a chave de título, ler o valor correspondente
                    if key == 'TITLE':
                        val_pos = data_table_start + data_offset
                        val_end = data.find(b'\x00', val_pos)
                        val = data[val_pos:val_end].decode('utf-8', errors='ignore')
                        # Limpar quebras de linha e espaços redundantes
                        return val.replace('\n', ' ').strip()
        except Exception as e:
            self.logger.error(f"Erro ao analisar o ficheiro PARAM.SFO do PS3: {e}")
        return "Jogo de PlayStation 3"

    def identify_disc(self):
        """
        Identifica o sistema correspondente ao disco inserido e extrai o nome do jogo.
        Efetua leituras RAW primeiro e depois tenta montagem para ler metadados.
        """
        self.logger.info("Iniciando processo de identificação do disco...")

        # 1. Tentar deteção RAW por hardware/setores (Saturn, Sega CD, Dreamcast)
        console, game_title = self.read_raw_sectors()
        if console:
            return console, game_title

        # 2. Tentar montagem lógica do disco para análise de ficheiros internos (PS1, PS2, PS3, Xbox, Wii, GC)
        os.makedirs(self.mount_point, exist_ok=True)
        self.unmount_device()  # Garantir que o ponto está limpo

        mounted = False
        # Percorrer sistemas de ficheiros suportados
        for fs in ['udf', 'iso9660']:
            mount_cmd = ['mount', '-t', fs, '-o', 'ro', self.device_path, self.mount_point]
            res = subprocess.run(mount_cmd, capture_output=True)
            if res.returncode == 0:
                mounted = True
                self.logger.info(f"Disco montado lógica e temporariamente usando o driver '{fs}'.")
                break

        if not mounted:
            self.logger.warning("Não foi possível montar o disco logicamente. Formato de ficheiro não suportado diretamente pelo Kernel.")
            return 'unknown', None

        # Análise de diretórios e ficheiros sob o ponto de montagem
        try:
            # A) Verificar PlayStation 3
            ps3_dir = os.path.join(self.mount_point, 'PS3_GAME')
            if os.path.exists(ps3_dir):
                sfo_path = os.path.join(ps3_dir, 'PARAM.SFO')
                title = "Jogo de PlayStation 3"
                if os.path.exists(sfo_path):
                    title = self.extract_ps3_title(sfo_path)
                self.unmount_device()
                return 'ps3', title

            # B) Verificar PlayStation 2 (SYSTEM.CNF contendo diretrizes BOOT2)
            # C) Verificar PlayStation 1 (SYSTEM.CNF contendo diretrizes BOOT)
            cnf_candidates = [
                os.path.join(self.mount_point, 'SYSTEM.CNF'),
                os.path.join(self.mount_point, 'system.cnf'),
                os.path.join(self.mount_point, 'System.cnf')
            ]
            for cnf_path in cnf_candidates:
                if os.path.exists(cnf_path):
                    self.logger.info(f"Ficheiro de definição do sistema encontrado: {cnf_path}")
                    with open(cnf_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    is_ps2 = False
                    boot_line = None
                    for line in content.split('\n'):
                        if 'BOOT2' in line.upper():
                            is_ps2 = True
                            boot_line = line
                            break
                        elif 'BOOT' in line.upper() and not boot_line:
                            boot_line = line

                    # Tentar extrair o ID de série do jogo (ex: SLUS-20123)
                    game_id = "Jogo Desconhecido"
                    if boot_line:
                        match = re.search(r'([A-Z]{3,4})_([0-9]{3})\.([0-9]{2})', boot_line.upper())
                        if match:
                            game_id = f"{match.group(1)}-{match.group(2)}{match.group(3)}"

                    self.unmount_device()
                    if is_ps2:
                        return 'ps2', f"PS2 ID: {game_id}"
                    else:
                        return 'psx', f"PSX ID: {game_id}"

            # D) Verificar Xbox Original (presença de default.xbe)
            xbox_candidates = ['default.xbe', 'DEFAULT.XBE', 'Default.xbe']
            for xbox_file in xbox_candidates:
                if os.path.exists(os.path.join(self.mount_point, xbox_file)):
                    self.unmount_device()
                    return 'xbox', "Jogo de Xbox Clássica"

            # E) Verificar Xbox 360 (presença de default.xex)
            x360_candidates = ['default.xex', 'DEFAULT.XEX', 'Default.xex']
            for x360_file in x360_candidates:
                if os.path.exists(os.path.join(self.mount_point, x360_file)):
                    self.unmount_device()
                    return 'xbox360', "Jogo de Xbox 360"

            # F) Verificar GameCube e Wii
            # GameCube/Wii têm abertura opening.bnr ou pasta sys/ com boot.bin
            if (os.path.exists(os.path.join(self.mount_point, 'sys', 'boot.bin')) or
                os.path.exists(os.path.join(self.mount_point, 'opening.bnr'))):
                is_wii = os.path.exists(os.path.join(self.mount_point, 'sys', 'main.dol')) or os.path.exists(os.path.join(self.mount_point, 'ticket'))
                self.unmount_device()
                if is_wii:
                    return 'wii', "Jogo de Nintendo Wii"
                else:
                    return 'gamecube', "Jogo de Nintendo GameCube"

        except Exception as e:
            self.logger.error(f"Erro durante a análise lógica de ficheiros de sistema: {e}")

        # Desmontar se nenhum padrão foi correspondido
        self.unmount_device()
        return 'unknown', None

    def send_osd_notification(self, title, msg):
        """Envia comandos para o script de notificações OSD."""
        notify_script = "/userdata/system/autodisc/scripts/notify.sh"
        if os.path.exists(notify_script):
            subprocess.run([notify_script, title, msg], capture_output=True)
        else:
            self.logger.warning("Script de notificação OSD não encontrado localmente.")

    def launch_game(self, disc_type, game_label):
        """
        Comunica com o script disc-launcher para iniciar o emulador de forma assíncrona.
        Garante que o monitor suspende as verificações enquanto o jogo decorre.
        """
        # Obter o emulador mapeado na configuração
        emulators = self.config.get('emulators', {})
        emulator = emulators.get(disc_type)

        if not emulator:
            self.logger.error(f"Nenhum emulador configurado para o tipo de disco: {disc_type}")
            return

        # Preparar argumentos de invocação
        launcher_path = "/userdata/system/autodisc/disc-launcher.py"
        cmd = [
            "python3", launcher_path,
            "--type", disc_type,
            "--emulator", emulator,
            "--device", self.device_path
        ]
        if game_label:
            cmd.extend(["--label", game_label])

        self.logger.info(f"A preparar arranque do emulador {emulator} para consola {disc_type}...")

        # Enviar notificações visuais amigáveis em português
        friendly_consoles = {
            'psx': 'PlayStation 1',
            'ps2': 'PlayStation 2',
            'ps3': 'PlayStation 3',
            'segacd': 'Sega CD',
            'saturn': 'Sega Saturn',
            'dreamcast': 'Sega Dreamcast',
            'gamecube': 'Nintendo GameCube',
            'wii': 'Nintendo Wii',
            'xbox': 'Xbox Original',
            'xbox360': 'Xbox 360'
        }

        console_name = friendly_consoles.get(disc_type, disc_type.upper())
        self.send_osd_notification(
            f"Disco {console_name} detetado",
            f"Jogo: {game_label or 'Título Desconhecido'}\nA iniciar {emulator}..."
        )

        # Aguardar tempo de estabilização do monitor/leitor
        time.sleep(3)

        try:
            # Executa de forma bloqueante no monitor para suspender leituras cíclicas do leitor
            self.logger.info(f"Executando lançador: {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode == 0:
                self.logger.info("Sessão de jogo concluída com sucesso. Retornando ao EmulationStation.")
                self.send_osd_notification("Jogo Terminado", "Regressando ao EmulationStation...")
            else:
                self.logger.error(f"Ocorreu um erro ao executar a sessão de jogo: {res.stderr}")
                self.send_osd_notification("Erro ao Iniciar", "Verifique os logs em /userdata/system/logs/autodisc/")
        except Exception as e:
            self.logger.error(f"Falha de execução do subprocesso do emulador: {e}")

    def monitor_loop(self):
        """Ciclo de monitorização infinito de polling inteligente."""
        self.logger.info("Ciclo de polling ativo e operacional.")
        while self.running:
            try:
                status = self.get_device_status()

                # Reagir apenas a mudanças de estado físico do leitor
                if status != self.last_status:
                    self.logger.info(f"Mudança de estado física registada: {self.last_status} -> {status}")

                    if status == 'inserted':
                        self.logger.info(f"Estabilizando o disco no leitor por {self.stabilization_delay}s...")
                        time.sleep(self.stabilization_delay)

                        disc_type, game_label = self.identify_disc()
                        if disc_type != 'unknown':
                            self.logger.info(f"Disco Identificado com sucesso: [{disc_type}] - [{game_label}]")
                            self.launch_game(disc_type, game_label)
                        else:
                            self.logger.warning("Inserido disco não reconhecido ou ilegível.")
                            self.send_osd_notification("Disco Não Reconhecido", "O formato deste disco não é suportado pelo AutoDisc.")

                    elif status == 'empty':
                        self.logger.info("O leitor de discos encontra-se agora vazio.")

                    self.last_status = status

                time.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"Erro no ciclo de monitorização: {e}")
                time.sleep(5)

    def run(self):
        """Inicia a thread de monitorização e mantém o processo pai em execução."""
        self.logger.info("A ligar subsistema de monitorização de discos óticos...")
        self.monitor_thread = Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        while self.running:
            time.sleep(1)

def main():
    """Ponto de entrada do serviço."""
    try:
        monitor = DiscMonitor()
        monitor.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Erro Crítico Fatal no Arranque do Monitor: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
