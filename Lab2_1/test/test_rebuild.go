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
