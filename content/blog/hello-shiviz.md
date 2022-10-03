---
title: "A ShiViz Hello World"
date: 2022-02-14 13:25:48 +0800
---

[ShiViz](https://bestchai.bitbucket.io/shiviz/) visualizes [space-time diagrams](https://www.cs.ubc.ca/~bestchai/papers/tosem20-shiviz.pdf), a succinct way to represent distributed system executions.

The examples on the site are all rather large, so here's a tiny Hello World example which illustrates the input format and basic ideas.

```
client1 "message 1 sent" {"client1":1}
client2 "message 2 sent" {"client2":1}
server "message 2 received" {"server":1, "client2":1}
server "message 1 sent received" {"client1":1, "server":2, "client2":1}
server "ack message 1" {"client1":1, "server":3, "client2":1}
client1 "internal" {"client1":2}
client1 "receive message 1 ack" {"client1":3, "server":3, "client2":1}
```

```regex
(?<host>\w+) "(?<event>.*)" (?<clock>\{.*\})
```

ShiViz takes unstructured log text as input, plus a regular expression with named groups to extract fields. The three fields above are the ones minimally needed; others may be added as metadata. `clock` is in JSON format.

Notably, there is no notion of messages being sent, only vector clocks, which are sufficient to causally order events. The size of the vector also does not need to be known upfront.
