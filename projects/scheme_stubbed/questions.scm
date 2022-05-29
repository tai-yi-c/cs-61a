(define (caar x) (car (car x)))

(define (cadr x) (car (cdr x)))

(define (cdar x) (cdr (car x)))

(define (cddr x) (cdr (cdr x)))

; Some utility functions that you may find useful to implement
(define (zip pairs) 
    'replace-this-line
    (define (combine lst1 lst2)
        (if (null? lst1)
            nil
            (if (list? (car lst1))
                (cons (append (car lst1) (list (car lst2))) (combine (cdr lst1) (cdr lst2)))
                (cons (append (list (car lst1)) (list (car lst2))) (combine (cdr lst1) (cdr lst2)))
                )
            
            )
        )
    
    (define (helper zipped rest)
        (if (null? rest)
            zipped
            (helper (combine zipped (car rest)) (cdr rest))
            )
        )
    (helper (car pairs) (cdr pairs))
    )

; ; Problem 5
; ; Returns a list of two-element lists
(define (-enumerate s rank)
  (if (null? s)
      nil
      (cons (cons rank (cons (car s) nil)) (-enumerate (cdr s) (+ rank 1)))))

(define (enumerate s) 
  ; BEGIN PROBLEM 5
  'replace-this-line
  (-enumerate s 0))

; END PROBLEM 5
; ; Problem 6
; ; Merge two lists LIST1 and LIST2 according to COMP and return
; ; the merged lists.
(define (merge comp list1 list2)
  ; BEGIN PROBLEM 6
  'replace-this-line
  (cond
        ((null? list1) list2)
        ((null? list2) list1)
        (else 
              (if (comp (car list1) (car list2)) 
                  (cons (car list1) (merge comp (cdr list1) list2))
                  (cons (car list2) (merge comp list1 (cdr list2)))
                  )
              )
        )
  
  )

; END PROBLEM 6
(merge < '(1 5 7 9) '(4 8 10))

; expect (1 4 5 7 8 9 10)
(merge > '(9 7 5 1) '(10 8 4 3))

; expect (10 9 8 7 5 4 3 1)
; ; Problem 7
(define (nondecreaselist s)
  ; BEGIN PROBLEM 17
  'replace-this-line
  (define (helper last so-far last-group s)
        (if (null? s) 
            (if (null? last-group)
                so-far
                (append so-far (list last-group))
                )
            (let ((cur (car s))) 
                (if (or (> cur last) (= cur last))
                    (helper cur so-far (append last-group (list cur))  (cdr s))
                    (helper cur (append so-far (list last-group)) (list cur) (cdr s))
                    )
                )
            )
             
        )
    (helper 0 nil nil s)
    )
; END PROBLEM 17
; ; Problem EC
; ; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
  (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))

(define define? (check-special 'define))

(define quoted? (check-special 'quote))

(define let? (check-special 'let))


(define (deal-params params)
    (if (null? params)
        nil
        (cons (let-to-lambda (car params)) (deal-params (cdr params)))
        )
    )
(define (unzip lsts)
    (if (null? lsts)
        (list nil nil)
        (BEGIN
            (define cur-f (car (car lsts)))
            (define cur-l (car (cdr (car lsts))))
            (define ret (unzip (cdr lsts)))
            (list (cons cur-f (car ret)) (cons cur-l (car (cdr ret))))
            )
        )
    )
; ; Converts all let special forms in EXPR into equivalent forms using lambda
(define (let-to-lambda expr)
  (cond 
    ((atom? expr)
     ; BEGIN PROBLEM EC
     'replace-this-line
     expr
     ; END PROBLEM EC
    )
    ((quoted? expr)
     ; BEGIN PROBLEM EC
     'replace-this-line
     expr
     ;(let-to-lambda (cdr expr))
     ; END PROBLEM EC
    )
    ((or (lambda? expr) (define? expr))
     (let ((form (car expr))
           (params (cadr expr))
           (body (cddr expr)))
       ; BEGIN PROBLEM EC
       'replace-this-line
       (define new-body (let-to-lambda body))
       (append (list form params) new-body)
       ; END PROBLEM EC
     ))
    ((let? expr)
     (let ((values (cadr expr))
           (body (cddr expr)))
       ; BEGIN PROBLEM EC
       'replace-this-line
       (define names-asgn-exprs (unzip values))
       (define names (car names-asgn-exprs))
       (define asgn-exprs (cadr names-asgn-exprs))
       (cons (append (list 'lambda  names) (let-to-lambda body)) (let-to-lambda asgn-exprs))
       ; END PROBLEM EC
     ))
    (else
     ; BEGIN PROBLEM EC
     (if (list? expr)
         (begin
             (define first-expr (car expr))
             (define rest-expr (cdr expr))
             (if (list? first-expr)
                 (if (let? first-expr)
                     (define first-expr-handled (let-to-lambda first-expr))
                     (define first-expr-handled (cons (car first-expr) (deal-params (cdr first-expr))))
                     )
                 (define first-expr-handled first-expr)
                 )
             
             (cons first-expr-handled (let-to-lambda rest-expr))
            )
          expr
         )
     ; END PROBLEM EC
    )))
