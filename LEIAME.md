## Portais de Transparência e Dados Abertos de estados e municípios do Brasil

Obter uma lista dos portais da transparência e de dados abertos de todos os 27
estados e 5.570 municípios brasileiros pode ser uma tarefa descomunal. Este
projeto tem o objetivo de consolidar e manter atualizadas todas essas
informações de referência.

Além disso, cada estado e município tem seu poder executivo e legislativo, o
que efetivamente duplica a quantidade de trabalho necessária.

### Passos para a descoberta de dados

Nós realizamos muitos passos para encontrar os portais que são de fato da
transparência e de dados abertos. Em primeiro lugar, precisamos encontrar
os sites institucionais das câmaras ou assembleias legislativas e prefeituras
no Brasil.

#### Encontrando os sites de câmaras e prefeituras

Poderia se esperar que um banco de dados contendo os sites oficiais de todas
as câmaras e prefeituras municipais do Brasil já existisse. Mas, na verdade,
não há. Então, tentamos obter possíveis links a partir de diversas fontes.

Essas fontes estão no diretório *[sources](sources)* (fontes). Verifique cada
pasta individual da fonte para mais informações. Alguns exemplos de fontes já
implementadas são:

* [tabela dos quadros 31 e 32](sources/research/klein-2017) da tese de doutorado de Rodrigo Klein (2017)
* [DBPedia](sources/dbpedia), a ferramenta da web semântica que extrai dados
  estruturados a partir da [Wikipédia](https://www.wikipedia.org/)

Os scripts que de fato fazem a importação estão no diretório
[tools/import](tools/import) (ferramentas/importar). Eles devolvem dados que
contêm os possíveis links para os sites das administrações locais, os quais
são armazenados no diretório [data/unverified](data/unverified) (dados/não
verificados). Espera-se que os dados guardados aqui ainda contenham muito
lixo e **não devem ser incluídos (commit) no repositório**.

O próximo passo é a validação de links. Isso é feito automaticamente, por um
bot, e manualmente, com a ajuda de um script. O código desses está no
diretório [tools/validation](tools/validation) (ferramentas/validação). A
saída, com dados validados, vai para o diretório [data/valid](data/valid).

#### Encontrando portais da transparência e dados abertos nos sites oficiais

Assim que temos os links para os sites oficiais de câmaras e prefeituras,
nós analisamos o conteúdo das páginas para procurar pela presença de links
para portais da transparência e dados abertos.

Esse passo ainda não está implementado.

### Objetivos

O objetivo desse projeto é construir uma base de dados de referência sobre
os estados e municípios brasileiros, contemplando os poderes legislativo e
executivo, contendo os seguintes dados sobre cada um deles:

* site oficial
* portal da transparência
* portal de dados abertos

Também pretendemos colaborar no monitoramento da transparência de estados e
municípios em projetos como o [Colaboradados](http://colaboradados.github.io/)
e a [lista de catálogos de dados abertos no
Brasil](https://github.com/dadosgovbr/catalogos-dados-brasil).

