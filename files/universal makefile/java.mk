# uniwersalny makefile dla języka C++

JC = gcc
JFLAGS = -g

all : $(TARGET)

$(TARGET) : $(SRC)
	$(JC) $(CFLAGS) $(SRC)
