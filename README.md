# chat-bot
### Instruções de execução da primeira entrega:
1. Baixe a pasta e extraia os arquivos
2. Considerando que já tenha Python3 instalado, abra duas abas do terminal no diretório em que baixou a pasta
3. Em uma das abas rode o comando: `python3 server.py`. O servidor será inicializado e irá aguardar alguma requisição.
4. Na outra aba do terminal rode o comando: `python3 client.py`. Em seguida digite o nome do arquivo que deseja enviar e tecle *Enter*
5. Observe na pasta do diretório que foram salvos dois novos arquivos: 
          "nfileRecvFromClient" refere-se ao arquivo que o servidor recebeu do cliente *n* é o numero pela ordem da requisição desde que o servidor foi executado;
          "fileRecvFromServer" refere-se ao arquivo que o cliente recebeu em resposta do servidor.
   Ambos os arquivos estão no formato referente ao arquivo enviado inicialmente pelo cliente.
6. Se desejar enviar mais arquivos, basta voltar ao passo 3 e executar o cliente novamente. Não é necessário executar o servidor novamente, pois ele fica esperando por mais requisições do cliente. 

**OBS.: O arquivo que deseja enviar deve estar salvo na mesma pasta do projeto**
