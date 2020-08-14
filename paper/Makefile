.PHONY: clean

spont.pdf: spont.tex
	pdflatex spont; bibtex spont; pdflatex spont

clean:
	rm -f spont.aux
	rm -f spont.bbl
	rm -f spont.blg
	rm -f spont.log
	rm -f spont.out
	rm -f spont.pdf
