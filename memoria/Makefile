MAIN = main.tex

.PHONY: all clean
all:
	@echo "Compilando una vez"
	latexmk -f -pdf $(MAIN)
	@echo "Compiland por segunda vez"
	latexmk -f -pdf $(MAIN)

clean:
	rm -f main.a* main.b* main.f* main.l* main.o* main.p* main.r* main.thm main.toc