# Conectar ao MOBI

No Blender 5.2 ou mais recente, abra Preferências › Extensões › Repositórios e adicione um repositório remoto com a fonte:

`https://mobi.caff.digital/blender/extensoes/index.json`

Deixe a verificação de atualizações ao iniciar ligada. Busque **CAFFMob Draw**, instale e permita o acesso à internet nas preferências do Blender.

Na Viewport 3D, abra a barra lateral (N) › CAFFMob Draw › Produção/Projeto › CAFF MOBI. Clique em **Conectar**, confirme o código no navegador e volte ao Blender. A conta mostra somente o titular conectado. O mesmo quadro está nas preferências do addon, junto do endereço do MOBI.

Use **Listar ambientes** e **Baixar** para abrir um ambiente. **Enviar ambiente** devolve paredes, aberturas e módulos do contrato do MOBI, incluindo medidas, posições e acabamentos aplicados. **Editar segmento** altera a parede selecionada. Na biblioteca, escolha **Do titular** ou **Pessoal**, liste e insira um modelo como cópia. Um módulo do MOBI pode ser enviado como versão do modelo de origem ou como modelo novo. Se houver duas versões, escolha a do Blender ou a do MOBI no aviso de conflito. A grade de texturas continua no painel Biblioteca.

Objetos soltos, luzes, câmeras e móveis de outras bibliotecas não sobem. **Se a cena contiver um armário criado pelo construtor da 015, Enviar ambiente é recusado inteiro, com aviso.** Esse armário também não pode ser enviado como modelo. Não há conversão automática dele para o contrato do MOBI (P-10).

A situação e o progresso aparecem no grupo CAFF MOBI. **Cancelar** interrompe a operação em curso e preserva a cena anterior ao download.

Para sair, clique em **Desconectar**: o aparelho é revogado e a sessão local é apagada. Sem rede, a sessão local é apagada e o aviso orienta a desconectar também em **Aparelhos conectados** no MOBI. A senha nunca passa pelo Blender.
