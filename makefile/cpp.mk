# uniwersalny makefile dla języka C++

CC = g++
CFLAGS = -Wall -g

OBJ = $(SRC:.cpp=.o)

all : $(TARGET)

$(TARGET) : $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

.cpp.o:
	$(CC) $(CFLAGS) -c $<  -o $@
