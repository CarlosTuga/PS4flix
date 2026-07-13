# Guia de Configuração - RetroBat AutoDisc (Windows)

Este documento serve como referência para personalizar o addon **RetroBat AutoDisc** no Windows.

---

## 1. Ficheiro de Configuração Principal (`configs/config.yaml`)

O ficheiro de parametrização principal encontra-se em `configs/config.yaml`.

```yaml
# Caminho absoluto da instalação do seu RetroBat
retrobat_path: "C:\\RetroBat"

# Letra da drive de DVD/CD (use "auto" para deteção dinâmica de qualquer drive CDROM)
device:
  path: "auto"

# Intervalo em segundos para verificar inserção/remoção de discos
polling_interval: 2

# Nível de logging
logging:
  level: "INFO"

# Segundos de estabilização após fechar a gaveta do leitor
timing:
  disc_stabilization: 3
```

---

## 2. Perfis de Consolas (`configs/*.yaml`)

Cada consola suportada possui o seu próprio ficheiro YAML de perfil na pasta `configs/` contendo o emulador a invocar, o caminho relativo do executável no RetroBat e definições de desempenho:

### Exemplo: `configs/ps2.yaml`
```yaml
emulator: "pcsx2"
executable: "emulators\\pcsx2\\pcsx2-qt.exe"

video:
  renderer: "vulkan"
  vsync: true

graphics:
  upscaling: "3x"
  texture_filtering: "bilinear"

performance:
  multithreading: true
  mtvu: true
```
Você pode editar estes ficheiros com qualquer editor de texto (como o Bloco de Notas) para ajustar resoluções ou mudar emuladores!
