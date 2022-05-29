(define (filter-lst fn lst)
  'YOUR-CODE-HERE
  (if (null? lst)
      nil
      (if (fn (car lst))
          (cons (car lst) (filter-lst fn (cdr lst)))
          (filter-lst fn (cdr lst)))))

; ;; Tests
(define (even? x) (= (modulo x 2) 0))

(filter-lst even? '(0 1 1 2 3 5 8))

; expect (0 2 8)
(define (interleave first second)
  'YOUR-CODE-HERE
  (cond 
    ((null? first)
     second)
    ((null? second)
     first)
    (else
     (cons (car first) (interleave second (cdr first))))))

(interleave (list 1 3 5) (list 2 4 6))

; expect (1 2 3 4 5 6)
(interleave (list 1 3 5) nil)

; expect (1 3 5)
(interleave (list 1 3 5) (list 2 4))

; expect (1 2 3 4 5)
(define (accumulate combiner start n term)
  'YOUR-CODE-HERE
  (if (eq? 0 n)
      start
      (accumulate combiner
                  (combiner start (term n))
                  (- n 1)
                  term)))

(define (find _set observe)
  (if (null?  _set)
      #f
      (if (= (car _set) observe)
          #t
          (find (cdr _set) observe))))

(define (memory)
  (begin (define _set nil)
         (lambda (observe)
           (if (find _set observe)
               #f
               (begin (set! _set (cons observe _set)) #t)))))

(define (no-repeats lst)
  'YOUR-CODE-HERE
  (begin (define fn (memory)) (filter-lst fn lst)))
