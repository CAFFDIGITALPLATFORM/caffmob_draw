# Procedimento de Empacotamento e Implantação (Deployment) — BlenderToMob

Este documento descreve as etapas para empacotamento, distribuição e instalação do add-on **BlenderToMob** no Blender 4.2+, documentado pelo agente **Architect** no nível de documentação **Detalhado**.

---

## 1. Empacotamento da Extensão (.zip)

O Blender 4.2+ introduziu um novo sistema de gerenciamento de add-ons estruturado como extensões. Para empacotar os arquivos de desenvolvimento no formato ZIP correto para distribuição:

1. Acesse a raiz do workspace `/home/theleoinfo/www/BlenderToMob`.
2. Execute o utilitário de empacotamento Python:
   ```bash
   python3 build.py
   ```
3. O script lerá o manifesto `blendertomob/blender_manifest.toml`, filtrará diretórios indesejados (como `__pycache__` e metadados do Git) e empacotará os arquivos recursivamente, gerando `blendertomob.zip` na raiz do projeto.

---

## 2. Instalação e Ativação no Blender (Host local)

Para implantar e testar o add-on gerado:

### 2.1 Passos para Instalação Física
1. Abra o **Blender 4.2** ou superior.
2. Acesse o menu superior: **Edit > Preferences** (Editar > Preferências).
3. Selecione a aba lateral **Get Extensions** (Obter Extensões) ou **Add-ons**.
4. Clique no ícone de engrenagem/seta no canto superior direito e escolha a opção **Install from Disk...** (Instalar do Disco...).
5. Selecione o arquivo compilado `blendertomob.zip`.
6. O Blender copiará o add-on para a pasta interna de extensões de usuário:
   * **Linux**: `~/.config/blender/4.2/extensions/user_default/blendertomob/`
   * **Windows**: `%USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\4.2\extensions\user_default\blendertomob\`
   * **macOS**: `~/Library/Application Support/Blender/4.2/extensions/user_default/blendertomob/`
7. A extensão será ativada automaticamente.

---

## 3. Verificação Pós-Implantação

1. Vá para o **3D Viewport** do Blender.
2. Pressione a tecla **N** para abrir a barra lateral (Sidebar).
3. Verifique se a aba **BlenderToMob** está visível.
4. Clique no painel **Criador de Ambientes** e clique em **Construir Parede** para verificar se o loop modal de desenho e os overlays da GPU funcionam corretamente.


## Re-extração 2026-10-10 — arquitetura atual

🟢 Implantação atual: extensão ZIP local gerada por `python3 build.py`, instalada no Blender 5.2. Fonte: build.py e blender_manifest.toml. Nenhum Dockerfile, compose ou configuração Terraform foi localizado na busca; não há novo diagrama de cloud a gerar. Build/instalação não foram executados nesta extração documental. A validação de distribuição requer wheels e ativos blend/texturas/biblioteca presentes; referência ADR 0007.
