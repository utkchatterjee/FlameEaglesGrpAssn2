;; Mars Rover sample collection domain (STRIPS + typing only)
(define (domain mars-rover)
  (:requirements :strips :typing)

  ;; one type per kind of object
  (:types location rover bay rock drill)

  (:predicates
    (rover-at ?r - rover ?l - location)          ; rover is at a location
    (connected ?from ?to - location)             ; directed edge (two-way routes are listed both ways)
    (rock-at ?k - rock ?l - location)            ; rock lies at a location
    (drill-at ?d - drill ?l - location)          ; drill lies at a location
    (soft ?k - rock)                             ; static: can be collected directly
    (hard ?k - rock)                             ; static: needs the drill
    (has-drill ?r - rover ?d - drill)            ; rover carries the drill
    (bay-of ?b - bay ?r - rover)                 ; static: bay belongs to rover
    (bay-empty ?b - bay)                         ; bay is free (used instead of "not full")
    (in-bay ?k - rock ?b - bay))                 ; rock is stored in bay

  ;; move along a directed edge
  (:action move
    :parameters (?r - rover ?from ?to - location)
    :precondition (and (rover-at ?r ?from) (connected ?from ?to))
    :effect (and (rover-at ?r ?to) (not (rover-at ?r ?from))))

  ;; take the drill; it is never dropped, so the rover keeps it
  (:action pick-drill
    :parameters (?r - rover ?d - drill ?l - location)
    :precondition (and (rover-at ?r ?l) (drill-at ?d ?l))
    :effect (and (has-drill ?r ?d) (not (drill-at ?d ?l))))

  ;; collect a soft rock into an empty bay
  (:action collect-soft
    :parameters (?r - rover ?k - rock ?b - bay ?l - location)
    :precondition (and (rover-at ?r ?l) (rock-at ?k ?l) (soft ?k)
                       (bay-of ?b ?r) (bay-empty ?b))
    :effect (and (in-bay ?k ?b) (not (rock-at ?k ?l)) (not (bay-empty ?b))))

  ;; collect a hard rock: same as soft but the rover must hold a drill
  (:action collect-hard
    :parameters (?r - rover ?k - rock ?b - bay ?l - location ?d - drill)
    :precondition (and (rover-at ?r ?l) (rock-at ?k ?l) (hard ?k)
                       (has-drill ?r ?d) (bay-of ?b ?r) (bay-empty ?b))
    :effect (and (in-bay ?k ?b) (not (rock-at ?k ?l)) (not (bay-empty ?b))))

  ;; drop a stored rock at the rover's current location, freeing the bay
  (:action deposit
    :parameters (?r - rover ?k - rock ?b - bay ?l - location)
    :precondition (and (rover-at ?r ?l) (in-bay ?k ?b) (bay-of ?b ?r))
    :effect (and (rock-at ?k ?l) (bay-empty ?b) (not (in-bay ?k ?b))))
)
