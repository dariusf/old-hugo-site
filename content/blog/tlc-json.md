---
title: "Getting JSON out of TLC"
date: 2022-09-02 09:29:25 +0800
---

For my own sanity, here are all the ways of getting TLC to render a trace resulting from a property violation in JSON and their respective tradeoffs.

# tla2json

The simplest way is to pipe the TLC log through [tla2json](https://github.com/japgolly/tla2json).

This works at first glance and gets you started quickly, but you'll soon realise that tla2json [does not handle all of TLA+](https://github.com/tlaplus/tlaplus/issues/640#issuecomment-1029316841) (at the time of writing; traces produced from the Raft spec fail to parse for some reason I haven't investigated).

tla2json also does not guarantee that every TLA+ datatype is unambiguously represented in JSON. I have a [patch](https://github.com/dariusf/tla2json) which fixes this for sets, but there are surely more edge cases.

# -dumpTrace and POSTCONDITION

The [TLC docs](https://github.com/tlaplus/tlaplus/blob/master/general/docs/current-tools.md) seem to provide a nice solution: the `-dumpTrace` flag, which allows one to do:

```sh
./tlc spec.tla -dumpTrace json trace.json
```

Unfortunately, this doesn't work with `-simulate`, which is useful for exploring large specs.

Some [digging](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/TLC.java) reveals that `-dumpTrace` is implemented by adding a POSTCONDITION - a formula which is evaluated when model checking completes.
Thus one can achieve the same thing with [this](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tla2sany/StandardModules/_JsonTrace.tla):

```tla
EXTENDS TLC, TLCExt, Json

Post == JsonSerialize("trace.json", ToTrace(CounterExample))
```

```
POSTCONDITION Post
```

When `-simulate` isn't passed, TLC creates a [ModelChecker](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/tool/ModelChecker.java), which uses a [Worker](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/tool/Worker.java) to explore the state space, checking the postcondition at the end.
With `-simulate`, a [Simulator](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/tool/Simulator.java) is instead created, which spawns a [SimulationWorker](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/tool/SimulationWorker.java) that ignores postconditions.

Supporting this for `-simulate` is a [work-in-progress](https://github.com/tlaplus/tlaplus/issues/601).
There are many issues to consider for a robust semantics so this is entirely fair.

# Procedural INVARIANTs

A third way is to take advantage of the fact that invariants are ordinary TLA+ formulae, which can perform arbitrary side effects via operators implemented in Java.
This [trick](https://twitter.com/lemmster/status/1337264737516580867) further (ab)uses the short-circuiting of disjunction: if the invariant is false, we write a JSON trace to disk, then exit.

So far this has been the most flexible and robust solution, at the cost of requiring additional setup.
One can also use a TLA+ operator to transform the generated trace before serialiazing it.

# Apalache

A final way is to use Apalache, which already outputs JSON in a specified [trace format](https://apalache.informal.systems/docs/adr/015adr-trace.html). Apalache imposes additional requirements on models so this may or may not be usable.
