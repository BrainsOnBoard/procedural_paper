# Simple Xe/LaTeX Makefile
# (C) Andrew Mundy 2012

# Configuration
TEX=pdflatex
BIB=bibtex
TEXFLAGS=--shell-escape
BIBFLAGS=
texdoc=procedural

TIKZ_PICTURES :=$(wildcard figures/*.tex)
TIKZ_EPS :=$(foreach fig,$(basename $(TIKZ_PICTURES)),$(fig).eps)

.PHONY: clean bib count all

# Make all items
all : $(texdoc).pdf $(TIKZ_EPS)

$(texdoc).pdf : $(texdoc).tex
	$(TEX) $(TEXFLAGS) $(texdoc)

# Generate reference requirements
$(texdoc).aux : $(texdoc).tex
	$(TEX) $(TEXFLAGS) $(texdoc)

# Generate the bibliography
bib : $(texdoc).aux
	$(BIB) $(BIBFLAGS) $(texdoc)
	$(TEX) $(TEXFLAGS) $(texdoc)
	$(TEX) $(TEXFLAGS) $(texdoc)

# Build PDFs from Tikz diagrams
figures/%.pdf: figures/%.tex
	pdflatex -output-directory=figures/ $< 

# Build EPSs from PDFs
figures/%.eps: figures/%.pdf
	gs -q -dNOCACHE -dNOPAUSE -dBATCH -dSAFER -sDEVICE=eps2write -sOutputFile=$@ $<

# Clean
clean :
	find . -type f -regex ".*$(texdoc).*\.\(aux\|bbl\|bcf\|blg\|log\|png\|out\|toc\|lof\|lot\|count\)" -delete
	rm -f $(texdoc).pdf $(texdoc).run.xml $(texdoc)-blx.bib
