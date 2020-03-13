Como contribuir para este projeto.

This text is also available in English: 🇬🇧[CONTRIBUTING.md](CONTRIBUTING.md).

## Introdução

Obrigado pelo seu interesse em contribuir com este projeto. Para que possamos
manter organizadas as contribuições de todos, por favor siga essas
recomendações antes de começar a mexer.

## Idioma

Este é um projeto bilíngue. Para manter o conjunto de possíveis contribuidores
o mais amplo possível e ser inclusivo, escreva as suas contribuições tanto em
português quanto em inglês, se puder. Se você não for fluente em ambos os
idiomas, aceitamos contribuições em apenas um deles. Se você for fluente, no
entanto, por favor ajude a traduzir as partes do projeto que ainda não forem
bilíngues.

## Fluxo de trabalho

Seguimos um fluxo de trabalho que é bem comum em projetos de código aberto.

1. Comece criando o seu próprio *fork*. Há um botão no Github só para isso, no
   canto superior direito.
2. Clone o seu *fork* para a sua máquina local. É possível editar arquivos
   diretamente na interface do Github, mas clonar o projeto para a sua
   própria máquina trará muito mais flexibilidade. Para clonar, digite:
   
   `$ git clone http://github.com/<SEU-NOME-DE-USUARIO-NO-GITHUB>/transparencia-dados-abertos-brasil.git`
3. Inicie um novo *branch*:
   
   `$ git checkout -b issue-nn`
   
   Se já houver uma *issue* no repositório sobre as mudanças que você pretende
   fazer, por favor use o nome `issue-nn`, onde `nn` é o número da *issue* no
   repositório. Isso nos ajudará a acompanhar sobre o que é o *branch* e
   também dá às pessoas um lugar para comentar, se necessário.
4. Faça as suas coisas
   
   Crie ou altere os arquivos para implementar a sua grande ou pequena ideia
   que irá ajudar o projeto.
5. Faça *add* e *commit* nas suas mudanças

   ```
   $ git add arquivos-que-mudei
   $ git commit -m 'My nifty contribution'
   ```
   
   Use verbos no infinitivo e escreva a sua mensagem em inglês, se puder.
   Tente fazer uma mensagem descritiva, mas sucinta, que reflita o que você
   fez.
6. Faça *push* das suas mudanças para o seu *fork*

   `$ git push --set-upstream origin issue-nn`
7. Crie um novo *pull request*

   A partir da sua página do *fork*, após detectar o seu *push*, o Github irá
   oferecer um botão para abrir um novo *pull request* para oferecer o seu
   código para revisão antes de ser incorporado de volta ao repositório
   principal.
   
   Certifique-se de escrever um título e uma descrição representativos.

## Tipos de contribuições

Você pode contribuir para quaisquer arquivos contidos no repositórios, mas
aqui estão algumas ideias de contribuições que podem ser úteis.

### Dados

Há algumas categorias de dados neste repositório:

* valid – os dados principais do repositório, que foram verificados de alguma
  maneira.
* auxiliary – dados que não são o objetivo principal do repositório, mas que
  são bastante úteis de se manterem por perto, de qualquer forma. Somente
  dados verificados devem entrar aqui.
* archive – dados que não são mais usados pelo projeto, mas que são mantidos
  para arquivamento. Dados velhos aqui não deveriam mudar nunca.
* unverified – dados não verificados devem ser mantidos fora do repositório.
  Guarde aqui somente dados temporários e nunca dê *commit* neles. O
  `.gitignore` está configurado para automaticamente excluir arquivos neste
  diretório.

Certifique-se de rodar

```
$ goodtables data/.../datapackage.json
```

nos dados que você está trabalhando, antes de fazer *commit* neles para o
repositório. Isso garante que apenas dados válidos entrem.

Faça com que o comando `goodtables` esteja disponível na sua linha de comando,
seguindo as instruções no nosso [LEIAME](LEIA.md) ou as
[instruções de instalação](https://github.com/frictionlessdata/goodtables-py#installing)
do próprio Goodtables.

### Código

Este repositório contém não apenas dados, mas também os scripts necessários
para mover os dados e validá-los. Os scripts moram no diretório
[tools](tools/).

Ao adicionar um novo script, certifique-se de incluir também a documentação
necessária (um arquivo LEIAME.md é o suficiente), com instruções sobre como
usá-lo. Inclua também qualquer configuração necessária, como um registro das
dependências. Se for um script Python, inclua um arquivo `requirements.txt`,
fixando os números de versão das bibliotecas utilizadas.

#### Scripts de importação

[Estes](tools/import/) são scripts que importam dados de [fontes](#sources)
externas ao projeto. Dados que saem dos scripts de importação normalmente vão
para o diretório [data/unverified](data/unverified/).

#### Scripts de exportação

[Estes](tools/export/) são scripts que exportam dados deste projeto para
outros  projetos para os quais contribuímos.

#### Scripts de validação

[Estes](tools/export/) scripts fazem a validação de dados no diretório
[data/unverified](data/unverified/) e enviam para [data/valid](data/valid/).
Os dados podem ser validados automaticamente ou manualmente. Neste caso,
normalmente é um script que recebe a interação do usuário, de forma a
auxiliá-lo a validar os dados manualmente de alguma forma.

### Fontes

Documentação sobre as fontes de dados. Use texto em markdown e
*[data packages](https://frictionlessdata.io/specs/data-package/)* para
fazê-lo.

### Documentação

Arquivos markdown como este documentam o projeto como um todo. Propostas de
melhorias nestes também são muito bem vindas.

### *Issues*

Se você tem uma ideia sobre como melhorar alguma coisa, mas não tem certeza de
como implementá-la, ou se quer discuti-la antes, por favor abra uma
[issue](/augusto-herrmann/transparencia-dados-abertos-brasil/issues) sobre ela.

