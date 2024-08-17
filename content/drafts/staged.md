---
# title: "Staged logic"
title: "Verifying effectful higher-order programs with staged logic"
date: 2024-08-16 11:59:39 +0800
math: true
---

<!-- (23 Aug 2024) -->
<!-- (13 Sep 2024) -->

*Text version of a talk given at the [NUS PLSE Seminar](https://nus-plse.github.io/seminars.html) and [FM 2024](https://www.fm24.polimi.it/?page_id=612) in Milan.*

- [Effectful higher-order functions](#effectful-higher-order-functions)
- [Specifying higher-order functions today](#specifying-higher-order-functions-today)
  - [Example 1: mutating the list](#example-1-mutating-the-list)
  - [Example 2: stronger precondition](#example-2-stronger-precondition)
  - [Example 3: effects outside metalogic](#example-3-effects-outside-metalogic)
- [Staged logic](#staged-logic)
  - [Effectful placeholders](#effectful-placeholders)
  - [Recursion](#recursion)
  - [Re-summarization](#re-summarization)
  - [Compaction via biabduction](#compaction-via-biabduction)
- [Solutions to the problematic examples](#solutions-to-the-problematic-examples)
  - [Example 1](#example-1)
  - [Example 2](#example-2)
  - [Example 3](#example-3)
- [Conclusion](#conclusion)

# Effectful higher-order functions

Programs written in mainstream languages today are rife with *effectful higher-order functions*:
functions which take other functions as arguments, where these arguments may use primitive side effects, such as state, exceptions, or algebraic effects.

In everyday programming, it is not unusual to do things like
use state in a closure to avoid traversing a list twice,
or use a continuation to return solutions when backtracking, and allow the continuation to throw an exception to end the search efficiently.
Using a modern I/O library makes effects pervasive.

Reasoning about such functions does not seem particularly difficult - we certainly do it informally every time we write such programs!
However, verifier support for such functions varies greatly:

- *Most automated verifiers require function arguments to be pure*. Examples include Dafny, Why3, and Cameleer. This is because they lift these functions into the underlying logic (usually the first-order logic of SMT) and are restricted by what can be expressed in it.
- *Other automated verifiers rely on type system guarantees*. Examples include Prusti and Creusot, which target Rust and can exploit the fact that closures can maintain invariants over their captured state via ownership.
- *Other verifiers are interactive*. Examples include Iris, CFML, and Steel/Pulse (F*). In practice, this means that they support varying levels of automation, from none at all to full automation in specific cases, with the tradeoff being that they are more expressive.

Even when higher-order functions are supported, they tend to be specified *imprecisely*. We'll see an example of this shortly.

The question we're concerned with in this work is: is there a *precise* and *general* way to support effectful higher-order functions in *automated* program verification?

# Specifying higher-order functions today

$\gdef\m#1{\mathit{#1}}$

$\gdef\foldr{\m{foldr}}$
$\gdef\xs{\m{xs}}$
$\gdef\ys{\m{ys}}$
$\gdef\res{\m{res}}$
$\gdef\inv{\m{Inv}}$
$\gdef\islist{\m{isList}}$
$\gdef\list{\m{List}}$
$\gdef\emp{\m{emp}}$

$\gdef\req#1{\mathbf{req}\ #1}$
$\gdef\ens#1{\mathbf{ens}\ #1}$

We'll use the classic $\foldr$ function as a running example.

```ocaml
let foldr f a l =
  match l with
  | [] => a
  | h :: t =>
    f h (foldr f a t)
```

$f$ is *effectful* - it may have state, exceptions, or algebraic effects.
$\foldr$ is hence an *effectful higher-order function*.

How can we specify $\foldr$ in a way that allows the following client to be verified?

```ocaml
let count = ref 0 in
foldr (fun c t -> incr count; c + t) 0 xs
```

[The conventional way to do it in a modern program logic, like Iris](https://iris-project.org/tutorial-pdfs/lecture6-foldr.pdf), is as follows.

$$
\forall P, \inv, f, \xs, l. \left\{ \begin{array}{l}
    (\forall x, a', \ys.\ \{P\ x * \inv\ \ys\ a'\}\ f(x, a')\ \{r.\ \inv\ (x::\ys)\ r\}) \\
    *\ \islist\ l\ \xs * \m{all}\ P\ \xs * \inv\ []\ a
 \end{array} \right\} \\
 \foldr\ f\ a\ l \\
 \{r.\ \islist\ l\ \xs * \inv\ \xs\ r \}
$$

1. A nested triple is used to specify $f$, as some knowledge of it is needed to reason about the call to it in $\foldr$.
2. The specification of $\foldr$ is parameterized over an *invariant* or *abstract property* $\inv$, which relates the content of the input list $\xs$ with the result of the fold. Its purpose is to *summarize* what $\foldr$ does.
3. As $f$ is called within $\foldr$ and its result contributes to that of $\foldr$, it must preserve the invariant - assuming the invariant holds of the tail $t$ and the result of the recursive call $a'$, $f$ must reestablish it for $l$ and its result $r$. The invariant also serves as a means of summarizing the behavior of $f$.
4. Anticipating that some clients may want to operate only on certain kinds of lists, the specification is further parameterized over a unary predicate $P$. A precondition $\m{all}\ P\ \xs$, which must be proved at each call site, allows $f$ to then rely on $P\ x$ in its precondition.
5. A *shape predicate* $\islist$ relating the structure $l$ to its content $\xs$ appears in both pre- and postcondition. This is to say that $\foldr$ should not change the list.

This specification elegantly solves the problem, but we argue that it is *imprecise*.
In particular, while it may be used to verify the client we provided earlier (using a separation logic invariant to relate the value of $\m{count}$ and $t$, and an identity $P$), there are many clients that *cannot be verified* using it *without significant changes*.

The [Iris tutorial](https://iris-project.org/tutorial-pdfs/iris-lecture-notes.pdf) says as much (pg 35):

> Different clients may instantiate foldr with some very different functions, hence it can be hard to give a specification for f that is reasonable and general enough to support all these choices.

The problem is that due to the use of abstract properties, this specification *commits prematurely* to a *summary* or *abstraction* of $f$'s behavior.
Due to the undue strengthening of the precondition of $\foldr$, *precision* is lost.
This leads to the symptom that the abstraction may not be precise enough for a given client.

We'll look at three examples of such clients.

## Example 1: mutating the list

Suppose we allowed $f$ to mutate the list.

```ocaml
let foldr_ex1 l = foldr (fun x r -> let v = !x in
                                    x := v+1; v+r) l 0
```

This is not allowed by the shape predicate in the postcondition, but suppose we changed it to $\islist\ l\ \xs'$.

Now the problem is that $\inv\ \xs\ r$ tells us nothing about $\xs'$.
We would have to add $\xs'$ as a parameter at least, and the client would have to relate it to $x$.

While this results in a more general specification, it is also cluttered with more anticipated client use cases.
The problem is really that the use of invariants requires us to *commit to a parameterization*.

## Example 2: stronger precondition

Suppose we would like to pass a function argument which relies on a property concerning intermediate folded results.

```ocaml
let foldr_ex2 l = foldr (fun x r -> assert(x+r>=0); x+r) l 0
```

Again, because we committed to a parameterization,
we can't use $P$ to strengthen the precondition of $f$,
as $P$ only constrains individual elements and cannot be used to talk about the suffixes of the list.

## Example 3: effects outside metalogic

This example illustrates a different problem with invariants: suppose we allowed the function to throw an exception.

```ocaml
let foldr_ex3 l = foldr (fun x r -> if x>=0 then x+r
                                    else raise Exc()) l 0
```

When we use an invariant to summarize the behavior of $\foldr$ or $f$,
we are really trying to abstract their behavior into a predicate of the underlying logic.
The behavior we can describe is now limited by the expressiveness of that logic.

For example, as mentioned earlier, many verifiers do not handle closures because they lift function arguments into the pure, first-order logic of SMT.

Here, separation logic allows state, but says nothing about exceptions/effects, as $f$ must return a value to preserve the invariant.
One would need some kind of encoding or [protocol](https://devilhena-paulo.github.io/thesis/de-vilhena-thesis.pdf), a fundamentally different specification.


<!-- ## Ordering

```ocaml
let hist = ref "" in
compose (fun _ -> hist := !hist ^ "a")
  (fun _ -> hist := !hist ^ "b") ()
```
-->

# Staged logic

Taking a step back, why did we have to abstract away the behavior of $f$ to begin with?

The problem was that it was difficult to represent (1) unknown higher-order effectful calls and (2) ordering of effects precisely in pre/post specifications.

Our idea is thus to generalize triples with those ingredients.
We extend the "language" of triples (where $\mathbf{req}$ and $\mathbf{ens}$ are viewed as atomic predicates) with two contructs: sequencing and (un)interpreted relations.
We call $\varphi$ a *staged formula*, for reasons that will be explained shortly.
$\sigma{\wedge}\pi$ is a symbolic-heap separation logic formula.

$$\varphi ::= \req{\sigma{\wedge}\pi} \mid \ens{\sigma{\wedge}\pi} \mid \varphi; \varphi \mid f(x, r) \mid \exists x.\ \varphi \mid \varphi \vee \varphi$$

What is the semantics of such formulae? We defer this question to [our paper](https://raw.githubusercontent.com/hipsleek/Heifer/StagedSL/docs/FM2024_TR.pdf), but a first approximation is the following generalization, starting from the (partial correctness) semantics of Hoare triples.

$$
\begin{align*}
\{ P \}\ e\ \{ Q \} \equiv & \ \forall s, s'. \langle s, e \rangle ⟶ \langle s', v \rangle \wedge P\ s \Rightarrow Q\ v\ s' \\
\{ \ens{\m{emp}} \}\ e\ \{ \varphi \} \equiv & \ \forall s, s'. \langle s, e \rangle ⟶ \langle s', v \rangle \Rightarrow \langle s \rightsquigarrow s', v \rangle \vDash \varphi
\end{align*}
$$

Where we previously had a precondition constraining $s$ and a postcondition constraining $s'$ and the result $v$, we now have a staged formula constraining the same three things.

The ingredients of our solution consist of the following.

1. Sequencing and uninterpreted relations
2. Recursive formulae
3. Re-summarization of recursion (lemmas)
4. Compact sequences of pre/post stages using biabduction

The insight is that these allow us to *defer abstraction* until appropriate.

We go over each in turn using examples, then present solutions to the examples.

## Effectful placeholders

Consider the following program, which manipulates the heap and has a call to an unknown function $f$.

```ocaml
let hello f x y =
  x := !x + 1;
  let r = f y in
  let r2 = !x + r in
  y := r2;
  r2
```

Here is a possible *staged specification* for it.

$$
\begin{array}{l}
\m{hello}(f, x, y, res) = \\
\quad \exists a.\ \req{x{\mapsto}a}; \ens{x{\mapsto}a{+}1} \\
\quad \exists r.\ f(y, r); \\
\quad \exists b.\ \req{x{\mapsto}b * y{\mapsto}\_}; \\
\quad \phantom{\exists b.\ } \ens{x{\mapsto}b * y{\mapsto}\m{res}{\wedge}\m{res}{=}b{+}r} \\
\end{array}
$$

- Uninterpreted relations allow us to represent unknown function parameters.
- Sequencing allows them to serve as *placeholders* for effects.
- Stateful behavior is otherwise *compacted* into a single $\textbf{req}$/$\textbf{ens}$ pair $f$ may be seen as *stratifying* the behavior of $\m{hello}$ into two *stages* under [compaction](#compaction-via-biabduction), hence the name "staged formulae", in allusion to *staged programming*.
- Note that we can no longer assume anything about $y$ after the call to $f$, as it is passed as an argument.
- We also cannot assume anything about $x$ after the call to $f$! It is possible that $x$ may have been captured by $f$. Thus it may have a potentially different value after, $b$.
- This specification assumes that $x$ and $y$ are not aliased. Details on how to relax this assumption in the paper.

Sequencing of multiple effectful functions can be represented directly.

```ocaml
let compose f g x = f (g x)
```

$$
\m{compose}(f, g, x, \m{res}) = \exists r.\ g(x, r); f(r, \m{res})
$$

## Recursion

Recursive specifications naturally represent recursive programs.

<!-- under a least fixed point interpretation -->

```ocaml
let foldr f a l =
  match l with
  | [] => a
  | h :: t =>
    f h (foldr f a t)
```

$$
\begin{array}{l}
\foldr(f, a, l, \m{res}) = \\
\quad \phantom{\vee\ } \ens{l{=}[]{\wedge}\m{res}{=}a} \\
\quad \vee\ \exists r, l_1.\ \ens{l{=}x{::}l_1}; \foldr(f, a, l_1, r); f(x, r, \m{res})
\end{array}
$$

Most importantly, the call to $f$ can be represented directly, without abstraction.

This specification looks very much like the program, because there is no state that could benefit from being expressed with separation logic.
However, it is still an abstraction of the program.

Comparing this to the previous specification, this time expressed as a single $\mathbf{req}$/$\mathbf{ens}$ pair in staged logic,

$$
\begin{array}{l}
\foldr(f, a, l, \m{res}) = \\
\quad \exists P, \inv, \xs.\ \req{\m{List(l, \xs)} * \inv([], a) \wedge \m{all}(P, \xs)} \\
\qquad \wedge f(x, a', r) \sqsubseteq (\exists ys.\ \req{\inv(\ys, a') \wedge P(x)}; \ens{\inv(x{::}\ys, r)}); \\
\quad \ens{\m{List}(l, \xs) * \inv(\xs, \m{res})}
\end{array}
$$

we see that leaving the recursion in the specification *before* we are aware of what clients expect (and thus, what kind of abstraction is appropriate) is what allows staged specifications to be more precise.

<!-- not precise when it comes to concurrency due to summary of stateful behavior, which may no longer be atomic -->

## Re-summarization

What kind of properties can we use staged logic to prove, and how do we do it?

First, we add a *subsumption* relation, which is true if a staged formula entails another staged formula.

$$\pi ::= ... \mid \varphi \sqsubseteq \varphi$$

Given a use of $\foldr$ such as the following,

```ocaml
let foldr_sum xs init =
  let g c t = c + t in
  foldr g xs init
```

We might wish to prove a functional correctness property, such as the fact that $\m{foldr\_sum}$ computes the sum of $\xs$ plus $\m{init}$.

This can be stated as follows:

$$
\forall \xs, \m{init}, \res.\ \m{foldr\_sum}(\xs, \m{init}, \res) \sqsubseteq \exists r.\ \ens{\res{=}r{+}\m{init}{\wedge}\m{sum}(\xs,r)}
$$

where $\m{foldr\_sum}$ is a staged formula representing the above program (derived from the program automatically in a syntax-directed manner), and $\m{sum}$ is a recursive pure function.

$$
\begin{array}{l}
\m{sum}(\xs,\res) = \\
\phantom{\vee\ } (xs{=}[]{\wedge}\res{=}0) \\
\vee\ (\exists x, l_1, r.\ l=x{::}l_1 \wedge \m{sum}(l_1, r)\wedge \res{=}x{+}r)
\end{array}
$$

In the paper, we define a set of syntactic proof rules for reducing $\sqsubseteq$-entailments (modulo compaction) into pure proof obligations,
which can be discharged using SMT.
This particular proof can be done automatically with an inferred (or provided, in general) induction hypothesis.

The above entailment can be seen as a lemma in staged logic.
We also call this *re-summarization* because
it is at this point that we abstract away the recursion from the relatively low-level staged specification,
and produce a non-recursive summary.

What do we gain from using staged logic here, one might ask, since $\m{foldr_sum}$ is pure, and the proof can also be done automatically in a verifier like Dafny, with its heuristics for synthesizing induction hypotheses?

What we gain is that we can handle effectful higher-order functions. Consider the following variation of $\m{foldr\_sum}$, which uses a closure.

```ocaml
let foldr_sum_state x xs init =
  let g c t = x := x + 1; c + t in
  foldr g xs init
```

The proof of the following entailment can also be done automatically, in a very similar manner,
because of how staged logic can naturally express sequencing of effects.

$$
\begin{array}{rl}
& \forall \xs, \m{init}, \res.\ \m{foldr\_sum\_state}(x, \xs, \m{init}, \res) \\
\sqsubseteq & \exists i,r.\ \req{x{\mapsto}i}; \ens{x{\mapsto}i{+}r{\wedge}\res{=}r{+}\m{init}{\wedge}\m{sum}(\xs,r)}
\end{array}
$$

## Compaction via biabduction

*Compaction* allows us to have the expressiveness of stages, but also the *succinctness* of triples when the extra expressiveness is not needed.
In short, it allows any staged formula to always be transformed into the following normal form.

$$
\big(\req{\sigma{\wedge}\pi}; \ens{\sigma{\wedge}\pi}; f(x, r); \big)^* \req{\sigma{\wedge}\pi}; \ens{\sigma{\wedge}\pi}
$$

We'll illustrate it by example on the first example we saw.

$$
\begin{array}{l}
\m{hello}(f, x, y, res) = \\
\quad \exists a.\ \req{x{\mapsto}a}; \ens{x{\mapsto}a{+}1} \\
\quad \exists r.\ f(y, r); \\
\quad \exists b.\ \req{x{\mapsto}b * y{\mapsto}\_}; \\
\quad \phantom{\exists b.\ } \ens{x{\mapsto}b * y{\mapsto}\m{res}{\wedge}\m{res}{=}b{+}r} \\
\end{array}
$$

This specification is already in normal form, but suppose we find out an interpretation for $f$, for example, from the following client.

```ocaml
let z = ref 0 in
let y = ref 1 in
hello (fun _ -> incr z; 0) z y
```

Now we have the following interpretation for $f$.

$$f(\_,\res) = \exists c.\ \req{z{\mapsto}c}; \ens{z{\mapsto}c{\wedge}\res{=}0}$$

Unfolding $f$ in $\m{hello}$ (and doing some renaming),

$$
\begin{array}{l}
\m{hello}(f, z, y, res) = \\
\quad \exists a.\ \req{z{\mapsto}a}; \boxed{\ens{z{\mapsto}a{+}1}} \\
\quad \exists r,c.\ \boxed{\req{z{\mapsto}c}}; \ens{z{\mapsto}c{\wedge}r{=}0} \\
\quad \exists b.\ \req{z{\mapsto}b * y{\mapsto}\_}; \\
\quad \phantom{\exists b.\ } \ens{z{\mapsto}b * y{\mapsto}\m{res}{\wedge}\m{res}{=}b{+}r} \\
\end{array}
$$

This specification is not in normal form.
Focusing on the boxed portions, we see an $\mathbf{ens}$ followed by a $\mathbf{req}$.
We can apply the following normalization rule.

$$
\frac{D_A * D_1 \vdash D_2 * D_F}{\ens{D_1};\req{D_2} \Rightarrow \req{D_A}; \ens{D_F}}
$$

In other words, it suffices to solve a [biabductive entailment](https://fbinfer.com/docs/separation-logic-and-bi-abduction/) to infer a pair of *frame* (in the separation logic sense) and *antiframe* (an additional condition $D_A$ required for $D_1$ to entail $D_2$).
We can then use these in place of the original conditions, "swapping" them around, or "pushing" the $\mathbf{req}$ "through" the $\mathbf{ens}$.

For this example, one solution is:

$$
z{\mapsto}a{+}1 * (a{+}1{=}c) \vdash z{\mapsto}c * \emp
$$

We can thus transform $\m{hello}$ as follow.

$$
\begin{array}{l}
\m{hello}(f, z, y, res) = \\
\quad \exists a.\ \boxed{\req{z{\mapsto}a}; \exists c.\ \req{a{+}1{=}c}} \\
\quad \exists r.\ \boxed{\ens{\emp}; \ens{z{\mapsto}c{\wedge}r{=}0}} \\
\quad \exists b.\ \req{z{\mapsto}b * y{\mapsto}\_}; \\
\quad \phantom{\exists b.\ } \ens{z{\mapsto}b * y{\mapsto}\m{res}{\wedge}\m{res}{=}b{+}r} \\
\end{array}
$$

Now we have two consecutive $\mathbf{req}$ and $\mathbf{ens}$ stages.
We can normalize them using the following rules.

$$
\req{D_1}; \req{D_2} \Rightarrow \req{(D_1 * D_2)} \\
\ens{D_1}; \ens{D_2} \Rightarrow \ens{(D_1 * D_2)}
$$

Now we have this, and again we have another $\mathbf{ens}$/$\mathbf{req}$ pair.

$$
\begin{array}{l}
\m{hello}(f, z, y, res) = \\
\quad \exists a,c.\ \req{z{\mapsto}a * a{+}1{=}c}; \\
\quad \exists r.\ \boxed{\ens{z{\mapsto}c{\wedge}r{=}0}} \\
\quad \exists b.\ \boxed{\req{z{\mapsto}b * y{\mapsto}\_}}; \\
\quad \phantom{\exists b.\ } \ens{z{\mapsto}b * y{\mapsto}\m{res}{\wedge}\m{res}{=}b{+}r} \\
\end{array}
$$

Here's the solution...

$$
z{\mapsto}c{+}1{\wedge}r{=}0 * (c{+}1{=}b{\wedge}y{\mapsto}\_) \vdash z{\mapsto}b * y{\mapsto}\_ * r{=}0
$$

... and final state, after one more round of simplification (not shown).

$$
\begin{array}{l}
\m{hello}(f, z, y, res) = \\
\quad \exists a,c.\ \req{z{\mapsto}a * y{\mapsto}\_ \wedge a{+}1{=}c{\wedge}c{+}1{=}b}; \\
\quad \exists b.\ \ens{z{\mapsto}b * y{\mapsto}\m{res}{\wedge}\m{res}{=}b}
\end{array}
$$

Now the specification for this call to $\m{hello}$ is in normal form, and we can use it for subsequent reasoning.
We see also that it precisely summarizes the aggregate behavior of this call, including the state changes.

Compaction can be seen as a normalization procedure for (programs represented as) staged formulae,
but also as a means of exploiting the *specification inference* capabilities of biabduction in a verification setting, to automate derivation of specifications and allow the user to focus only on the nontrivial ones.

# Solutions to the problematic examples

Going back to the examples we highlighted previously,
how can we tackle them using staged logic,
and how does the approach differ from the invariant-based way of writing specifications given in the introduction?

All the following assume the specification for $\foldr$ is as given in the previous section.
Crucially, none have to change it to solve all problems.

## Example 1

```ocaml
let foldr_ex1 l = foldr (fun x r -> let v = !x in
                                    x := v+1; v+r) l 0
```

An invariant to tell us about the content of the list is not needed.
Instead, we describe the final content of the list using another pure, recursive function (mapinc), alongside the result.
The list is described using a shape predicate.

$$
\begin{array}{l}
\m{mapinc}(\xs, \ys) = \\
\quad \phantom{\vee\ } (\xs{=}[]{\wedge}\ys) \\
\quad \vee\ (\exists x, \xs_1, \ys.\ \xs{=}x{::}\xs_1{\wedge}\ys{=}(x{+}1){::}\ys_1) \wedge \m{mapinc}(\xs_1, \ys_1) \\ \\
\list(l, \m{rs}) = \\
\quad \phantom{\vee\ } (\emp{\wedge}l{=}[]) \\
\quad \vee\ (\exists x, \m{rs}_1, l_1.\ x{\mapsto}r * \list(l_1,\m{rs}_1){\wedge}l{=}x{::}l_1 {\wedge} \m{rs}{=}r{::}\m{rs}_1)
\end{array}
$$

We can then prove

$$
\begin{array}{rl}
& \m{foldr\_ex1}(l,\res) \\
\sqsubseteq & \exists \xs, \ys.\ \req{\list(l,\xs)}; \ens{\list(l,\ys){\wedge}\m{mapinc}(\xs, \ys){\wedge}\m{sum}(\xs, \res)}
\end{array}
$$

## Example 2

```ocaml
let foldr_ex2 l = foldr (fun x r -> assert(x+r>=0); x+r) l 0
```

To enable the assertion in the function argument to be proved, we explicate the assumption that all suffix-sums of the list are positive using the following pure function.

$$
\begin{array}{l}
\m{allSPos}(l) = \\
\phantom{\vee\ } (l{=}[]) \\
\vee\ (\exists x, r, l_1.\ l=x{::}l_1 \wedge \m{allSPos}(l_1)\wedge \m{sum}(l,r) \wedge r{\geq}0)
\end{array}
$$

We can then prove

$$
\m{foldr\_ex2}(l,\res) \sqsubseteq \req{\m{allSPos}(l)}; \ens{\m{sum}(l,\res)}
$$

## Example 3

```ocaml
let foldr_ex3 l = foldr (fun x r -> if x>=0 then x+r
                                    else raise Exc()) l 0
```

An exception can be modelled as an *interpreted* relation (more on the semantics of handlers in our ICFP 2024 paper).

Given a pure function to describe lists containing only positive elements,

$$
\begin{array}{l}
\m{allPos}(l) = \\
\phantom{\vee\ } (l{=}[]) \\
\vee\ (\exists x, l_1.\ l=x{::}l_1 \wedge \m{allPos}(l_1)\wedge r{\geq}0)
\end{array}
$$

we can give a precise description of the conditions under which an exception is thrown via the following entailment.

$$
\m{foldr\_ex3}(l,\res) \sqsubseteq \ens{\m{allPos}(l){\wedge}\m{sum}(l,\res) \vee \ens{\neg\m{allPos}(l)}; \m{Exc}()}
$$

We could go even further and describe the prefix of elements which must be positive, if the exception carried that information to its handler.

The underlying logic is still symbolic-heap separation logic; we do not delegate effects to it,
yet can describe programs performing arbitrary (algebraic) effects.

# Conclusion

We have described *staged logic*, a generalization of Hoare triples that is particularly effective at specifying effectful higher-order programs.
It forms the basis of a new verification methodology based on the following ideas.

1. Sequencing and uninterpreted relations
2. Recursive formulae
3. Re-summarization of recursion (lemmas)
4. Compact sequences of pre/post stages using biabduction

All the ingredients together enable a strongest-postcondition-like workflow where,
given a program and an entailment about a property it should satisfy,
a staged formula is derived from the program, and the entailment is automatically proved.

Since staged logic generalizes Hoare logic,
one can easily "fall back" to triples in cases where the increased expressiveness of stages is not needed,
and employ abstraction, invariants, and all the other techniques which have been developed for program proofs.
There is no need to always specify programs as disjunctions of paths, or always capture the ordering of every function call and effect,
however the crucial thing is that *the option to do so is available* where it makes specifications for certain kinds of programs more natural.

Check out [the paper](https://raw.githubusercontent.com/hipsleek/Heifer/StagedSL/docs/FM2024_TR.pdf) for the details.

These ideas have been implemented in a prototype verifier called [Heifer](https://github.com/hipsleek/heifer), which we hope will grow into a practical verification tool for real programs.