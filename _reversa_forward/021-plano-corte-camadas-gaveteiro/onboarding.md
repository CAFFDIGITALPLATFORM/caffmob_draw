# Onboarding de Testes: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Público: humano validando a feature pela primeira vez no Blender ≥ 5.2

## Pré-requisitos

1. Empacote e instale a extensão atualizada via `python3 build.py` no Blender 5.2+.
2. Abra uma cena nova com o painel lateral do **CAFFMob Draw** visível na Viewport 3D.

## Roteiro passo a passo

### 1. Parâmetros rápidos na aba Ferramentas e Camada `Arquitetura`
1. Na aba **Ferramentas**, defina **Pé-direito padrão** = `2,80 m` e **Espessura padrão de parede** = `150 mm`.
2. Abra o **Editor de Parede** e desenhe um cômodo fechado (4 paredes) e confirme em **OK**.
   - **Verifique:** as paredes nascem com `2,80 m` de altura e `150 mm` de espessura dentro de `Arquitetura > Parede`.
3. Gere o **Piso** com espessura `120 mm` e direção **Para baixo**.
   - **Verifique:** o piso fica em `Arquitetura > Piso`, com topo em `Z = 0,000 m` e base em `Z = −0,120 m`.
4. Altere a direção da espessura do piso para **Para cima** e atualize.
   - **Verifique:** o piso ocupa de `Z = 0,000 m` a `Z = +0,120 m`.
5. Gere o **Teto** e insira uma **Porta** ou **Janela**.
   - **Verifique:** o teto entra em `Arquitetura > Teto` e a abertura em `Arquitetura > Aberturas`.

### 2. Parede rebaixada e restauração
1. Selecione uma parede fora do editor e clique em **Rebaixar Parede**.
2. Clique diretamente na parede rebaixada (150 mm) na Viewport 3D.
   - **Verifique:** o addon reconhece o objeto e exibe o botão **Restaurar Parede**.
3. Clique em **Restaurar Parede**.
   - **Verifique:** a parede original retorna à altura de `2,80 m` e o proxy de 150 mm desaparece.

### 3. Criar Armário direto no Construtor v2, Biblioteca CAFFMob e Camada `Marcenaria`
1. Clique no botão **Criar Armário**.
   - **Verifique:** o **Construtor de Armários v2** abre diretamente (sem passar pela galeria verde-escura legada).
2. Confirme a criação do armário.
   - **Verifique:** o armário nasce dentro da coleção `Marcenaria`.
3. Abra o painel de **Biblioteca** de armários.
   - **Verifique:** a paleta visual segue a identidade oficial da CAFFMob (sem o verde escuro legado) e um armário inserido dela edita normalmente no Construtor v2.

### 4. Colisão global no cabeçalho e correção do ciclo ao Desgrudar
1. Observe o **cabeçalho (header) da Viewport 3D** e clique no botão global de **Colisões**.
   - **Verifique:** o ícone/estado alterna entre ligado e desligado e reflete `collision_global`.
2. Com o armário grudado em uma parede, clique em **Desgrudar** e mova o armário `30 mm` para frente (saindo da parede).
   - **Verifique:** aguarde 1 segundo; o armário permanece na nova posição sem ser puxado de volta para a parede.

### 5. Converter em Gaveteiro (malha completa e incompleta)
1. Modele ou importe um gaveteiro manual (teste uma vez com malha única contendo 6 peças e outra vez com objetos separados faltando Contrafrente e Fundo).
2. Clique com o **botão direito** (ou toque longo) e navegue até **Converter em: > Gaveteiro**.
   - **Verifique (completo):** as 6 peças (2 laterais, contrafrente, traseira, fundo, frente) são reconhecidas, ferragens ficam configuráveis e o editor abre ao final.
   - **Verifique (incompleto):** o addon lista as peças ausentes, **pergunta se deseja completá-las** sem bloquear a criação, respeita sua escolha (gerar ou manter parcial) e abre o editor para edição livre.

### 6. Lista de peças agrupadas por módulo e Plano de Corte OpCut offline
1. Com 2 ou mais armários na cena, abra o painel de **Plano de Corte**.
2. Ative a visualização de **Lista de peças agrupadas por módulo**.
   - **Verifique:** as chapas aparecem agrupadas por módulo e nenhuma ferragem (corrediça/puxador) entra como chapa.
3. Desconecte a internet (opcional, para provar operação offline) e gere o **Plano de Corte (OpCut)**.
   - **Verifique:** a prévia das chapas aparece dentro do Blender sem sobreposições; exporte em **HTML**, **SVG** e **PDF** e abra os arquivos gerados.

### 7. Sincronizar Texturas Perdidas
1. Aplique uma textura do catálogo do addon a uma chapa, salve e apague o arquivo da textura no diretório de cache local.
2. No painel de **Texturas/Materiais**, clique em **Sincronizar Texturas Perdidas**.
   - **Verifique:** o addon identifica o arquivo ausente, baixa novamente, reconecta o material e reporta o total sincronizado.
