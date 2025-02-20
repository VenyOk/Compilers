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
