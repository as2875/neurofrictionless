.PHONY: clean

spont.pdf: spont.tex
	pdflatex spont; bibtex spont; pdflatex spont

clean:
	rm -f spont.aux spont.bbl spont.blg  spont.log  spont.out spont.pdf
