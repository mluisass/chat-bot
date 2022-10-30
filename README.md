# Projeto de Infraestrutura de Comunicações
## Equipe
* Elisson Rodrigo da Silva Araujo (ersa)

* Maria Luísa dos Santos Silva (mlss)

* Rebecca Lima Sousa (rls7)

* Tales Vinícius Alves da Cunha (tvac)

## Instruções de execução da terceira entrega
1. Baixe a pasta e extraia os arquivos.
2. Considerando que já tenha Python3 instalado, abra, no mínimo, duas abas do terminal no diretório em que baixou a pasta.
3. Em uma das abas execute o comando: 
   ```
   python3 server.py
   ```
   O servidor será inicializado e irá aguardar alguma requisição.
4. Na outra aba do terminal execute o comando: 
   ```
   python3 client.py
   ```
5. Você pode iniciar vários clientes repetindo o passo 3 em mais abas do terminal.
6. Para entrar no chat da sala use o comando "hi, meu nome é <nome_de_usuario>" indicando o nome de usuário que deseja usar.
7. Para sair da sala use o comando "bye".
8. Para exibir a lista de usuários conectados à sala use o comando "list".
9. Para enviar uma mensagem particular (inbox) use o comando @<nome_de_usuario> <mensagem> indicando o usuário que deseja falar e qual a mensagem.
10. Se deseja expulsar algum usuário da sala, use o comando "ban @<nome_de_usuario>". Após um usuário receber pelo menos 2/3 da quantidade de usuários em ban's, ele será expulso. Os ban's são contabilizados com pelo menos 10 segundos de diferença desde o último.
