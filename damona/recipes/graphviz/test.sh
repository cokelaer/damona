


ENV="damona_graphviz__testing__"
damona env --create $ENV
damona activate $ENV
damona install graphviz
dot -Tsvg test.dot -o test.sv
damona env --delete $ENV --force
damona deactivate $ENV
