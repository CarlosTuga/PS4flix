# Guia de Configuração - Batocera AutoDisc

Este documento serve como referência completa para a parametrização, ajuste de perfis e otimização de emuladores do addon **Batocera AutoDisc**.

---

## 1. Ficheiro de Configuração Principal (`config.yaml`)

O ficheiro principal de parametrização encontra-se localizado de forma centralizada em:
`/userdata/system/configs/autodisc/config.yaml`

Abaixo encontra-se a explicação detalhada de cada bloco chave:

### Bloco `device` (Hardware)
```yaml
device:
  path: /dev/sr0           # Caminho Unix do leitor ótico físico (SATA/HP)
  mount_point: /mnt/disc_temp  # Ponto de montagem temporário do sistema de ficheiros do disco
```

### Bloco `timing` (Temporização de Barramento)
```yaml
timing:
  disc_stabilization: 3    # Tempo de espera em segundos após a inserção mecânica para leitura física
```

### Bloco `emulators` (Associação de Consola para Emulador)
Mapeia o tipo de disco detetado para a linha de comando do emulador correspondente no Batocera.
```yaml
emulators:
  psx: duckstation         # Emulador padrão para PlayStation 1 (DuckStation)
  ps2: pcsx2               # Emulador padrão para PlayStation 2 (PCSX2)
  segacd: retroarch        # Emulador padrão para Sega CD
  saturn: retroarch        # Emulador padrão para Sega Saturn
  dreamcast: flycast       # Emulador padrão para Sega Dreamcast (Alternativa: redream)
  gamecube: dolphin        # Emulador padrão para Nintendo GameCube
  wii: dolphin             # Emulador padrão para Nintendo Wii
  xbox: xemu               # Emulador padrão para Xbox Original
  ps3: rpcs3               # Emulador padrão para PlayStation 3
  psp: ppsspp              # Emulador padrão para PlayStation Portable
```

### Bloco `notifications` (Sistema de Alertas Visuais)
```yaml
notifications:
  enabled: true            # Ativar notificações OSD (On-Screen Display)
  timeout: 5000            # Duração de exibição do balão de alerta em milissegundos
```

---

## 2. Perfis de Desempenho de Emuladores (`profiles/`)

Os perfis de emuladores estão localizados na pasta `/userdata/system/autodisc/profiles/` e utilizam o formato YAML. Foram altamente ajustados para aproveitar ao máximo a combinação de CPU **Intel Core i7-8700** e GPU **NVIDIA GTX 1060 (3GB)**:

### 2.1 DuckStation (`duckstation.yaml`)
* **API Gráfica:** Vulkan.
* **Resolução Interna:** 4x (1080p).
* **Speedhacks:** Ativados por predefinição.
* **Multithreading:** Ativo (Threaded Rendering) para distribuição ideal pelos 12 threads virtuais do i7-8700.

### 2.2 PCSX2 (`pcsx2.yaml`)
* **API Gráfica:** Vulkan.
* **Resolução Interna:** 3x (Alta qualidade gráfica sem saturar os 3GB de VRAM física da GPU GTX 1060).
* **MTVU (Multi-Threaded microVU):** Ativado para aproveitar o processador multinúcleo.
* **Ciclos de CPU:** Configurado com EE Cycle Rate a `2` e VU Cycle Steal a `1` para emulação fluida mesmo em jogos pesados como Shadow of the Colossus.

### 2.3 Dolphin (`dolphin.yaml`)
* **API Gráfica:** Vulkan.
* **Resolução Interna:** 3x (1080p).
* **Dual-Core:** Ativado para processamento físico/gráfico paralelo.
* **EFB Hacks:** Ativado `skip_efb_access` e `efb_to_texture` para evitar stutters e quedas abruptas de fotogramas.

### 2.4 Flycast & Redream (`flycast.yaml` / `redream.yaml`)
* **API Gráfica:** Vulkan.
* **Resolução Interna:** 4x para renderização sem aliasing de polígonos.
* **Shader Cache:** Ativo.

### 2.5 RPCS3 (`rpcs3.yaml`)
* **API Gráfica:** Vulkan.
* **Descodificadores:** PPU em LLVM e SPU em ASMJIT para compilação super rápida.
* **Multithreading:** Limite de 6 threads configurado de forma a garantir estabilidade nos núcleos lógicos do i7-8700.

### 2.6 Xemu (`xemu.yaml`)
* **API Gráfica:** Vulkan.
* **Resolução Interna:** 2x.

---

## 3. Customização e Resolução de Problemas

Se um jogo específico sofrer lentidão crónica ou falhas gráficas, o utilizador pode abrir o perfil correspondente na pasta de perfis e reduzir o multiplicador de resolução:

```bash
# Exemplo: Reduzir a resolução do PCSX2 para 2x
nano /userdata/system/autodisc/profiles/pcsx2.yaml

# Modificar a chave correspondente:
# upscaling: 2x
```
