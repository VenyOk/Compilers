% Лабораторная работа № 1.1. Раскрутка самоприменимого компилятора
% 18 февраля 2025 г.
% Вениамин Шемякин, ИУ9-62Б

# Цель работы
Целью данной работы является ознакомление с раскруткой самоприменимых компиляторов
 на примере модельного компилятора.

# Индивидуальный вариант
Компилятор P5. Сделать так, чтобы можно было использовать идентификаторы любой длины, 
но при этом символы идентификатора, начиная с одиннадцатого, не учитывались.


# Реализация

Различие между файлами `pcom.pas` и `pcom2.pas`:

```diff
--- pcom.pas    2025-02-18 01:02:48.812479100 +0300
+++ pcom2.pas   2025-02-18 16:00:46.945378900 +0300
@@ -324,7 +324,7 @@
    maxaddr    =  maxint;
    maxsp      = 39;  { number of standard procedures/functions }
    maxins     = 78;  { maximum number of instructions }
-   maxids     = 250; { maximum characters in id string (basically, a full line) }
+   maxids     = 10; { maximum characters in id string (basically, a full line) }
    maxstd     = 39;  { number of standard identifiers }
    maxres     = 35;  { number of reserved words }
    reslen     = 9;   { maximum length of reserved words }
@@ -1344,9 +1344,11 @@
       letter:
         begin k := 0; ferr := true;
           repeat
-            if k < maxids then
-             begin k := k + 1; id[k] := ch end
-            else if ferr then begin error(182); ferr := false end;
+            if k < 10 then
+              begin
+                k := k + 1;
+                id[k] := ch
+              end;
             nextch
           until chartp[ch] in [special,illegal,chstrquo,chcolon,
                                 chperiod,chlt,chgt,chlparen,chspace,chlcmt];
```

Различие между файлами `pcom2.pas` и `pcom3.pas`:

```diff
--- pcom2.pas   2025-02-18 16:00:46.945378900 +0300
+++ pcom3.pas   2025-02-18 16:14:19.532017300 +0300
@@ -1575,7 +1575,7 @@
 1:  fcp1 := fcp
   end (*searchsection*) ;

-  procedure searchidnenm(fidcls: setofids; var fcp: ctp; var mm: boolean);
+  procedure seearchidnenm(fidcls: setofids; var fcp: ctp; var mm: boolean);
     label 1;
     var lcp: ctp;
         disxl: disprange;
@@ -1604,7 +1604,7 @@
   procedure searchidne(fidcls: setofids; var fcp: ctp);
     var mm: boolean;
   begin
-    searchidnenm(fidcls, fcp, mm);
+    seearchidnenm(fidcls, fcp, mm);
     if mm then error(103)
   end (*searchidne*) ;

@@ -2062,16 +2062,16 @@
     function filecomponent(fsp: stp): boolean;
     var f: boolean;
       { tour identifier tree }
-      function filecomponentre(lcp: ctp): boolean;
+      function fiilecomponentre(lcp: ctp): boolean;
       var f: boolean;
       begin
         f := false; { set not file by default }
         if lcp <> nil then with lcp^ do begin
           if filecomponent(idtype) then f := true;
-          if filecomponentre(llink) then f := true;
-          if filecomponentre(rlink) then f := true
+          if fiilecomponentre(llink) then f := true;
+          if fiilecomponentre(rlink) then f := true
         end;
-        filecomponentre := f
+        fiilecomponentre := f
       end;
     begin
       f := false; { set not a file by default }
@@ -2081,7 +2081,7 @@
         pointer:  ;
         power:    ;
         arrays:   if filecomponent(aeltype) then f := true;
-        records:  if filecomponentre(fstfld) then f := true;
+        records:  if fiilecomponentre(fstfld) then f := true;
         files:    f := true;
         tagfld:   ;
         variant:  ;
@@ -2112,7 +2112,7 @@
         lcp1 := fwptr;
         fwptr := lcp1^.next;
         strassfv(id, lcp1^.name);
-        searchidnenm([types], lcp2, mm);
+        seearchidnenm([types], lcp2, mm);
         if lcp2 <> nil then lcp1^.idtype^.eltype := lcp2^.idtype
         else begin
           if fe then begin error(117); writeln(output) end;
@@ -2271,7 +2271,7 @@
             if sy = ident then
               begin
                 { find possible type first }
-                searchidnenm([types],lcp1,mm);
+                seearchidnenm([types],lcp1,mm);
                 { now set up as field id }
                 new(lcp,field); ininam(lcp);
                 with lcp^ do
```

# Тестирование

Тестовый пример:

```pascal
program test(output);
var 
  verylongidentifiervariable: integer;
begin
  verylongidentifiervariable := 42;     
  writeln(verylongidentif);         
end.
```

Вывод тестового примера на `stdout`

```
P5 Pascal interpreter vs. 1.0

Assembling/loading program
Running program

P5 Pascal compiler vs. 1.0


     1       40 program test(output);
     2       40 var
     3       40   verylongidentifiervariable: integer;
     4       44 begin
     5        3   verylongidentifiervariable := 42;
     6        7   writeln(verylongidentif);
     7       14 end.

Errors in program: 0

program complete
```

# Вывод
В ходе данной лабораторной работы мне удалось изменить код компилятора p5 
для другой работы с идентификаторами, а также раскрутить его. Также были частично
 восстановлены знания о паскале, которые были утеряны несколько лет назад...