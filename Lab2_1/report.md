% Лабораторная работа № 2.1. Синтаксические деревья
% 19 февраля 2025 г.
% Вениамин Шемякин, ИУ9-62Б

# Цель работы
Целью данной работы является изучение представления синтаксических деревьев в памяти компилятора и 
приобретение навыков преобразования синтаксических деревьев.

# Индивидуальный вариант
Подсчёт, сколько раз в ходе работы программы вызывались сопрограммы.

# Реализация

Демонстрационная программа:

```go
package main

import (
	"fmt"
	"time"
)

var count int

func main() {
	go func() {
		sayHello()
	}()
	go func() {
		sayGoodbye()
	}()
	time.Sleep(1 * time.Second)
	fmt.Println("Total goroutines launched:", count)
}

func sayHello() {
	fmt.Println("Hello")
}

func sayGoodbye() {
	fmt.Println("Goodbye")
}

```

Программа, осуществляющая преобразование синтаксического дерева:

```go
package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"os"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Println("usage: transform <filename.go>")
		return
	}

	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments)
	if err != nil {
		fmt.Printf("Errors in %s: %v\n", os.Args[1], err)
		return
	}

	modifyGoroutines(file)

	writer, err := os.Create("test/test_rebuild.go")
	if err != nil {
		fmt.Printf("Error creating file: %v\n", err)
		return
	}
	defer writer.Close()

	if err := format.Node(writer, fset, file); err != nil {
		fmt.Printf("Formatter error: %v\n", err)
	}

	// ast.Fprint(os.Stdout, fset, file, nil)
}

func modifyGoroutines(file *ast.File) {
	ast.Inspect(file, func(node ast.Node) bool {
		if goStmt, ok := node.(*ast.GoStmt); ok {
			incrementStmt := &ast.IncDecStmt{
				X:   ast.NewIdent("count"),
				Tok: token.INC,
			}

			blockStmt := &ast.BlockStmt{
				List: []ast.Stmt{
					incrementStmt,
					&ast.ExprStmt{X: goStmt.Call},
				},
			}

			goStmt.Call = &ast.CallExpr{
				Fun: &ast.FuncLit{
					Type: &ast.FuncType{
						Params:  &ast.FieldList{},
						Results: &ast.FieldList{},
					},
					Body: blockStmt,
				},
			}
		}
		return true
	})
}

```

# Тестирование

Результат трансформации демонстрационной программы:

```go
package main

import (
	"fmt"
	"time"
)

var count int

func main() {
	go func() {
		count++
		func() {
			sayHello()
		}()
	}()
	go func() {
		count++
		func() {
			sayGoodbye()
		}()
	}()
	time.Sleep(1 * time.Second)
	fmt.Println("Total goroutines launched:", count)
}

func sayHello() {
	fmt.Println("Hello")
}

func sayGoodbye() {
	fmt.Println("Goodbye")
}

```

Вывод тестового примера на `stdout` (если необходимо)

```
Goodbye
Hello
Total goroutines launched: 2
```

# Вывод
В ходе данной лабораторной работы я научился работать с синтаксическими деревьями в языке Go, 
а также трансформировать их для решения определенной задачи.