---
layout: page
title: Resume
permalink: /resume/
description: 'My resume'
---

<style>

  p.company {
    border-bottom: 1px solid var(--text-color);
    font-weight: bold;
    margin-bottom: 0px;
  }
  p.position {
    margin-top: 0px;
    margin-bottom: 0px;
    font-style: italic;
  }
  div.bio {
    padding: 6px 6px 6px 80px;
    float: right;
    border-radius: 3px;
  }
  p.name {
    font-size: 1.15em;
    font-weight: bold;
    margin-bottom: 0px;
  }
</style>

<!--
<div class="bio">
  <p class="name">Darius Foo</p>
  darius.foo.tw at gmail<br/>
  https://dariusf.github.io<br/>
</div>
-->

<!--
hugo doesn't render template substitutions in {{ .Site.BaseURL }} in markdown without custom shortcodes.
also this floating bio penetrates the header boxes without a summary.
probably not needed anyway since i'll probably want a much shorter, standalone resume for distribution in future.
-->

# Resume

## Professional Experience

<p class="company">National University of Singapore</p>
<p class="position">PhD Student</p>
<!-- Graduate Tutor -->
Aug 2020 &ndash; Present

- Started my PhD!

<p class="company">SourceClear (and, by acquisition, Veracode)</p>
<p class="position">Senior Software Engineer</p>
May 2016 &ndash; Jul 2020
<!-- typographer doesn't work in files with inline html, apparently -->

- Worked on the SourceClear Agent, a tool which uses a combination of static analysis and instrumentation to discover and automatically upgrade library dependencies from CI/CD pipelines.
- Maintained a code analysis pipeline for precomputing partial static analysis results for large numbers of open source libraries.
- Authored 4 papers with colleagues on the following tools:
    + Update Advisor, a scalable static analysis for detecting breaking changes in order to perform automated library upgrades safely.
    + Sapling, a web app which optimizes story assignments for SAFe PI Planning using answer set programming.
    + SGL, a domain-specific graph query language able to represent security vulnerabilities.

<details markdown="1" style="padding-bottom: 1em;">

  <summary>Past</summary>

<div style="padding: 15px; border: solid 1px var(--faint-color);">

<p class="company">Experimental Systems & Technology Lab<br/>Ministry of Education Singapore</p>
<p class="position">Software Engineering Intern</p>
Jun 2015 &ndash; Aug 2015

- Worked on [Coursemology](https://coursemology.org/), an open source, gamified education platform used in select modules at NUS and various schools in Singapore.

<p class="company">National University of Singapore (NUS)</p>
<p class="position">Teaching Assistant</p>
Aug 2013 &ndash; Dec 2015

- Led discussion group sessions and graded assignments in [CS1101S](https://www.comp.nus.edu.sg/~cs1101s/), an accelerated introduction to programming based on the text _Structure and Interpretation of Computer Programs (Abelson, Sussman)_ and conducted in JavaScript.
- Maintained a source-to-source JavaScript-to-Java compiler used by students to run their JavaScript programs on Lego NXT robots.

<p class="company">Singapore University of Technology and Design</p>
<p class="position">Programmer</p>
Dec 2013 &ndash; Feb 2014

- Worked on [Getzapp](https://www.youtube.com/watch?v=HjXklXXprAA), an educational puzzle game. Released commercially.

<p class="company">Game Innovation Programme<br/>Singapore University of Technology and Design</p>
<p class="position">Intern (Programmer)</p>
May 2013 &ndash; Aug 2013

- Developed [Tower of Myr: Crystal Stream](https://www.youtube.com/watch?v=1nM9Xh58SYU), a turn-based strategy game for Android. Implemented major parts of the gameplay and user interface.

<!-- --- -->
</div>

</details>

## Education

**BComp (Computer Science)**<br/>
National University of Singapore<br/>
2012 -- 2016

## Skills

- OCaml, Haskell, Java, Python, Bash, JS
- Spring Boot, React
- Docker, Kubernetes
- Unity
