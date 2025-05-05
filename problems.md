---
title: "Problems"
layout: default
---

# Construction Problems

<ul>
  {% for problem in site.problems %}
    <li>{{ problem.path }}</li>
  {% else %}
    <li>No problems found. Check _config.yml and _problems/ folder.</li>
  {% endfor %}
</ul>