MAIN = main.tex

.PHONY: all clean
all:
	@echo "Compilando por primera vez"
	latexmk -f -pdf $(MAIN)
	@echo "Compilando por segunda vez"
	latexmk -f -pdf $(MAIN)

clean:
	rm -f main.a* main.b* main.f* main.l* main.o* main.p* main.r* main.thm main.toc