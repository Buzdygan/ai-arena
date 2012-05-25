# uniwersalny makefile dla języka PYTHON

all : $(SRC)
	python -m py_compile $(SRC)
	cp $(SRC) $(TARGET)
