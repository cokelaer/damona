# This is just a quick hack to test locally
# .............................................................................

all:
	rm -f paper.bbl paper.log paper.blg paper.aux paper.out
	pandoc -f markdown -t latex --pdf-engine=xelatex  --biblatex --bibliography paper.bib paper.md -o paper.tex --template latex.template 
	pdflatex paper.tex
	#bibtex paper
	pdflatex paper.tex

